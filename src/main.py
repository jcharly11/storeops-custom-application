import json
import logging
import queue
import signal
import time
import datetime
import os
from typing import Any
import config.settings as settings
from fastapi import FastAPI, Response, Request

from logging.config import dictConfig
from fastapi import FastAPI
from fastapi_mqtt import FastMQTT, MQTTConfig
from fastapi_utils.tasks import repeat_every
from database.model.datamaster import Datamaster
from fastapi.responses import  JSONResponse, PlainTextResponse
from database.model.epc_inventory_API import EPC_Inventory_API
from database.model.epc_unknown_API import EPC_Unknown_API

from database.model.item import Item
from models import LogConfig
from services import RESTService, MQTTService
from database.model.event_EPCs import EventEPCs
from database.model.epcs import EPCS
from services.csv_service import CSV_Service
from services.sftp_service import SFTP_Service
from database.db import dataBase
from database.datamaster_db import datamasterDB
from utils.environment_validator import EnvironmentValidator
from utils.time_functions import TimeUtils
from utils.task_create_csv import taskCreateCSV
from utils.task_delete_policy import TaskDeletePolicy
import uuid
from typing import Dict, Any

# globals
# queue for event processing
EnvironmentValidator()

event_queue = queue.Queue()
error_queue = queue.Queue()
alarm_queue = queue.Queue()
data_master_queue = queue.Queue()
data_events_list = []
# application logging
dictConfig(LogConfig().dict())
logger = logging.getLogger("main")
# main application
app = FastAPI()
timer = TimeUtils()
sftp_service= SFTP_Service()
taskCSV = taskCreateCSV()
taskDeletePolicy = TaskDeletePolicy()
# mqtt support
mqtt_config = MQTTConfig(host=settings.MQTT_SERVER, port=settings.MQTT_PORT,
                         keepalive=settings.MQTT_KEEP_ALIVE)
mqtt = FastMQTT(config=mqtt_config)
mqtt.init_app(app)
# MQTT service
mqtt_service = MQTTService(mqtt=mqtt)
# REST service
rest_service = RESTService(
    url=settings.SERVER_URL, timeout=settings.SERVER_TIMEOUT_SEC, mqtt_service=mqtt_service)

csv_service = CSV_Service()
sftp_service= SFTP_Service()
db_service= dataBase()
datmaster_db_service= datamasterDB()

settings.timeout_create_csv = datetime.datetime.now() + datetime.timedelta(seconds=settings.SHEDULE_CREATE_CSV_FILES)
settings.timeout_clean_old = datetime.datetime.now() - datetime.timedelta(seconds=settings.SHEDULE_CLEAN_OLD_INFO)

# callback for internal MQTT connect
@mqtt.on_connect()
def connect(client, flags, rc, properties):
    logger.info(f"MQTT Connected")


# callback for internal MQTT disconnect
@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    logger.info(f"MQTT Disconnected")


# callback for all alarms (alarm)
@mqtt.subscribe(settings.TOPIC_ALARM)
async def message_to_topic_wirama_epc_all(client, topic, payload, qos, properties):
    logger.debug(
        f"MQTT Received message to specific topic: {topic}, {payload.decode()}, {qos}, {properties}")
    if not settings.CUSTOM_APP_ALARM_DECISION_ENABLED:
        event_queue.put(payload.decode())

@mqtt.subscribe(settings.TOPIC_CUSTOM_NOTIFICATION_ALARM)
async def message_to_topic_wirama_epc_all(client, topic, payload, qos, properties):
    logger.debug(
        f"MQTT Received message to specific topic: {topic}, {payload.decode()}, {qos}, {properties}")
    if settings.CUSTOM_APP_ALARM_DECISION_ENABLED:
        event_queue.put(payload.decode())

# callback for server forbidden-tags errors
@mqtt.subscribe(settings.TOPIC_SERVER_STATS+'/forbidden-tags/errors/#')
async def message_to_topic_forbidden_tags_errors(client, topic, payload, qos, properties):
    logger.debug(
        f"MQTT Received message to specific topic: {topic}, {payload.decode()}, {qos}, {properties}")
    error_queue.put(payload.decode())


# callback for server user-login errors
@mqtt.subscribe(settings.TOPIC_SERVER_STATS+'/user-login/errors/#')
async def message_to_topic_user_login_errors(client, topic, payload, qos, properties):
    logger.debug(
        f"MQTT Received message to specific topic: {topic}, {payload.decode()}, {qos}, {properties}")
    error_queue.put(payload.decode())


# callback for store/info
@mqtt.subscribe(settings.TOPIC_CUSTOM_METHOD)
async def message_to_topic_store_info(client, topic, payload, qos, properties):
    logger.debug(
        f"MQTT Received message for custom app status: {topic}, {payload.decode()}, {qos}, {properties}")
    try:
        json_item = json.loads(payload.decode())

        if "type" in json_item and "defaultAlarming" in json_item:
            if json_item["type"] == "custom":
                if json_item["defaultAlarming"] == 0:
                    settings.CUSTOM_APP_ALARM_DECISION_ENABLED = True
                else:
                    settings.CUSTOM_APP_ALARM_DECISION_ENABLED = False

    except Exception as err:
        logger.error(f"Unexpected {err}, {type(err)}")


# callback for store/info
@mqtt.subscribe(settings.TOPIC_STORE_INFO)
async def message_to_topic_store_info(client, topic, payload, qos, properties):
    logger.debug(
        f"MQTT Received message to specific topic: {topic}, {payload.decode()}, {qos}, {properties}")
    try:
        json_item = json.loads(payload.decode())
        
        if "storeNumber" in json_item:
            settings.STORE_NUMBER = json_item["storeNumber"]
        if "serialNumber" in json_item:
            settings.DEVICE_ID = json_item["serialNumber"]
 
        if "doorNumber" in json_item:
            settings.DOOR_NUMBER = json_item["doorNumber"]

        if "accountNumber" in json_item:
            settings.ACCOUNT_ID= json_item["accountNumber"]

    except Exception as err:
        logger.error(f"Unexpected {err}, {type(err)}")


# check the event queue every set schedule
@app.on_event("startup")
@repeat_every(seconds=settings.SCHEDULE_PROCESS_EVENTS_SEC, wait_first=True)
def process_events_queue() -> None:
    try:
        epcs = []
       
        if(event_queue.qsize() > 0):
            time.sleep(settings.ALARM_AGGREGATION_WINDOW_SEC)
            alarm_type= 22 #Silence
            is_first = True
            while not event_queue.empty():
                alarm = json.loads(event_queue.get())
                if is_first:
                    event_time = datetime.datetime.strptime(alarm["extraPayload"]["timestamp"], '%Y-%m-%d %H:%M:%S.%f')
                    is_first = False
                if alarm["extraPayload"]["audible_alarm"]:
                    alarm_type = 21 #Sound alarm
                
                if len(alarm["extraPayload"]["epc"]) > 0: 
                    epcs.append(alarm["extraPayload"]["epc"])

            if len(epcs) > 0:
                id = uuid.uuid4().__str__()
                alarm_event = { "event": EventEPCs(
                                            id_event= id,
                                            store_number=settings.STORE_NUMBER,
                                            event_code=401,
                                            alarm_type=alarm_type,
                                            inventory_alarm=31,
                                            event_date= event_time.strftime("%m/%d/%Y").__str__(),
                                            event_time= event_time.strftime('%H:%M:%S.%f')[:-5],
                                            alarm_direction=3,
                                            SGLN="SFERO",
                                            pedestal_id=0,
                                            account_id=settings.ACCOUNT_ID,
                                            door_id=settings.DOOR_NUMBER,
                                            date=event_time.strftime("%m%d%Y_%H-%M-%S"),
                                            datetime_inserted=event_time.isoformat(),
                                            csv_general_created=False,
                                            csv_created= False
                                        ),
                                "epcs": epcs
                }
                logger.info(f"Received alarm with epcs: {epcs}")
                alarm_queue.put(alarm_event)
        else:
            # prevent high CPU usage
            time.sleep(10/1000)

    except Exception as err:
        logger.error(f"process_events_queue {err}, {type(err)}")


# refresh authentication token a minute before an hour
# @app.on_event("startup")
# @repeat_every(seconds=settings.SCHEDULE_AUTH_TOKEN_REFRESH_SEC, wait_first=False)
# def authenticate_token_refresh() -> None:
#     logger.info("Refreshing the authentication token...")
#     try:
#         # TODO: Add code logic for refreshing authentication token
#         logger.warning(f"Add authentication code...")
#         # Example code to authenticate to REST server
#         # rest_service.authenticate(username=settings.SERVER_USERNAME, password=settings.SERVER_PASSWORD)
#     except Exception as err:
#         logger.error(f"authenticate_token_refresh {err}, {type(err)}")


# check authentication token every minute
# @app.on_event("startup")
# @repeat_every(seconds=settings.SCHEDULE_AUTH_TOKEN_CHECK_SEC, wait_first=True)
# def authenticate_token_check() -> None:
#     logger.debug("Checking the authentication token...")
#     try:
#         # TODO: Add code logic for checking authentication token
#         logger.warning(f"Add authentication code...")
#         # Example code to authenticate to REST server
#         # if rest_service.token == None:
#         #     rest_service.authenticate(
#         #         username=settings.SERVER_USERNAME, password=settings.SERVER_PASSWORD)
#     except Exception as err:
#         logger.error(f"authenticate_token_check {err}, {type(err)}")


# check the error queue every set schedule and log to errors.log file
@app.on_event("startup")
@repeat_every(seconds=settings.SCHEDULE_PROCESS_ERRORS_SEC, wait_first=True)
def process_errors_queue() -> None:
    logger.debug(f"Processing errors queue...")
    try:
        if not error_queue.empty():
            with open("./logs/errors.log", "a+") as errors_file:
                while not error_queue.empty():
                    errors_file.write(error_queue.get()+"\n")
    except Exception as err:
        logger.error(f"process_errors_queue {err}, {type(err)}")


# need to send store/info request?
@app.on_event("startup")
@repeat_every(seconds=settings.SCHEDULE_STORE_INFO_SEC, wait_first=False)
def check_for_store_info_request() -> None:
    logger.debug(f"Checking if need to send store/info request")
    try:
        # request for the information if any of the properties were empty
        if settings.DEVICE_ID == 'EMPTY' or settings.LOCATION_ID == 'EMPTY':
            mqtt_service.send_store_info_get()
    except Exception as err:
        logger.error(f"check_for_store_info_request {err}, {type(err)}")


# inform other services to enable custom method
@app.on_event("startup")
@repeat_every(seconds=settings.SCHEDULE_CUSTOM_METHOD_SEC, wait_first=False)
def notify_custom_method() -> None:
    logger.debug(f"Checking if need to send store/info request")
    try:
        #mqtt_service.send_custom_method(default_alarming=0)
        pass
    except Exception as err:
        logger.error(f"notify_custom_method {err}, {type(err)}")


# inform other services to disable custom method
@app.on_event("shutdown")
def notify_disable_custom_method() -> None:
    logger.debug(f"Sending request to disable custom method")
    try:
        #mqtt_service.send_custom_method(default_alarming=1)
        pass
    except Exception as err:
        logger.error(f"notify_disable_custom_method {err}, {type(err)}")




@app.get("/api/events/inventory",status_code=200)
def get_epcs_inventory() -> Any:
    try:
        master = datmaster_db_service.getdatamaster()

        inventory=list()

        #cruzar contra data master
        for event in data_events_list:
            timestamp= event[0]
            epc_event= event[1]
            alarm_type_value= event[2]
            description=""
            image=""
            alarm_type=""

            if(alarm_type_value=="21"):
                alarm_type="ALARM"
            else:
                alarm_type="SILENT ALARM"
                
            for data in master:
                epc_datamaster= str(data[0])
                if(epc_datamaster==epc_event):
                    description= data[1]
                    sku= data[2]
                    image= data[3]
                    #date= data[4]        
                    inventory.append(EPC_Inventory_API(epc_event,timestamp,alarm_type,description,image,sku))
                    break

        return inventory
    
    except Exception as err:
        logger.error(f"error inventory API {err}, {type(err)}")
        return list()

@app.get("/api/events/unknown",status_code=200)
def get_epcs_unknown() -> Any:
    try:
        master = datmaster_db_service.getdatamaster()

        unknown= list()

        #cruzar contra data master
        for event in data_events_list:
            in_datamaster = False
            timestamp= event[0]
            epc_event= event[1]
            alarm_type_value= event[2]
            description=""
            image=""
            alarm_type=""

            if(alarm_type_value=="21"):
                alarm_type="ALARM"
            else:
                alarm_type="SILENT ALARM"
                
            for data in master:
                epc_datamaster= str(data[0])
                if(epc_datamaster==epc_event):
                    in_datamaster = True
                    break

            if not in_datamaster:
                unknown.append(EPC_Unknown_API(epc_event,alarm_type,timestamp))
    
        return unknown
    
    except Exception as err:
        logger.error(f"error unknown API {err}, {type(err)}")
        return list()


@app.post("/api/events/datamaster", status_code=200)
def save_datamaster(response: Response, item: Item ) -> Any:
    #logger.info(f"Received: {item.type}, {item.sku}, {item.epc},{item.description},{item.image}")
    datmaster_db_service.insert_datamaster(item)
    data = {"saved":True}
    return JSONResponse(content=data)



@app.post("/api/events/delete_datamaster", status_code=200)
def delete_datamaster() -> Any:
    logger.info(f"deleting")
    
    datmaster_db_service.delete_datamaster()
    data = {"deleted":True}
    return JSONResponse(content=data)


@app.post("/api/events/clear_data", status_code=200)
def clear_data() -> Any:
    logger.info(f"clear data")
    data_events_list.clear()
    
    data = {"data all cleared":True}
    return JSONResponse(content=data)





@app.on_event("startup")
@repeat_every(seconds=0.1, wait_first=False)
def process_events_database() -> None:
    process_alarm_queue()
    create_csv_files()
    clear_old_info()



def process_alarm_queue():
    try:
        iterations = 0
        while not alarm_queue.empty() and iterations<100:
            iterations += 1
            alarm_event = alarm_queue.get()
        
            id_event= alarm_event["event"].id_event.__str__()
            
          
            db_service.save_event(event = alarm_event["event"])
            for epc in alarm_event["epcs"]:
                db_service.save_epcc(epcs=EPCS(idEvent= id_event, epc=epc))

                #Add to the visualizator list
                data_events_list.insert(0,[alarm_event['event'].datetime_inserted.__str__(), epc, alarm_event['event'].alarm_type.__str__()])
                if len (data_events_list) > settings.EVENT_VIEWER_MAX_LENGTH:
                    data_events_list.pop(len(data_events_list)-1)

            taskCSV.createGeneralCSV(True)
    except Exception as err:
        logger.error(f"process_events_database {err}, {type(err)}")

def create_csv_files():
    try:
        if(settings.CREATE_CSV_FILES_ENABLE==1):
            if datetime.datetime.now() > settings.timeout_create_csv:
                logger.debug("Executing csv task")
                settings.timeout_create_csv = datetime.datetime.now() + datetime.timedelta(seconds=settings.SHEDULE_CREATE_CSV_FILES)
                taskCSV.createCSVFile()
                sftp_service.send_files_sftp()
    except Exception as err:
        logger.error(f"CSV ERROR {err}, {type(err)}")


def clear_old_info():
 try:
     if datetime.datetime.now() > settings.timeout_clean_old:
         logger.debug("Clear old info task")
         settings.timeout_clean_old = datetime.datetime.now() + datetime.timedelta(seconds=settings.SHEDULE_CLEAN_OLD_INFO)
         taskCSV.cleanOldData(settings.CSV_STORE_DAYS)
         logger.debug("Clear data old than 24hrs in general csv")
         #taskDeletePolicy.cleanData()
 except Exception as err:
     logger.error(f"Clean old data ERROR {err}, {type(err)}")


@app.get("/restart", status_code=200)
def restart_application():
    os.kill(os.getpid(),signal.SIGKILL)
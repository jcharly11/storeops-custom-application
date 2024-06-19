import json
import logging
import queue
import time
import datetime
import uuid
import config.settings as settings
import os
import signal

from logging.config import dictConfig
from fastapi import FastAPI
from fastapi_mqtt import FastMQTT, MQTTConfig
from fastapi_utils.tasks import repeat_every

from models import LogConfig
from services import RESTService, MQTTService
from services.sharepoint_service import SharepointService
from utils.environment_validator import EnvironmentValidator


# globals
# queue for event processing

environment = EnvironmentValidator()
event_queue = queue.Queue()
error_queue = queue.Queue()
# application logging
dictConfig(LogConfig().dict())
logger = logging.getLogger("main")
# main application
app = FastAPI()
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

sharepoint_service= SharepointService()

# callback for internal MQTT connect
@mqtt.on_connect()
def connect(client, flags, rc, properties):
    logger.info(f"MQTT Connected")


# callback for internal MQTT disconnect
@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    logger.info(f"MQTT Disconnected")


# callback for all epc events
@mqtt.subscribe(settings.TOPIC_WIRAMA_EPC_ALL)
async def message_to_topic_wirama_epc_all(client, topic, payload, qos, properties):
    logger.debug(
        f"MQTT Received message to specific topic: {topic}, {payload.decode()}, {qos}, {properties}")
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
@mqtt.subscribe(settings.TOPIC_STORE_INFO)
async def message_to_topic_store_info(client, topic, payload, qos, properties):
    logger.debug(
        f"MQTT Received message to specific topic: {topic}, {payload.decode()}, {qos}, {properties}")
    try:
        json_item = json.loads(payload.decode())
        if "storeNumber" in json_item:
            settings.LOCATION_ID = json_item["storeNumber"]
        if "serialNumber" in json_item:
            settings.DEVICE_ID = json_item["serialNumber"]
    except Exception as err:
        logger.error(f"Unexpected {err}, {type(err)}")


# callback for restart application
@mqtt.subscribe(settings.TOPIC_RESTART_APPLICATION)
async def message_restart_application(client, topic, payload, qos, properties):
    logger.info(
        f"MQTT Received restart custom application: {payload.decode()}")
    try:
        logger.info(f"Restarting custom application")
        os.kill(os.getpid(),signal.SIGKILL)
    except Exception as err:
        logger.info(
        f"Error restarting custom application: {err}")


# check the event queue every set schedule
@app.on_event("startup")
@repeat_every(seconds=settings.SCHEDULE_PROCESS_EVENTS_SEC, wait_first=True)
def process_events_queue() -> None:
    try:
        epcs = []
        while not event_queue.empty():
            json_item = json.loads(event_queue.get())
            # check if EAS event type
            if "type" in json_item and json_item["type"] == "eas":
                # check if not suppressed
                if "event_type" in json_item and json_item["event_type"] != 2:
                    # capture epc
                    if "epc" in json_item:
                        epcs.append(json_item["epc"])

        if len(epcs) > 0:
            logger.info(f"{len(epcs)} epc is available")
            # TODO: Add code logic for the detected EPC
            logger.warning(f"Add EPC processing code...")
            # Example codes to request for audible sound and led light
            # mqtt_service.send_voice_alarm(light=settings.ALARM_NORMAL_LIGHT_ENABLE, light_color=settings.ALARM_NORMAL_LIGHT_COLOR, sound=settings.ALARM_NORMAL_SOUND_ENABLE, sound_volume=settings.ALARM_NORMAL_SOUND_VOLUME)
            # mqtt_service.send_voice_alarm(light=settings.ALARM_DELAYED_LIGHT_ENABLE, light_color=settings.ALARM_DELAYED_LIGHT_COLOR, sound=settings.ALARM_DELAYED_SOUND_ENABLE, sound_volume=settings.ALARM_DELAYED_SOUND_VOLUME)
        else:
            # prevent high CPU usage
            time.sleep(10/1000)
    except Exception as err:
        logger.error(f"process_events_queue {err}, {type(err)}")


# refresh authentication token a minute before an hour
@app.on_event("startup")
@repeat_every(seconds=settings.SCHEDULE_AUTH_TOKEN_REFRESH_SEC, wait_first=False)
def authenticate_token_refresh() -> None:
    logger.info("Refreshing the authentication token...")
    try:
        # TODO: Add code logic for refreshing authentication token
        logger.warning(f"Add authentication code...")
        # Example code to authenticate to REST server
        # rest_service.authenticate(username=settings.SERVER_USERNAME, password=settings.SERVER_PASSWORD)
    except Exception as err:
        logger.error(f"authenticate_token_refresh {err}, {type(err)}")


# check authentication token every minute
@app.on_event("startup")
@repeat_every(seconds=settings.SCHEDULE_AUTH_TOKEN_CHECK_SEC, wait_first=True)
def authenticate_token_check() -> None:
    logger.debug("Checking the authentication token...")
    try:
        # TODO: Add code logic for checking authentication token
        logger.warning(f"Add authentication code...")
        # Example code to authenticate to REST server
        # if rest_service.token == None:
        #     rest_service.authenticate(
        #         username=settings.SERVER_USERNAME, password=settings.SERVER_PASSWORD)
    except Exception as err:
        logger.error(f"authenticate_token_check {err}, {type(err)}")


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
@repeat_every(seconds=settings.SCHEDULE_STORE_INFO_SEC, wait_first=True)
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
        mqtt_service.send_custom_method(default_alarming=0)
    except Exception as err:
        logger.error(f"notify_custom_method {err}, {type(err)}")


# inform other services to disable custom method
@app.on_event("shutdown")
def notify_disable_custom_method() -> None:
    logger.debug(f"Sending request to disable custom method")
    try:
        mqtt_service.send_custom_method(default_alarming=1)
    except Exception as err:
        logger.error(f"notify_disable_custom_method {err}, {type(err)}")




#ONVIF MQTT MESSAGES
@mqtt.subscribe(settings.TOPIC_CAMERA_IMAGE_RESP)
async def message_topic_camera_image(client, topic, payload, qos, properties):
    logger.info(f"Starting upload image")
    try:
        json_item = json.loads(payload.decode())
        image = json_item['data']["image"] 
        if image:
            uuid_name= uuid.uuid4()
            filename= f"{uuid_name}.png"
            sharepoint_service.upload_file(data=image,file= filename)

    except Exception as ex:
        logger.error(f"Error executing upload image task: {ex}")

    

@mqtt.subscribe(settings.TOPIC_CAMERA_IMAGE_BUFFER_RESP)
async def message_topic_camera_buffer(client, topic, payload, qos, properties):
    logger.info(f"Starting upload buffer")
    try:
        json_item = json.loads(payload.decode())
        image_list = json_item['data']["image_buffer"] 
        if image_list:
            for image in image_list:
                uuid_name= uuid.uuid4()
                filename= f"{uuid_name}.png"
                sharepoint_service.upload_file(data=image,file= filename)

    except Exception as ex:
        logger.error(f"Error executing upload buffer task: {ex}")


@mqtt.subscribe(settings.TOPIC_CAMERA_VIDEO_RESP)
async def message_topic_camera_video(client, topic, payload, qos, properties):
    logger.info(f"Starting upload video")
    try:
        json_item = json.loads(payload.decode())
        path = json_item['data']["destination_path"] 
        file_name = json_item['data']["file_name"] 
        uuid = json_item['header']["uuid"] 
        sharepoint_service.upload_video(uuid=uuid, path=path)

    except Exception as ex:
        logger.error(f"Error executing upload video task: {ex}")


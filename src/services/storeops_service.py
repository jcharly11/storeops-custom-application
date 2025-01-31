import traceback
import sys
from database.database import DataBase
import threading
import logging
from utils.time_utils import DateUtils
from utils.log_message_utils import LogMessagesUtil
import json
import multiprocessing as mp 
import config.storeops_settings as settings
from config.settings import TOPIC_RESTART_APPLICATION
import time
import datetime
from messages.storeops_messages import StoreOpsMessage, CommandMessage
from mqtt.client_ssl import ClientSSL
from mqtt.client import Client
from utils.restart import Restart

class StoreopsService():
    
    TOPIC_STORE_INFO = "store/info"
    TOPIC_COMMAND_LOCAL = "command/storeops/#"
    TOPIC_COMMAND_RESP_LOCAL = "command_resp/storeops"

    CUSTOMER_ID = 'EMPTY'
    STORE_ID = '-1'
    DEVICE_ID = 'EMPTY'
    DEVICE_TYPE = 'SFERO'
    TOPIC_RESTART_APPLICATION = TOPIC_RESTART_APPLICATION

    def __init__(self, environment) -> None:
        self.logger = logging.getLogger("main")
        self.log_prefix = "storeops_service"
        self.context_intialized = False
        self.database = DataBase()
        self.storeopsQueue = mp.Queue()
        self.storeopInternalQueue = mp.Queue() 
        self.clientSSL =  ClientSSL(environment = environment)
        self.clientSSL.instance().on_message = self.onMessageStoreOps
        self.restart = Restart()
        self.messageLogger = LogMessagesUtil()
        self.messageLogger.create()


        self.command_topic = ""
        self.clientLocal = Client().instance()
        self.clientLocal.on_message = self.onMessageLocal
        self.clientLocal.subscribe(self.TOPIC_STORE_INFO)
        self.clientLocal.subscribe(self.TOPIC_COMMAND_LOCAL)
        self.clientLocal.subscribe(self.TOPIC_RESTART_APPLICATION)
        self.clientLocal.publish(topic= self.TOPIC_STORE_INFO, payload= json.dumps({'type':'get'}) )

        self.subscribers = []

        thread = threading.Thread(target=self.storeopsThread)
        thread.start()
        
        self.messages = []
        self.dateUtils =  DateUtils()
        self.nextRetrySendStoreops = datetime.datetime.now()
        self.nextOldMessageRemove = datetime.datetime.now()

        threadDB = threading.Thread(target=self.storeopsDatabaseThread)
        threadDB.start()

        
    def subscribeToStoreOpsCommand(self):
        if self.context_intialized:
            new_command_topic = f"checkpoint/{self.CUSTOMER_ID}/{self.STORE_ID}/service/command/#"
            if self.command_topic != new_command_topic:
                self.logger.info(f"{self.log_prefix}: subscribe to storeOps command topic {new_command_topic}")
                self.clientSSL.subscribe(new_command_topic)
                if self.command_topic != "":
                    self.logger.info(f"{self.log_prefix}: Unsubscribe to storeOps old command topic {new_command_topic}")
                    self.clientSSL.unsubscribe(self.command_topic)
                self.command_topic = new_command_topic

        
    def publishToStoreops(self, message): 
        try:
           
            if isinstance(message, StoreOpsMessage):
                self.storeopsQueue.put(message)
            else:
                self.logger.error(f"{self.log_prefix}: publishToStoreops tried to publish not correct message {message}")
                
        except Exception as err:
            self.logger.error(f"{self.log_prefix}: publishToStoreops {err}, {type(err)}")
   

    def subscribeResponses(self, subscriber):
        if subscriber is not None:
            self.subscribers.append(subscriber)


    def publishResponseToSubscribers(self, message):
        self.logger.info(f"{self.log_prefix}: push to subscribers {message}")

        for sub in self.subscribers:
            try:
                sub.processStoreopsMessage(message)
            except Exception as err:
                self.logger.error(f"{self.log_prefix}: publishResponseToSubscribers sub {sub} has not function processStoreopsMessage: {err}, {type(err)}")

    
    def saveVariables(self, file):
        file.write(f"export STOREOPS_MQTT_SSL_SERVER={settings.STOREOPS_MQTT_SSL_SERVER}"+ "\n")
        file.write(f"export STOREOPS_RETRY_SEND_MIN={settings.STOREOPS_RETRY_SEND_MIN}"+ "\n")
        file.write(f"export STOREOPS_KEEP_MESSAGES_DAYS={settings.STOREOPS_KEEP_MESSAGES_DAYS}"+ "\n")

        file.write(f"export STOREOPS_CERTIFICATES_REQUEST_USER={settings.STOREOPS_CERTIFICATES_REQUEST_USER}"+ "\n")
        file.write(f"export STOREOPS_CERTIFICATES_REQUEST_PASS={settings.STOREOPS_CERTIFICATES_REQUEST_PASS}"+ "\n")
        file.write(f"export STOREOPS_CERTIFICATES_REQUEST_URL={settings.STOREOPS_CERTIFICATES_REQUEST_URL}"+ "\n")
        


    def storeopsThread(self): 
        while True:
            try:
                time.sleep(0.1)
                while self.storeopsQueue.qsize() > 0:
                    message = self.storeopsQueue.get()
                    self.logger.info(f"{self.log_prefix}: Message storeopsThread:{message} of type {message.type}")

                    if message.type  == 'internal':
                        #Only for internal command, not for sending mqtt anywhere
                        pass
                    else:
                        sent = self.sendMessage(message)
                        if sent is not True:
                            self.logger.info(f"{self.log_prefix}: Message send to internal queue to database")
                            self.storeopInternalQueue.put({'type':'message', 'message': message, 'sent': sent})
        
            except Exception as err:
                self.logger.error(f"{self.log_prefix}: storeopsThread {err}, {type(err)}")
                self.logger.error(traceback.format_exc())
                self.logger.error(sys.exc_info()[2])



    def storeopsDatabaseThread(self): 
        while True:
            try:
                time.sleep(0.1)
                now = datetime.datetime.now()

                while self.storeopInternalQueue.qsize() > 0:
                    message = self.storeopInternalQueue.get()
                    
                    if message['type'] == 'message':                    
                        message_status = 'not_sent'
                        if message['sent']:
                            message_status = 'sent' 
                        self.database.saveMessage( message = message, message_status= message_status)            

                self.retrySendToStoreops(now)
                self.removeOldMessages(now)
                #check conexion con borker ssl
                self.checkSSLConnection()

            except Exception as err:
                self.logger.error(f"{self.log_prefix}: storeopsDatabaseThread {err}, {type(err)}")
                self.logger.error(traceback.format_exc())
                self.logger.error(sys.exc_info()[2])

    
    def sendMessage(self, message):
        sentToStoreops = False
        payload = self.getMessagePayloadToSend(message) 
        
        if payload is None:
            return False

        if message.send_local:
            topic = self.getLocalTopic(message)
            self.logger.info(f"{self.log_prefix}: Sending local: {message.send_local} to topic: {topic}")
            if topic is not None:                                 
                result = self.clientLocal.publish(topic= topic, payload= json.dumps(payload) )
                self.logger.info(f"{self.log_prefix}: Result message : {result} ")

        if message.send_storeops:
            topic = self.getStoreopsTopic(message) 
            self.logger.info(f"{self.log_prefix}: Sending storeOps: {message.send_storeops} to topic: {topic}")
            if topic is not None:                        
                #self.logger.info(f"Message for External MQTT: {json.dumps(payload)} ")
                result = self.clientSSL.publish(topic = topic, payload = json.dumps(payload) )
                self.logger.info(f"{self.log_prefix}: Result message : {result} ")
                if result:
                    self.messageLogger.save(message=message)
                    sentToStoreops = True
        else:
            sentToStoreops = True
  
        return sentToStoreops

    def getLocalTopic(self, message):
        if message.type == 'event':
            return f"event/storeops/{message.event_id}"
        elif message.type == 'status':
            return f"status/storeops/{message.status_id}"
        elif message.type == 'configuration':
            return f"config/storeops/{message.configuration_id}"
        elif message.type == 'command':
            return f"command/storeops/{message.command_id}"
        elif message.type == 'response':
            return f"command_resp/storeops/{message.response_id}"
        return None

    def getStoreopsTopic(self, message):
        if message.type == 'event':
            return f"checkpoint/{message.technology}/{message.customer}/{message.store}/event/{message.group}/{message.event_id}"
        elif message.type == 'status':
            return f"checkpoint/{message.technology}/{message.customer}/{message.store}/status/{message.group}/{message.status_id}"
        elif message.type == 'configuration':
            return f"checkpoint/{message.technology}/{message.customer}/{message.store}/configuration/{message.group}/{message.configuration_id}"
        elif message.type == 'command':
            return f"checkpoint/{message.customer}/{message.store}/service/command/{message.command_id}"
        elif message.type == 'response':
            return f"checkpoint/{message.customer}/{message.store}/service/response/{message.response_id}"
        return None

    def getMessagePayloadToSend(self, message):
        message_to_send = None
        if message.type == 'event' or message.type == 'status' or message.type == 'configuration':
            message_to_send = {
                                'uuid': message.uuid,
                                'timestamp': message.timestamp,
                                'device_model': message.device_model,
                                'device_id': message.device_id,
                                'version': message.version,
                                'data': message.data
            }
        elif message.type == 'command':
            message_to_send = {
                                'uuid': message.uuid,
                                'timestamp': message.timestamp,
                                'version': message.version,
                                'destination': message.destination,
                                'expiration_date': message.expiration_date,
                                'data': message.data
            }
        elif message.type == 'response':
            message_to_send = {
                                'uuid': message.uuid,
                                'uuid_request': message.uuid_request,
                                'timestamp': message.timestamp,
                                'version': message.version,
                                'data': message.data
            }
        return message_to_send


    def retrySendToStoreops(self, now):
        if now > self.nextRetrySendStoreops:
            self.nextRetrySendStoreops = now + datetime.timedelta(minutes=int(settings.STOREOPS_RETRY_SEND_MIN))
            #Get any message from database with status "not_sent" and retry sending (only to storeOps not internal)
            self.messages = self.database.getMessages(status='not_sent', date= now)
            for message in self.messages: 
                message.send_local = False
                self.logger.info(f"{self.log_prefix}: Retry of message {message}")
                if self.sendMessage(message=message):
                    self.database.upadateMessage(request_id=message['uui'], status = 'sent')


    def removeOldMessages(self, now):
        now = datetime.datetime.now()
        timeout_retry = datetime.timedelta(hours=4)
        rt =  + timeout_retry.total_seconds()

        if now > self.nextOldMessageRemove:
            self.nextOldMessageRemove = now + datetime.timedelta(hours=int(settings.STOREOPS_CHECK_OLD_MESSAGES_HOUS))
            self.logger.info(f"{self.log_prefix}: Remove old messages in database.")
            self.database.deleteOldMessage(now - datetime.timedelta(hours=int(settings.STOREOPS_KEEP_MESSAGES_DAYS)))
             
    def checkSSLConnection(self): 
        if  not self.clientSSL.isConnected():
            self.clientSSL.reconnect()


    def onMessageLocal(self, client, userdata, message, properties=None):
        try:
            payload = json.loads(message.payload.decode())
            topic = message.topic

            if topic == self.TOPIC_RESTART_APPLICATION:
                self.logger.info(f"Restarting custom application")
                self.restart.run()

            if topic == self.TOPIC_STORE_INFO:
                if "isResponse" in payload:
                    if payload["isResponse"]:
                        if "storeNumber" in payload:
                            self.STORE_ID = payload["storeNumber"]
                        if "serialNumber" in payload:
                            self.DEVICE_ID = payload["serialNumber"]
                        if "accountNumber" in payload:
                            self.CUSTOMER_ID= payload["accountNumber"]
                        if "systemType" in payload:
                            if payload["systemType"] == "apollo":
                                self.DEVICE_TYPE = 'SFERO'
                            else:
                                self.DEVICE_TYPE = 'AB_WIRAMA'

                        self.context_intialized = True
                        self.clientSSL.setAccountAndDevice(self.CUSTOMER_ID, self.DEVICE_ID)
                        self.subscribeToStoreOpsCommand()

            elif topic.startswith(self.TOPIC_COMMAND_LOCAL[:-1]):
                self.logger.info(f"{self.log_prefix}: Receive local command {payload}")
                self.publishReceivedCommand(topic, payload, send_local=True)


        except Exception as err:
            self.logger.error(f"{self.log_prefix}: onMessageLocal: Error: {err}, TypeError: {type(err)}")

    def onMessageStoreOps(self, client, userdata, message, properties=None):
        try:
            if not self.context_intialized:
                return

            payload = json.loads(message.payload.decode())
            topic = message.topic
            isDestinationCorrect = False

            for dest in payload["destination"]:
                if dest == self.DEVICE_ID:
                    isDestinationCorrect= True
                    break

            if isDestinationCorrect:
                self.logger.info(f"{self.log_prefix}: Command directed to me")
                expiration_date = datetime.datetime.fromisoformat(payload["expiration_date"])
                if expiration_date > datetime.datetime.now():
                    self.publishReceivedCommand(topic, payload, send_storeops=True)
                else:
                    self.logger.info(f"{self.log_prefix}: Command expired")
        except Exception as err:
            self.logger.error(f"{self.log_prefix}: onMessageStoreOps: Error: {err}, TypeError: {type(err)}")

    def publishReceivedCommand(self, topic, payload, send_local=False, send_storeops=False):
        command = CommandMessage()
        command.customer = self.CUSTOMER_ID
        command.store = self.STORE_ID
        command.command_id = topic.rpartition('/')[-1]
        command.uuid = payload["uuid"]
        command.version = payload["version"]
        if "destination" in payload:
            command.destination = payload["destination"]
        else:
            command.destination.append(self.DEVICE_ID)
        command.data = payload["data"]
        command.timestamp = self.dateUtils.getDateISOFormat()
        command.send_local = send_local
        command.send_storeops = send_storeops
        self.publishResponseToSubscribers(command)


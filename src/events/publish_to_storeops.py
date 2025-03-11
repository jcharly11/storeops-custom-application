from events.event_class import Event
from messages.storeops_messages import StatusMessage, EventMessage, ConfigurationMessage, ResponseMessage, InfoMessage
from utils.time_utils import DateUtils

import logging
import os
import queue
import time
import uuid
import datetime
import config.settings as settings
import json

class PublishToStoreops(Event):

    #Allows send to local/storeOps any kind of message:
    #Needed payload:
    # { "id":"name of the event",
    #   "type": "type of event",
    #   "device_id": device_id to use. Optional value,
    #   "uuid_request": uuid_request to use. Optional value,
    #   "expiration_date": expiration date of message. Optional value
    #   "is_local": True/False, Optional value, True by default
    #   "send_storeops": True/False, Optional value, True by default
    #   "version": "version of message"
    #   "data": []
    # }

    PUBLISH_STOREOPS_ID = 'publish_to_storeops_id'
    STATUS_ID = 'status'
    EVENT_ID = 'event'
    CONF_ID = 'configuration'
    RESPONSE_ID = 'response'
    INFO_ID = 'info'

    PUBLISH_TO_STOREOPS_TOPIC = 'status/publish_to_storeops'
    PUBLISH_COMMAND_FROM_STOREOPS = 'command/command_from_storeops'
    PUBLISH_INFO_FROM_STOREOPS = 'info_resp/info_from_storeops'

    def __init__(self, mqtt_client, sharepointService, storeopsService, environment):
        super().__init__( mqtt_client=mqtt_client, sharepointService=sharepointService, storeopsService=storeopsService, enable_thread = True, environment=environment)
        self.logger = logging.getLogger("main")

        self.addTopicToSubscribe(self.PUBLISH_TO_STOREOPS_TOPIC)
        self.event_queue = queue.Queue()
        self.forceSendConf = True
        self.dateUtils = DateUtils()


    def updateVariablesToSave(self, variables):
        pass


    def processTopic(self, topic, payload):
        super().processTopic(topic, payload)
        
        if topic == self.PUBLISH_TO_STOREOPS_TOPIC:
            self.event_queue.put(payload)

    
    def eventThread(self):
        while True:
            try:
                time.sleep(0.1)

                if self.isContextInitialized():
                    while not self.event_queue.empty():
                        json_item = json.loads(self.event_queue.get())
                        self.logger.info(f"{self.PUBLISH_STOREOPS_ID}: received petition to forward message {json_item}")
                        self.sendMessageToStoreOps(json_item)

            except Exception as err:
                self.logger.error(f"{self.PUBLISH_STOREOPS_ID} eventThread {err}, {type(err)}")
                
    
    def sendMessageToStoreOps(self, message_to_send):
        try:
            if message_to_send["type"] == self.STATUS_ID:
                message = self.prepareHeaderMessage(StatusMessage())
                message.status_id = message_to_send["id"]
            elif message_to_send["type"] == self.EVENT_ID:
                message = self.prepareHeaderMessage(EventMessage())
                message.event_id = message_to_send["id"]
            elif message_to_send["type"] == self.CONF_ID:
                message = self.prepareHeaderMessage(ConfigurationMessage())
                message.configuration_id = message_to_send["id"]
            elif message_to_send["type"] == self.RESPONSE_ID:
                message = self.prepareHeaderMessage(ResponseMessage())
                message.response_id = message_to_send["id"]
                message.uuid_request = message_to_send["uuid_request"]
            elif message_to_send["type"] == self.INFO_ID:
                message = self.prepareHeaderMessage(InfoMessage())
                message.info_id = message_to_send["id"]
                if "expiration_date" in  message_to_send:
                    message.expiration_date = message_to_send["uuid_request"]
                else:
                    message.expiration_date = self.dateUtils.getDateISOFormat(offset_sec=3600)
            else:
                self.logger.info(f"{self.PUBLISH_STOREOPS_ID}: unknown type for message {message_to_send}")
                return

            if "device_id" in message_to_send:
                message.device_id = message_to_send["device_id"]

            if "send_local" in message_to_send:
                message.send_local = message_to_send["send_local"]

            if "send_storeops" in message_to_send:
                message.send_storeops = message_to_send["send_storeops"]

            message.version = message_to_send["version"]
            message.data = message_to_send["data"]

            self.logger.info(f"{self.PUBLISH_STOREOPS_ID}: send to storeops {message} from {message_to_send} received")
            self.publishToStoreops(message)

        except Exception as err:
            self.logger.error(f"{self.PUBLISH_STOREOPS_ID} sendMessageToStoreOps: message_to_send {message_to_send} not correct {err}")


    def processStoreopsMessage(self, message):
        try:
            if message.type == 'command':
                payload = {"uuid": message.uuid,
                           "command_id": message.command_id,
                           "destination": message.destination,
                           "timestamp": message.timestamp,
                           "version": message.version,
                           "data": message.data }

                self.publishInternalBroker(self.PUBLISH_COMMAND_FROM_STOREOPS, payload)
            elif message.type == 'info':
                payload = {"uuid": message.uuid,
                           "info_id": message.command_id,
                           "uuid_request": message.uuid_request,
                           "timestamp": message.timestamp,
                           "version": message.version,
                           "data": message.data }

                self.publishInternalBroker(self.PUBLISH_INFO_FROM_STOREOPS, payload)

        except Exception as err:
            self.logger.error(f"{self.PUBLISH_STOREOPS_ID} processStoreopsMessage: message_to_send {message} not correct {err}")

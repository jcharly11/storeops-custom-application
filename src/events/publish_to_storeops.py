from events.event_class import Event
from messages.storeops_messages import StatusMessage, EventMessage, ConfigurationMessage, ResponseMessage

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
    #   "is_local": True/False, Optional value, True by default
    #   "send_storeops": True/False, Optional value, True by default
    #   "version": "version of message"
    #   "data": []
    # }

    PUBLISH_STOREOPS_ID = 'publish_to_storeops_id'
    STATUS_ID = 'status'
    EVENT_ID = 'event'
    CONF_ID = 'configuration'

    PUBLISH_TO_STOREOPS_TOPIC = 'status/publish_to_storeops'

    def __init__(self, mqtt_client, sharepointService, storeopsService, environment):
        super().__init__( mqtt_client=mqtt_client, sharepointService=sharepointService, storeopsService=storeopsService, enable_thread = True, environment=environment)
        self.logger = logging.getLogger("main")

        self.addTopicToSubscribe(self.PUBLISH_TO_STOREOPS_TOPIC)
        self.event_queue = queue.Queue()
        self.forceSendConf = True


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
            else:
                self.logger.info(f"{self.PUBLISH_STOREOPS_ID}: unknown type for message {message_to_send}")
                return

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


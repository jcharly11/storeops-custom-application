from events.event_class import Event
from messages.storeops_messages import StatusMessage, ConfigurationMessage, ResponseMessage

import logging
import os
import queue
import time
import uuid
import datetime
import config.settings as settings
import json

class OnvifStatus(Event):

    ONVIF_ID = 'onvif_status'
    ONVIF_GET_ID = 'get_storeops_onvif_status'
    ONVIF_SET_ID = 'set_storeops_onvif_status'
    ONVIF_ENABLE_ID = 'onvif_status_enable'
    ONVIF_UPDATE_STATUS_HOURS_ID = 'onvif_status_update_hours'

    TOPIC_ONVIF_STATUS = 'status/onvif/camera'

    ONVIF_ENABLE = int(os.getenv("ONVIF_ENABLE", default=1))
    ONVIF_STATUS_UPDATE_HOURS = float(os.getenv("ONVIF_STATUS_UPDATE_HOURS", default=1.0))


    def __init__(self, mqtt_client, sharepointService, storeopsService, environment):
        super().__init__( mqtt_client=mqtt_client, sharepointService=sharepointService, storeopsService=storeopsService, enable_thread = True, environment=environment)
        self.logger = logging.getLogger("main")

        self.addTopicToSubscribe(self.TOPIC_ONVIF_STATUS)

        self.last_onvif_recv = None
        self.last_onvif_sent = None
        self.nextSendStatus = datetime.datetime.now()
        self.forceSendConf = True


    def updateVariablesToSave(self, variables):
        variables.append(("ONVIF_ENABLE", self.ONVIF_ENABLE))
        variables.append(("ONVIF_STATUS_UPDATE_HOURS", self.ONVIF_STATUS_UPDATE_HOURS))


    def processTopic(self, topic, payload):
        super().processTopic(topic, payload)
        
        if self.ONVIF_ENABLE:
            if topic == self.TOPIC_ONVIF_STATUS:
                self.last_onvif_recv = json.loads(payload)

    
    def eventThread(self):
        while True:
            try:
                time.sleep(0.1)
                now = datetime.datetime.now()

                if self.ONVIF_ENABLE:
                    self.sendPeriodicStatus(now)

                self.sendEventConfiguration()

            except Exception as err:
                self.logger.error(f"{self.ONVIF_ID} eventThread {err}, {type(err)}")
    

    def sendPeriodicStatus(self, now):
        if now > self.nextSendStatus and self.last_onvif_recv is not None and self.isContextInitialized():
            self.nextSendStatus = now + datetime.timedelta(hours=self.ONVIF_STATUS_UPDATE_HOURS)

            onvif_status = self.prepareHeaderMessage(StatusMessage())
            onvif_status.status_id = self.ONVIF_ID
            onvif_status.version = "1.0.0"

            if self.last_onvif_sent is not None and self.last_onvif_sent == self.last_onvif_recv:
                onvif_status.data.append({'key': 'status', 'type': 'string', 'value': ['error']})
            else:
                onvif_status.data.append({'key': 'status', 'type': 'string', 'value': [self.last_onvif_recv['data']['status'].lower()]})
                onvif_status.data.append({'key': 'online', 'type': 'string', 'value': [self.last_onvif_recv['data']['online']]})
                onvif_status.data.append({'key': 'ip', 'type': 'string', 'value': [self.last_onvif_recv['data']['ip']]})
                onvif_status.data.append({'key': 'port', 'type': 'string', 'value': [self.last_onvif_recv['data']['port']]})
                onvif_status.data.append({'key': 'image_taking_enable', 'type': 'string', 'value': [self.last_onvif_recv['data']['image_taking_enable']]})
                onvif_status.data.append({'key': 'video_recording', 'type': 'string', 'value': [self.last_onvif_recv['data']['video_recording']]})

            self.logger.info(f"{self.ONVIF_ID}: send {self.ONVIF_ID} message: {onvif_status}")
            self.publishToStoreops(onvif_status)


    def sendEventConfiguration(self):
        if self.forceSendConf and self.isContextInitialized():
            self.forceSendConf = False
            onvif_conf_message = self.prepareHeaderMessage(ConfigurationMessage())
            onvif_conf_message.configuration_id = self.ONVIF_ID
            onvif_conf_message.version = "1.0.0"
            onvif_conf_message.data.append({'key': self.ONVIF_ENABLE_ID, 'type': 'boolean', 'value': [self.ONVIF_ENABLE]})
            onvif_conf_message.data.append({'key': self.ONVIF_UPDATE_STATUS_HOURS_ID, 'type': 'float', 'value': [self.ONVIF_STATUS_UPDATE_HOURS]})

            self.logger.info(f"{self.ONVIF_ID}: send {self.ONVIF_ID} configuration message: {onvif_conf_message}")
            self.publishToStoreops(onvif_conf_message)


    def processStoreopsMessage(self, message):
        if message.type == 'command':
            if message.command_id == self.ONVIF_GET_ID:
                self.getStoreopsConf(message)
            elif message.command_id == self.ONVIF_SET_ID:
                self.setStoreopsConf(message)


    def getStoreopsConf(self, message):
        self.logger.info(f"{self.ONVIF_ID}: Received {message.command_id} configuration message: {message}")
        self.forceSendConf = True
        self.publishResponseToStoreops(self.ONVIF_ID, message.uuid, status='ok')


    def setStoreopsConf(self, message):
        try:
            self.logger.info(f"{self.ONVIF_ID}: Received {message.command_id} configuration message: {message}")
            for param in message.data:
                if param['key'] == self.ONVIF_ENABLE_ID:
                    self.ONVIF_ENABLE = int(param['value'][0])
                elif param['key'] == self.ONVIF_UPDATE_STATUS_HOURS_ID:
                    self.ONVIF_STATUS_UPDATE_HOURS = float(param['value'][0])

            self.updateLocalVariablesFile(restart=False)
            self.nextSendStatus = datetime.datetime.now()
            self.publishResponseToStoreops(self.ONVIF_ID, message.uuid, status='ok')
        except Exception as err:
            self.logger.error(f"{self.ONVIF_ID}: configuration message {message.command_id} error {err}, {type(err)}")
            self.publishResponseToStoreops(self.ONVIF_ID, message.uuid, status='error', details=str(err))

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

class WiramaStatus(Event):

    STATUS_ID = 'wirama_status'
    EVENT_GET_STOREOPS_CONF_ID = 'get_storeops_wirama_status'
    EVENT_SET_STOREOPS_CONF_ID = 'set_storeops_wirama_status'

    STATUS_ENABLE_ID = 'wirama_status_enable'
    STATUS_UPDATE_HOURS_ID = 'wirama_status_update_hours'

    TOPIC_WIRAMA_ENABLED = 'Wirama/Devices/enabled'

    WIRAMA_STATUS_ENABLE = int(os.getenv("WIRAMA_STATUS_ENABLE", default=1))
    WIRAMA_STATUS_UPDATE_HOURS = float(os.getenv("WIRAMA_STATUS_UPDATE_HOURS", default=1.0))

    STATUS_ASK_INTERNAL_STATUS_MIN = 5

    def __init__(self, mqtt_client, sharepointService, storeopsService, environment):
        super().__init__( mqtt_client=mqtt_client, sharepointService=sharepointService, storeopsService=storeopsService, enable_thread = True, environment=environment)
        self.logger = logging.getLogger("main")

        self.addTopicToSubscribe(self.TOPIC_WIRAMA_ENABLED)

        self.last_wirama_enabled = None

        self.nextSendStatus = datetime.datetime.now() + datetime.timedelta(hours=self.WIRAMA_STATUS_UPDATE_HOURS)
        self.askWiramaEnable = datetime.datetime.now() - datetime.timedelta(minutes=self.STATUS_ASK_INTERNAL_STATUS_MIN)

        self.forceSendEventConf = True
        self.forceSendStatus = False


    def updateVariablesToSave(self, variables):
        variables.append(("WIRAMA_STATUS_ENABLE", self.WIRAMA_STATUS_ENABLE))
        variables.append(("WIRAMA_STATUS_UPDATE_HOURS", self.WIRAMA_STATUS_UPDATE_HOURS))


    def processTopic(self, topic, payload):
        super().processTopic(topic, payload)
        
        if self.WIRAMA_STATUS_ENABLE:
            if topic == self.TOPIC_WIRAMA_ENABLED:
                json_item = json.loads(payload)
                if "readers" in json_item:
                    if self.last_wirama_enabled is None:
                        self.forceSendStatus = True
                    self.last_wirama_enabled = json_item

    
    def eventThread(self):
        while True:
            try:
                time.sleep(0.1)
                now = datetime.datetime.now()

                if self.WIRAMA_STATUS_ENABLE:
                    self.askInternalStatus(now)
                    self.sendPeriodicStatus(now)

                self.sendEventConfiguration()

            except Exception as err:
                self.logger.error(f"{self.STATUS_ID} eventThread {err}, {type(err)}")
                
    
    def askInternalStatus(self, now):
        if now > self.askWiramaEnable:
            self.askWiramaEnable = now + datetime.timedelta(minutes=self.STATUS_ASK_INTERNAL_STATUS_MIN)
            self.publishInternalBroker(self.TOPIC_WIRAMA_ENABLED, {'type':'get'})


    def sendPeriodicStatus(self, now):

        if not self.isContextInitialized():
            return

        if now > self.nextSendStatus or self.forceSendStatus:
            self.nextSendStatus = now + datetime.timedelta(hours=self.WIRAMA_STATUS_UPDATE_HOURS)
            self.forceSendStatus = False

            for reader in self.last_wirama_enabled["readers"]:
                wirama_status = self.prepareHeaderMessage(StatusMessage())
                wirama_status.status_id = self.STATUS_ID
                wirama_status.version = "1.0.0"
                wirama_status.data.append({'key': 'serialNumber', 'type': 'string', 'value': [reader['serialNumber']]})
                wirama_status.data.append({'key': 'ip', 'type': 'string', 'value': [reader['ip']]})
                wirama_status.data.append({'key': 'fwVersion', 'type': 'string', 'value': [reader['fwVersion']]})
                wirama_status.data.append({'key': 'position', 'type': 'string', 'value': [reader['position']]})
                wirama_status.data.append({'key': 'role', 'type': 'string', 'value': [reader['role']]})
                wirama_status.data.append({'key': 'expectedFwVersion', 'type': 'string', 'value': [reader['expectedFwVersion']]})
                wirama_status.data.append({'key': 'isConfigured', 'type': 'boolean', 'value': [reader['isConfigured']]})
                wirama_status.data.append({'key': 'uptime', 'type': 'float', 'value': [reader['uptime']]})
                wirama_status.data.append({'key': 'autoRunState', 'type': 'string', 'value': [reader['autoRunState']]})
                wirama_status.data.append({'key': 'profile', 'type': 'string', 'value': [reader['profile']]})
                wirama_status.data.append({'key': 'isOnline', 'type': 'boolean', 'value': [reader['isOnline']]})
                wirama_status.data.append({'key': 'configurationVersion', 'type': 'string', 'value': [reader['configurationVersion']]})
                wirama_status.data.append({'key': 'expectedConfigurationVersion', 'type': 'string', 'value': [reader['expectedConfigurationVersion']]})
                wirama_status.data.append({'key': 'isFinalized', 'type': 'boolean', 'value': [reader['isFinalized']]})
                wirama_status.data.append({'key': 'isSuppressionOn', 'type': 'boolean', 'value': [reader['isSuppressionOn']]})
                wirama_status.data.append({'key': 'isWhitelistOn', 'type': 'boolean', 'value': [reader['isWhitelistOn']]})
                wirama_status.data.append({'key': 'isRawFilterOn', 'type': 'boolean', 'value': [reader['isRawFilterOn']]})
                wirama_status.data.append({'key': 'isScheduleLearnOn', 'type': 'boolean', 'value': [reader['isScheduleLearnOn']]})
                wirama_status.data.append({'key': 'txBand', 'type': 'string', 'value': [reader['txBand']]})
                wirama_status.data.append({'key': 'region', 'type': 'string', 'value': [reader['region']]})

                self.logger.info(f"{self.STATUS_ID}: send {self.STATUS_ID} message: {wirama_status}")
                self.publishToStoreops(wirama_status)        


    def sendEventConfiguration(self):
        if self.forceSendEventConf and self.isContextInitialized():
            self.forceSendEventConf = False
            wirama_status_conf_status = self.prepareHeaderMessage(ConfigurationMessage())
            wirama_status_conf_status.configuration_id = self.STATUS_ID
            wirama_status_conf_status.version = "1.0.0"
            wirama_status_conf_status.data.append({'key': self.STATUS_ENABLE_ID, 'type': 'boolean', 'value': [self.WIRAMA_STATUS_ENABLE]})
            wirama_status_conf_status.data.append({'key': self.STATUS_UPDATE_HOURS_ID, 'type': 'float', 'value': [self.WIRAMA_STATUS_UPDATE_HOURS]})

            self.logger.info(f"{self.STATUS_ID}: send {self.STATUS_ID} storeops configuration message: {wirama_status_conf_status}")
            self.publishToStoreops(wirama_status_conf_status)


    def processStoreopsMessage(self, message):
        if message.type == 'command':
            if message.command_id == self.EVENT_GET_STOREOPS_CONF_ID:
                self.getStoreopsConf(message)
            elif message.command_id == self.EVENT_SET_STOREOPS_CONF_ID:
                self.setStoreopsConf(message)


    def getStoreopsConf(self, message):
        self.logger.info(f"{self.STATUS_ID}: Received {message.command_id} configuration message: {message}")
        self.forceSendEventConf = True
        self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='ok', exec_date=response_conf.timestamp)


    def setStoreopsConf(self, message):
        try:
            self.logger.info(f"{self.STATUS_ID}: Received {message.command_id} configuration message: {message}")
            for param in message.data:
                if param['key'] == self.STATUS_ENABLE_ID:
                    self.WIRAMA_STATUS_ENABLE = int(param['value'][0])
                elif param['key'] == self.STATUS_UPDATE_HOURS_ID:
                    self.WIRAMA_STATUS_UPDATE_HOURS = float(param['value'][0])
                    
            self.updateLocalVariablesFile(restart=False)
            self.nextSendStatus = datetime.datetime.now()
            self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='ok', exec_date=response_conf.timestamp)
        except Exception as err:
            self.logger.error(f"{self.STATUS_ID}: storeops configuration message {message.command_id} error {err}, {type(err)}")
            self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='error', exec_date=response_conf.timestamp, details=str(err))

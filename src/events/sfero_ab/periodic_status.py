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

class AlarmBoxPeriodicStatus(Event):

    STATUS_ID = 'periodic_status'
    EVENT_GET_STATUS_ID = 'get_storeops_periodic_status'
    EVENT_SET_STATUS_ID = 'set_storeops_periodic_status'
    STATUS_PERIODIC_ENABLE_ID = 'periodic_status_enable'
    STATUS_PERIODIC_UPDATE_HOURS_ID = 'periodic_status_update_hours'

    TOPIC_WIRAMA_ENABLED = 'Wirama/Devices/enabled'
    TOPIC_ONVIF_STATUS = 'status/onvif/camera'

    STATUS_PERIODIC_ENABLE = int(os.getenv("STATUS_PERIODIC_ENABLE", default=1))
    STATUS_PERIODIC_UPDATE_HOURS = float(os.getenv("STATUS_PERIODIC_UPDATE_HOURS", default=1.0))

    STATUS_ASK_INTERNAL_STATUS_MIN = 5

    def __init__(self, mqtt_client, sharepointService, storeopsService, environment):
        super().__init__( mqtt_client=mqtt_client, sharepointService=sharepointService, storeopsService=storeopsService, enable_thread = True, environment=environment)
        self.logger = logging.getLogger("main")

        self.addTopicToSubscribe(self.TOPIC_WIRAMA_ENABLED)
        self.addTopicToSubscribe(self.TOPIC_ONVIF_STATUS)

        self.last_wirama_enabled = None
        self.last_onvif_enabled = None
        self.is_initialized = False
        self.sent_wirama_enabled = None
        self.sent_uptime = time.monotonic() + float(self.STATUS_PERIODIC_UPDATE_HOURS * 3600)

        self.nextSendStatus = datetime.datetime.now() 
        self.askWiramaEnable = datetime.datetime.now() - datetime.timedelta(minutes=self.STATUS_ASK_INTERNAL_STATUS_MIN)

        self.forceSendConf = True


    def updateVariablesToSave(self, variables):
        variables.append(("STATUS_PERIODIC_ENABLE", self.STATUS_PERIODIC_ENABLE))
        variables.append(("STATUS_PERIODIC_UPDATE_HOURS", self.STATUS_PERIODIC_UPDATE_HOURS))


    def processTopic(self, topic, payload):
        super().processTopic(topic, payload)
        
        if self.STATUS_PERIODIC_ENABLE:
            if topic == self.TOPIC_WIRAMA_ENABLED:
                json_item = json.loads(payload)
                if "readers" in json_item:
                    self.last_wirama_enabled = json_item
            elif topic == self.TOPIC_ONVIF_STATUS:
                self.last_onvif_enabled = json.loads(payload)

    
    def eventThread(self):
        while True:
            try:
                time.sleep(0.1)
                now = datetime.datetime.now()

                if self.STATUS_PERIODIC_ENABLE:
                    self.askWiramaEnableTopic(now)
                    self.sendPeriodicStatus(now)

                self.sendEventConfiguration()

            except Exception as err:
                self.logger.error(f"{self.STATUS_ID} eventThread {err}, {type(err)}")
                
    
    def askWiramaEnableTopic(self, now):
        if now > self.askWiramaEnable:
            self.askWiramaEnable = now + datetime.timedelta(minutes=self.STATUS_ASK_INTERNAL_STATUS_MIN)
            payload = { "type":"get" }
            self.publishInternalBroker(self.TOPIC_WIRAMA_ENABLED, payload)


    def sendPeriodicStatus(self, now):
        force_sending = False
        uptime = time.monotonic()
        current_status = 'ok'
        current_details = ''

        if not self.is_initialized and self.isContextInitialized():
            if self.last_wirama_enabled is not None:
                self.is_initialized = True
                force_sending = True
                self.sent_wirama_enabled = self.last_wirama_enabled

        if self.is_initialized:
            if force_sending or now > self.nextSendStatus:
                if self.sent_uptime > uptime:
                    current_status = 'warning'
                    current_details += 'reboot alarm box;'
                
                if self.last_onvif_enabled is not None:
                    if self.last_onvif_enabled['data']['status'] == 'DISABLED':
                        current_status = 'warning'
                        current_details += 'onvif camera disabled;'

                if len(self.last_wirama_enabled['readers']) > len(self.sent_wirama_enabled['readers']):
                    current_status = 'warning'
                    for last_reader in self.last_wirama_enabled['readers']:
                        found = False
                        for sent_reader in self.sent_wirama_enabled['readers']:
                            if sent_reader['serialNumber'] == last_reader['serialNumber']:
                                found = True
                        if not found:
                            current_details += f"added wirama {last_reader['serialNumber']} reader;"
                else:
                    for sent_reader in self.sent_wirama_enabled['readers']:
                        for last_reader in self.last_wirama_enabled['readers']:
                            if sent_reader['serialNumber'] == last_reader['serialNumber']:
                                if sent_reader['uptime'] > last_reader['uptime']:
                                    current_status = 'warning'
                                    current_details += f"reboot wirama reader {sent_reader['serialNumber']};"


                if len(self.last_wirama_enabled['readers']) < len(self.sent_wirama_enabled['readers']):
                    current_status = 'error'
                    for sent_reader in self.sent_wirama_enabled['readers']:
                        found = False
                        for last_reader in self.last_wirama_enabled['readers']:
                            if sent_reader['serialNumber'] == last_reader['serialNumber']:
                                found = True
                        if not found:
                            current_details += f"removed wirama {sent_reader['serialNumber']}reader;"
                else:
                    for last_reader in self.last_wirama_enabled['readers']:
                        if not last_reader['isOnline'] or last_reader['autoRunState'] != "Run":
                            current_status = 'error'
                            current_details += f"wirama reader {sent_reader['serialNumber']} stopped or not running;"

                self.sent_uptime = uptime
                self.sent_wirama_enabled = self.last_wirama_enabled

                self.nextSendStatus = now + datetime.timedelta(hours=self.STATUS_PERIODIC_UPDATE_HOURS)

                periodic_status = self.prepareHeaderMessage(StatusMessage())
                periodic_status.status_id = self.STATUS_ID
                periodic_status.version = "1.0.0"
                periodic_status.data.append({'key': 'status', 'type': 'string', 'value': [current_status]})
                periodic_status.data.append({'key': 'details', 'type': 'string', 'value': [current_details]})
                periodic_status.data.append({'key': 'additional_info', 'type': 'string', 'value': []})
                periodic_status.data.append({'key': 'uptime', 'type': 'float', 'value': [self.sent_uptime]})

                self.logger.info(f"{self.STATUS_ID}: send {self.STATUS_ID} message: {periodic_status}")
                self.publishToStoreops(periodic_status)


    def sendEventConfiguration(self):
        if self.forceSendConf and self.isContextInitialized():
            self.forceSendConf = False
            periodic_status_conf_status = self.prepareHeaderMessage(ConfigurationMessage())
            periodic_status_conf_status.configuration_id = self.STATUS_ID
            periodic_status_conf_status.version = "1.0.0"
            periodic_status_conf_status.data.append({'key': self.STATUS_PERIODIC_ENABLE_ID, 'type': 'boolean', 'value': [self.STATUS_PERIODIC_ENABLE]})
            periodic_status_conf_status.data.append({'key': self.STATUS_PERIODIC_UPDATE_HOURS_ID, 'type': 'float', 'value': [self.STATUS_PERIODIC_UPDATE_HOURS]})

            self.logger.info(f"{self.STATUS_ID}: send {self.STATUS_ID} configuration message: {periodic_status_conf_status}")
            self.publishToStoreops(periodic_status_conf_status)


    def processStoreopsMessage(self, message):
        if message.type == 'command':
            if message.command_id == self.EVENT_GET_STATUS_ID:
                self.getStoreopsConf(message)
            elif message.command_id == self.EVENT_SET_STATUS_ID:
                self.setStoreopsConf(message)


    def getStoreopsConf(self, message):
        self.logger.info(f"{self.STATUS_ID}: Received {message.command_id} configuration message: {message}")
        self.forceSendConf = True
        self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='ok')


    def setStoreopsConf(self, message):
        try:
            self.logger.info(f"{self.STATUS_ID}: Received {message.command_id} configuration message: {message}")
            for param in message.data:
                if param['key'] == self.STATUS_PERIODIC_ENABLE_ID:
                    self.STATUS_PERIODIC_ENABLE = int(param['value'][0])
                elif param['key'] == self.STATUS_PERIODIC_UPDATE_HOURS_ID:
                    self.STATUS_PERIODIC_UPDATE_HOURS = float(param['value'][0])
                    
            self.updateLocalVariablesFile(restart=False)
            self.nextSendStatus = datetime.datetime.now()
            self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='ok')
        except Exception as err:
            self.logger.error(f"{self.STATUS_ID}: configuration message {message.command_id} error {err}, {type(err)}")
            self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='error', details=str(err))

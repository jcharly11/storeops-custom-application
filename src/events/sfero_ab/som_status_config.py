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
from deepdiff import DeepDiff

class SomStatusConfig(Event):

    STATUS_ID = 'som_status'
    CONFIG_ID = 'som_config'
    EVENT_GET_STOREOPS_CONF_ID = 'get_storeops_som_status'
    EVENT_SET_STOREOPS_CONF_ID = 'set_storeops_som_status'
    EVENT_GET_CONFIG_ID = 'get_som_config'

    STATUS_ENABLE_ID = 'som_status_enable'
    STATUS_UPDATE_HOURS_ID = 'som_status_update_hours'
    CONFIG_UPDATE_HOURS_ID = 'som_config_update_hours'

    TOPIC_WIRAMA_ENABLED = 'Wirama/Devices/enabled'
    TOPIC_ONVIF_STATUS = 'status/onvif/camera'
    TOPIC_STORE_INFO = "store/info"
    TOPIC_ALARM_CONFIGURATION = "data/settings/alarm/get"
    TOPIC_ALARM_CONFIGURATION_REQUEST = "command/settings/alarm/get"

    SOM_STATUS_ENABLE = int(os.getenv("SOM_STATUS_ENABLE", default=1))
    SOM_STATUS_UPDATE_HOURS = float(os.getenv("SOM_STATUS_UPDATE_HOURS", default=1.0))
    SOM_CONFIG_UPDATE_HOURS = float(os.getenv("SOM_CONFIG_UPDATE_HOURS", default=24.0))

    STATUS_ASK_INTERNAL_STATUS_MIN = 5

    def __init__(self, mqtt_client, sharepointService, storeopsService, environment):
        super().__init__( mqtt_client=mqtt_client, sharepointService=sharepointService, storeopsService=storeopsService, enable_thread = True, environment=environment)
        self.logger = logging.getLogger("main")

        self.addTopicToSubscribe(self.TOPIC_WIRAMA_ENABLED)
        self.addTopicToSubscribe(self.TOPIC_ONVIF_STATUS)
        self.addTopicToSubscribe(self.TOPIC_STORE_INFO)
        self.addTopicToSubscribe(self.TOPIC_ALARM_CONFIGURATION)

        self.last_wirama_enabled = None
        self.last_onvif_enabled = None
        self.last_store_info = None
        self.sent_store_info = None
        self.last_alarm_info = None
        self.sent_alarm_info = None

        self.nextSendStatus = datetime.datetime.now() + datetime.timedelta(hours=self.SOM_STATUS_UPDATE_HOURS)
        self.nextSendConfig = datetime.datetime.now() + datetime.timedelta(hours=self.SOM_CONFIG_UPDATE_HOURS)
        self.askWiramaEnable = datetime.datetime.now() - datetime.timedelta(minutes=self.STATUS_ASK_INTERNAL_STATUS_MIN)

        self.forceSendEventConf = True
        self.forceSendStatus = False
        self.forceSendConf = True


    def updateVariablesToSave(self, variables):
        variables.append(("SOM_STATUS_ENABLE", self.SOM_STATUS_ENABLE))
        variables.append(("SOM_STATUS_UPDATE_HOURS", self.SOM_STATUS_UPDATE_HOURS))
        variables.append(("SOM_CONFIG_UPDATE_HOURS", self.SOM_CONFIG_UPDATE_HOURS))


    def processTopic(self, topic, payload):
        super().processTopic(topic, payload)
        
        try:
            if self.SOM_STATUS_ENABLE:
                if topic == self.TOPIC_WIRAMA_ENABLED:
                    json_item = json.loads(payload)
                    if "readers" in json_item:
                        if self.last_wirama_enabled is None:
                            self.forceSendStatus = True
                        self.last_wirama_enabled = json_item
                elif topic == self.TOPIC_ONVIF_STATUS:
                    if self.last_onvif_enabled is None:
                        self.forceSendStatus = True
                    self.last_onvif_enabled = json.loads(payload)
                elif topic == self.TOPIC_STORE_INFO:
                    json_item = json.loads(payload)
                    if "isResponse" in json_item and "type" in json_item:
                        if json_item["isResponse"] == True and json_item["type"] == "get":
                            json_item["session"] = ""
                            self.last_store_info = json_item
                elif topic == self.TOPIC_ALARM_CONFIGURATION:
                    self.last_alarm_info = json.loads(payload)["data"]
                
        except Exception as err:
            self.logger.error(f"{self.STATUS_ID} processTopic {err}, {type(err)}")

    
    def eventThread(self):
        while True:
            try:
                time.sleep(0.1)
                now = datetime.datetime.now()

                if self.SOM_STATUS_ENABLE:
                    self.askInternalStatus(now)
                    self.sendPeriodicStatus(now)
                    self.sendPeriodicConfiguration(now)

                self.sendEventConfiguration()

            except Exception as err:
                self.logger.error(f"{self.STATUS_ID} eventThread {err}, {type(err)}")
                
    
    def askInternalStatus(self, now):
        if now > self.askWiramaEnable:
            self.askWiramaEnable = now + datetime.timedelta(minutes=self.STATUS_ASK_INTERNAL_STATUS_MIN)
            self.publishInternalBroker(self.TOPIC_WIRAMA_ENABLED, {'type':'get'})
            self.publishInternalBroker(self.TOPIC_STORE_INFO, {'type':'get'})
            self.publishInternalBroker(self.TOPIC_ALARM_CONFIGURATION_REQUEST, {'id': uuid.uuid4().__str__()})


    def sendPeriodicStatus(self, now):
        uptime = time.monotonic()
        current_status = 'ok'
        current_details = ''
        childs = []
        childs_type = []

        if not self.isContextInitialized():
            return

        if now > self.nextSendStatus or self.forceSendStatus:
            self.nextSendStatus = now + datetime.timedelta(hours=self.SOM_STATUS_UPDATE_HOURS)
            self.forceSendStatus = False

            if self.last_wirama_enabled is not None:
                for last_reader in self.last_wirama_enabled['readers']:
                    childs.append(last_reader['serialNumber'])
                    childs_type.append("wirama")

            if self.last_onvif_enabled is not None:
                childs.append(f"{self.DEVICE_ID}_onvif")
                childs_type.append("onvif")

            som_status = self.prepareHeaderMessage(StatusMessage())
            som_status.status_id = self.STATUS_ID
            som_status.version = "1.0.0"
            som_status.data.append({'key': 'childs', 'type': 'string', 'value': childs})
            som_status.data.append({'key': 'childs_type', 'type': 'string', 'value': childs_type})
            som_status.data.append({'key': 'uptime', 'type': 'float', 'value': [uptime]})
            #IP/MASK/GW WAN
            #DNS WAN
            #VPN STATUS AND IP
            #NTP
            #CPU
            #MEMORY
            #DISK
            #SW VERSION

            self.logger.info(f"{self.STATUS_ID}: send {self.STATUS_ID} message: {som_status}")
            self.publishToStoreops(som_status)        

    
    def sendPeriodicConfiguration(self, now):
        if not self.isContextInitialized():
            return

        if self.last_store_info == None or self.last_alarm_info == None:
            return

        diff = DeepDiff(self.last_store_info, self.sent_store_info)
                                                        
        if diff:                                                                        
            self.logger.info(f'{self.STATUS_ID} config has changed. Force send it again: {diff}')                                                 
            self.forceSendConf = True

        diff = DeepDiff(self.last_alarm_info, self.sent_alarm_info)
                                                        
        if diff:                                                                        
            self.logger.info(f'{self.STATUS_ID} alarm config has changed. Force send it again: {diff}')                                                 
            self.forceSendConf = True


        if now > self.nextSendConfig or self.forceSendConf:
            self.nextSendConfig = now + datetime.timedelta(hours=self.SOM_CONFIG_UPDATE_HOURS)
            self.forceSendConf = False
            self.sent_store_info = self.last_store_info
            self.sent_alarm_info = self.last_alarm_info
            
            som_configuration = self.prepareHeaderMessage(ConfigurationMessage())
            som_configuration.configuration_id = self.CONFIG_ID
            som_configuration.version = "1.0.0"
            som_configuration.data.append({'key': 'suppressionEnabled', 'type': 'boolean', 'value': [self.last_store_info['suppressionEnabled']]})
            som_configuration.data.append({'key': 'lognewEasEnabled', 'type': 'boolean', 'value': [self.last_store_info['lognewEasEnabled']]})
            som_configuration.data.append({'key': 'region', 'type': 'string', 'value': [self.last_store_info['region']]})
            for store_day in self.last_store_info['storeHours']:
                day = []
                day.append(store_day['name'])
                day.append(str(store_day['isCustom']))
                day.append(store_day['day'])
                day.append(store_day['open_time'])
                day.append(store_day['close_time'])
                day.append(str(store_day['lightDisabled']))
                day.append(str(store_day['soundDisabled']))
                day.append(str(store_day['readerInvOutsideStoreHours']))
                som_configuration.data.append({'key': f'storeHours_{store_day["id"]}', 'type': 'string', 'value': day})
            whitelist = []
            whitelist.append(str(self.last_store_info['whitelistSettings']['isEnabled']))
            whitelist.append(self.last_store_info['whitelistSettings']['url'])
            whitelist.append(self.last_store_info['whitelistSettings']['updateTime'])
            whitelist.append(str(self.last_store_info['whitelistSettings']['updateDelayMin']))
            som_configuration.data.append({'key': 'whitelistSettings', 'type': 'string', 'value': whitelist})

            som_configuration.data.append({'key': 'lightEnabled', 'type': 'boolean', 'value': [self.last_alarm_info['lightEnabled']]})
            som_configuration.data.append({'key': 'lightColor', 'type': 'string', 'value': [self.last_alarm_info['lightColor']]})
            som_configuration.data.append({'key': 'volume', 'type': 'integer', 'value': [self.last_alarm_info['volume']]})

            self.logger.info(f"{self.STATUS_ID}: send {self.CONFIG_ID} message: {som_configuration}")
            self.publishToStoreops(som_configuration)


    def sendEventConfiguration(self):
        if self.forceSendEventConf and self.isContextInitialized():
            self.forceSendEventConf = False
            som_status_conf_status = self.prepareHeaderMessage(ConfigurationMessage())
            som_status_conf_status.configuration_id = self.STATUS_ID
            som_status_conf_status.version = "1.0.0"
            som_status_conf_status.data.append({'key': self.STATUS_ENABLE_ID, 'type': 'boolean', 'value': [self.SOM_STATUS_ENABLE]})
            som_status_conf_status.data.append({'key': self.STATUS_UPDATE_HOURS_ID, 'type': 'float', 'value': [self.SOM_STATUS_UPDATE_HOURS]})
            som_status_conf_status.data.append({'key': self.CONFIG_UPDATE_HOURS_ID, 'type': 'float', 'value': [self.SOM_CONFIG_UPDATE_HOURS]})

            self.logger.info(f"{self.STATUS_ID}: send {self.STATUS_ID} storeops configuration message: {som_status_conf_status}")
            self.publishToStoreops(som_status_conf_status)


    def processStoreopsMessage(self, message):
        if message.type == 'command':
            if message.command_id == self.EVENT_GET_STOREOPS_CONF_ID:
                self.getStoreopsConf(message)
            elif message.command_id == self.EVENT_SET_STOREOPS_CONF_ID:
                self.setStoreopsConf(message)
            elif message.command_id == self.EVENT_GET_CONFIG_ID:
                self.getCurrentEventConf(message)


    def getStoreopsConf(self, message):
        self.logger.info(f"{self.STATUS_ID}: Received {message.command_id} configuration message: {message}")
        self.forceSendEventConf = True
        self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='ok', exec_date=response_conf.timestamp)

    def getCurrentEventConf(self, message):
        self.logger.info(f"{self.STATUS_ID}: Received {message.command_id} message: {message}")
        self.forceSendConf = True
        self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='ok', exec_date=response_conf.timestamp)

    def setStoreopsConf(self, message):
        try:
            self.logger.info(f"{self.STATUS_ID}: Received {message.command_id} configuration message: {message}")
            for param in message.data:
                if param['key'] == self.STATUS_ENABLE_ID:
                    self.SOM_STATUS_ENABLE = int(param['value'][0])
                elif param['key'] == self.STATUS_UPDATE_HOURS_ID:
                    self.SOM_STATUS_UPDATE_HOURS = float(param['value'][0])
                elif param['key'] == self.CONFIG_UPDATE_HOURS_ID:
                    self.SOM_CONFIG_UPDATE_HOURS = float(param['value'][0])
                    
            self.updateLocalVariablesFile(restart=False)
            self.nextSendStatus = datetime.datetime.now()
            self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='ok', exec_date=response_conf.timestamp)
        except Exception as err:
            self.logger.error(f"{self.STATUS_ID}: storeops configuration message {message.command_id} error {err}, {type(err)}")
            self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='error', exec_date=response_conf.timestamp, details=str(err))

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

class SomCommands(Event):

    STATUS_ID = 'som_commands'

    SOM_COMMAND_SET_VOLUME = 'som_command_set_volume'
    SOM_COMMAND_UPGRADE = 'som_command_upgrade'
    SOM_COMMAND_REBOOT = 'som_command_reboot'

    SOM_COMMAND_SET_VOLUME_NEW_ID = 'set_volume'

    UPDATE_VOLUME_TOPIC = 'command/settings/alarm/update'
    TOPIC_ALARM_CONFIGURATION_REQUEST = 'command/settings/alarm/get'
    TOPIC_ALARM_CONFIGURATION = 'data/settings/alarm/get'

    TOPIC_REBOOT_REQUEST = 'manage/reboot'
    TOPIC_UPDATE_FIRMWARE_REQUEST = 'UpdateFirmware'

    def __init__(self, mqtt_client, sharepointService, storeopsService, environment):
        super().__init__( mqtt_client=mqtt_client, sharepointService=sharepointService, storeopsService=storeopsService, enable_thread = True, environment=environment)
        self.logger = logging.getLogger("main")

        self.addTopicToSubscribe(self.TOPIC_ALARM_CONFIGURATION)

        self.event_queue = queue.Queue()
        self.last_alarm_info = None
        self.upate_volume = False
        self.new_volume = 0


    def updateVariablesToSave(self, variables):
        pass


    def processTopic(self, topic, payload):
        super().processTopic(topic, payload)
        
        if topic == self.TOPIC_ALARM_CONFIGURATION:
            self.last_alarm_info = json.loads(payload)["data"]
    
    def eventThread(self):
        while True:
            try:
                time.sleep(0.1)
                if self.upate_volume:
                    self.upate_volume = False
                    self.last_alarm_info["volume"] = self.new_volume
                    self.logger.info(f"{self.STATUS_ID}: setting new volume, message {self.last_alarm_info}")
                    self.publishInternalBroker(self.UPDATE_VOLUME_TOPIC, {'id': uuid.uuid4().__str__(), 'data': self.last_alarm_info})

            except Exception as err:
                self.logger.error(f"{self.STATUS_ID} eventThread {err}, {type(err)}")
                
    
    def processStoreopsMessage(self, message):
        if message.type == 'command':
            if message.command_id == self.SOM_COMMAND_SET_VOLUME:
                self.setVolume(message)
            elif message.command_id == self.SOM_COMMAND_UPGRADE:
                self.upgradeSystem(message)
            elif message.command_id == self.SOM_COMMAND_REBOOT:
                self.rebootSom(message)


    def setVolume(self, message):
        try:
            self.logger.info(f"{self.STATUS_ID}: Received {message.command_id} command: {message}")
            for param in message.data:
                if param['key'] == self.SOM_COMMAND_SET_VOLUME_NEW_ID:
                    self.new_volume = int(param['value'][0])
                    self.upate_volume = True
                    self.publishInternalBroker(self.TOPIC_ALARM_CONFIGURATION_REQUEST, {'id': uuid.uuid4().__str__()})
            self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='ok')
        except Exception as err:
            self.logger.error(f"{self.STATUS_ID}: configuration message {message.command_id} error {err}, {type(err)}")
            self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='error', details=str(err))


    def upgradeSystem(self, message):
        try:
            self.logger.info(f"{self.STATUS_ID}: Received {message.command_id} command: {message}")
            if self.isContextInitialized():
                mac = ':'.join(''.join(pair) for pair in zip(*[iter(self.DEVICE_ID[-12:])]*2)) 
                self.publishInternalBroker(self.TOPIC_UPDATE_FIRMWARE_REQUEST, {"command": "updateFirmware","macAddress": mac,'uuid': uuid.uuid4().__str__()})
                self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='ok')
            else:
                self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='error', details='System not initialized for performing command')
        except Exception as err:
            self.logger.error(f"{self.STATUS_ID}: configuration message {message.command_id} error {err}, {type(err)}")
            self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='error', details=str(err))


    def rebootSom(self, message):
        try:
            self.logger.info(f"{self.STATUS_ID}: Received {message.command_id} command: {message}")
            if self.isContextInitialized():
                mac = ':'.join(''.join(pair) for pair in zip(*[iter(self.DEVICE_ID[-12:])]*2)) 
                self.publishInternalBroker(self.TOPIC_REBOOT_REQUEST, {"command": "reboot","macAddress": mac,'uuid': uuid.uuid4().__str__()})
                self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='ok')
            else:
                self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='error', details='System not initialized for performing command')
        except Exception as err:
            self.logger.error(f"{self.STATUS_ID}: configuration message {message.command_id} error {err}, {type(err)}")
            self.publishResponseToStoreops(self.STATUS_ID, message.uuid, status='error', details=str(err))

from events.event_class import Event
from messages.storeops_messages import EventMessage, ConfigurationMessage, ResponseMessage
import logging
import os
import queue
import time
from utils.time_utils import DateUtils
import json

class RFIDExitEvent(Event):

    EVENT_ID = 'rfid_exit'
    EVENT_GET_CONFIG_ID = 'get_storeops_rfid_exit'
    EVENT_SET_CONFIG_ID = 'set_storeops_rfid_exit'
    EVENT_RFID_EXIT_ENABLE_ID = 'rfid_exit_enable'
    EVENT_RFID_EXIT_USE_LOGNEW_ENABLE_ID = 'rfid_exit_use_lognew'
    EVENT_RFID_EXIT_AGGREGATION_WINDOW_SEC_ID = 'rfid_exit_aggregation_window_sec'
    #EVENT_RFID_EXIT_CONF_UPDATE_HOURS_ID = 'rfid_exit_status_conf_hours'

    TOPIC_WIRAMA_EPC_ALL = 'Wirama/EPC/All'

    EVENT_RFID_EXIT_ENABLE = int(os.getenv("EVENT_RFID_EXIT_ENABLE", default=0))
    EVENT_RFID_EXIT_USE_LOGNEW_ENABLE = int(os.getenv("EVENT_RFID_EXIT_USE_LOGNEW_ENABLE", default=1))
    EVENT_RFID_EXIT_AGGREGATION_WINDOW_SEC = float(os.getenv("EVENT_RFID_EXIT_AGGREGATION_WINDOW_SEC", default=3.0))
    #EVENT_RFID_EXIT_CONF_UPDATE_HOURS = float(os.getenv("EVENT_RFID_EXIT_CONF_UPDATE_HOURS", default=48.0))


    def __init__(self, mqtt_client, sharepointService, storeopsService, environment):
        super().__init__( mqtt_client=mqtt_client, sharepointService=sharepointService, storeopsService=storeopsService, enable_thread = True, environment=environment)
        self.logger = logging.getLogger("main")
        self.dateUtils =  DateUtils()

        self.addTopicToSubscribe(self.TOPIC_WIRAMA_EPC_ALL)

        self.event_queue = queue.Queue()

        #self.nextSendConf = datetime.datetime.now()
        self.sendConf = True


    def updateVariablesToSave(self, variables):
        variables.append(("EVENT_RFID_EXIT_ENABLE", self.EVENT_RFID_EXIT_ENABLE))
        variables.append(("EVENT_RFID_EXIT_USE_LOGNEW_ENABLE", self.EVENT_RFID_EXIT_USE_LOGNEW_ENABLE))
        variables.append(("EVENT_RFID_EXIT_AGGREGATION_WINDOW_SEC", self.EVENT_RFID_EXIT_AGGREGATION_WINDOW_SEC))
        #variables.append(("EVENT_RFID_EXIT_CONF_UPDATE_HOURS", self.EVENT_RFID_EXIT_CONF_UPDATE_HOURS))


    def processTopic(self, topic, payload):
        super().processTopic(topic, payload)
        
        if self.EVENT_RFID_EXIT_ENABLE:
            if topic == self.TOPIC_WIRAMA_EPC_ALL:
                self.event_queue.put(payload)


    def eventThread(self):
        while True:
            try:
                time.sleep(0.1)
                epcs = []
                txs = []
                ips = []
                if self.event_queue.qsize() > 0:
                    is_first = True

                    while not self.event_queue.empty():
                        json_item = json.loads(self.event_queue.get())

                        epc = None
                        if self.EVENT_RFID_EXIT_USE_LOGNEW_ENABLE:
                            if "type" in json_item and json_item["type"] == "debug-lognew":
                                epc = json_item["epc"]
                        else:
                            if "type" in json_item and json_item["type"] == "eas":
                                epc = json_item["epc"]

                        if epc is not None:
                            if epc not in epcs:
                                epcs.append(epc)
                                txs.append(json_item["tx"])
                                ips.append(json_item["ip_address"].split(':')[0])
                                if is_first:
                                    is_first = False
                                    event_time = self.dateUtils.getDateISOFormat() 
                                    if self.EVENT_RFID_EXIT_AGGREGATION_WINDOW_SEC > 0.0:
                                        time.sleep(self.EVENT_RFID_EXIT_AGGREGATION_WINDOW_SEC)
                    
                    if len(epcs) > 0 and self.isContextInitialized():
                        rfid_exit_event = self.prepareHeaderMessage(EventMessage(), set_timestamp=event_time)
                        rfid_exit_event.event_id = self.EVENT_ID
                        rfid_exit_event.version = "1.0.0"
                        rfid_exit_event.data.append({ 'key': "epc", 'type': 'string', "value": epcs})
                        rfid_exit_event.data.append({ 'key': "tx", 'type': 'string', "value": txs})
                        rfid_exit_event.data.append({ 'key': "ip", 'type': 'string', "value": ips})

                        self.logger.info(f"{self.EVENT_ID}: send {self.EVENT_ID} event message: {rfid_exit_event}")
                        self.publishToStoreops(rfid_exit_event)

                self.sendEventConfiguration()

            except Exception as err:
                self.logger.error(f"{self.EVENT_ID}: error process_events_queue {err}, {type(err)}")

                
    def processStoreopsMessage(self, message):
        if message.type == 'command':
            if message.command_id == self.EVENT_GET_CONFIG_ID:
                self.getStoreopsConf(message)
            elif message.command_id == self.EVENT_SET_CONFIG_ID:
                self.setStoreopsConf(message)


    def sendEventConfiguration(self):
        #now = datetime.datetime.now()
        #if now > self.nextSendConf or self.sendConf:
        #    self.nextSendConf = now + datetime.timedelta(hours=self.EVENT_RFID_EXIT_CONF_UPDATE_HOURS)
        if self.sendConf and self.isContextInitialized():
            self.sendConf = False
            rfid_exit_conf_status = self.prepareHeaderMessage(ConfigurationMessage())
            rfid_exit_conf_status.configuration_id = self.EVENT_ID
            rfid_exit_conf_status.version = "1.0.0"
            rfid_exit_conf_status.data.append({'key': self.EVENT_RFID_EXIT_ENABLE_ID, 'type': 'boolean', 'value': [self.EVENT_RFID_EXIT_ENABLE]})
            rfid_exit_conf_status.data.append({'key': self.EVENT_RFID_EXIT_USE_LOGNEW_ENABLE_ID, 'type': 'boolean', 'value': [self.EVENT_RFID_EXIT_USE_LOGNEW_ENABLE]})
            rfid_exit_conf_status.data.append({'key': self.EVENT_RFID_EXIT_AGGREGATION_WINDOW_SEC_ID, 'type': 'float', 'value': [self.EVENT_RFID_EXIT_AGGREGATION_WINDOW_SEC]})
            #rfid_exit_conf_status.data.append({'key': self.EVENT_RFID_EXIT_CONF_UPDATE_HOURS_ID, 'type': 'float', 'value': [self.EVENT_RFID_EXIT_CONF_UPDATE_HOURS]})

            self.logger.info(f"{self.EVENT_ID}: send configuration message: {rfid_exit_conf_status}")
            self.publishToStoreops(rfid_exit_conf_status)


    def getStoreopsConf(self, message):
        self.logger.info(f"{self.EVENT_ID}: Received {message.command_id} configuration message: {message}")
        self.sendConf = True
        self.publishResponseToStoreops(self.EVENT_ID, message.uuid, status='ok')


    def setStoreopsConf(self, message):
        try:
            self.logger.info(f"{self.EVENT_ID}: Received {message.command_id} configuration message: {message}")
            #Check types of data
            for param in message.data:
                if param['key'] == self.EVENT_RFID_EXIT_ENABLE_ID:
                    self.EVENT_RFID_EXIT_ENABLE = int(param['value'][0])
                elif param['key'] == self.EVENT_RFID_EXIT_USE_LOGNEW_ENABLE_ID:
                    self.EVENT_RFID_EXIT_USE_LOGNEW_ENABLE = int(param['value'][0])
                elif param['key'] == self.EVENT_RFID_EXIT_USE_LOGNEW_ENABLE_ID:
                    self.EVENT_RFID_EXIT_AGGREGATION_WINDOW_SEC_ID = float(param['value'][0])
#                elif param['key'] == self.EVENT_RFID_EXIT_CONF_UPDATE_HOURS_ID:
#                    self.EVENT_RFID_EXIT_CONF_UPDATE_HOURS = float(param['value'][0])
            self.updateLocalVariablesFile(restart=False)
            self.sendConf = True
            self.publishResponseToStoreops(self.EVENT_ID, message.uuid, status='ok')
        except Exception as err:
            self.logger.error(f"{self.EVENT_ID}: error configuration message {message.command_id} error {err}, {type(err)}")
            self.publishResponseToStoreops(self.EVENT_ID, message.uuid, status='error', details=str(err))

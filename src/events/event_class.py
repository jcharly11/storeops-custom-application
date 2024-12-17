import threading
import logging
import config.settings as settings
import json
import uuid
from utils.time_utils import DateUtils
from messages.storeops_messages import ResponseMessage

class Event():

    EVENT_TOPICS = []

    TOPIC_STORE_INFO = "store/info"

    CUSTOMER_ID = 'EMPTY'
    CUSTOMER_NAME = 'EMPTY'
    STORE_ID = '-1'
    DOOR_NAME = 'EMPTY'
    DOOR_NUMBER = '-1'
    DEVICE_TYPE = 'SFERO'
    DEVICE_ID = 'EMPTY'
    #SERIAL NUMBER

    def __init__(self,  mqtt_client, storeopsService, sharepointService, enable_thread , environment):
        self.logger = logging.getLogger("main")
        self.enable_thread = enable_thread
        self.mqtt_client = mqtt_client
        self.storeopsService = storeopsService
        self.sharepointService = sharepointService
        self.environment = environment
        self.context_intialized = False
        self.dateUtils =  DateUtils()
        
        self.addTopicToSubscribe(self.TOPIC_STORE_INFO)

        self.storeopsService.subscribeResponses(self)

        if enable_thread:
            thread = threading.Thread(target=self.eventThread)
            thread.start()

        self.publishInternalBroker(self.TOPIC_STORE_INFO, {'type':'get'})


    def isContextInitialized(self):
        return self.context_intialized

    def processStoreopsMessage(self, message):
        pass

    def updateVariablesToSave(self, variables):
        pass

    def updateLocalVariablesFile(self, restart=False):
        self.environment.updateLocalVariables(restart)

    def saveVariables(self, file):
        variables = []
        self.updateVariablesToSave(variables)
        if len(variables) > 0:
            for variable, value in variables:
                file.write(f"export {variable}={value}\n")

    def addTopicToSubscribe(self, topic):
        if topic not in self.EVENT_TOPICS:
            self.EVENT_TOPICS.append(topic)

    def getTopicsList(self):
        return self.EVENT_TOPICS

    def processTopic(self, topic, payload):
        if topic == self.TOPIC_STORE_INFO:
            payload = json.loads(payload)
            if "isResponse" in payload:
                if payload["isResponse"]:
                    if "storeNumber" in payload:
                        self.STORE_ID = payload["storeNumber"]
                        settings.STORE_NUMBER = self.STORE_ID 

                    if "serialNumber" in payload:
                        self.DEVICE_ID = payload["serialNumber"]
                        settings.DEVICE_ID = self.DEVICE_ID
                        
                    if "doorName" in payload:
                        self.DOOR_NAME = payload["doorName"]

                    if "doorNumber" in payload:
                        self.DOOR_NUMBER = str(payload["doorNumber"])

                    if "accountNumber" in payload:
                        self.CUSTOMER_ID= payload["accountNumber"]
                        settings.ACCOUNT_NUMBER = self.CUSTOMER_ID

                    if "customerName" in payload:
                        self.CUSTOMER_NAME= payload["customerName"]
                    if "systemType" in payload:
                        if payload["systemType"] == "apollo":
                            self.DEVICE_TYPE = 'SFERO'
                        else:
                            self.DEVICE_TYPE = 'AB_WIRAMA'

                    self.context_intialized = True


    def prepareHeaderMessage(self, message, set_timestamp=None, set_uuid=None):
        if hasattr(message, 'technology'):
            message.technology = settings.TECHNOLOGY_RFID
        if hasattr(message, 'customer'):
            message.customer = self.CUSTOMER_ID
        if hasattr(message, 'store'):
            message.store = self.STORE_ID
        if hasattr(message, 'group'):
            message.group = self.DOOR_NUMBER
        if hasattr(message, 'uuid'):
            if set_uuid:
                message.uuid = set_uuid
            else:
                message.uuid = uuid.uuid4().__str__()
        if hasattr(message, 'timestamp'):
            if set_timestamp:
                message.timestamp = set_timestamp
            else:
                message.timestamp = self.dateUtils.getDateISOFormat()
        if hasattr(message, 'device_model'):
            message.device_model = self.DEVICE_TYPE
        if hasattr(message, 'device_id'):
            message.device_id = self.DEVICE_ID

        return message

    def publishResponseToStoreops(self, response_id, uuid_request, status, exec_date=None, details=''):
        if exec_date == None:
            exec_date = self.dateUtils.getDateISOFormat()
        response_conf = self.prepareHeaderMessage(ResponseMessage())
        response_conf.response_id = response_id
        response_conf.uuid_request = uuid_request
        response_conf.version = "1.0.0"
        response_conf.data.append({'key': 'status', 'type': 'string', 'value': [status]})
        response_conf.data.append({'key': 'execution_date', 'type': 'timestamp', 'value': [exec_date]})
        response_conf.data.append({'key': 'details', 'type': 'string', 'value': [details]})
        self.publishToStoreops(response_conf)


    def publishToStoreops(self, message):

        self.storeopsService.publishToStoreops(message)


    def publishInternalBroker(self, topic, payload):
        self.mqtt_client.publish(topic=topic, payload = json.dumps(payload))

    def eventThread(self):
        pass
        

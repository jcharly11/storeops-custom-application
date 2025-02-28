from events.event_class import Event
from messages.storeops_messages import EventMessage, ConfigurationMessage, ResponseMessage
from messages.sharepoint_messages import SharepointCreateLinkMessage, SharepointUploadFilesMessage
from utils.images_utils import ImageUtils

import logging
import os
import queue
import time
import datetime
import config.settings as settings
from utils.time_utils import DateUtils
import json

class RFIDAlarmEvent(Event):

    EVENT_ID = 'rfid_alarm'
    EVENT_GET_CONFIG_ID = 'get_storeops_rfid_alarm'
    EVENT_SET_CONFIG_ID = 'set_storeops_rfid_alarm'

    EVENT_RFID_ALARM_ENABLE_ID = 'rfid_alarm_enable'
    EVENT_RFID_ALARM_AGGREGATION_WINDOW_SEC_ID = 'rfid_alarm_aggregation_window_sec'
    EVENT_RFID_ALARM_IMAGES_CAPTURE_ENABLE_ID = 'rfid_alarm_image_capture_enable'
    EVENT_RFID_ALARM_VIDEO_CAPTURE_ENABLE_ID = 'rfid_alarm_video_capture_enable'
    EVENT_RFID_ALARM_MEDIA_LINK_CREATION_TIMEOUT_SEC_ID = 'rfid_alarm_link_creation_timeout_sec'
    MIN_EPCS_TO_REQUEST_MEDIA_ID = 'min_epcs_to_request_media'


    TOPIC_CUSTOM_METHOD = "/settings/alarm"
    TOPIC_STANDARD_ALARM = "alarm"
    TOPIC_CUSTOM_NOTIFICATION_ALARM = "event/custom/alarm"
    TOPIC_CAMERA_STATUS = "status/onvif/camera"
    TOPIC_CAMERA_IMAGE_BUFFER = "command/onvif/image/get_buffer"
    TOPIC_CAMERA_IMAGE_BUFFER_RESP = "command_resp/onvif/image/get_buffer"
    TOPIC_CAMERA_VIDEO = "command/onvif/video/get_video"
    TOPIC_CAMERA_VIDEO_RESP = "command_resp/onvif/video/get_video"
    TOPIC_CAMERA_VIDEO_MEDIALINK_EAS = str(os.getenv("TOPIC_CAMERA_VIDEO_MEDIALINK_EAS", default="command_resp/storeops/media"))
    TOPIC_RFID_ALARM = str(os.getenv("TOPIC_RFID_ALARM", default="event/storeops/rfid_alarm"))


    EVENT_RFID_ALARM_ENABLE = int(os.getenv("EVENT_RFID_ALARM_ENABLE", default=1))
    EVENT_RFID_ALARM_AGGREGATION_WINDOW_SEC = float(os.getenv("EVENT_RFID_ALARM_AGGREGATION_WINDOW_SEC", default=3.0))
    EVENT_RFID_ALARM_IMAGES_CAPTURE_ENABLE = int(os.getenv("EVENT_RFID_ALARM_IMAGES_CAPTURE_ENABLE", default=1))
    EVENT_RFID_ALARM_VIDEO_CAPTURE_ENABLE = int(os.getenv("EVENT_RFID_ALARM_VIDEO_CAPTURE_ENABLE", default=1))
    EVENT_RFID_ALARM_MEDIA_LINK_CREATION_TIMEOUT_SEC = float(os.getenv("EVENT_RFID_ALARM_MEDIA_LINK_CREATION_TIMEOUT_SEC", default=4))
    EVENT_RFID_ALARM_MEDIA_REQUEST_TIMEOUT_MIN = 10
    MIN_EPCS_TO_REQUEST_MEDIA = float(os.getenv("MIN_EPCS_TO_REQUEST_MEDIA", default=2))



    def __init__(self, mqtt_client, sharepointService, storeopsService, environment):
        super().__init__( mqtt_client=mqtt_client, sharepointService=sharepointService, storeopsService=storeopsService, enable_thread = True, environment=environment)
        self.logger = logging.getLogger("main")
        self.dateUtils =  DateUtils()
        self.imageUtils = ImageUtils()

        self.addTopicToSubscribe(self.TOPIC_CUSTOM_METHOD)
        self.addTopicToSubscribe(self.TOPIC_STANDARD_ALARM)
        self.addTopicToSubscribe(self.TOPIC_CAMERA_STATUS)
        self.addTopicToSubscribe(self.TOPIC_CUSTOM_NOTIFICATION_ALARM)
        self.addTopicToSubscribe(self.TOPIC_CAMERA_IMAGE_BUFFER_RESP)
        self.addTopicToSubscribe(self.TOPIC_CAMERA_VIDEO_RESP)

        self.custom_app_alarm_decision_enabled = False

        self.event_queue = queue.Queue()
        
        self.images_in_process = []
        self.video_in_process = []
        self.event_messages = []
        self.event_messages_timeout = []
        self.sharepointService = sharepointService
        self.sharepointService.subscribeResponses(self)

        self.isSharepointEnabled = False
        
        self.sendConf = True     


    def updateVariablesToSave(self, variables):
        variables.append(("EVENT_RFID_ALARM_ENABLE", self.EVENT_RFID_ALARM_ENABLE))
        variables.append(("EVENT_RFID_ALARM_AGGREGATION_WINDOW_SEC", self.EVENT_RFID_ALARM_AGGREGATION_WINDOW_SEC))
        variables.append(("EVENT_RFID_ALARM_IMAGES_CAPTURE_ENABLE", self.EVENT_RFID_ALARM_IMAGES_CAPTURE_ENABLE))
        variables.append(("EVENT_RFID_ALARM_VIDEO_CAPTURE_ENABLE", self.EVENT_RFID_ALARM_VIDEO_CAPTURE_ENABLE))
        variables.append(("EVENT_RFID_ALARM_MEDIA_LINK_CREATION_TIMEOUT_SEC", self.EVENT_RFID_ALARM_MEDIA_LINK_CREATION_TIMEOUT_SEC))
        
        variables.append(("MIN_EPCS_TO_REQUEST_MEDIA", self.MIN_EPCS_TO_REQUEST_MEDIA))


    def processTopic(self, topic, payload):
        super().processTopic(topic, payload)
        
        if topic == self.TOPIC_STANDARD_ALARM:
            if not self.custom_app_alarm_decision_enabled:
                #check epc is not empty
                self.logger.info(f"{self.EVENT_ID}: processTopic TOPIC_STANDARD_ALARM: {payload}")
                self.event_queue.put(payload)

        if topic == self.TOPIC_CUSTOM_NOTIFICATION_ALARM:
            if self.custom_app_alarm_decision_enabled:
                #check epc is not empty
                self.logger.info(f"{self.EVENT_ID}: processTopic TOPIC_CUSTOM_NOTIFICATION_ALARM: {payload}")
                self.event_queue.put(payload)

        if  topic == self.TOPIC_CUSTOM_METHOD:
            alarm_method = json.loads(payload)
            if "type" in alarm_method and "defaultAlarming" in alarm_method:
                if alarm_method["type"] == "custom":
                    if alarm_method["defaultAlarming"] == 0:
                        self.custom_app_alarm_decision_enabled = True
                    else:
                        self.custom_app_alarm_decision_enabled = False


        if topic == self.TOPIC_CAMERA_IMAGE_BUFFER_RESP:
            self.logger.info(f"{self.EVENT_ID}: executing processImageBuffer")
            self.processImageBuffer(payload)

        if topic == self.TOPIC_CAMERA_VIDEO_RESP:
            self.logger.info(f"{self.EVENT_ID}: executing processVideo")
            self.processVideo(payload)

        if topic == self.TOPIC_CAMERA_STATUS:
            if self.EVENT_RFID_ALARM_IMAGES_CAPTURE_ENABLE or self.EVENT_RFID_ALARM_VIDEO_CAPTURE_ENABLE:
                if not self.isSharepointEnabled:
                    self.logger.info(f"{self.EVENT_ID}: camera detected")
                self.isSharepointEnabled = True            


    def eventThread(self):
        while True:
            try:
                time.sleep(0.1)
                epcs = []
                if (self.event_queue.qsize() > 0):   
                    is_first = True
                    is_silence = True

                    while not self.event_queue.empty():
                        alarm = json.loads(self.event_queue.get())

                        if is_first:
                            is_first = False
                            event_uuid = alarm['uuid'] 
                            event_time = self.dateUtils.getDateISOFormat()
                            if self.EVENT_RFID_ALARM_AGGREGATION_WINDOW_SEC > 0.0:
                                time.sleep(self.EVENT_RFID_ALARM_AGGREGATION_WINDOW_SEC)

                        if alarm["extraPayload"]["audible_alarm"]:
                            is_silence = False

                        if alarm["extraPayload"]["epc"] not in epcs:
                            epcs.append(alarm["extraPayload"]["epc"])

                    if self.isSharepointEnabled and len(epcs) >= self.MIN_EPCS_TO_REQUEST_MEDIA:
                        event_uuid = alarm['uuid'] 
                        self.request_media_creation(event_uuid)  

                    rfid_alarm_event = self.prepareHeaderMessage(EventMessage(), set_timestamp=event_time, set_uuid=event_uuid)
                    rfid_alarm_event.event_id = self.EVENT_ID
                    rfid_alarm_event.version = "1.0.0"
                    rfid_alarm_event.data.append({ "key": "epc","type":"string" ,"value": epcs})
                    rfid_alarm_event.data.append({ "key": "silent","type":"boolean" ,"value": [is_silence]})

                    if self.isSharepointEnabled and len(epcs) >= self.MIN_EPCS_TO_REQUEST_MEDIA:

                        create_link_message = SharepointCreateLinkMessage()
                        create_link_message.uuid = event_uuid
                        self.sharepointService.publishToSharepoint(create_link_message)

                        self.event_messages.append({ "uuid": event_uuid, "message": rfid_alarm_event, "timestamp_request": datetime.datetime.now()})
                        
                        self.logger.info(f"{self.EVENT_ID}: created event {self.EVENT_ID} waiting mediaLink")
                    else:
                        self.logger.info(f"{self.EVENT_ID}: send {self.EVENT_ID} message: {rfid_alarm_event}")
                        self.publishToStoreops(rfid_alarm_event)

                self.checkEventMessagesTimeout()
                self.checkRequestMediaTimeout()
                self.sendEventConfiguration()
            except Exception as err:
                self.logger.error(f"{self.EVENT_ID}: process_events_queue {err}, {type(err)}")
                
    

    def checkEventMessagesTimeout(self):
        delete_events = []
        now = datetime.datetime.now()
        timeout = datetime.timedelta(seconds=(self.EVENT_RFID_ALARM_MEDIA_LINK_CREATION_TIMEOUT_SEC + self.EVENT_RFID_ALARM_AGGREGATION_WINDOW_SEC))
       
        for event in self.event_messages:
            dt = event["timestamp_request"] + timeout
            if now > dt:
                self.logger.info(f"{self.EVENT_ID}: send message without link by timeout: {event['message'].data}")
                
                self.publishToStoreops(event["message"])
                
                self.event_messages_timeout.append(event)
                delete_events.append(event)

        for event in delete_events:
            self.event_messages.remove(event)


    def processSharepointMessage(self, message):
        try:
            
            delete_events = []
            for event in self.event_messages:
                self.logger.info(f"{self.EVENT_ID}: Event {event['uuid']}")
                
                if event["uuid"] == message['uuid']:
                    if message['link'] is not None:
                        self.sendMessageToStoreops(event=event, link=message['link'])   
                        delete_events.append(event)    
 
            
            for event in self.event_messages_timeout:
                self.logger.info(f"{self.EVENT_ID}: Event in timeout {event['uuid']}")
                if event["uuid"] == message['uuid']:
                    self.sendMessageToStoreops(event=event, link=message['link'])
                    delete_events.append(event)                         


            for event in delete_events:
                if self.event_messages.count(event) >  0 :
                    self.event_messages.remove(event)
                elif self.event_messages_timeout.count(event) >  0:
                     self.event_messages_timeout.remove(event)


        except Exception as err:
            self.logger.error(f"{self.EVENT_ID}: processSharepointMessage {err}, {type(err)}")


    def sendMessageToStoreops(self, event, link):
        event["message"].data.append({ "key": "mediaLink","type":'string' ,"value": [link]})
        self.logger.info(f"{self.EVENT_ID}: send message: {event['message']}")
        self.publishToStoreops(message = event["message"])
         


    def request_media_creation(self, event_uuid):
        if self.EVENT_RFID_ALARM_IMAGES_CAPTURE_ENABLE:
            payload = {
                    "header":{
                        "timestamp": self.dateUtils.getDateISOFormat(),
                        "uuid_request": event_uuid,
                        "version":settings.MESSAGE_VERSION},
                    "data": {
                        "get_buffer": True
                        }
                    }
            self.logger.info(f"{self.EVENT_ID}: request_media_creation Images {event_uuid}")
            self.publishInternalBroker(self.TOPIC_CAMERA_IMAGE_BUFFER, payload)
            self.images_in_process.append({ "uuid": event_uuid, "timestamp_request": datetime.datetime.now() })


        if self.EVENT_RFID_ALARM_VIDEO_CAPTURE_ENABLE:
            payload = {
                    "header":{
                        "timestamp": self.dateUtils.getDateISOFormat(),
                        "uuid_request": event_uuid,
                        "version":settings.MESSAGE_VERSION},
                    "data": {
                        "get_video": True,
                        "destination_path": ""
                        }
                    }
            self.logger.info(f"{self.EVENT_ID}: request_media_creation Video {event_uuid}")
            self.publishInternalBroker(self.TOPIC_CAMERA_VIDEO, payload)
            self.video_in_process.append({ "uuid": event_uuid, "timestamp_request": datetime.datetime.now() })


    def checkRequestMediaTimeout(self):
        timeout = datetime.timedelta(minutes=self.EVENT_RFID_ALARM_MEDIA_REQUEST_TIMEOUT_MIN)
        self.checkTimeout(self.images_in_process, timeout )
        self.checkTimeout(self.video_in_process,  timeout)
        self.checkTimeout(self.event_messages_timeout,  timeout)
        


    def checkTimeout(self, events_list, timeout):
        delete_events = []
        now = datetime.datetime.now()
        for event in events_list:
            dt = event["timestamp_request"] + timeout
            if now > dt:
                self.logger.info(f"{self.EVENT_ID}: timeout waiting {event}")
                delete_events.append(event)
        for event in delete_events:
            events_list.remove(event)

    
    def processImageBuffer(self, payload):
        delete_events = []
        payload = json.loads(payload)
        files = []

        for requests in self.images_in_process:
            self.logger.info(f"{self.EVENT_ID}: Payload:  {payload}")
            self.logger.info(f"{self.EVENT_ID}: Requests {requests}") 
            if payload["header"]["uuid_request"] == requests["uuid"]:
                  
                self.logger.info(f"{self.EVENT_ID}: Receive image buffer for request {requests['uuid']}")
                if payload["data"]["status"] == "OK":

                    uploadFilesMessage = SharepointUploadFilesMessage() 
                    uploadFilesMessage.uuid = requests['uuid']
                    uploadFilesMessage.destination_path = payload["data"]["destination_path"]        
                    uploadFilesMessage.path = f"{self.CUSTOMER_ID}/{self.STORE_ID}/{requests['uuid']}"
                    

                    #TODO  Reove extension name from onvif list
                    for file in payload["data"]["file_name"]:
                        files.append(f"{file}") 
                        
                    uploadFilesMessage.files = files
                    self.sharepointService.publishToSharepoint(uploadFilesMessage)
                    delete_events.append(requests)

        for event in delete_events:
            self.images_in_process.remove(event)


    def processVideo(self, payload):
        delete_events = []
        payload = json.loads(payload)
        for requests in self.video_in_process:
            if payload["header"]["uuid_request"] == requests["uuid"]:
                self.logger.info(f"{self.EVENT_ID}: Receive video for request {requests['uuid']} with status {payload['data']['status']}")
                if payload["data"]["status"] == "OK": 
                    uploadFilesMessage = SharepointUploadFilesMessage()
                    uploadFilesMessage.uuid = requests['uuid']
                    uploadFilesMessage.destination_path = payload["data"]["destination_path"]
                    uploadFilesMessage.path = f"{self.CUSTOMER_ID}/{self.STORE_ID}/{requests['uuid']}"
                    fileName =  payload["data"]["file_name"]
                    uploadFilesMessage.files = [fileName]
                    self.sharepointService.publishToSharepoint(uploadFilesMessage)
                    delete_events.append(requests)

        for event in delete_events:
            self.video_in_process.remove(event)


    def processStoreopsMessage(self, message):
        if message.type == 'command':
            if message.command_id == self.EVENT_GET_CONFIG_ID:
                self.getStoreopsConf(message)
            elif message.command_id == self.EVENT_SET_CONFIG_ID:
                self.setStoreopsConf(message)


    def sendEventConfiguration(self):
        if self.sendConf and self.isContextInitialized():
            self.sendConf = False
            rfid_exit_conf_status = self.prepareHeaderMessage(ConfigurationMessage())
            rfid_exit_conf_status.configuration_id = self.EVENT_ID
            rfid_exit_conf_status.version = "1.0.0"
            rfid_exit_conf_status.data.append({'key': self.EVENT_RFID_ALARM_ENABLE_ID, 'type': 'boolean', 'value': [self.EVENT_RFID_ALARM_ENABLE]})
            rfid_exit_conf_status.data.append({'key': self.EVENT_RFID_ALARM_AGGREGATION_WINDOW_SEC_ID, 'type': 'integer', 'value': [self.EVENT_RFID_ALARM_AGGREGATION_WINDOW_SEC]})
            rfid_exit_conf_status.data.append({'key': self.EVENT_RFID_ALARM_IMAGES_CAPTURE_ENABLE_ID, 'type': 'boolean', 'value': [self.EVENT_RFID_ALARM_IMAGES_CAPTURE_ENABLE]})
            rfid_exit_conf_status.data.append({'key': self.EVENT_RFID_ALARM_VIDEO_CAPTURE_ENABLE_ID, 'type': 'boolean', 'value': [self.EVENT_RFID_ALARM_VIDEO_CAPTURE_ENABLE]})
            rfid_exit_conf_status.data.append({'key': self.EVENT_RFID_ALARM_MEDIA_LINK_CREATION_TIMEOUT_SEC_ID, 'type': 'integer', 'value': [self.EVENT_RFID_ALARM_MEDIA_LINK_CREATION_TIMEOUT_SEC]})
            rfid_exit_conf_status.data.append({'key': self.MIN_EPCS_TO_REQUEST_MEDIA_ID, 'type': 'integer', 'value': [self.MIN_EPCS_TO_REQUEST_MEDIA]})

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
                if param['key'] == self.EVENT_RFID_ALARM_ENABLE_ID:
                    self.EVENT_RFID_ALARM_ENABLE = int(param['value'][0])
                elif param['key'] == self.EVENT_RFID_ALARM_AGGREGATION_WINDOW_SEC_ID:
                    self.EVENT_RFID_ALARM_AGGREGATION_WINDOW_SEC = int(param['value'][0])
                elif param['key'] == self.EVENT_RFID_ALARM_IMAGES_CAPTURE_ENABLE_ID:
                    self.EVENT_RFID_ALARM_IMAGES_CAPTURE_ENABLE = float(param['value'][0])
                    self.isSharepointEnabled = False
                elif param['key'] == self.EVENT_RFID_ALARM_VIDEO_CAPTURE_ENABLE_ID:
                    self.EVENT_RFID_ALARM_VIDEO_CAPTURE_ENABLE = float(param['value'][0])
                    self.isSharepointEnabled = False
                elif param['key'] == self.EVENT_RFID_ALARM_MEDIA_LINK_CREATION_TIMEOUT_SEC_ID:
                    self.EVENT_RFID_ALARM_MEDIA_LINK_CREATION_TIMEOUT_SEC = float(param['value'][0])
                elif param['key'] == self.MIN_EPCS_TO_REQUEST_MEDIA_ID:
                    self.MIN_EPCS_TO_REQUEST_MEDIA = float(param['value'][0])
            self.updateLocalVariablesFile(restart=False)
            self.sendConf = True
            self.publishResponseToStoreops(self.EVENT_ID, message.uuid, status='ok')
        except Exception as err:
            self.logger.error(f"{self.EVENT_ID}: error configuration message {message.command_id} error {err}, {type(err)}")
            self.publishResponseToStoreops(self.EVENT_ID, message.uuid, status='error', details=str(err))

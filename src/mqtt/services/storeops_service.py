from mqtt.service import Service
import logging
from database.database import DataBase
from config import settings as settings
from events.event_bus import EventBus
import threading
import multiprocessing
import json
import time
import datetime
class StoreOpsService(Service):
    
    """Receives from other services message to upload files to sharepoint. 

        Files tree structure is created by this service. 

        Retries uploading if fails. 

        Generates an internal message of the custom app with the sharepoint link to the files. 

        Only keep database of files until they are uploaded. 
"""
    def __init__(self):
        self.logger = logging.getLogger("main")  
        self.database = DataBase() 
        self.logger.info(f"Starting service ")
        self.service =Service() 
        #self.mutex = queue.Queue().mutex
        
     
    def run(self, queueAlarm: multiprocessing.Queue, queueInfo):
         self.queueAlarm = queueAlarm
         self.queueInfo = queueInfo
         EventBus.subscribe('Alarm',self)
         EventBus.subscribe('MessageSnapshot',self)
         EventBus.subscribe('SubscriberInfo',self)
         EventBus.subscribe('PublishMessageAlarm',self)
         EventBus.subscribe('MessageBuffer',self)
         
         EventBus.subscribe('MessageVideo',self)
         alarmThread = threading.Thread(target=self.processAlarm,args=(self.queueAlarm,))
         alarmThread.start() 
             
 
    def handleMessage(self, event_type, data=None):
        message =data['payload']

        if event_type == 'Alarm':#Put alarm event to queue
            self.logger.info("***************************")
            self.logger.info(message)
            self.logger.info(datetime.datetime.now())
            self.logger.info("***************************")

            self.queueAlarm.put_nowait(message)

        if event_type == 'MessageSnapshot':#Request snapshot to onvif 
            timestamp = message['timestamp']
            uuid_request = message['uuid']
            
            payload = {
                    "header":{
                        "timestamp": timestamp,
                        "uuid_request": uuid_request,
                        "version":settings.MESSAGE_VERSION},
                    "data": {
                        "take_snapshot": True
                        }
                    }
            #topic = f"checkpoint/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}/service/"+settings.TOPIC_CAMERA_IMAGE
            topic = settings.TOPIC_CAMERA_IMAGE               
            result = self.service.pub(topic=topic, payload=json.dumps(payload))
        
        if event_type == 'SubscriberInfo': #Subscribe info topic 
            self.service.subscribeSnapshotResp(accoutNumber= message['accountNumber'], storeId= message['storeId'])
            self.service.subscribeBufferResp()
            self.service.subscribeVideoResp()

        if event_type == 'PublishMessageAlarm':#Publish mesage for alarm
            #topic = f"checkpoint/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}/service/"+settings.TOPIC_CAMERA_VIDEO_MEDIALINK_EAS                
            topic = settings.TOPIC_RFID_ALARM
            try:
                result = self.service.pub(topic=topic, payload=json.dumps(message))
                self.logger.info(f"Reuslt mqtt message: { result }")
                self.database.deleteMessage(message=message)
            except Exception as ex:
                self.logger.info(f"Error sending mqtt {topic}")
            #delete from database

        if event_type == 'MessageBuffer':#Request buffer to onvif 
            timestamp = message['timestamp']
            uuid_request = message['uuid']
            
            payload = {
                    "header":{
                        "timestamp": timestamp,
                        "uuid_request": uuid_request,
                        "version":settings.MESSAGE_VERSION},
                    "data": {
                        "get_buffer": True
                        }
                    }
            #topic = f"checkpoint/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}/service/"+settings.TOPIC_CAMERA_IMAGE_BUFFER
            topic = settings.TOPIC_CAMERA_IMAGE_BUFFER            

            result = self.service.pub(topic=topic, payload=json.dumps(payload))
        



    def processAlarm(self,  queue): 
        alarms =[]
        while True:
             if not queue.empty():
                time.sleep(settings.ALARM_AGGREGATION_WINDOW_SEC)
                self.logger.info(f"Items in queue: {queue.qsize()}")
                while not queue.empty():
                    alarm = json.loads(queue.get(block = False))
                    alarms.append(alarm)
                    if queue.empty():
                        self.logger.info(f"Sending list of alarm messages {len(alarms)}")
                        EventBus.publish('AlarmProcess' , {'alarms': alarms})#Send internal message to AlarmProcess
                        alarms.clear()
             time.sleep(0.5)
 
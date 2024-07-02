from mqtt.service import Service
import logging
from database.database import DataBase
from config import settings as settings
from events.event_bus import EventBus
import threading
import queue
import json
import time
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
        self.mutex = queue.Queue().mutex
        
     
    def run(self, queueAlarm, queueInfo):
         self.queueAlarm = queueAlarm
         self.queueInfo = queueInfo
         EventBus.subscribe('Alarm',self)
         EventBus.subscribe('MessageSnapshot',self)
         EventBus.subscribe('SubscriberInfo',self)
         EventBus.subscribe('PublishMessageItemOptix',self)
         alarmThread = threading.Thread(target=self.processAlarm,args=(self.queueAlarm,))
         alarmThread.start() 
             
 
    def handleMessage(self, event_type, data=None):
        message =data['payload']

        if event_type == 'Alarm':

            self.queueAlarm.put(message)


        if event_type == 'MessageSnapshot':#Request snapshot to onvif 
            timestamp = message['timestamp']
            uuid_request = message['uuid']
            
            payload = {
                    "header":{
                        "timestamp":timestamp,
                        "uuid_request":uuid_request,
                        "version":settings.MESSAGE_VERSION},
                    "data": {
                        "take_snapshot": True
                        }
                    }
            topic = f"checkpoint/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}/service/"+settings.TOPIC_CAMERA_IMAGE                
            result = self.service.pub(topic=topic, payload=json.dumps(payload))
        
        if event_type == 'SubscriberInfo':
            self.logger.info("storesop service SubscriberInfo ")
            self.service.subscribeSnapshotResp(accoutNumber= message['accountNumber'], storeId= message['storeId'])

        if event_type == 'PublishMessageItemOptix':
            topic = f"checkpoint/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}/service/"+settings.TOPIC_CAMERA_VIDEO_MEDIALINK_EAS                

            self.service.pub(topic=topic, payload=json.dumps(message['body']))



    def processAlarm(self,  queue): 
        self.logger.info(f"Starting validatio of alarm queue")
        alarms =[]
        while True:
            with self.mutex:
                 if not queue.empty():
                      time.sleep(settings.ALARM_AGGREGATION_WINDOW_SEC)
                      self.logger.info("Stop waiting")
                      self.logger.info(f"imtesn in queue: {queue.qsize()}")
                      while not queue.empty():
                           alarm = json.loads(queue.get())  
                           alarms.append(alarm)
                           if queue.empty():
                               self.logger.info(f"Sending list of alarm messages")
                               EventBus.publish('AlarmProcess' , {'alarms': alarms})#Send internal message to AlarmProcess

 
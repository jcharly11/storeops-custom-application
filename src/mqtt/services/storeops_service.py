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
         EventBus.subscribe('Info',self)
         EventBus.subscribe('MessageSnapshot',self)
         alarmThread = threading.Thread(target=self.processAlarm,args=(self.queueAlarm,))
         alarmThread.start() 
         infoThread = threading.Thread(target=self.processInfo,args=(self.queueInfo,))
         infoThread.start()          
 
    def handleMessage(self, event_type, data=None):
        message =data['payload']

        if event_type == 'Alarm':

            self.queueAlarm.put(message)

        if event_type == 'Info':
            self.queueInfo.put(message)

        if event_type == 'MessageSnapshot':
            self.logger.info(f"Trying to send snapshot message")
            timestamp = message['timestamp']
            uuid_request = message['uuid']
            payload = {
                    "header":f"{{timestamp:{timestamp}, uuid_request:{uuid_request}, version:{settings.MESSAGE_VERSION}}}",
                    "data": f"{{take_snapshot: True}}"
                    }                
            self.service.pub(topic=settings.TOPIC_CAMERA_IMAGE, payload=json.dumps(payload))

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
                               EventBus.publish('AlarmProcess' , {'alarms': alarms})

    def processInfo(self, queue):
        while True:
            with self.mutex:
                 if not queue.empty():
                       
                      info = json.loads(queue.get()) 
                      EventBus.publish('MessageInfo',info)
from mqtt.service import Service
import logging
from database.database import DataBase
from config import settings as settings
from events.event_bus import EventBus

import threading
import queue
import json

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


    def processAlarm(self,  queue): 
        while True:
            with self.mutex:
                 if not queue.empty():
                       
                      alarm = json.loads(queue.get())
                      print(alarm['uuid'])

    def processInfo(self, queue):
        while True:
            with self.mutex:
                 if not queue.empty():
                       
                      info = json.loads(queue.get()) 
                      EventBus.publish('MessageInfo',info)
from mqtt.client import Client
import logging
from database.database import DataBase
from config import settings as settings
import threading
import queue
import json
 
class StoreOpsService(Client):
    
    def __init__(self):
        self.logger = logging.getLogger("main")  
        self.database = DataBase() 
        self.logger.info(f"Starting service ")
        self.client = Client().instance() 
        self.client.on_message = self.onMessage
        self.client.on_subscribe = self.onSubscribe
        self.client.subscribe(settings.TOPIC_CUSTOM_ALARM)
        self.mutex = queue.Queue().mutex
        self.queue = None

        
        
       

    def setQueue(self, queue):
          self.queue = queue
          bufferThread = threading.Thread(target=self.getAlarmBuffer,args=(self.queue,))
          bufferThread.start()    
         
    def getAlarmBuffer(self,  queue): 
        while True:
            with self.mutex:
                 if not queue.empty():
                       
                      alarm = json.loads(queue.get())
                      self.pub(uuid=alarm['uuid'])

    def onSubscribe(self,client, userdata, mid, qos, properties=None):
            self.logger.info(f"MQTT onSubscribed {client},{userdata}")    


    def onMessage(self, client, userdata, message, properties=None):
          
          payload =  message.payload.decode()
          topic = message.topic
          self.logger.info(f"Recivening message from topic :{topic}")

          if topic == "alarm":
                    self.queue.put(payload)


    def pub(self,  uuid):
         self.logger.info("Publish message")
         try:
             payload={ 
                    "header":{
                         "uuid_request": uuid
                             },
                    "snapshot": "true"
                    }
             result = self.client.publish(topic=settings.TOPIC_CAMERA_IMAGE,payload = json.dumps(payload) )
             
             status = result[0]
             if status == 0:
                  print(f"Send `{uuid}` to topic `{settings.TOPIC_CAMERA_IMAGE}`")
                  
             else:
                  print(f"Failed to send message to topic {settings.TOPIC_CAMERA_IMAGE}")
          
         except Exception as ex:
             self.logger.error(f"Publish alarm exception:{ex}")
         
 
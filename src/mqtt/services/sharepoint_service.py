from mqtt.client import Client
import config.settings as settings
import logging
import queue
from database.database import DataBase
from utils.sharepoint_utils import SharepointUtils
class SharePointService(Client):

    def __init__(self): 
            self.idService = type(self).__name__
            self.logger = logging.getLogger("main") 
            self.queue = queue.Queue()
            self.database = DataBase()
            self.sharepoint = SharepointUtils()
            self.logger.info(f"Starting service ")
            self.client = Client().instance() 
            self.client.on_message = self.onMessage
            self.client.on_subscribe = self.onSubscribe 

    def onSubscribe(self,client, userdata, mid, qos, properties=None):
            self.logger.info(f"MQTT onSubscribed {client},{userdata}")    


    def onMessage(self, client, userdata, message, properties=None): 
          self.logger.info(f"onMessage =  message:{message.payload.decode()}")
          payload =  message.payload.decode()
          self.queue.put(payload)
          

       
    def pub(self,  payload,id , uuid, messageId, timestamp, data):
          self.logger.info("Publish message")
          try:
               payload={ 
                    "header":{
                         "uuid_request": uuid
                             },
                    "snapshot": "true"
                    }
               
               result = self.client.publish(topic=settings.TOPIC_CAMERA_IMAGE, payload=payload)
               status = result[0]
               
               
          except Exception as ex:
             self.logger.error(f"Publish {self.idService} exception:{ex}")
         
 
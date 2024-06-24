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
            self.client.subscribe("input/video")  

    def onSubscribe(self,client, userdata, mid, qos, properties=None):
            self.logger.info(f"MQTT onSubscribed {client},{userdata}")    


    def onMessage(self, client, userdata, message, properties=None): 
          self.logger.info(f"onMessage =  message:{message.payload.decode()}")
          payload =  message.payload.decode()
          id = payload["requester_id"]
          uuid = payload["uuid"]
          messageId = payload["message_id"]
          timestamp = payload["timestamp"]
          data = payload["data"]
          for path in data:
               
               result = self.sharepoint.upload_video(uuid=uuid, path=path)

               if result:
                    
                    self.pub(payload=payload, id=id, uuid=uuid,messageId=messageId,timestamp=timestamp,data=data)
               else:
                    self.database.saveMessage(message=payload, status="FAIL")

       
    def pub(self,  payload,id , uuid, messageId, timestamp, data):
         self.logger.info("Publish message")
         try:
             topic = "output/video"
             payload={ 
                   "requester_id": id,
                   "uuid": uuid,
                   "message_id": messageId, 
                   "timestamp": timestamp,
                   "data": data
                   }
             
             result = self.client.publish(topic=topic, payload=payload)
             status = result[0]
             if status == 0:
                  print(f"Send `{messageId}` to topic `{topic}`")
                  
             else:
                  print(f"Failed to send message to topic {topic}")
          
         except Exception as ex:
             self.logger.error(f"Publish {self.idService} exception:{ex}")
         
 
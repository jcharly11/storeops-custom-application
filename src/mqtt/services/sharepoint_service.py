from mqtt.client import Client
import config.settings as settings
import logging

class SharePointService(Client):

    def __init__(self) -> None:
        
        try:
            self.idService = type(self).__name__
            self.logger   = logging.getLogger(type(self).__name__)
            self.logger.info("Starting service")
            self.client = Client()  
            self.client.on_subscribe = self.onSubscribe
            self.client.subscribe(settings.TOPIC_SHAREPOINT_UPLOAD) 
           
            
        except Exception as ex:
            self.logger.error(f"SharePointService:{ex}")

    def onSubscribe(self):
        self.logger.info(f"topic:{ settings.TOPIC_SHAREPOINT_UPLOAD }")    
        self.logger.info(f"status: OK")    

    def onPublish(self, client, data, mid):
        self.logger.info(f"mid:{ mid }")
        self.logger.info(f"userdata:{ data }")


    def pub(self,  payload):
         self.logger.info("Publish message")
         try:
             self.client.publish(topic=settings.TOPIC_SHAREPOINT_UPLOAD, payload=payload)
          
         except Exception as ex:
             self.logger.error(f"Publish {self.idService} exception:{ex}")
         
 
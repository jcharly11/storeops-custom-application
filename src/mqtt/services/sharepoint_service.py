from mqtt.client import Client
import config.settings as settings
import logging

class SharePointService(Client):

    def __init__(self): 
            self.idService = type(self).__name__
            self.logger = logging.getLogger("main") 
            self.logger.info(f"Starting service ")
            self.client = Client().instance() 
            self.client.on_message = self.onMessage
            self.client.on_subscribe = self.onSubscribe 
            self.client.subscribe("input/video")  

    def onSubscribe(self,client, userdata, mid, qos, properties=None):
            self.logger.info(f"MQTT onSubscribed {client},{userdata}")    

    def onMessage(self, client, userdata, message, properties=None): 
          self.logger.info(f"onMessage =  message:{message}")     

       
    def pub(self,  payload):
         self.logger.info("Publish message")
         try:
             self.client.publish(topic="output/video", payload=payload)
          
         except Exception as ex:
             self.logger.error(f"Publish {self.idService} exception:{ex}")
         
 
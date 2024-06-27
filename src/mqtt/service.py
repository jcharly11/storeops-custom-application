from mqtt.client import Client
from events.event_bus import EventBus

import config.settings as settings
import logging


class Service(Client):

    def __init__(self) -> None:
        self.logger = logging.getLogger("main") 
        self.client = Client().instance()
        self.client.on_message = self.onMessage
        self.client.on_subscribe = self.onSubscribe
        self.client.subscribe(settings.TOPIC_CUSTOM_ALARM)
        self.client.subscribe(settings.TOPIC_CAMERA_IMAGE_RESP)
        self.client.subscribe(settings.TOPIC_STORE_INFO) 
        
  
 
    def onSubscribe(self,client, userdata, mid, qos, properties=None):
            self.logger.info(f"MQTT onSubscribed {client},{userdata}")    
    
    def onMessage(self, client, userdata, message, properties=None):
          payload =  message.payload.decode()
          topic = message.topic
          
          self.logger.info(f"Recivening message from topic :{topic}")

          if topic == settings.TOPIC_CUSTOM_ALARM:
               EventBus.publish('Alarm', {'payload': payload})

          if topic == settings.TOPIC_STORE_INFO:
               EventBus.publish('Info', {'payload': payload})

          if topic  == settings.TOPIC_CAMERA_IMAGE_RESP:
               print("********************")
               EventBus.publish('Snapshot', {'payload': payload})
 
    def pub(self, topic , payload):
         self.client.publish(topic=topic, payload = payload)
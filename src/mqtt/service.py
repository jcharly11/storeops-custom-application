from mqtt.client import Client
from events.event_bus import EventBus

import config.settings as settings
import logging
import json

class Service(Client):

    def __init__(self) -> None:
        self.logger = logging.getLogger("main") 
        self.client = Client().instance()
        self.client.on_message = self.onMessage
        self.client.on_subscribe = self.onSubscribe
        self.baseTopic = f"checkpoint/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}/service/"
        self.client.subscribe(settings.TOPIC_CUSTOM_ALARM)
        self.client.subscribe(self.baseTopic+settings.TOPIC_CAMERA_IMAGE_RESP)
        self.client.subscribe(settings.TOPIC_STORE_INFO)
        self.client.subscribe(settings.TOPIC_RESTART_APPLICATION)
        
  
 
    def onSubscribe(self,client, userdata, mid, qos, properties=None):
            self.logger.info(f"MQTT onSubscribed {client},{userdata}")
            self.getInfo()    
    
    def onMessage(self, client, userdata, message, properties=None):
          payload =  message.payload.decode()
          topic = message.topic
     
          
          self.logger.info(f"Recivening message from topic :{topic}")

          if topic == settings.TOPIC_RESTART_APPLICATION:
               
               EventBus.publish('Restart', {'payload': payload})#Send internal message to restart service

          if topic == settings.TOPIC_CUSTOM_ALARM:
                  
               EventBus.publish('Alarm', {'payload': payload})#Send internal message to storeopservice

          if topic == settings.TOPIC_STORE_INFO:
                self.logger.info(f"Recivening message from topic :{topic}")

                if topic == settings.TOPIC_STORE_INFO:
                    try:
                         EventBus.publish('MessageInfo', {'payload': payload})
 
                    except Exception as err:
                         self.logger.error(f"Unexpected {err}, {type(err)}")
               #
          if topic  == self.baseTopic+settings.TOPIC_CAMERA_IMAGE_RESP:
               print("***************")
               EventBus.publish('Snapshot', {'payload': payload})
 
    def pub(self, topic , payload):
         self.client.publish(topic=topic, payload = payload)
   
    def getInfo(self):
         try:
          
          param = {
                "type": "get"
                }
          self.logger.info(f"Requesting info store")
          self.client.publish(topic = settings.TOPIC_STORE_INFO, payload =  json.dumps(param))
         except Exception as err:
          self.logger.error(f"send_store_info_get {err}, {type(err)}")

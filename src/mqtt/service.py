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
        self.client.subscribe(settings.TOPIC_CUSTOM_ALARM)
        self.client.subscribe(settings.TOPIC_STORE_INFO)
        self.client.subscribe(settings.TOPIC_RESTART_APPLICATION)
        self.getInfo()#request info to broker

    
    def onMessage(self, client, userdata, message, properties=None):
          payload =  message.payload.decode()
          topic = message.topic
          #topicResp =  f"checkpoint/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}/service/"

          if topic == settings.TOPIC_RESTART_APPLICATION:
               
               EventBus.publish('MessageRestart', {'payload': payload})#Send internal message to restart service

          if topic == settings.TOPIC_CUSTOM_ALARM:
                  
               EventBus.publish('Alarm', {'payload': payload})#Send internal message to storeopservice

          if topic == settings.TOPIC_STORE_INFO:
              if settings.ACCOUNT_NUMBER == 'EMPTY' and settings.LOCATION_ID == 'EMPTY':
                  self.logger.info("Incoming info store from mqtt broker")
                  EventBus.publish('MessageInfo', {'payload': payload})  #Send internal message to storeopservice
               
          if topic  == settings.TOPIC_CAMERA_IMAGE_RESP:
               self.logger.info(f"Incoming message from onvif module")
               EventBus.publish('Snapshot', {'payload': payload})
          
          if topic == settings.TOPIC_RESTART_APPLICATION:
               EventBus.publish('MessageRestart', {'payload': payload})

          if topic  == settings.TOPIC_CAMERA_IMAGE_BUFFER_RESP:
               self.logger.info(f"Incoming message from BUFFER onvif module")
               EventBus.publish('Buffer', {'payload': payload})

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
   
    def subscribeSnapshotResp(self, accoutNumber, storeId):
         
        #topic = f"checkpoint/{accoutNumber}/{storeId}/service/"+settings.TOPIC_CAMERA_IMAGE_RESP
        topic = settings.TOPIC_CAMERA_IMAGE
        
        self.logger.info(f"subscribeSnapshotResp: {topic}")
        self.client.subscribe(topic)
        self.logger.info(f"Subcriber to response of onvif: {topic}")
from config import settings as settings 
import logging
from events.event_bus import EventBus
import json
class ServiceInfo():
    
    def __init__(self):
         self.logger = logging.getLogger("main")
         EventBus.subscribe('MessageInfo',self)


  
    def getInfo(self, payload):
          
            if "accountNumber" in payload:
                settings.ACCOUNT_NUMBER = payload["accountNumber"]   
            if "storeNumber" in payload:
                settings.LOCATION_ID = payload["storeNumber"]
            if "serialNumber" in payload:
                settings.DEVICE_ID = payload["serialNumber"]
            if "doorName" in payload:
                settings.DOOR_NAME = payload["doorName"]
            if "doorNumber" in payload:
                settings.DOOR_NUMBER = payload["doorNumber"]


            EventBus.publish('SubscriberInfo', {'accountNumber': settings.ACCOUNT_NUMBER,'storeId':settings.LOCATION_ID}) 
    
    def handleMessage(self, event_type, data=None):
         payload = data['payload']
         json_item = json.loads(payload)
         self.getInfo(json_item)
         
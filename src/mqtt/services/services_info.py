from config import settings as settings 
import logging
from events.event_bus import EventBus

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
    
    def handleMessage(self, event_type, data=None):
         self.logger.info(f"Setting info store to environment")
         if event_type == 'MessageInfo':
              try:
                message =data['info']
                self.getInfo(payload=message)
              except Exception as ex:
                  self.logger.error(f"Error setting for store Info")       

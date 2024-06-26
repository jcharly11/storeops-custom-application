from config import settings as settings 

class InfoTool():
    
    def __init__(self):
         pass
  
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
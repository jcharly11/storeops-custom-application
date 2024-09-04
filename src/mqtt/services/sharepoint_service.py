import logging 
from events.event_bus import EventBus
from utils.sharepoint_utils import SharepointUtils
import json
import threading
import datetime
import config.settings as settings
from database.database import DataBase
from mqtt.service import Service

class SharePointService:

    def __init__(self): 
            self.idService = type(self).__name__
            self.logger = logging.getLogger("main")
            self.sharePointUtils = SharepointUtils()
            self.database = DataBase()
            self.service = Service() 
            EventBus.subscribe('Snapshot',self)
            EventBus.subscribe('Buffer',self)
            EventBus.subscribe('Video',self)


    def handleMessage(self, event_type, data=None):
        if(event_type=="Snapshot"):
            self.logger.info(f"Processing snapshot")
            try:
                payload = json.loads(data['payload'])
                
                header = payload['header']
                uuid = header['uuid_request']
                timestamp = header['timestamp']
                body = payload['data'] 
                status = body['status'] 
                img = body['image']

                if status == "OK":
                    files = [uuid]
                    uploaded, link = self.sharePointUtils.upload_group(path=path, uuid=uuid, files = files)
                    if uploaded:
                        EventBus.publish('MessageLink', {'payload': {"uuid":uuid, "timestamp":timestamp, "link":link}})
                else:
                    EventBus.publish('ErrorService', {'payload': {"uuid":uuid, "timestamp":timestamp, "error":"Error with onvif module"}})


            except Exception as ex:
                self.logger.error(f"Error requesting snapshot: {ex}")  
        
        if(event_type=="Buffer"):
            self.logger.info(f"Processing buffer")
            try:
                payload = json.loads(data['payload'])
                header = payload['header']
                uuid = header['uuid_request']
                timestamp = header['timestamp']
                body = payload['data'] 
                status = body['status']
                image_number = body['image_number'] 
                path = body['destination_path']
                
                if status == "OK":
                    cont = 1
                    files = []
                    for i in range(int(image_number)):
                        name= str(cont)
                        files.append(f"{name}.jpg")
                        cont += 1 
                        
                    upload = threading.Thread(target=self.upload,args=(path, uuid, timestamp, files,))
                    upload.start()
                    

                else:
                    EventBus.publish('ErrorService', {'payload': {"uuid":uuid, "timestamp":timestamp, "error":"Error with onvif module"}})


            except Exception as ex:
                self.logger.error(f"Error requesting buffer: {ex}")  

        if(event_type=="Video"):
            self.logger.info(f"Processing video")
            try:
                payload = json.loads(data['payload'])
                header = payload['header']
                uuid = header['uuid_request']
                timestamp = header['timestamp']
                body = payload['data'] 
                status = body['status'] 
                fileName = body['file_name']
                path  = body['destination_path']

                if status == "OK":
                    files = [fileName]
                    upload = threading.Thread(target=self.upload,args=(path, uuid, timestamp, files,))
                    upload.start()

            except Exception as ex:
                self.logger.error(f"Error requesting snapshot: {ex}")  
 


    def upload(self, path, uuid, timestamp, files):
         uploaded, link = self.sharePointUtils.upload_group(path=path, uuid=uuid,  files = files)
         if uploaded:
             result = self.database.getMessages(request_uuid = uuid)
             if result:
                    data=[
                            {
                            "key": "silence",
                            "value": result[0][2] 
                            } ,
                            {"key": "EPC","value": result[0][1].replace("[","").replace("]","").replace("'","").replace(" ","").split(",")} ,
                            { 
                                "key": "media",
                                "value":link
                            } 
                    ]
                    body={ 
                            "uuid":uuid,
                            "timestamp": datetime.datetime.now().__str__(),
                            "device_model": "SFERO",
                            "device_id": settings.DEVICE_ID,
                            "version": "1.0.0",
                            "data": data
                    }               
            
             try:                
                result = self.service.pub(topic=settings.TOPIC_RFID_ALARM, payload=json.dumps(body))
                self.logger.info(f"Result RFID ALARM message: { result }")
                self.database.deleteMessage(request_uuid=uuid)
             except Exception as ex:
                self.logger.info(f"Error sending mqtt {settings.TOPIC_RFID_ALARM}")



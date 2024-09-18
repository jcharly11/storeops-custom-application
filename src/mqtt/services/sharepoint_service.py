import logging 
from events.event_bus import EventBus
from utils.sharepoint_utils import SharepointUtils
import json
import datetime
import config.settings as settings
from database.database import DataBase
from concurrent.futures import ThreadPoolExecutor
from utils.file_utils import FileUtils
from utils.upload_utils import UploadUtils

class SharePointService:

    def __init__(self): 
            self.idService = type(self).__name__
            self.logger = logging.getLogger("main")
            self.sharePointUtils = SharepointUtils()
            self.database = DataBase()
            self.file_utils = FileUtils()
            self.upload_utils = UploadUtils()
            self.executor = ThreadPoolExecutor(max_workers=2)
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
                    files = [f'{uuid}.jpg']
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
                        name= str(cont).zfill(2)
                        files.append(f"{name}.jpg")
                        cont += 1
                    self.executor.submit(self.upload_utils.run, path, uuid, files, None)

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
                path = path[:-1]

                if status == "OK":
                    files = [fileName]
                    self.executor.submit(self.upload_utils.run, path, uuid, files, None)

            except Exception as ex:
                self.logger.error(f"Error requesting snapshot: {ex}")  
 

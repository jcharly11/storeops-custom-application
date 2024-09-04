import config.settings as settings
import logging 
from events.event_bus import EventBus
from utils.sharepoint_utils import SharepointUtils
import json
import os
class SharePointService:

    def __init__(self): 
            self.idService = type(self).__name__
            self.logger = logging.getLogger("main")
            self.sharePointUtils = SharepointUtils()
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
                    uploaded, link = self.sharePointUtils.upload_group(path=path, uuid=uuid, file_name= files)
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
                    for i in range(image_number):
                        name= str(cont)
                        files.append(f"{name}.jpg")
                        cont+=1 
                        
                    uploaded, link = self.sharePointUtils.upload_group(path=path, uuid=uuid, file_name = files)
                    if uploaded:
                        EventBus.publish('MessageLink', {'payload': {"uuid":uuid, "timestamp":timestamp, "link":link}})

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
                    folder, uploaded = self.uploadVideo(uuid=uuid,path=path, file_name=fileName)
                    if uploaded:
                        link = self.sharePointUtils.generateLink(id_folder=folder)
                        EventBus.publish('MessageLink', {'payload': {"uuid":uuid, "timestamp":timestamp, "link":link}})

            except Exception as ex:
                self.logger.error(f"Error requesting snapshot: {ex}")  

   
                 
    def uploadVideo(self, uuid, path ,file_name):
        try:
            self.logger.info("begin upload video") 
            folder = self.sharePointUtils.upload_video(uuid=uuid, path=path, file_name=file_name)
            if folder != None:
                return (folder, True)
            else:
                return (None,False)      
        except Exception as ex:
                self.logger.error(f"Error begin upload files: {ex}")       
                                  
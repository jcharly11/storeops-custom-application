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
                    folder, uploaded = self.upload(img=img, uuid=uuid,file_name=uuid)
                    if uploaded is not True:
                        folder, uploaded = self.upload(img=img, uuid=uuid,file_name=uuid)
                        
                    link = self.sharePointUtils.generateLink(id_folder=folder)
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
                img_buffer = body['image_buffer']

                cont=1
                if status == "OK":
                    for img in img_buffer:
                        name= str(cont)

                        folder, uploaded = self.upload(img=img, uuid=uuid, file_name=name)

                        if uploaded:
                            cont+=1
                        elif uploaded is not True:
                            folder, uploaded = self.upload(img=img, uuid=uuid,file_name=name)
                        
                    link = self.sharePointUtils.generateLink(id_folder=folder)
                    EventBus.publish('MessageLink', {'payload': {"uuid":uuid, "timestamp":timestamp, "link":link}})
                else:
                    EventBus.publish('ErrorService', {'payload': {"uuid":uuid, "timestamp":timestamp, "error":"Error with onvif module"}})


            except Exception as ex:
                self.logger.error(f"Error requesting buffer: {ex}")  


    def upload(self, img, uuid,file_name):
        try:
            self.logger.info("begin upload file")
            file= f"{file_name}.png"
            folder =self.sharePointUtils.upload_file(data=img, uuid=uuid, file_name= file)
            if folder != None:
                os.remove(f"./snapshots/{file_name}.png")
                return (folder, True)
            else:
                return (None,False)       
        except Exception as ex:
                self.logger.error(f"Error begin upload files: {ex}")       
                 
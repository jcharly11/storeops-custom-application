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
            


    def handleMessage(self, event_type, data=None):
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
                folder, uploaded = self.upload(img=img, uuid=uuid)
                if uploaded is not True:
                    folder, uploaded = self.upload(img=img, uuid=uuid)
                        
                link = self.sharePointUtils.generateLink(id_folder=folder)
                EventBus.publish('MessageSnapshotLink', {'payload': {"uuid":uuid, "timestamp":timestamp, "link":link}})
            else:
                EventBus.publish('ErrorService', {'payload': {"uuid":uuid, "timestamp":timestamp, "error":"Error with onvif module"}})


          except Exception as ex:
                    self.logger.error(f"Error requesting snapshot: {ex}")  


    def upload(self, img, uuid):
      folder =self.sharePointUtils.upload_file(data=img,file_name= f"{uuid}.png")
      if folder != None:
            os.remove(f"./snapshots/{uuid}.png")
            return (folder, True)
      else:
           return (None,False)            
                 
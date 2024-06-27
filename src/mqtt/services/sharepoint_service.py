import config.settings as settings
import logging 
from events.event_bus import EventBus
from utils.sharepoint_utils import SharepointUtils
import json
class SharePointService:

    def __init__(self): 
            self.idService = type(self).__name__
            self.logger = logging.getLogger("main")
            self.sharePointUtils = SharepointUtils()
            EventBus.subscribe('Snapshot',self)


    def handleMessage(self, event_type, data=None):
          self.logger.info(f"Processing snapshot")
          try:
           if event_type == 'Snapshot':#Getting smapshot from onvi,  upload to sharepoint, download link generation
                 payload = json.loads(data['payload'])
                 
                 header = payload['header']
                 uuid = header['uuid_request']
                 timestamp = header['timestamp']
                 body = payload['data']
                 status = body['status']
                 img = body['image']
                 folder =self.sharePointUtils.upload_file(data=img,file_name= f"{uuid}.png")
                 link = self.sharePointUtils.generateLink(id_folder=folder)
                 EventBus.publish('MessageSnapshotLink', {'payload': {"uuid":uuid, "timestamp":timestamp, "link":link}})
                 #SUBIMOS IMG


                    

          except Exception as ex:
                    self.logger.error(f"Error requesting snapshot: {ex}")  


 
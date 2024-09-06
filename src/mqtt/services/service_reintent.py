from config import settings as settings 
import logging
from concurrent.futures import ThreadPoolExecutor
import queue
import time
from utils.upload_utils import UploadUtils
from events.event_bus import EventBus

class ServiceReintent():
    
    def __init__(self):
         self.logger = logging.getLogger("ServiceReintent")
         self.executor = ThreadPoolExecutor(max_workers=1)
         self.upload_utils = UploadUtils()
         self.queue = queue.Queue()
         self.executor.submit(self.upload, self.queue)
         
         EventBus.subscribe('PublishMessageAlarmReintent',self)
         

    
    def handleMessage(self, event_type, data=None):
        
        try:
            
            self.queue.put(data)

        except Exception as err:
            self.logger.info(
            f"Error PublishMessageAlarmReintent : {err}")
    
    
    def upload(self):
        while True:
            time.sleep(settings.STOREOPS_REINTENT_DELAY_SECONDS)
            item = self.queue.get()
            uuid =  item['uuid']
            link =  item['link']
            files = item['files']
            path =  item['path']
            self.upload_utils.run(path=path, uuid=uuid, files=files, link = link)

            
            
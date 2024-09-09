from config import settings as settings 
import logging
from concurrent.futures import ThreadPoolExecutor
import queue
import time
from utils.upload_utils import UploadUtils
from events.event_bus import EventBus
import threading

class ServiceReintent():
    
    def __init__(self):
         self.logger = logging.getLogger("main")
         self.logger.info("Starting reintent service")
         self.upload_utils = UploadUtils()
         self.queue = queue.Queue() 
         reintentThread = threading.Thread(target=self.upload,args=(self.queue,))
         reintentThread.start() 
         EventBus.subscribe('PublishMessageAlarmReintent',self)
         

    
    def handleMessage(self, event_type, data=None):
        
        try:
            
            self.queue.put(data)
            self.logger.info(f"Content in reintent queue{self.queue.qsize()}")

        except Exception as err:
            self.logger.info(
            f"Error PublishMessageAlarmReintent : {err}")
    
    
    def upload(self , queue):
        while True:
            if  not queue.empty():
                


                time.sleep(settings.STOREOPS_REINTENT_DELAY_SECONDS)
                item = queue.get()
                uuid =  item['uuid']
                link =  item['link']
                files = item['files']
                path =  item['path']
                self.logger.info(f"Reintento of {uuid}")
                self.upload_utils.run(path=path, uuid=uuid, files=files, link = link)

            
            
import traceback
import datetime
import sys
import logging 
from messages.sharepoint_messages import SharepointMessage,SharepointUploadFilesMessage
 
import config.sharepoint_settings as sharepoint_settings
from utils.sharepoint_utils import SharepointUtils
from utils.file_utils import FileUtils
from utils.files_manager_task import FilesManagerTaks
import time
import threading
import multiprocessing as mp

class SharepointService():
    def __init__(self):   
        self.logger = logging.getLogger("main")
        self.SERVICE_ID = 'sharepoint_service'
        self.sharepointQueue = mp.Queue()
        self.sharepointInternalQueue = mp.Queue()
        self.sharepointUtils= SharepointUtils()
        self.filesUtils =  FileUtils()
        self.fileManageTask = FilesManagerTaks()
        # if self.EVENT_RFID_ALARM_IMAGES_CAPTURE_ENABLE or self.EVENT_RFID_ALARM_VIDEO_CAPTURE_ENABLE:

        self.subscribers = []
        self.links = []
        self.sendSharepointLastRetry = datetime.datetime.now()
        self.removeOldMessagesLastRetry = 0

        thread = threading.Thread(target=self.sharepointThread)
        thread.start()

        thread_uploading = threading.Thread(target=self.sharepointThreadUploading)
        thread_uploading.start()



    def publishToSharepoint(self, message):
        try:
            if isinstance(message, SharepointMessage):
                self.sharepointQueue.put(message)
            else:
                self.logger.error(f"{self.SERVICE_ID}: publishToSharepoint tried to publish not correct message {message}")
        except Exception as err:
            self.logger.error(f"publishToSharepoint {err}, {type(err)}")


    def subscribeResponses(self, subscriber):
        if subscriber is not None:
            self.subscribers.append(subscriber)


    def publishResponseToSubscribers(self, message):
        for sub in self.subscribers:
            try:
                self.logger.info("GETTING MESSAGE WITH LINK")
                sub.processSharepointMessage(message)
            except Exception as err:
                self.logger.error(f"publishResponseToSubscribers sub {sub} has not function processSharepointMessage: {err}, {type(err)}")

    def saveVariables(self, file):
        file.write(f"export SHAREPOINT_CREATE_LINK_TIMEOUT_MIN={sharepoint_settings.SHAREPOINT_CREATE_LINK_TIMEOUT_MIN}"+ "\n")
        file.write(f"export SHAREPOINT_CREATE_LINK_RETRY_SEC={sharepoint_settings.SHAREPOINT_CREATE_LINK_RETRY_SEC}"+ "\n")

        file.write(f"export SHAREPOINT_RETRY_SEND_MIN={sharepoint_settings.SHAREPOINT_RETRY_SEND_MIN}"+ "\n")
        file.write(f"export SHAREPOINT_KEEP_MESSAGES_DAYS={sharepoint_settings.SHAREPOINT_KEEP_MESSAGES_DAYS}"+ "\n")
   
    def sharepointThread(self):
        requests_link = []
        while True:
            try:
                time.sleep(0.1)

                while self.sharepointQueue.qsize() > 0:
                    message = self.sharepointQueue.get()

                    if message.type == "upload":
                        
                        self.sharepointInternalQueue.put(message)

                    elif message.type == "create_link":
                        timeout = datetime.timedelta(minutes=sharepoint_settings.SHAREPOINT_CREATE_LINK_TIMEOUT_MIN)
                        timestamp_last_try =  datetime.datetime.now() - timeout
                        requests_link.append({ "timestamp_request": datetime.datetime.now(), "timestamp_last_try": datetime.datetime.now() , "message": message })
 



                delete_request = []
                lr = len(requests_link)
               
                for request in requests_link:
                    
                    now = datetime.datetime.now()
                    timeout = datetime.timedelta(minutes=sharepoint_settings.SHAREPOINT_CREATE_LINK_TIMEOUT_MIN)
                    timestamp_request = request["timestamp_request"] + timeout
                     
                    if now >  timestamp_request :
                        self.logger.info(f"Deleting request: {request}")
                        delete_request.append(request)

                    else:
                        
                         
                        retry = datetime.timedelta(seconds=sharepoint_settings.SHAREPOINT_CREATE_LINK_RETRY_SEC)
                        timestamp_last_try = request["timestamp_last_try"]
                        
                        if isinstance(timestamp_last_try, datetime.datetime):
                            dd = timestamp_last_try + retry 
                            if now > dd :

                                id_folder = message.uuid
                                self.logger.info(f"{self.SERVICE_ID}: Request link: {id_folder}") 
                                link = self.sharepointUtils.generateLink(uuid=id_folder)   
                                                
                                if link is not None:
                                    uuid =message['uuid']
                                    self.logger.info(f"{self.SERVICE_ID}: Link generated: {uuid}") 
                                    request["message"].link = link
                                    self.links.append({"uuid":message['uuid'], "link": link}) 
                                    self.publishResponseToSubscribers(request["message"])
                                    delete_request.append(request)
                                else:
                                    self.logger.info("Going to reintent because timeout requesting link")
                                    request["timestamp_last_try"] = datetime.datetime.now() # addinglast time to reintent request link
                                    self.logger.info(f"Content on requests {lr}")

                
                for request in delete_request:
                    requests_link.remove(request)

                  
            except Exception as err:
                self.logger.error(f"sharepointThread {err}, {type(err)}")
                self.logger.error(traceback.format_exc())
                self.logger.error(sys.exc_info()[2]) # This line is getting for the error type.
    
    def sharepointThreadUploading(self): 
        while True:
            try:
                time.sleep(0.1)

                while self.sharepointInternalQueue.qsize() > 0:
                    message = self.sharepointInternalQueue.get()
                    self.logger.info(f"{self.SERVICE_ID}: Processing upload queue values destination_path: {message.destination_path} , uuid:  {message.uuid}, files: {message.files}]") 
                    self.uploadToSharepoint(message = message)


                #check if pending files to upload and push them.
                #when files uploaded remove them from database.
                #control max timeout trying to upload files and remove them
                self.retrySendToSharepoint()
                self.removeOldFiles()

            except Exception as err:
                self.logger.error(f"sharepointThreadUploading {err}, {type(err)}")
                self.logger.error(traceback.format_exc())
                self.logger.error(sys.exc_info()[2])

    def retrySendToSharepoint(self):
        now = datetime.datetime.now()
        timeout_retry = datetime.timedelta(seconds=float(sharepoint_settings.SHAREPOINT_RETRY_SEND_MIN))
        current_retry = self.sendSharepointLastRetry + timeout_retry
       
       
        if now >= current_retry: # Reintent to upload using local upload default method
            items = self.fileManageTask.getItems()  
            if items is not None:

                for item in items:
                    self.logger.info("Retry upload files")
                    message  = SharepointUploadFilesMessage()
                    message.type = 'upload'
                    message.uuid= item[0]
                    message.files = item[1].split(",")
                    link = item[2]
                    message.path= item[3]
                    self.links.append({"uuid":message.uuid, "link":link })
                    self.logger.info(f"UUID: {message.uuid}, IMAGES:{message.files} LINK:{link} ")
                    self.uploadToSharepoint(message = message)
            
                 

    def removeOldFiles(self):
        now = datetime.datetime.now()
        timeout_retry = datetime.timedelta(hours=4)
        rt = self.removeOldMessagesLastRetry + timeout_retry.total_seconds()

        if now > datetime.datetime.fromtimestamp(rt):
            #Get any message older than SHAREPOINT_KEEP_MESSAGES_DAYS from now and remove them from databasae
            pass

    def uploadToSharepoint(self, message):
        link = None
        link = self.checkLink(message.uuid) # check for link previus request
        if link is None:
            link = self.sharepointUtils.generateLink(message.uuid)# generate link in case of previus None exist
        
        uploaded = self.sharepointUtils.uploadGroup(path = message.destination_path, uuid = message.uuid, data = message.files)

        if uploaded:
            self.logger.info(f"{self.SERVICE_ID}: Success uploading {uploaded}")
            self.publishResponseToSubscribers(message={"uuid":message.uuid ,"link": link})
            self.filesUtils.deleteFolderContent(folder=message.destination_path)

        else:
           
            self.logger.info(f"{self.SERVICE_ID}: Fail uploading saving data to db images")
            self.sendSharepointLastRetry = datetime.datetime.now()
            self.fileManageTask.addItem({
                'files': message.files, 
                'uuid': message.uuid, 
                'path': message.destination_path,
                'link': link})
             
        
    def checkLink(self, uuid):
        link = None
        for item in self.links:
            if item['uuid'] == uuid:
                link =  item['link']
                self.links.remove(item)
                break

        return link
                

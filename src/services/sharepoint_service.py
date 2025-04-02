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

                self.createLinkManagement(requests_link)
            except Exception as err:
                self.logger.error(f"{self.SERVICE_ID}: sharepointThread {err}, {type(err)}")
                self.logger.error(traceback.format_exc())
                self.logger.error(sys.exc_info()[2]) # This line is getting for the error type.

    def createLinkManagement(self, requests_link):
        try:
            delete_request = []       
            for request in requests_link:
                now = datetime.datetime.now()
                timeout = datetime.timedelta(days=sharepoint_settings.SHAREPOINT_KEEP_MESSAGES_DAYS)
                timestamp_request = request["timestamp_request"] + timeout
                 
                if now >  timestamp_request :
                    self.logger.info(f"{self.SERVICE_ID}:Deleting create link request: {request}")
                    delete_request.append(request)
                    request["message"].status = SharepointMessage.TIMEOUT
                    self.publishResponseToSubscribers(request["message"])

                else:
                    retry = datetime.timedelta(seconds=sharepoint_settings.SHAREPOINT_CREATE_LINK_RETRY_SEC)
                    timestamp_last_try = request["timestamp_last_try"]
                    
                    if isinstance(timestamp_last_try, datetime.datetime):
                        dd = timestamp_last_try + retry 
                        if now > dd :
                            id_folder = request["message"].uuid
                            self.logger.info(f"{self.SERVICE_ID}: Request link: {id_folder}") 
                            link = self.sharepointUtils.generateLink(uuid=id_folder)   
                                            
                            if link is not None:
                                uuid = request["message"]['uuid']
                                self.logger.info(f"{self.SERVICE_ID}: Link generated: {uuid}") 
                                request["message"].link = link
                                request["message"].status = SharepointMessage.LINK_CREATED
                                self.publishResponseToSubscribers(request["message"])
                                delete_request.append(request)
                            else:
                                self.logger.info(f"{self.SERVICE_ID}: Going to reintent {request['message']['uuid']} because timeout requesting link")
                                request["timestamp_last_try"] = datetime.datetime.now() # addinglast time to reintent request link
            
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
                    self.logger.info(f"{self.SERVICE_ID}: Processing upload queue values destination_path: {message.path} , uuid:  {message.uuid}, files: {message.files}]") 
                    self.uploadToSharepoint(message)


                #check if pending files to upload and push them.
                #when files uploaded remove them from database.
                #control max timeout trying to upload files and remove them
                self.retrySendToSharepoint()
                #self.removeOldFiles()

            except Exception as err:
                self.logger.error(f"{self.SERVICE_ID}:sharepointThreadUploading {err}, {type(err)}")
                self.logger.error(traceback.format_exc())
                self.logger.error(sys.exc_info()[2])

    def retrySendToSharepoint(self):
        now = datetime.datetime.now()
        timeout_retry = datetime.timedelta(seconds=float(sharepoint_settings.SHAREPOINT_RETRY_SEND_MIN))
        current_retry = self.sendSharepointLastRetry + timeout_retry
       
        if now >= current_retry: # Reintent to upload using local upload default method
            self.sendSharepointLastRetry = now
            items = self.fileManageTask.getItems()  
            if items is not None:
                for item in items:
                    message  = SharepointUploadFilesMessage()
                    message.type = 'upload'
                    message.uuid = item[0]
                    message.files = item[1].split(",")
                    message.path = item[4]
                    self.logger.info(f"{self.SERVICE_ID}:Retry upload message : {message.uuid}, IMAGES:{message.files} ,PATH: {message.path}")
                    self.uploadToSharepoint(message = message)
            
                 

    def removeOldFiles(self):
        #SRJ: get from self.fileManagerTask items older than SHAREPOINT_KEEP_MESSAGES_DAYS.
        #Then remote the files and self.fileManageTask.deleteItem
        daysKeeped = sharepoint_settings.SHAREPOINT_KEEP_MESSAGES_DAYS
        now = datetime.datetime.now()
        dateBackup = now - datetime.timedelta(days = daysKeeped)
        
        try:
            
            old = self.fileManageTask.getItemsOlderThan(timestamp=dateBackup)
            for data in old:
                uuid = data['uuid']
                path = data['path']
                self.filesUtils.deleteFolderContent(folder= path)
                self.fileManageTask.deleteItem(uuid=uuid, path=path)
                message = SharepointUploadFilesMessage()
                message.status = SharepointMessage.TIMEOUT
                self.publishResponseToSubscribers(message)
                    
        
            #Get any message older than SHAREPOINT_KEEP_MESSAGES_DAYS:
            #  1- Delete files in backup folder
            #  2- publishResponeToSubscriber con status TIMEOUT
            #  3- Remove from database
        except Exception as err:
                self.logger.error(f"{self.SERVICE_ID }: {err}, {type(err)}")
                self.logger.error(traceback.format_exc())
                self.logger.error(sys.exc_info()[2])

    def uploadToSharepoint(self, message):    
        uploaded = self.sharepointUtils.uploadGroup(path = message.path, uuid = message.uuid, data = message.files)

        if uploaded:
            self.logger.info(f"{self.SERVICE_ID}: Success uploading: {message.uuid}, uuid:{message.path}")
            message.status = SharepointMessage.UPLOADED
            self.publishResponseToSubscribers(message)
            self.filesUtils.deleteFolderContent(folder=message.path)
            self.fileManageTask.deleteItem( uuid = message.uuid, path=message.path)
        
        else:
             self.logger.info(f"{self.SERVICE_ID}: Fail uploading: {message.uuid}, uuid:{message.path}")
             self.fileManageTask.addItem(message)
             

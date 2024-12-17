import threading
import logging
import multiprocessing as mp
import time
from database.database_azure import DataBaseFiles
from utils.file_utils import FileUtils
from config.settings import BACKUP_FILES_AZURE_PATH
class FilesManagerTaks:
    def __init__(self) -> None:
        self.logger = logging.getLogger("main")
        self.sharepointImagesQueue = mp.Queue()
        
        self.database = DataBaseFiles()# to save image afet unsuccess upload
        self.fileUtils = FileUtils() # to move files from tmp to backup path

        thread = threading.Thread(target=self.fileManager, args=(self.sharepointImagesQueue,))
        thread.start()

    def addItem(self, uuid):
        self.sharepointImagesQueue.put(uuid)

    def fileManager(self, sharepointImagesQueue):
        while True:
            time.sleep(0.1)
            if not sharepointImagesQueue.empty() :
                data = sharepointImagesQueue.get()
                try:
                    
                    files = data['files'] 
                    uuid = data['uuid']
                    path = data['path']
                    link = data['link']
                    content = data['content']
                    dests = []
                    if content:
                        if not self.fileUtils.existFolder(f"{BACKUP_FILES_AZURE_PATH}/{uuid}"):
                            self.fileUtils.createFolderFull(f"{BACKUP_FILES_AZURE_PATH}/{uuid}")
                        for file_name in files:
                            file_full_path = f"{path}/{file_name}"
                            dest =  f"{BACKUP_FILES_AZURE_PATH}/{uuid}/{file_name}"
                            if self.fileUtils.exist(file=file_full_path):
                                self.fileUtils.moveFiles(file_full_path, dest)  
                                dests.append(dest)
                        destinations = ','.join(dests) 
                        self.database.saveFiles(request_uuid=uuid, link=link, files=destinations,path=path)
                    else:
                        self.database.deleteFiles(request_uuid=uuid)
                    

                except Exception as ex:
                    self.logger.error(f"Error in backup process: {ex}")
                    self.sharepointImagesQueue.put(data)
    
    def getItems(self):
        return self.database.getAllFiles()
         


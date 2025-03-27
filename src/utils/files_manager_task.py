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
        self.sharepointMediaQueue = mp.Queue()
        
        self.database = DataBaseFiles()# to save image afet unsuccess upload
        self.fileUtils = FileUtils() # to move files from tmp to backup path
        if not self.fileUtils.folderExist(BACKUP_FILES_AZURE_PATH):
            self.fileUtils.createFolderFull(BACKUP_FILES_AZURE_PATH)

        thread = threading.Thread(target=self.fileManager, args=(self.sharepointMediaQueue,))
        thread.start()

    def addItem(self, message):
        self.sharepointMediaQueue.put(message)

    def fileManager(self, sharepointMediaQueue):
        while True:
            time.sleep(0.1)
            if not sharepointMediaQueue.empty() :
                data = sharepointMediaQueue.get()
                try:
                    
                    files = data['files'] 
                    uuid = data['uuid']
                    path = data['path']
                    link = data['link']
                    dests = []
                    backupPath = str(path).replace('.','')
                    backupLocation = f"{BACKUP_FILES_AZURE_PATH}{backupPath}"
                    if not self.fileUtils.existFolder(backupLocation):
                        self.fileUtils.createFolderFull(f"{backupLocation}")

                    for file_name in files:
                        file_full_path = f"{path}/{file_name}"
                        dest =  f"{backupLocation}/{file_name}"
                        if self.fileUtils.exist(file=file_full_path):
                            self.fileUtils.moveFiles(file_full_path, dest)
                            dests.append(dest)
                        destinations = ','.join(dests) 
                    self.database.saveFiles(request_uuid=uuid, link=link, files=destinations,path=path)

                except Exception as ex:
                    self.logger.error(f"Error in backup process: {ex}")
                    self.sharepointMediaQueue.put(data)
    
    def getItems(self):
        return self.database.getAllFiles()
         


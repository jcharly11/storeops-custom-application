import logging
import multiprocessing as mp
import datetime
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

    def addItem(self, message):
        try:
            files = message['files'] 
            uuid = message['uuid']
            path = message['path']
            moved = False
            backupPath = str(path).replace('.','')
            backupLocation = f"{BACKUP_FILES_AZURE_PATH}{backupPath}"
            if not self.fileUtils.existFolder(backupLocation):
                self.fileUtils.createFolderFull(f"{backupLocation}")

            for file_name in files:
                file_full_path = f"{path}/{file_name}"
                dest =  f"{backupLocation}/{file_name}"
                self.logger.info(f"Moving file: {file_full_path} to {dest}")
                if self.fileUtils.exist(file=file_full_path):
                    moved = self.fileUtils.moveFiles(file_full_path, dest)
            if moved:
                files = ",".join(files)    
                self.database.saveFiles(request_uuid=uuid, link=None, files=files, path=backupLocation)  

        except Exception as ex:
            self.logger.error(f"Error in backup process: {ex}")
    
    def getItems(self):
        return self.database.getAllFiles()

    def deleteItem(self, uuid):
        return self.database.deleteFiles(uuid)

    def getItemsOlderThan(self, timestamp):
        items = self.database.getFilesOlderThan()
        result = []
        for item in items:
             if item[0] and item[1]:
                uuid = item[0]
                di =   item[1]
                path = item[2]
                date_inserted = datetime.datetime.strptime(di, "%Y-%m-%d %H:%M:%S.%f")
                if  date_inserted <= timestamp:
                    result.append({'uuid':uuid, 'path': path})       
        return result
         


import logging
import config.settings as settings
import os
import shutil
 
class FileUtils():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def createFolder(self, folder):
        try:
            os.makedirs(folder)
            return folder
        except Exception as ex:
            self.logger.error(f"Error creating folder:  {ex}")
            return None

    def deleteFolderContent(self, folder):
        try:
           shutil.rmtree(folder)
        except Exception as ex:
            self.logger.error(f"Error deleting folder: {folder,ex}")    
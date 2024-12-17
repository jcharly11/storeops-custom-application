import os
import shutil
import logging

class FileUtils():
    def __init__(self) -> None:
        self.logger = logging.getLogger("main")

    def createFolder(self, uuid):
        try:
            folder =  f"./snapshots/{uuid}"
            os.makedirs(folder)
            return folder
            
        except Exception as ex:
            self.logger.error(f"Error creating folder:  {ex}")
            return None
        
    def createFolderFull(self, path):
        try:
            os.makedirs(path)
            return path
            
        except Exception as ex:
            self.logger.error(f"Error creating full folder:  {ex}")
            return None      
    def deleteFolderContent(self, folder):
        try:
           shutil.rmtree(folder)
        except Exception as ex:
            self.logger.error(f"Error deleting folder: {folder,ex}")    

    def moveFiles(self, origin, detiny):
        try:
            
           shutil.move(origin, detiny)
           return True
           
        except Exception as ex:
            self.logger.error(f"Error moving folder content: {ex}") 
            pass 
            return False 
    
    def exist(self, file):
        return os.path.isfile(file)
    
    def existFolder(self, folder):
        return os.path.isdir(folder)   

    def deleteSingleFile(self, file):
        return os.remove(file)
    
    def deleteContent(self, folder):
        list = os.listdir(folder)
        for item in list:
            os.remove(f"{folder}/{item}")
        return True
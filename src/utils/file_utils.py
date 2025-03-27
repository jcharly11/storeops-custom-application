import os
import shutil
import logging

class FileUtils():
    def __init__(self) -> None:
        self.logger = logging.getLogger("main")

    def fileExists(self, path):
        try:
            return os.path.exists(path)
            
        except Exception as ex:
            self.logger.error(f"Error looking for file:  {ex}")
            return None    
        
    def folderExist(self, path):
        try:
            return os.path.isdir(path)
             
            
        except Exception as ex:
            self.logger.error(f"Error looking for folder:  {ex}")
            return None    
        
    def createFolderFull(self, path):
        try:
            os.makedirs(path, mode=777)
            return path
            
        except Exception as ex:
            self.logger.error(f"Error creating full folder:  {ex}")
            return None      
        
    def deleteFolderContent(self, folder):
        try:
           shutil.rmtree(folder)
        except Exception as ex:
            self.logger.error(f"Error deleting folder: {folder,ex}")    

    def moveFiles(self, origin, destiny):
        try:
           
           
           shutil.move(origin, destiny)
           self.logger.info(f"Success moving to backup")
           
           return True
           
        except Exception as ex:
            self.logger.error(f"Error moving folder content: {ex}") 
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
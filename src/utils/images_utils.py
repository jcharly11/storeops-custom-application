import base64
import os
import shutil
import logging

class ImageUtils():
   def __init__(self) -> None:
       self.logger = logging.getLogger("main")
   
   def createImageFromBase64(self, file, data):
        try:
            print(data)
            with open(file, "wb") as img_result:
                img_result.write(base64.b64decode(data))
            return True
            
        except Exception as ex:
            self.logger.error(f"Error creating image:  {ex}")
            return False
        

   def createImagePath(self, uuid):
        try:
            folder =  f"./snapshots/{uuid}"
            os.makedirs(folder)
            return folder
            
        except Exception as ex:
            self.logger.error(f"Error creating folder:  {ex}")
            return None
        
   def deleteLocalImages(self, folder):
        try:
           shutil.rmtree("./snapshots/"+folder)
        except Exception as ex:
            self.logger.error(f"Error deleting folder: {folder,ex}")    

   def createImage(self, file, data):
        try:
            print(data)
            with open(file, "wb") as img_result:
                img_result.write(base64.b64decode(data))
            return True
            
        except Exception as ex:
            self.logger.error(f"Error creating image:  {ex}")
            return False

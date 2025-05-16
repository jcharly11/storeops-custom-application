from utils.time_functions import TimeUtils
from config import settings
import os
class TaskDeletePolicy():


    def __init__(self , ) -> None:
        self.timeUtils = TimeUtils()
        self.path = settings.EPC_FILE_PATH
        self.contentFile = []
        self.backPath = settings.EPC_FILE_BACKUP_PATH
        self.fullBackupPath = self.backPath + settings.BACKUP_FILES_NAME
        if not os.path.exists(self.backPath):
            os.makedirs(self.backPath)

        pass
    
    def cleanData(self):
        dateLimit = self.timeUtils.get24HoursFromNow()
        with open(self.path) as file:
            content = file.readlines()
            for line in content:
                 dateRegister = line.split(",")
                 dataString = dateRegister[2].strip()
                 dateRegister = self.timeUtils.stringToDateTime(dataString) 
                 if(dateRegister > dateLimit):
                     self.contentFile.append(line.strip())
                
        file.close()
        self.reabuildFile()   


    def reabuildFile(self):
        with open(self.fullBackupPath, "w") as file:
            for line in self.contentFile:
                file.write(line + "\n")

        file.close()
        os.replace(src=self.fullBackupPath,dst= self.path)
    
  
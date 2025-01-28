import logging  
import config.settings as settings
from utils.time_utils import DateUtils
from utils.file_utils import FileUtils
import csv
class LogMessagesUtil:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.path = settings.LOGS_MESSAGE_PATH
        self.dateUtils =DateUtils()
        self.fileUtils = FileUtils()
        self.writes = None
        self.file = None

    def create(self):
        try:
            date=self.dateUtils.getTimeStampSimple()
            self.file= f"{date}.csv"
            if self.fileUtils.folderExist(self.path) is False:
                self.fileUtils.createFolderFull(self.path)
            return True  
        except Exception as ex:
             return False    

        
        


    def save(self, message):
        with open(f"{self.path}/{self.file}", mode='w') as file:
                    self.writer = csv.writer(file)
                    self.writer.writerow(f"{message} \n")

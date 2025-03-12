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
            self.file= f"logs-storeops-messages.csv"
            if self.fileUtils.folderExist(self.path) is False:
                self.fileUtils.createFolderFull(self.path)
            return True  
        except Exception as ex:
             return False    

        
        


    def save(self, message, storeId, customerId, doorId, topic):
        
        data = message.data
        row = [message.timestamp, message.uuid, customerId, storeId, doorId, message.device_id, message.type, topic]
        for item in data:
            row.append(item['key'])
            if len(item['value']) > 0 :
                 row.append(item['value'][0])
             
        with open(f"{self.path}/{self.file}", mode='a') as flog:
                    self.writer = csv.writer(flog, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    self.writer.writerow(row)

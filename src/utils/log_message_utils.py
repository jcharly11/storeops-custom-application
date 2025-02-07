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
            self.file= f"storeops-messages-{date}.csv"
            if self.fileUtils.folderExist(self.path) is False:
                self.fileUtils.createFolderFull(self.path)
            return True  
        except Exception as ex:
             return False    

        
        


    def save(self, message, storeId, customerId, doorId, topic):
        self.writer = csv.writer(file,delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data = message.data
        #timestamp,uuid,customer,store,door,device,typo,eventid,datakey0,datavalue0,datakey1,datavalue1
        row = [message.timestamp, message.uuid, customerId, storeId, doorId, message.device_id, message.type, topic]
        for item in data:
             row.append(item['key'])
             row.append(item['value'][0])
             
        with open(f"{self.path}/{self.file}", mode='a') as file:
                    self.writer.writerow(row)

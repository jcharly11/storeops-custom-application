from config import settings as settings 
from events.event_bus import EventBus
from utils.sharepoint_utils import SharepointUtils
from database.database import DataBase
from utils.file_utils import FileUtils
import logging
import datetime 
class UploadUtils:

    def __init__(self) -> None:
         self.logger = logging.getLogger("ServiceReintent")
         self.sharePointUtils = SharepointUtils()
         self.database = DataBase()
         self.file_utils = FileUtils()


    def run(self, path, uuid, files, link):

        if link ==  None:
             link= self.sharePointUtils.generateLink(uuid)
        else:
             link = link

        uploaded = self.sharePointUtils.upload_group(path=path, uuid=uuid, files = files)
        if uploaded:
            self.file_utils.deleteFolderContent(folder = path)
            result = self.database.getMessages(request_uuid = uuid)
            if result:
                    data=[
                            {
                            "key": "silence",
                            "value": result[0][2] 
                            } ,
                            {"key": "EPC","value": result[0][1].replace("[","").replace("]","").replace("'","").replace(" ","").split(",")} ,
                            { 
                                "key": "media",
                                "value":link
                            } 
                    ]
                    body={ 
                            "uuid":uuid,
                            "timestamp": datetime.datetime.now().__str__(),
                            "device_model": "SFERO",
                            "device_id": settings.DEVICE_ID,
                            "version": "1.0.0",
                            "data": data
                    }               
                    EventBus.publish('PublishMessageAlarm',{'payload': {'body':body}})
        else:

            EventBus.publish('PublishMessageAlarmReintent',{'payload': {'link': link,'uuid': uuid,'files': files,'path': path}})
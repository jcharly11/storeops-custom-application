from events.event_bus import EventBus
import logging
from database.database import DataBase
from database.model.message_alarm import MessageAlarm
import datetime
import config.settings as settings

class ErrorProcess:
    def __init__(self) -> None:
        self.logger = logging.getLogger("main")
        self.database = DataBase()
        EventBus.subscribe('ErrorService', self)

    def handleMessage(self, event_type, data=None):
        self.logger.info(f"Processing message error")
        try:
            if event_type == 'ErrorService':
                message = data['payload']
                result = self.database.getMessages(message=message)

                data=[
                        {
                            "key": "silence",
                            "value": result[0][2] 
                        },
                        {"key": "EPC","value": result[0][1].replace("[","").replace("]","").replace("'","").split(",") } ,
                          { 
                              "key": "media",
                              "value":"camera unavailable"
                         } 
                 ]
                body={ 
                        "uuid": message['uuid'],
                        "timestamp": datetime.datetime.now().__str__(),
                        "device_model": "SFERO",
                        "device_id": settings.DEVICE_ID,
                        "version": "1.0.0",
                        "data": data
                 }  
                EventBus.publish('PublishMessageAlarm',{'payload': {'body':body}})
        except Exception as ex:
            self.logger.error(f"Error requesting snapshot: {ex}")  
       
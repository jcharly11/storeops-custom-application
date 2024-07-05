from events.event_bus import EventBus
import logging
import json
from database.database import DataBase
import uuid
import datetime
class MessageProcessor:
    def __init__(self) -> None:
        self.logger = logging.getLogger("main")
        self.database = DataBase()
        EventBus.subscribe("MessageLink", self)

    
    
    def handleMessage(self, event_type, data=None):#Proccessing message for alarm
          self.logger.info(f"Processing message for alarm")
          try:
           if event_type == 'MessageLink':
                 message = data['payload']
                 result = self.database.getMessages(message=message)

                 data=[
                         {
                         "key": "silence",
                          "value": result[0][2] 
                          } ,
                          {"key": "EPC","value": result[0][1].replace("[","").replace("]","").replace("'","").split(",") } ,
                          { 
                              "key": "media",
                              "value":message['link']
                         } 
                 ]
                 body={ 

                        "type": 1,
                        "uuid": message['uuid'] ,
                        "message_id": uuid.uuid4().__str__() ,
                        "timestamp": datetime.datetime.now().__str__(),
                        "version": 1,
                        "data": data
                 }  
                 EventBus.publish('PublishMessageAlarm',{'payload': {'body':body}})

                 
                 

                 #update database
                 #read database
                 #send message alarm
                 #delete message or save
                 
          except Exception as ex:
              self.logger.error(f"Error processing message for alarm: {ex}")        
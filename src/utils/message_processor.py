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
        EventBus.subscribe("MessageSnapshotLink", self)

    
    
    def handleMessage(self, event_type, data=None):#Proccessing message for item optix
          self.logger.info(f"Processing message for itemoptix")
          try:
           if event_type == 'MessageSnapshotLink':
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
                        "uuid_request": None, 
                        "timestamp": datetime.datetime.now().__str__(),
                        "version": 1,
                        "data": data
                 }  
                 EventBus.publish('PublishMessageItemOptix',{'payload': {'body':body}})

                 
                 

                 #update database
                 #read database
                 #send message itx
                 #delete message or save
                 
          except Exception as ex:
              self.logger.error(f"Error processing message fot ITX: {ex}")        
from events.event_bus import EventBus
import logging
import json
from database.database import DataBase
class MessageProcessor:
    def __init__(self) -> None:
        self.logger = logging.getLogger("main")
        self.database = DataBase()
        EventBus.subscribe("MessageSnapshotLink", self)

    
    
    def handleMessage(self, event_type, data=None):#Proccessing message for item optix
          self.logger.info(f"Processing message for itemoptix")
          try:
           if event_type == 'MessageSnapshotLink':
                 payload = data['payload']
                 uuid = payload['uuid']
                 self.database.getMessages()

                 #update database
                 #read database
                 #send message itx
                 #delete message or save
                 print(payload)
          except Exception as ex:
              self.logger.error(f"Error processing message fot ITX: {ex}")        
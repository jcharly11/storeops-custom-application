from events.event_bus import EventBus
import logging
import json
from database.database import DataBase
import uuid
import datetime
import config.settings as settings
class MessageProcessor:
    def __init__(self) -> None:
        self.logger = logging.getLogger("main")
        self.images_video_reqeusts = []
        EventBus.subscribe("MessageLinkPreProcess", self)

    
    
    def handleMessage(self, event_type, data=None):#Proccessing message for alarm
          self.logger.info(f"Processing message for alarm")
          try:
           if event_type == 'MessageLinkPreProcess':
               pass
                 
          except Exception as ex:
              self.logger.error(f"Error processing message for alarm: {ex}")        
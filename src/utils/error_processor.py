from events.event_bus import EventBus
import logging
from database.database import DataBase
from database.model.message_alarm import MessageAlarm

class ErrorProcess:
    def __init__(self) -> None:
        self.logger = logging.getLogger("main")
        self.database = DataBase()
        EventBus.subscribe('ErrorService', self)

    def handleMessage(self, event_type, data=None):
        pass
       
       
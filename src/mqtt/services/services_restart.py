from config import settings as settings 
import logging
from events.event_bus import EventBus
import json
import os
import signal

class ServiceRestart():
    
    def __init__(self):
         self.logger = logging.getLogger("main")
         EventBus.subscribe('MessageRestart',self)

    
    def handleMessage(self, event_type, data=None):
        self.logger.info(
               f"MQTT Received restart custom application")
        try:
            self.logger.info(f"Restarting custom application")
            os.kill(os.getpid(),signal.SIGKILL)
        except Exception as err:
            self.logger.info(
            f"Error restarting custom application: {err}")
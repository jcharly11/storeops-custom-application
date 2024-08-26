from config import settings as settings 
import logging
from events.event_bus import EventBus
import json
import os
import signal

class ServiceCustomMethod():
    
    def __init__(self):
         self.logger = logging.getLogger("main")
         EventBus.subscribe('CustomMethod',self)

    
    def handleMessage(self, event_type, data=None):
        self.logger.info(
               f"MQTT Received custom  method alarm application")
        try:
            payload = json.loads(data['payload'])
            
            if payload["defaultAlarming"] == 0:
                settings.CUSTOM_APP_ALARM_DECISION_ENABLED = True
            else:
                settings.CUSTOM_APP_ALARM_DECISION_ENABLED = False

        except Exception as err:
            self.logger.info(
            f"Error restarting custom application: {err}")
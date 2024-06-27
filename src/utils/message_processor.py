from events.event_bus import EventBus
import logging
import json
class MessageProcessor:
    def __init__(self) -> None:
        self.logger = logging.getLogger("main")
        EventBus.subscribe("c", self)
    
    
    def handleMessage(self, event_type, data=None):
          self.logger.info(f"Processing message for itemoptix")
          try:
           if event_type == 'MessageProcessor':
                 payload = json.loads(data['payload'])
                 print(payload)
          except Exception as ex:
              self.logger.error(f"Error processing message fot ITX: {ex}")        
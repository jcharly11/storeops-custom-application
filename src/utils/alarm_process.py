from events.event_bus import EventBus
import logging
class AlarmProcess:
    def __init__(self) -> None:
        self.logger = logging.getLogger("main")  
        EventBus.subscribe('AlarmProcess', self)

    def handleMessage(self, event_type, data=None):
        self.logger.info(f"Processing alarm")
        alarm = False
        if event_type == 'AlarmProcess':
            try:
                alarms =data['alarms']
                self.logger.info(f"Processing alarm: {len(alarms)}")

                for item in alarms:
                    uuid = item['uuid'] 
                    timestamp = item['extraPayload']['timestamp']
                    alarm = item['extraPayload']['audible_alarm']
                    
                if alarm == True:
                     EventBus.publish('MessageSnapshot',{'payload': {'uuid':uuid,'timestamp':timestamp}}   )
                    

            except Exception as ex:
                    self.logger.error(f"Error requesting snapshot: {ex}")  

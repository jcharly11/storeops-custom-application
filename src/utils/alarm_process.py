from events.event_bus import EventBus
import logging
from database.database import DataBase
from database.model.message_alarm import MessageAlarm
import config.settings as settings
class AlarmProcess:
    def __init__(self) -> None:
        self.logger = logging.getLogger("main")
        self.database = DataBase()
        self.epcsList = []  


        EventBus.subscribe('AlarmProcess', self)

    def handleMessage(self, event_type, data=None):
        self.logger.info(f"Processing alarm")
        alarmGlobal = False
        if event_type == 'AlarmProcess':
            try:
                alarms =data['alarms']
                self.logger.info(f"Processing alarm: {len(alarms)}")

                for item in alarms:
                    alarmGlobal = item['extraPayload']['audible_alarm']
                    if alarmGlobal == True:
                        request_uuid = item['uuid']
                        timestamp = item['extraPayload']['timestamp']
                        break

                if alarmGlobal == True:
                    for item in alarms: 
                        epc = item['epc']
                        self.epcsList.append(epc)  
 
                    alarm_event = { "message": MessageAlarm(
                                        request_uuid= request_uuid,
                                        message= str(self.epcsList),
                                        status=alarmGlobal,
                                        type=1,
                                        datetime_inserted=timestamp
                                    ) }
                   
                    

                    self.database.saveMessage(message=alarm_event["message"])
                    if settings.STOREOPS_MEDIA_FILES_ENABLE == '1':
                        EventBus.publish('MessageBuffer',{'payload': {'uuid':request_uuid,'timestamp':timestamp}})
                        EventBus.publish('MessageVideo',{'payload': {'uuid':request_uuid,'timestamp':timestamp}})
                    else: 
                        self.logger.info(f"Media Files Disabled no request buffer or video")
                        EventBus.publish('MessageLink', {'payload': {"uuid":request_uuid, "timestamp":timestamp, "link":""}})

                    self.logger.info(f"*******************************")
                    self.logger.info(f"Epcs in list fo messagee{self.epcsList}")
                    self.logger.info(f"*******************************")
                    self.epcsList.clear()
                  

            except Exception as ex:
                    self.logger.error(f"Error requesting snapshot: {ex}")  

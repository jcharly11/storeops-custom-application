from events.publish_to_storeops import PublishToStoreops
from events.sfero_ab.rfid_alarm import RFIDAlarmEvent 
from events.sfero_ab.rfid_exit import RFIDExitEvent
from events.sfero_ab.periodic_status import AlarmBoxPeriodicStatus
from events.sfero_ab.som_status_config import SomStatusConfig
from events.sfero_ab.wirama_status import WiramaStatus
from events.sfero_ab.onvif_status import OnvifStatus
from events.sfero_ab.som_commands import SomCommands

from mqtt.client import Client
import logging

class Event_manager(Client):

    def __init__(self, storeopsService, sharepointService, environment) -> None:
        self.logger = logging.getLogger("main") 
        self.client = Client().instance()
        self.client.on_message = self.onMessage 
        self.sharepointService = sharepointService
        self.environment = environment
        self.storeopsService = storeopsService

        self.event_list = []
        self.createEvents( mqtt_client = self.client,
                          storeopService = self.storeopsService,
                          sharepointService = self.sharepointService,
                          environment= self.environment
                            )
        self.environment.addManager(self)
        self.subscribeTopics()


    def createEvents(self, mqtt_client, storeopService, sharepointService, environment):
        self.event_list.append(PublishToStoreops(mqtt_client=mqtt_client,
                                              storeopsService=storeopService,
                                              sharepointService=sharepointService,
                                              environment=environment))
        self.logger.info("publish_to_storeops added to eventlist")

        self.event_list.append(RFIDAlarmEvent(mqtt_client=mqtt_client,
                                              storeopsService=storeopService,
                                              sharepointService=sharepointService,
                                              environment=environment))
        
        self.logger.info("rfidalarmevent added to eventlist")

        self.event_list.append(RFIDExitEvent(mqtt_client=mqtt_client,
                                              storeopsService=storeopService,
                                              sharepointService=sharepointService,
                                              environment=environment))
        self.logger.info("rfidexitevent added to eventlist")


        self.event_list.append(AlarmBoxPeriodicStatus(mqtt_client=mqtt_client,
                                              storeopsService=storeopService,
                                              sharepointService=sharepointService,
                                              environment=environment))
        self.logger.info("periodicstatus added to eventlist")


        self.event_list.append(SomStatusConfig(mqtt_client=mqtt_client,
                                              storeopsService=storeopService,
                                              sharepointService=sharepointService,
                                              environment=environment))
        self.logger.info("SomStatusConfig added to eventlist")


        self.event_list.append(WiramaStatus(mqtt_client=mqtt_client,
                                              storeopsService=storeopService,
                                              sharepointService=sharepointService,
                                              environment=environment))
        self.logger.info("WiramaStatus added to eventlist")


        self.event_list.append(OnvifStatus(mqtt_client=mqtt_client,
                                              storeopsService=storeopService,
                                              sharepointService=sharepointService,
                                              environment=environment))
        self.logger.info("onvif added to eventlist")

        self.event_list.append(SomCommands(mqtt_client=mqtt_client,
                                              storeopsService=storeopService,
                                              sharepointService=sharepointService,
                                              environment=environment))
        self.logger.info("SomCommands added to eventlist")

    def subscribeTopics(self):
        topics = []
        for event in self.event_list:
            topics.extend(event.getTopicsList())

        topics = list(set(topics))

        for topic in topics:
            self.client.subscribe(topic)
            self.logger.info(f"Subscribing to topic: {topic}")

    def onMessage(self, client, userdata, message, properties=None):
        try:
            if isinstance(message.payload, bytes):

                payload =  message.payload.decode()
                topic = message.topic
                
                for event in self.event_list:
                    event.processTopic(topic, payload)

        except Exception as err:
            self.logger.error(f"Event_manager onMessage: Topic: {topic}, Error: {err}, TypeError: {type(err)}")


    def saveVariables(self, file):
        for event in self.event_list:
            event.saveVariables(file)

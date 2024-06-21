
from paho.mqtt import client as mqtt
import uuid
import logging
import config.settings as settings
 
class Client():

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, 
                                  uuid.uuid4().__str__())
    
    def onConnect(self, client, userdata, flags, reason_code, properties=None):
            self.logger.info(f"MQTT Connected {client},{userdata},{flags},{reason_code}")

    def onDisConnect(self, client, userdata,  reason_code):
            self.logger.info(f"MQTT Disconnected {client},{userdata},{reason_code}")    
            
    def create(self):
        try:
            self.client.connect(host=settings.MQTT_SERVER, 
                            port=settings.MQTT_PORT)
            self.client.on_connect = self.onConnect
            self.client.on_disconnect = self.onDisConnect

            self.client.loop_start()
            return self.client
        except Exception as ex:
            self.logger.error("Error connection mqtt: {ex}")
    
    def susbcribe(self, subscribe):
         pass

    def publish(self):
         pass

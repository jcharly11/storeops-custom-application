
from paho.mqtt import client as mqtt
import uuid
import logging
import config.settings as settings
from mqtt.client_singleton import  singleton

@singleton 
class Client(object):

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creating instance of client")
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, 
                                  uuid.uuid4().__str__())
                                  
        try:
            self.client.connect(host="192.168.127.3", port=settings.MQTT_PORT)
            self.client.on_connect = self.onConnect
            self.client.on_disconnect = self.onDisConnect
            self.client.on_publish = self.onPublish
            self.logger.info("Creating connection")
            
            
        except Exception as ex:
            self.logger.info(f"Error connection mqtt: {ex}")

    
    def subscribe(self, topic):
         self.client.subscribe(topic=topic)

    def publish(self, topic, payload):
         self.client.publish(topic=topic, payload=payload)
             
    def onConnect(self, client, userdata, flags, reason_code, properties=None):
           print(f"MQTT Connected {client},{userdata},{flags},{reason_code}")

    def onDisConnect(self, client, userdata,  reason_code):
            print(f"MQTT Disconnected {client},{userdata},{reason_code}")    

    def onSubscribe(self, topic):
         pass

    def onPublish(self,client, data,mid):
         pass        

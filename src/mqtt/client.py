
from paho.mqtt import client as mqtt
import uuid
import logging
import config.settings as settings
from mqtt.client_singleton import  singleton

@singleton 
class Client(object):

    def __init__(self) -> None:
        self.logger = logging.getLogger("main")
        self.logger.info("Creating instance of client")
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, 
                                  uuid.uuid4().__str__())
                                  
        try:
            self.client.connect(host=settings.MQTT_SERVER, port=settings.MQTT_PORT)
            self.client.on_connect = self.onConnect
            self.client.on_disconnect = self.onDisConnect
            self.client.on_publish = self.onPublish 
            self.logger.info("Creating connection")
            self.client.loop_start()
           
            
            
        except Exception as ex:
            self.logger.info(f"Error connection mqtt: {ex}")


    def instance(self):
         return self.client


    def subscribe(self, topic):
         self.client.subscribe(topic=topic)

    def publish(self, topic, payload):
         self.client.publish(topic=topic, payload=payload)
             
    def onConnect(self, client, userdata, flags, reason_code, properties=None):
           self.logger.info(f"MQTT Connected {client},{flags},{reason_code}")

    def onDisConnect(self, client, userdata,  reason_code):
            self.logger.info(f"MQTT Disconnected {client},{userdata},{reason_code}")    

    def onSubscribe(self,client, userdata, mid, qos, properties=None):
         pass

    def onPublish(self,client, data,mid):
         pass        
     
    def onMessage(self, client, userdata, message, properties=None):
         pass
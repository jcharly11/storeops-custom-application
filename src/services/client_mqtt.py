
import paho.mqtt.client as mqtt
import config.settings as settings
import logging
import uuid

class ClientMQTT():
    def __init__(self) -> None:
        
        self.logger = logging.getLogger("ClientMQTTSSL")
        try:
            self.client =  mqtt.Client(callback_api_version = mqtt.CallbackAPIVersion.VERSION2,
                                    client_id=uuid.uuid4.__str__(), 
                                    protocol=mqtt.MQTTv5)
            # self.client.username_pw_set(username=settings.SERVER_SSL_USERNAME_ITEMOPTIX, 
            #                             password=settings.SERVER_SSL_PASSWORD_ITEMOPTIX)
            
            # self.client.tls_set( ca_certs = settings.MQTT_SSL_CA_CERTIVICATE_PATH,
            #                 certfile = settings.MQTT_SSL_SERVER_CERTIVICATE_PATH,
            #                 keyfile = settings.MQTT_SSL_KEY_CERTIVICATE_PATH )
            
        except Exception as ex:
            self.logger.error(f"mqtt error: {ex} ")



    def setOnconnectCallbak(self, callbak):
        self.client.on_connect = callbak

    def run(self):
        self.client.connect(host=settings.MQTT_SERVER, 
                            port=settings.MQTT_PORT, 
                            keepalive=settings.MQTT_KEEP_ALIVE)
        self.client.loop_start()
        return self.client
         
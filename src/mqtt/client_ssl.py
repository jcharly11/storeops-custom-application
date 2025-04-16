
from paho.mqtt import client as mqtt
import ssl
import logging
import config.storeops_settings as storeopsSettings  
from utils.certificates_utils import CertificateUtils 
from utils.file_utils import FileUtils
import time

class ClientSSL():

    # validar la existencia de certificados, esta clase maneja la solicitud de certificados al API
    # considerar reintento de solictud de certificados
    # valdacion de certificado correcto
    # reconexion considerando ondisconnect

    def __init__(self, environment, onMessage) -> None:
        self.logger = logging.getLogger("main")
        self.logger.info(f"Creating instance of SSL client")
        self.environment = environment
        self.log_prefix = "client_ssl"
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        url = f"{storeopsSettings.STOREOPS_CERTIFICATES_REQUEST_URL}:{storeopsSettings.STOREOPS_CERTIFICATES_REQUEST_PORT}"
        self.certificateUtils = CertificateUtils(url= url,
                                                 user= storeopsSettings.STOREOPS_CERTIFICATES_REQUEST_USER,
                                                 password= storeopsSettings.STOREOPS_CERTIFICATES_REQUEST_PASS)
        
        self.connected = False
        self.certificates = False
        self.fileUtils = FileUtils()

        self.subscribe_topics = []
        self.onMessage = onMessage
        
        self.connect() 
              
    def setAccountAndDevice(self, account, device):
          self.certificateUtils.setAccountAndDevice(account, device)


    def reintentCertificatesGeneration(self):
         while True:
          if self.certificates == False :
               self.certificateUtils.generate()
               self.certificates = True
               self.connect()   

          time.sleep(storeopsSettings.STOREOPS_CERTIFICATES_REQUEST_RETRY_SECS)
                   
    def connect(self):
        try:
          certificate = self.certificateUtils.exists(path=storeopsSettings.STOREOPS_FOLDER_SSL)
          if certificate is not None:
               
               self.setVariablesCredentials(username=certificate,
                                            pem=f"{storeopsSettings.STOREOPS_FOLDER_SSL}/{certificate}.pem",
                                            key=f"{storeopsSettings.STOREOPS_FOLDER_SSL}/{certificate}.key")
               
               if not self.connected:
                    self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
                    self.client.tls_set(ca_certs=None,
                                        certfile=storeopsSettings.STOREOPS_MQTT_SSL_CA_CERTIFICATE_PATH,
                                        keyfile=storeopsSettings.STOREOPS_MQTT_SSL_KEY_CERTIFICATE_PATH,
                                        cert_reqs=ssl.CERT_NONE,tls_version=ssl.PROTOCOL_TLSv1_2,ciphers=None )
                    self.client.username_pw_set(
                         username=storeopsSettings.STOREOPS_SERVER_SSL_USERNAME,
                         password=None)
                    
                    self.client.on_connect = self.onConnect
                    self.client.on_disconnect = self.onDisConnect 
                    self.client.on_message = self.onMessage
                    self.logger.info(f"{self.log_prefix}: connecting to broker: {storeopsSettings.STOREOPS_MQTT_SSL_SERVER}")
                    self.client.connect(host=storeopsSettings.STOREOPS_MQTT_SSL_SERVER, port=storeopsSettings.STOREOPS_MQTT_SSL_PORT, keepalive=60)
                    self.logger.info(f"{self.log_prefix}: Creating secure connection")
                    self.client.loop_start()
                    self.connected = True
          else:
               print(f"{self.log_prefix}: No certificates founded")
               self.generateCertificates()
               
         
        except Exception as ex:
            self.logger.info(f"{self.log_prefix}: Error secure connection mqtt: {ex.args[0]}")
            if ex.args[0] in [2,9]:
                 self.fileUtils.deleteContent(folder=storeopsSettings.STOREOPS_FOLDER_SSL)

    def generateCertificates(self):
          created, _, _, _ =self.certificateUtils.generate()
          if created:
               self.connect()              

  
  
    def subscribe(self, topic):
         if topic not in self.subscribe_topics:
            self.subscribe_topics.append(topic)
            if self.connected:
              self.client.subscribe(topic=topic)

    def unsubscribe(self, topic):
          if topic in self.subscribe_topics:
            self.subscribe_topics.remove(topic)
            if self.connected:
              self.client.unsubscribe(topic=topic)     


    def publish(self, topic, payload):
         if self.connect:
              return self.client.publish(topic=topic, payload=payload)
         else:
              return False
             
    def onConnect(self, client, userdata, flags, rc):
           self.logger.info(f"{self.log_prefix}: MQTT ssl Connected:  {client},{flags},{rc}")
           self.connected = True
           for topic in self.subscribe_topics:
              self.client.subscribe(topic=topic)

    def onDisConnect(self, client, userdata,  reason_code):
            self.logger.info(f"{self.log_prefix}: MQTT ssl Disconnected: {client},reason_code={reason_code}")
            self.connected = False
           
            
    def onMessage(self, client, userdata, message):
         self.logger.info(f"{self.log_prefix}: MQTT ssl Disconnected {client},{userdata},{message}")


    def isConnected(self):
         return self.connected
    
    def reconnect(self): 
         self.connect()

    def setVariablesCredentials(self, username , pem, key):
         try:
          storeopsSettings.STOREOPS_MQTT_SSL_CA_CERTIFICATE_PATH = pem
          storeopsSettings.STOREOPS_MQTT_SSL_KEY_CERTIFICATE_PATH = key
          storeopsSettings.STOREOPS_SERVER_SSL_USERNAME = username 
         except Exception as ex:
              self.logger.error(ex) 
               


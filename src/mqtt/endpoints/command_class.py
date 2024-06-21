from mqtt.services import MqttService


class Command(MqttService):

    def __init__(self) -> None:
        super().__init__()
        self.mqtt = MqttService()
        
        
    
    def command(self):
        timestamp = None
        version="1.0.0"
        status = None
        base64_image = None
        params = params
        
        self.mqtt.send(params=params) 

    


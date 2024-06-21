from mqtt.client import Client

class MqttService:

    def __init__(self) -> None:
        self.client = Client().create()

    def send(self, params):
        self.client.publish(params)

    def subscribe(self, topic):
        self.client.subscribe(topic=topic)
 
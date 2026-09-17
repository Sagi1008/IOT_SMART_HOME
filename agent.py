import paho.mqtt.client as mqtt
from init import BROKER, PORT

class MqttClient:
    def __init__(self, client_id):
        self.client = mqtt.Client(client_id=client_id, clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.connected = False

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        self.connected = (reason_code == 0)

    def on_disconnect(self, client, userdata, reason_code, properties=None):
        self.connected = False

    def on_message(self, client, userdata, msg):
        pass

    def connect(self, host=BROKER, port=PORT):
        self.client.connect(host, port)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop(); self.client.disconnect()

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

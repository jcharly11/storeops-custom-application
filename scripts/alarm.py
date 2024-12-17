import datetime
import uuid 
import paho.mqtt.client as paho
broker="72.20.30.1"
port=1883


def on_publish(client,userdata,result):              
    print("data published \n")
    pass
client1= paho.Client(paho.CallbackAPIVersion.VERSION2, uuid.uuid4().__str__())                     
client1.on_publish = on_publish                           
client1.connect(broker,port)  

dt = datetime.datetime.now() 
uuid = uuid.uuid4().__str__() 

template = {"uuid": f"{uuid}", "door_name": "1", "door_number": 1, "store": "1", "serial": "000e26f9df6c9d3", "epc": "E280689400005014CB64F4B6", "hostname": "ckp-e26f9df6c9d3", 
"extraPayload": {"epc": "E280689400005014CB64F4B6", "event_type": 0, "ip_address": "172.20.30.50:7240", "type": "eas", "timestamp": f"{dt}" , "sold": False, "audible_alarm": True, "readcount": 
"5:0", "tx": "1", "role": "Left PEDESTAL", "disable_light": False, "disable_sound": False}}

ret= client1.publish("alarm",template)  
print(ret)
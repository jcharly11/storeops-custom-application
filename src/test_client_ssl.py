from mqtt.client_ssl import ClientSSL
import time
import datetime
client = ClientSSL()
client.connect()

print("Client connected")
start = datetime.datetime.now()
print(f"stating at { start }")
while True:
    time.sleep(5.0)
    if  not client.isConnected():
        end = datetime.datetime.now()
        print(f"Diconnection happend at : {end}")
    
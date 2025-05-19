import config.storage_settings as storageSettings 
import json
from base64 import b64encode
import os
import requests

class StorageUtils:
    def __init__(self):
        self.username = storageSettings.USERNAME
        self.password = storageSettings.PASSWORD
        self.url = storageSettings.URL
        self.basic = b64encode(f'{self.username}:{self.password}'.encode('utf-8')).decode('ascii')
        self.headers = { 'Authorization': f'Basic {self.basic}'}

    def upload(self, path, payload):

        try:

            files = os.listdir(path)
            data = []

            for file in files:
                
                data.append(('media[]',(f"{file}",open(f'{path}/{file}','rb'),'application/octet-stream')))

            response = requests.request("POST", self.url, headers=self.headers, data=payload, files=data)
            if response.status_code == 200:
                response = json.loads(response.content)# response is a list of responses from server
                result = response[0]
                return result['url']
            else:
                return None
            
        except Exception as ex:
            return None

        
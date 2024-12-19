import requests
import logging
import os
import json
import config.storeops_settings as storeopsSettings  
from utils.file_utils import FileUtils

class CertificateUtils:

    def __init__(self, url, user, password) -> None:
        self.logger = logging.getLogger("main")
        self.utils = FileUtils()
        self.url= url
        self.token = None
        self.IdInitialized = False
        self.account = None
        self.name = None
        self.user = user
        self.password = password
        self.log_prefix = "certificate_utils"
        
    def setAccountAndDevice(self, account, device):
        self.account = account
        self.name = device
        self.IdInitialized = True
        

    def generate(self):
        if not self.IdInitialized:
            print(f" {self.log_prefix}:  class not initialzed wait for device info message to fill deveice id")
            return False , None, None, None

        status , self.token = self.getToken()
        if status:
            self.logger.info(f" {self.log_prefix}:  generated to request certificates")
            created, key , pem = self.create()

            if created:
                k, kf = self.download(url = key )
                p, pf = self.download(url = pem )
                if k and p :
                    
                    return True, self.name , kf, pf
                else:
                    return False

    def exists(self, path):

        if self.utils.existFolder(path) is False:
            self.utils.createFolderFull(path=path)

        self.logger.info(f" {self.log_prefix}: Check content of certificates path:{path}")
         
        content =  os.listdir(path)
        if len(content) > 0:
            name =   content[0]
            n = name.split(".")
            return n[0]
        else:
            return None
            


    def getToken(self):
        try:
            headers={"Content-Type": "application/json"}
            data = {
                    "username": self.user,
                    "password": self.password
                }
            response =  requests.post(url= f"{self.url}/login", headers=headers,json=data ,verify=False)
            response.raise_for_status()
            if response.status_code == 200: 
                result = json.loads(response.text)
                return True, result['token'] 
            else:
                return False , None 
        except Exception as ex:
            self.logger.error(f"{self.log_prefix} : Exception requesting token: {ex}")
            return False , None

    def download(self, url ):
        try:
            file = url
            file = file.split("/")
            localFile = f"{storeopsSettings.STOREOPS_FOLDER_SSL}/{file[-1]}" 
            response = requests.get(url=url, headers={'Authorization': self.token}, verify=False)    
            if response.status_code == 200:

                with open(localFile, mode="wb") as file:
                    for data in response.iter_content(chunk_size=10 * 1024):
                        file.write(data)
                return True, localFile
            
            else:
                return False, ""
          

        except Exception as ex:
            self.logger.info(f"Error downloading certificates: {ex}")

    def create(self):
        try:
            headers = {
                    "Authorization": self.token
                } 
            data ={
                    "attributes": {
                        "accountCode": self.account,
                        "type": "sfero"
                        },
                    "description": "Certificate description...",
                    "name": f"{self.name}"
                }

            url = f"{self.url}/create-certificate"
            self.logger.info(f"Requesting creation to: {url}")
            self.logger.info(f"Requesting creation to: {data}")
            response = requests.post(url = url , json=data, headers=headers, verify=False)
            response.raise_for_status()
            if response.status_code == 200:
                result = json.loads(response.text)
                self.logger.info(f"{self.log_prefix}: Key value for certificate: {result['key_url']}")
                self.logger.info(f"{self.log_prefix}: pem value for certificate: {result['pem_url']}")
                return True, result['key_url'], result['pem_url']
            
            else:
                return False, None, None

        except Exception as ex:
                
                self.logger.info(f"{self.log_prefix}: Error requesting creation: {ex}")
                return False, None, None
    
    
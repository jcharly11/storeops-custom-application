
import json
import logging 
import os
import config.settings as settings
import requests
from database.database import DataBase

class SharepointService():
    def __init__(self):   
        self.logger = logging.getLogger(__name__)
        
    def upload_file(self,data, origin_file, file_name):
        self.logger.info("Starting to upload file to azure storage")
        response= None
        try:
            access_token= self.getAuthToken()
            folder_name="Video"
            upload_url = f'{settings.BASE_URL}/sites/{settings.SITE_ID}/drives/{settings.DRIVE_ID}/items/root:/{folder_name}/{file_name}:/content'

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }

            with open(origin_file, 'rb') as file:
                response = requests.put(upload_url, headers=headers, data=file)
                self.logger.info(f"file upload: {response.json()}")
            
            if(response.status_code==201 or response.status_code==200):
                DataBase.saveMessage(self,response.json(),True)
            else:
                DataBase.saveMessage(self,response.json(),False)

        except Exception as err:
            self.logger.error(f"error uploading the file: {err}, {type(err)}")
            DataBase.saveMessage(self,response.json(),False)




    def upload_video(self,uuid, path):
        self.logger.info("Starting to upload video to sharepoint")
        print("Starting to upload video to sharepoint")
        try:
            access_token= self.getAuthToken()
            folder_name="Video"
            upload_url = f'{settings.BASE_URL}/sites/{settings.SITE_ID}/drives/{settings.DRIVE_ID}/items/root:/{folder_name}/{uuid}.mp4:/content'

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }

            #origin_file=f"./tmp/onvif-camera/files/{uuid}.mp4"
            origin_file=f"/home/cbernal/Github/storeops/storeops-custom-application/src/services/video/{uuid}.mp4"
            print(f"-------------------- {origin_file}")
            #origin_file=f"{uuid}.mp4"
            with open(origin_file, 'rb') as file:
                response = requests.put(upload_url, headers=headers, data=file)
                self.logger.info(f"file upload: {response.json()}")

            
            if(response.status_code==201 or response.status_code==200):
                print(f"upload video successfully")
                self.logger.info(f"upload video successfully")
            else:
                print(f"upload video fail")
                self.logger.info(f"upload video fail")
                
        except Exception as err:
            self.logger.error(f"error uploading the file: {err}, {type(err)}")


    def generateLink(self, id_folder):
        try:
            url=f"{settings.BASE_URL}/sites/{settings.SITE_ID}/drive/items/{id_folder}/createLink"
            access_token= self.getAuthToken()
            headers = {
                "Authorization": f"{access_token}",
                "Content-Type": "application/json"
            }

            expiration_date= "2024-06-13T09:18:00Z"
            data = {
                "expirationDateTime": f"{expiration_date}",
                "type": "view",
                "password": "TestCkp",
                "scope": "anonymous",
                "retainInheritedPermissions": "false"
            }
            body= json.dumps(data)
            
            resLink = requests.post(url, headers=headers, data=body)
            resJs= resLink.json()
            folderLink= resJs["link"]["webUrl"]
            return folderLink

        except Exception as err:
            self.logger.error(f"error creating link: {err}, {type(err)}")
            return None


    def getAuthToken(self):
        try:
            auth_url = f'{settings.BASE_URL_LOGIN}/{settings.TENANT_ID}/oauth2/v2.0/token'
            data = {
                'grant_type': 'client_credentials',
                'client_id': settings.CLIENT_ID,
                'client_secret': settings.CLIENT_SECRET,
                'scope': 'https://graph.microsoft.com/.default'
                }
            response = requests.post(auth_url, data=data)
            return response.json()['access_token']
        except Exception as err:
            self.logger.error(f"error get token: {err}, {type(err)}")
            return None


   

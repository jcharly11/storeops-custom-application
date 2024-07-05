import base64
import datetime
import io
import json
import logging 
import os
import config.settings as settings
import requests
from PIL import Image
from utils.images_tools import ImageEncoder

class SharepointUtils():
    def __init__(self):   
        self.logger = logging.getLogger("main")
        self.encoder = ImageEncoder()
        
    def upload_file(self,data, uuid, file_name, type_message):
        self.logger.info(f"Starting to upload file to azure storage: {file_name}")
        try:
            access_token= self.getAuthToken()
            folder_name=""
            folder_base=""
            response_json= None
            
            if(type_message=="snapshot"):
                folder_name=f"Onvif_Photos/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}"
            else:
                folder_name=f"Onvif_Photos/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}/{uuid}"

            folder_base=f"Onvif_Photos/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}"
            
            url=f"{settings.BASE_URL}/drives/{settings.DRIVE_ID}/root:/{folder_base}:/children"
            upload_url = f'{settings.BASE_URL}/sites/{settings.SITE_ID}/drives/{settings.DRIVE_ID}/items/root:/{folder_name}/{file_name}:/content'

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }
            name =  f"./snapshots/{file_name}"
            with open(name, "wb") as img_result:
                img_result.write(base64.b64decode(data.encode()))
            
            
            with open(name, 'rb') as file:
                response = requests.put(upload_url, headers=headers, data=file)
                response_json= response.json()
            
            id_folder=""

            if(type_message=="snapshot"):
                id_folder=response_json["id"]
            else:
                response_folder = requests.get(url, headers=headers)
                response_json= response_folder.json()
                for folder in response_json["value"]:
                    name=folder["name"]
                    if(name==uuid):
                        id_folder= folder["id"]
                        break

            return id_folder

        except Exception as err:
            self.logger.error(f"error uploading the file: {err}, {type(err)}")
            return None



    def upload_video(self,uuid, path):
        self.logger.info("Starting to upload video to sharepoint")
        try:
            access_token= self.getAuthToken()
            folder_name="Video"
            upload_url = f'{settings.BASE_URL}/sites/{settings.SITE_ID}/drives/{settings.DRIVE_ID}/items/root:/{folder_name}/{uuid}.mp4:/content'

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }

            origin_file=f"./snapshots/{uuid}.mp4"
            
            #origin_file=f"{uuid}.mp4"
            with open(origin_file, 'rb') as file:
                response = requests.put(upload_url, headers=headers, data=file)
                self.logger.info(f"file upload: {response.json()}")

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


            date_now = datetime.datetime.now()
            modified_date = date_now + datetime.timedelta(days=60)
            expiration_date = modified_date.strftime("%Y-%m-%dT%H:%M:%SZ") 
            
            data = {
                "expirationDateTime": f"{expiration_date}",
                "type": "view",
                "scope": "anonymous",
                "retainInheritedPermissions": "false"
            }
            body= json.dumps(data)
            
            resLink = requests.post(url, headers=headers, data=body)
            resJs= resLink.json()
            print(resJs)
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
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
        self.logger = logging.getLogger(__name__)
        self.encoder = ImageEncoder()
        
    def upload_file(self,data, file_name):
        self.logger.info("Starting to upload file to azure storage")
        try:
            access_token= self.getAuthToken()
            folder_name="Video"
            url= f"h{settings.BASE_URL}/drives/{settings.DRIVE_ID}/items/root/children/Video"
            upload_url = f'{settings.BASE_URL}/sites/{settings.SITE_ID}/drives/{settings.DRIVE_ID}/items/root:/{folder_name}/{file_name}:/content'

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }
            name =  f"./tmp/{file_name}"
            bdata = self.encoder.encodeBytes(data)
            image = Image.open(io.BytesIO(bdata))
            image.save(name)

            with open(name, 'rb') as file:
                response = requests.put(upload_url, headers=headers, data=file)
                self.logger.info(f"file upload: {response.json()}")

            
            response_folder = requests.get(url, headers=headers)
            response_json= response.json()
            id_folder= response_json["id"]
            return id_folder

        except Exception as err:
            self.logger.error(f"error uploading the file: {err}, {type(err)}")



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

            origin_file=f"./tmp/onvif-camera/files/{uuid}.mp4"
            
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

            date_now = datetime.datetime.strptime(datetime.datetime.now(), "%Y/%m/%dT%H:%M:%SZ")
            expiration_date = date_now + datetime.timedelta(days=60)
            data = {
                "expirationDateTime": f"{expiration_date}",
                "type": "view",
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
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
        
    def upload_file(self,path, uuid, file_name):
        self.logger.info(f"Starting to upload file to azure storage: {file_name}")
        try:
            access_token= self.getAuthToken()
            folder_name=""
            response_json= None
            
            folder_name=f"Onvif_Photos/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}/{uuid}"
            folder_base=f"Onvif_Photos/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}"
            
            url=f"{settings.BASE_URL}/drives/{settings.DRIVE_ID}/root:/{folder_base}:/children"
            upload_url = f'{settings.BASE_URL}/sites/{settings.SITE_ID}/drives/{settings.DRIVE_ID}/items/root:/{folder_name}/{file_name}:/content'
            file_full_path = f"{path}/{file_name}"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }
            
            with open(file_full_path, 'rb') as file:
                response = requests.put(upload_url, headers=headers, data=file)
                response_json= response.json()
            
            id_folder=""

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



    def upload_video(self,uuid, path, file_name):
        self.logger.info("Starting to upload video to sharepoint")
        try:
            access_token= self.getAuthToken()
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }
            #Path should be defined 
            folder_name=f"Onvif_Photos/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}/{uuid}"
            folder_base=f"Onvif_Photos/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}" 
            url=f"{settings.BASE_URL}/drives/{settings.DRIVE_ID}/root:/{folder_base}:/children"
            upload_url = f'{settings.BASE_URL}/sites/{settings.SITE_ID}/drives/{settings.DRIVE_ID}/items/root:/{folder_name}/{file_name}:/content'
            file_full_path = path + file_name
            with open(file_full_path, 'rb') as file:
                response = requests.put(upload_url, headers=headers, data=file)
                if response:
                    os.remove(file_full_path)
                    self.logger.info("Deleting video after upload")
                self.logger.info("UPLOADING VIDEO COMPLETE")
            
            id_folder=""

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

    def upload_group(self, path, uuid, files):
        self.logger.info(f"Starting to upload files : {len(files)} items")

        try:
            access_token= self.getAuthToken()
            success = False
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }
            folder_name=f"Onvif_Photos/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}/{uuid}"
            folder_base=f"Onvif_Photos/{settings.ACCOUNT_NUMBER}/{settings.LOCATION_ID}" 
            url=f"{settings.BASE_URL}/drives/{settings.DRIVE_ID}/root:/{folder_base}:/children"
            self.logger.info(f"Upload group id:{uuid}")
            for file_name in files:
                file_full_path = f"{path}/{file_name}"
                self.logger.info(f"Uploading file group: {file_full_path}")
                upload_url = f'{settings.BASE_URL}/sites/{settings.SITE_ID}/drives/{settings.DRIVE_ID}/items/root:/{folder_name}/{file_name}:/content'
                with open(file_full_path, 'rb') as file:
                    response = requests.put(upload_url, headers=headers, data=file)
                    
                    if response:

                        success=True
                    else:
                        success = False
                        break


            if success:
                folder_name=""
                id_folder=""
                response_folder = requests.get(url, headers=headers)
                response_folder_json= response_folder.json()
                for folder in response_folder_json["value"]:
                    name=folder["name"]
                    if(name==uuid):
                        id_folder= folder["id"]
                        break

            return True , self.generateLink(id_folder=id_folder)

        except Exception as err:
            self.logger.error(f"error uploading group of files : {err}, {type(err)}")
            return False, None

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
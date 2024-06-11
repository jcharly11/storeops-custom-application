
import logging 
import os
import config.settings as settings
import requests

class SharepointService():
    def __init__(self):   
        self.logger = logging.getLogger(__name__)
        
    def upload_file(self,data, origin_file, file_name):
        self.logger.info("Starting to upload file to azure storage")
        auth_url = f'https://login.microsoftonline.com/{settings.TENANT_ID}/oauth2/v2.0/token'

        try:
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': settings.CLIENT_ID,
                'client_secret': settings.CLIENT_SECRET,
                'scope': 'https://graph.microsoft.com/.default'
            }
            response = requests.post(auth_url, data=data)
            access_token = response.json()['access_token']

            
            upload_url = f'https://graph.microsoft.com/v1.0/sites/{settings.SITE_ID}/drives/{settings.DRIVE_ID}/items/root:/{settings.FOLDER_NAME}/{file_name}:/content'

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }

            with open(origin_file, 'rb') as file:
                response = requests.put(upload_url, headers=headers, data=file)
                self.logger.info(f"file upload: {response.json()}")



        except Exception as err:
            self.logger.error(f"error uploading the file: {err}, {type(err)}")

   

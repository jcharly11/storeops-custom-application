import traceback
import sys
import datetime
import json
import logging 
import config.settings as settings
import config.sharepoint_settings  as sharepointSettings
import requests
from utils.images_tools import ImageEncoder
from utils.file_utils import FileUtils

class SharepointUtils():
    def __init__(self):   
        self.logger = logging.getLogger("main")
        self.encoder = ImageEncoder()
        self.access_token = None
        self.filesUtils =  FileUtils()
 

    def uploadGroup(self, path, uuid, data, check_folder=True, isReintent=False): 
        try:
            self.access_token = self.getAuthToken()
            self.logger.info(f"Starting to upload files : {len(data)} items")
            self.logger.info(f"Path: {path}")

            if check_folder:
                if self.createFolderAzure(uuid) is None:
                    self.logger.error(f"error creating folder for uuid: {uuid}")
                    return False
            
            uploaded =False
            files = []
            urls = []
            today = datetime.datetime.today()
        
            year = today.year
            month =  str(today.month).zfill(2)
            day = str(today.day).zfill(2)
            folder_name=f"StoreOps_media_site/{settings.ACCOUNT_NUMBER}/{settings.STORE_NUMBER}/{year}/{month}/{year}{month}{day}/{uuid}"

            self.logger.info(f"Upload group id:{uuid}")
            for file_name in data:
                file_full_path = f"{path}/{file_name}"
                
                
                self.logger.info(f"Prepare upload file full path: {file_full_path}")
                upload_url = f'{sharepointSettings.BASE_URL}/sites/{sharepointSettings.SITE_ID}/drives/{sharepointSettings.DRIVE_ID}/items/root:/{folder_name}/{file_name}:/content'
                files.append(file_full_path) 
                urls.append(upload_url) 
                
            uploaded = map(self.upload, urls, files)
           
            return all(i for i in list(uploaded)) 
        
        except Exception as ex:
            self.logger.error(f"Exception uploadGroup: {ex}")
            self.logger.error(traceback.format_exc())
            self.logger.error(sys.exc_info()[2])
            return False
        
    def upload(self,  url, file_url ):
        success = False
        headers = {'Authorization': f'Bearer {self.access_token}','Content-Type': 'application/octet-stream'}
        try:
            with open(file_url, 'rb') as file:
                response = requests.put(url, headers=headers, data=file)
                if response:
                    success=True
                else:
                    success = False
             
        except Exception as ex:
            self.logger.error(f"Exception uploading images: {ex}")
            self.logger.error(traceback.format_exc())
            self.logger.error(sys.exc_info()[2])
            return False
            
        return success
                 

    def generateLink(self, uuid):
        try:
            id_folder= self.createFolderAzure(uuid)

            if id_folder is None:
                self.logger.error(f"error creating folder for uuid: {uuid}")
                return None
            
            url=f"{sharepointSettings.BASE_URL}/sites/{sharepointSettings.SITE_ID}/drive/items/{id_folder}/createLink"
            headers = {
                "Authorization": f"{self.access_token}",
                "Content-Type": "application/json"
            }


            date_now = datetime.datetime.now()
            modified_date = date_now + datetime.timedelta(days=90)
            expiration_date = modified_date.strftime("%Y-%m-%dT%H:%M:%SZ") 
            
            data = {
                "expirationDateTime": f"{expiration_date}",
                "type": "view",
                "scope": "anonymous",
                "retainInheritedPermissions": "false"
            }
            body= json.dumps(data)
            
            resLink = requests.post(url, headers=headers, data=body )
            resJs= resLink.json()
           

            if "link" in resJs:
                folderLink= resJs["link"]["webUrl"]
                return folderLink
            else:
                self.logger.error(f"error creating link: {resJs['error']['code']}, {resJs['error']['message']}")
                return None
            
        except Exception as err:
            self.logger.error(f"error creating link: {err}")
            return None


    def getAuthToken(self):
        try:
            auth_url = f'{sharepointSettings.BASE_URL_LOGIN}/{sharepointSettings.TENANT_ID}/oauth2/v2.0/token'
            data = {
                'grant_type': 'client_credentials',
                'client_id': sharepointSettings.CLIENT_ID,
                'client_secret': sharepointSettings.CLIENT_SECRET,
                'scope': 'https://graph.microsoft.com/.default'
                }
            response = requests.post(auth_url, data=data)
            return response.json()['access_token']
        except Exception as err:
            self.logger.error(f"error get token: {err}, {type(err)}")
            return None
        

    def createFolderAzure(self,uuid):
        try:
            id_folder = None
            self.access_token=self.getAuthToken()
            today = datetime.datetime.today()
    
            year = today.year
            month = str(today.month).zfill(2)
            day = str(today.day).zfill(2)

            folder_base= F"{settings.ACCOUNT_NUMBER}/{settings.STORE_NUMBER}/{year}/{month}"
            folder_base= F"StoreOps_media_site/{settings.ACCOUNT_NUMBER}/{settings.STORE_NUMBER}/{year}/{month}/{year}{month}{day}"

            url=f"{sharepointSettings.BASE_URL}/drives/{sharepointSettings.DRIVE_ID}/root:/{folder_base}:/children"
            
            headers = {
                "Authorization": f"{self.access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "name": f"{uuid}",
                "folder": { },
                "@microsoft.graph.conflictBehavior": "fail"
                }
            body= json.dumps(data)
            
            response = requests.post(url, headers=headers, data=body)
            
            if(response.status_code==200 or response.status_code==201):
                resJs= response.json()
                id_folder = resJs["id"]
                return  id_folder
            
            #folder already exists
            elif(response.status_code==409):
                response_folder = requests.get(url, headers=headers)
                response_folder_json= response_folder.json()
                 
                for folder in response_folder_json["value"]:
                    name=folder["name"]
                    
                    if(name==uuid):
                        id_folder= folder["id"]
                        break
                return id_folder


        except Exception as err:
            self.logger.error(f"error create sharepoint folder: {err}, {type(err)}")
            return None

    def count(self):
            try:
                headers = {
                    "Authorization": f"{self.access_token}",
                    "Content-Type": "application/json"
                    }
                url=f"{sharepointSettings.BASE_URL}/drives/{sharepointSettings.DRIVE_ID}/root:/{sharepointSettings.FOLDER_NAME}:/children"
                response = requests.get(url= url, headers=headers)
                return response.json()
            except Exception as err:
                self.logger.error(f"error get token: {err}, {type(err)}")
                return None
                
    def ping(self,  url ):
            success = False
            headers = {'Authorization': f'Bearer {self.access_token}','Content-Type': 'application/octet-stream'}
            try:
                with open(url, 'rb')  as res:
                #res =  requests.put(url, headers=headers, data=None)
                    print(res)
                    return res
                
            except Exception as ex:
                self.logger.error(f"Exception making ping images: {ex}")
                
            return success
    
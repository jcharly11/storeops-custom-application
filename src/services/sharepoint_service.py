
import logging 
import os
import config.settings as settings
from azure.storage.fileshare import ShareServiceClient,ShareFileClient


class SharepointService():
    def __init__(self):   
        self.logger = logging.getLogger(__name__)
        self.file_share_name = settings.STOREOPS_SHAREPOINT_BASE_DIRECTORY
        fileshare_exists = False
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={settings.STOREOPS_SHAREPOINT};AccountKey={settings.AZURE_KEY};EndpointSuffix=core.windows.net"

        try:
            self.service_client = ShareServiceClient.from_connection_string(self.connection_string, logging_enable=True)

            # Get a share client to interact with a specific sharefile
            self.file_share = self.service_client.get_share_client(self.file_share_name)

            try:
                share_properties = self.file_share.get_share_properties()
                fileshare_exists = True  # If the share exists
            except Exception as e:
                fileshare_exists = False

            if not fileshare_exists:
                # Create a sharefile for the shareclient
                print("CREATE FILESHARE")
                self.file_share.create_share()

                self.logger.info(f"File share '{self.file_share_name}' created successfully.")
            
        except Exception as err:
            self.logger.error(f"Error creating a file share: {err}")
        
        
    def upload_file(self,data, file):
        self.logger.info("Starting to upload file to azure storage")
        share_file_client = ShareFileClient.from_connection_string(conn_str=self.connection_string,\
                                                                        share_name=self.file_share_name, file_path=file)
        try:
            if os.path.exists(f"./files/{file}"):
             
                with open(f"./files/{file}", "rb") as source_file:
                    share_file_client.upload_file(source_file)
                
                self.logger.info(f"CSV file uploaded: {file}")

                return True
            else:
                self.logger.error(f"file {file} doesn't exist")
                
                return False

        except Exception as err:
            self.logger.error(f"error uploading the file: {err}, {type(err)}")

   

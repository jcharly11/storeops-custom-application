import json
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext, UserCredential
from office365.runtime.client_request import ClientRequest
from office365.runtime.http.request_options import RequestOptions


import requests
from shareplum import Office365
from shareplum import Site
from shareplum.site import Version

site_url = 'https://checkptsystems.sharepoint.com/'
username = "StoreOperations@checkptsystems.onmicrosoft.com"
password = "5F6c5tL!W2"

import os
import requests

# Azure AD app registration credentials
client_id = '474f7a33-805f-492f-a390-f88e355c1cf2'
client_secret = 'mdr8Q~rWmQSxij2MXTDoi6jhSQ-k5zR-CisYkaSo'
tenant_id = '1b7f891b-ffd5-438b-afd7-e35a90c2bf8d'

# SharePoint Online site URL and library name
site_id = 'e8a31de1-fce7-46f2-91e5-4a6a8fed9551'
library_name = 'Documents'
drive_id = 'b!4R2j6Of88kaR5Upqj-2VUacVEhofnqxEt475XUzCXmVl86v_nzYUQJUBUE63Ixc_'


# Authenticate and get an access token
auth_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'https://graph.microsoft.com/.default'
}
response = requests.post(auth_url, data=data)
access_token = response.json()['access_token']





# Upload a file to the SharePoint document library using the Microsoft Graph API
file_path = './src/services/test.txt' #local file path
file_name = 'test2.txt'
folder_name = 'Video'
upload_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/root:/{folder_name}/{file_name}:/content'

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/octet-stream'
}

with open(file_path, 'rb') as file:
    response = requests.put(upload_url, headers=headers, data=file)
    print(response.json())

vr=1





    
#site_url = site_url + "sites/iovideos"
Sharepoint_folder = 'Shared Documents'
fileName = '/test.txt'

authcookie = Office365(site_url, username = username, password=password).GetCookies()
site = Site(site_url, version=Version.v365, authcookie=authcookie)
folder = site.Folder(Sharepoint_folder)
with open(fileName, mode='rb') as file:
    fileContent = file.read()

folder.upload_file(fileContent, "test.txt")




















localpath = "/test.txt"
remotepath = "/sites/iovideos/"+"test.txt"
 
ctx_auth = AuthenticationContext(url=site_url)
if ctx_auth.acquire_token_for_user(username=username, password=password):
 
    ctx = ClientContext(site_url, ctx_auth)
    web=ctx.web
    ctx.load(web)
    ctx.execute_query()

    target_library = ctx.web.lists.get_by_title("iovideos")
 
 
    with open(f"/test.txt", "rb") as file:
        target_folder = target_library.root_folder
        upload_file = target_folder.upload_file("test.txt", file)
        ctx.execute_query()
else:
    print("error", ctx_auth.get_last_error())


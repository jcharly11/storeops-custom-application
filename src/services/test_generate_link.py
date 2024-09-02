import json

from office365.sharepoint.client_context import ClientContext, UserCredential
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from office365.sharepoint.webs.web import Web
import requests


site_url = 'https://checkptsystems.sharepoint.com/'
username = "StoreOperations@checkptsystems.onmicrosoft.com"
password = "5F6c5tL!W2"

client_id = '474f7a33-805f-492f-a390-f88e355c1cf2'
client_secret = 'mdr8Q~rWmQSxij2MXTDoi6jhSQ-k5zR-CisYkaSo'
tenant_id = '1b7f891b-ffd5-438b-afd7-e35a90c2bf8d'

site_id = 'e8a31de1-fce7-46f2-91e5-4a6a8fed9551'
library_name = 'Documents'
drive_id = 'b!4R2j6Of88kaR5Upqj-2VUacVEhofnqxEt475XUzCXmVl86v_nzYUQJUBUE63Ixc_'
folder_name= "Video"

id_folder="01G7JZHVJ5OVKN7AOY4FEL3EY2LQB3JW5F"
graph_endpoint = f"https://graph.microsoft.com/v1.0/sites/{site_id}/Ej11VN-B2OFIvZMaXAO026UB8qwsneRFod6rim58NZyBXQ"

auth_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'https://graph.microsoft.com/.default'
}
response = requests.post(auth_url, data=data)
access_token = response.json()['access_token']


headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

url= f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/root/children/Video"
#url=f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{id_folder}/createLink"
#url=f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{id_folder}/createLink"




#url= f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/Shared Documents/Video:/children"
response = requests.get(url, headers=headers)
va= response.json()
for item in va['folder']:
    print(item)
ai=1

from msgraph import GraphServiceClient
from msgraph.generated.drives.item.items.item.create_link.create_link_post_request_body import CreateLinkPostRequestBody
from msal import ConfidentialClientApplication

authority = f'https://login.microsoftonline.com/{tenant_id}'
scopes = ["https://graph.microsoft.com/.default"]
app = ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret,
)

response = app.acquire_token_for_client(scopes)

graph_client = GraphServiceClient(response, scopes)

request_body = CreateLinkPostRequestBody(
	type = "view",
    password= password,
	scope = "anonymous",
	retain_inherited_permissions = False,
)

result = graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(id_folder).create_link.post(request_body)
res= result.json()

auth_url2 = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
data2 = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'https://graph.microsoft.com/.default'
}
response2 = requests.post(auth_url2, data=data2)
access_token2 = response2.json()['access_token']


headers2 = {
    "Authorization": f"Bearer {access_token2}",
    "Content-Type": "application/json"
}

param = {
                  "body":f"{{type:'view', password:'password', expirationDateTime:'', retainInheritedPermissions: False, scope:'organization'}}"
                  }
body= json.dumps(param)

response = requests.post(url, headers=headers2, data=body)
code= response.status_code
res= response.json()
ai=1    
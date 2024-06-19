import asyncio
import json
from msgraph import GraphServiceClient
from msgraph.generated.drives.item.items.item.create_link.create_link_post_request_body import CreateLinkPostRequestBody
from azure.core.credentials import TokenCredential
from azure.core.credentials import AccessToken
import msal
import requests




async def createLink():
        await asyncio.sleep(1)
        client_id = '474f7a33-805f-492f-a390-f88e355c1cf2'
        client_secret = 'mdr8Q~rWmQSxij2MXTDoi6jhSQ-k5zR-CisYkaSo'
        tenant_id = '1b7f891b-ffd5-438b-afd7-e35a90c2bf8d'

        site_id = 'e8a31de1-fce7-46f2-91e5-4a6a8fed9551'

        id_folder="01G7JZHVJ5OVKN7AOY4FEL3EY2LQB3JW5F"
        drive_id = 'b!4R2j6Of88kaR5Upqj-2VUacVEhofnqxEt475XUzCXmVl86v_nzYUQJUBUE63Ixc_'

        authority = f'https://login.microsoftonline.com/{tenant_id}'
        scopes = ["https://graph.microsoft.com/.default"]

        auth_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'

        url=f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/Video/createLink"

        # app = msal.ConfidentialClientApplication(
        #     client_id,
        #     authority=authority,
        #     client_credential=client_secret,
        # )

        # response=None
        # response = app.acquire_token_silent(scopes, account=None)
        # if not response:
        #     response = app.acquire_token_for_client(scopes=scopes)

        # token= response["access_token"]

        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
            }
        response = requests.post(auth_url, data=data)
        token= response.json()['access_token']

        headers2 = {
            "Authorization": f"{token}",
            "Content-Type": "application/json"
        }
        body2 = {
            "expirationDateTime": "2024-06-13T09:18:00Z",
            "type": "view",
            "password": "TestCkp",
            "scope": "anonymous",
            "retainInheritedPermissions": "false"
        }
        body= json.dumps(body2)
        #body= "{'expirationDateTime':'2024-06-13T09:18:00Z','type':'view','password':'TestCkp','scope':'anonymous','retainInheritedPermissions':'false'}"
        
        
        resLink = requests.post(url, headers=headers2, data=body)
        resJs= resLink.json()
        folderLink= resJs["link"]["webUrl"]
        vas=1


asyncio.run(createLink())

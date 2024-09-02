import os
import requests

try: 
    client_id = '376f340a-7b96-40c6-89fb-xxxxxxxxx'
    client_secret = ''
    tenant_id = ''

   
    site_id = ''
    library_name = 'sites'
    drive_id = '' 
    auth_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    response = requests.post(auth_url, data=data)
    access_token = response.json()['access_token']

    file_path = '/home/hugo/STOREOPS/storeops-custom-application/src/services/test.txt' 
    file_name = 'test.txt'
    folder_name = 'sri'
    upload_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/root:/{folder_name}/{file_name}:/content'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(os.path.getsize(file_path))
    }
    with open(file_path, 'rb') as file:
        response = requests.put(upload_url, headers=headers, data=file)
        print(response.json())
except Exception as ex:
    print(ex)
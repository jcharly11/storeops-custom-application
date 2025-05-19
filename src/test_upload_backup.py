from utils.storage_utils import StorageUtils
import datetime

storegeUtils = StorageUtils()
payload = {
    'uuID': '0000000-00000000',
    'storeID': '5200',
    'datetime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
}
result = storegeUtils.upload(path='tests', payload=payload)
print(result)


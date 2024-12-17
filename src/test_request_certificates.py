from mqtt.client_ssl import ClientSSL
from utils.certificates_utils import CertificateUtils

import config.storeops_settings as storeopsSettings

url = f"{storeopsSettings.STOREOPS_CERTIFICATES_REQUEST_URL}:{storeopsSettings.STOREOPS_CERTIFICATES_REQUEST_PORT}"
utils = CertificateUtils(url= url,user= storeopsSettings.STOREOPS_CERTIFICATES_REQUEST_USER,password= storeopsSettings.STOREOPS_CERTIFICATES_REQUEST_PASS)
token = utils.getToken()
print(token)
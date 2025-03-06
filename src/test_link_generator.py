from utils.sharepoint_utils import SharepointUtils
import config.settings as settings

print("*****************************")
uuid = "0000-0000-0000-00002"
settings.STORE_NUMBER = "110"
settings.ACCOUNT_NUMBER = "4784"
utils = SharepointUtils()
link = utils.generateLink(uuid=uuid)
print(link)
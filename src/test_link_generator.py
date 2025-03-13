from utils.sharepoint_utils import SharepointUtils
import config.settings as settings
import time
print("*****************************")

t = 0
while t <= 1000:
    uuid = f"0000-0000-0000-0000{t}"
    settings.STORE_NUMBER = "110"
    settings.ACCOUNT_NUMBER = "4784"
    utils = SharepointUtils()
    link = utils.generateLink(uuid=uuid)
    print(uuid)
    print(link)
    time.sleep(1)
    t += 1
    # total = utils.count()
    # print(total)
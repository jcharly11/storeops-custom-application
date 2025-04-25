from utils.sharepoint_utils import SharepointUtils
import config.settings as settings
import time
import random

print("*****************************")

numc = random.randrange(1, 10**3)
nums = random.randrange(1, 10**3)


t = 0
while t <= 10000:
    uuid = f"0000-0000-0000-0000{t}"
    settings.STORE_NUMBER = str(nums).zfill(0)
    settings.ACCOUNT_NUMBER = str(numc).zfill(0)
    utils = SharepointUtils()
    link = utils.generateLink(uuid=uuid)
    print(uuid)
    print(link)
    time.sleep(1)
    t += 1
   
   

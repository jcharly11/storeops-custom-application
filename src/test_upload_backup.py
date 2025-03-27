from utils.sharepoint_utils import SharepointUtils
import config.settings as settings
import random


settings.ACCOUNT_NUMBER = "5200"
nums = random.randrange(1, 10**3)
settings.STORE_NUMBER = str(nums).zfill(0)

uuid = f"0000-0000-0000-0000"
utils = SharepointUtils()
link = utils.generateLink(uuid=uuid)
print(f"Upload link:{ link }")
res = utils.uploadGroup(path=f"test/snapshots/{uuid}", uuid=uuid, data=["1.jpg","2.jpg","3.jpg","4.jpg","5.jpg"])


   
   

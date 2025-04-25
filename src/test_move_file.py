from utils.sharepoint_utils import SharepointUtils
from utils.file_utils import FileUtils
import config.settings as settings
import random


settings.ACCOUNT_NUMBER = "5200"
nums = random.randrange(1, 10**3)
settings.STORE_NUMBER = str(nums).zfill(0)
from config.settings import BACKUP_FILES_AZURE_PATH

uuid = f"0000-0000-0000-0000"
filesUitils = FileUtils()
BACKUP_FILES_AZURE_PATH="backup"
if not filesUitils.folderExist(BACKUP_FILES_AZURE_PATH):
            filesUitils.createFolderFull(BACKUP_FILES_AZURE_PATH)

if not filesUitils.folderExist(f"{BACKUP_FILES_AZURE_PATH}/snapshots/{uuid}"):
            filesUitils.createFolderFull(f"{BACKUP_FILES_AZURE_PATH}/snapshots/{uuid}")
            
origin=f"test/snapshots/{uuid}/1.jpg"
destiny=f"{BACKUP_FILES_AZURE_PATH}/snapshots/{uuid}/1.jpg"

filesUitils.moveFiles(origin=origin,destiny=destiny)


   
   

import os

# TODO: Update default values

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", default="INFO")

# MQTT local Settings
MQTT_SERVER = os.getenv("MQTT_SERVER", default="172.20.30.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", default=1883))
MQTT_KEEP_ALIVE = int(os.getenv("MQTT_KEEP_ALIVE", default=60))

# MQTT Topics
TOPIC_WIRAMA_EPC_ALL = os.getenv(
    "TOPIC_WIRAMA_EPC_ALL", default="Wirama/EPC/All")
TOPIC_SERVER_STATS = os.getenv("TOPIC_LPP_STATS", default="server/stats")
TOPIC_STORE_INFO = os.getenv("TOPIC_STORE_INFO", default="store/info")
TOPIC_CUSTOM_ALARM = os.getenv("TOPIC_VOICE_ALARM", default="/custom/alarm")
TOPIC_CUSTOM_METHOD = os.getenv("TOPIC_CUSTOM_METHOD", default="/settings/alarm")
TOPIC_RESTART_APPLICATION = os.getenv("TOPIC_RESTART_APPLICATION", default="command/request/custom/storeops-custom-application/refresh-environment")

# MQTT Topics storeops


# Default REST call values
DEVICE_TYPE = os.getenv("DEVICE_TYPE", default="SFERO_SFP10")
DEVICE_ID = 'EMPTY'
LOCATION_ID = 'EMPTY'
ACCOUNT_NUMBER = 'EMPTY'
STORE_NUMBER = 'EMPTY'
MESSAGE_VERSION = '1.0'

TECHNOLOGY_RFID = 'rfid'


DATETIME_STRING_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
MQTT_KEEP_ALIVE_ITEMOPTIX = True

REQUEST_MEDIA_IMAGES_TIMEOUT = 1
REQUEST_MEDIA_VIDEO_TIMEOUT = 1

#Default host paths

BACKUP_FILES_AZURE_PATH = './backup'

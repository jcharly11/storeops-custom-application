import os

# TODO: Update default values

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", default="INFO")

# MQTT Settings
MQTT_SERVER = os.getenv("MQTT_SERVER", default="172.20.30.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", default=1883))
MQTT_KEEP_ALIVE = int(os.getenv("MQTT_KEEP_ALIVE", default=60))

# MQTT Topics
TOPIC_WIRAMA_EPC_ALL = os.getenv(
    "TOPIC_WIRAMA_EPC_ALL", default="Wirama/EPC/All")
TOPIC_SERVER_STATS = os.getenv("TOPIC_LPP_STATS", default="server/stats") 
TOPIC_CUSTOM_ALARM = os.getenv("TOPIC_VOICE_ALARM", default="alarm")
TOPIC_CUSTOM_ALARM_EAS = os.getenv("TOPIC_VOICE_ALARM", default="event/custom/alarm")
TOPIC_CUSTOM_METHOD = os.getenv("TOPIC_CUSTOM_METHOD", default="/settings/alarm")
TOPIC_RESTART_APPLICATION = os.getenv("TOPIC_RESTART_APPLICATION", default="command/request/custom/refresh-environment")
TOPIC_STORE_INFO = os.getenv("TOPIC_STORE_INFO", default="store/info")

# Server Settings
SERVER_URL = os.getenv("SERVER_URL", default="http://sfero-test-server")
SERVER_USERNAME = os.getenv("SERVER_USERNAME", default="ckp")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD", default="test")
SERVER_TIMEOUT_SEC = int(os.getenv("SERVER_TIMEOUT_SEC", default=5))
SERVER_URL_POST_LOGIN = os.getenv(
    "SERVER_URL_POST_LOGIN", default='{}/api/user/login'.format(SERVER_URL))
SERVER_URL_FORBIDDEN_TAGS = os.getenv(
    "SERVER_URL_FORBIDDEN_TAGS", default='{}/api/v1/gates/forbidden-tags'.format(SERVER_URL))
SERVER_RESPONSE_TOLERANCE_MS = int(
    os.getenv("SERVER_RESPONSE_TOLERANCE_MS", default=200))

# Default REST call values
DEVICE_TYPE = os.getenv("DEVICE_TYPE", default="SFERO_SFP10")
DEVICE_ID = 'EMPTY'
LOCATION_ID = 'EMPTY'

# Alarm configurations
ALARM_NORMAL_SOUND_ENABLE = 1
ALARM_NORMAL_SOUND_VOLUME = -1
ALARM_DELAYED_SOUND_ENABLE = 0
ALARM_DELAYED_SOUND_VOLUME = -1
ALARM_NORMAL_LIGHT_ENABLE = 1
ALARM_NORMAL_LIGHT_COLOR = "red"
ALARM_DELAYED_LIGHT_ENABLE = 1
ALARM_DELAYED_LIGHT_COLOR = "blue"

# Timer configurations
VOICE_ALARM_TOLERANCE_SEC = int(
    os.getenv("VOICE_ALARM_TOLERANCE_SEC", default=4))
SCHEDULE_PROCESS_EVENTS_SEC = float(
    os.getenv("SCHEDULE_PROCESS_EVENTS_SEC", default=0.1))
SCHEDULE_PROCESS_ERRORS_SEC = int(os.getenv(
    "SCHEDULE_PROCESS_ERRORS_SEC", default=60))
SCHEDULE_AUTH_TOKEN_REFRESH_SEC = int(os.getenv(
    "SCHEDULE_AUTH_TOKEN_REFRESH_SEC", default=60 * 59))
SCHEDULE_AUTH_TOKEN_CHECK_SEC = int(os.getenv(
    "SCHEDULE_AUTH_TOKEN_CHECK_SEC", default=60))
SCHEDULE_STORE_INFO_SEC = int(os.getenv(
    "SCHEDULE_STORE_INFO_SEC", default=60))
SCHEDULE_CUSTOM_METHOD_SEC = int(os.getenv(
    "SCHEDULE_CUSTOM_METHOD_SEC", default=60))



#STOREOPS ENVIRONMENT
STOREOPS_MQTT_ENABLE = os.getenv("STOREOPS_MQTT_ENABLE", default=1)
STOREOPS_SERVER = os.getenv("STOREOPS_SERVER", default="")
STOREOPS_PORT = os.getenv("STOREOPS_PORT", default="")
STOREOPS_USERNAME = os.getenv("STOREOPS_USERNAME", default="")
STOREOPS_PASSWORD = os.getenv("STOREOPS_PASSWORD", default="")
STOREOPS_MESSAGES_RETENTION_DAYS = os.getenv("STOREOPS_MESSAGES_RETENTION_DAYS", default=7)
STOREOPS_DEVICE_MODEL = os.getenv("STOREOPS_DEVICE_MODEL", default="SFERO")
STOREOPS_TECHNOLOGY = os.getenv("STOREOPS_TECHNOLOGY", default="rfid")
STOREOPS_TIMEZONE = os.getenv("STOREOPS_TIMEZONE", default="")
STOREOPS_SHAREPOINT_ENABLE = os.getenv("STOREOPS_SHAREPOINT_ENABLE", default=0)
STOREOPS_SHAREPOINT_XXX = os.getenv("STOREOPS_SHAREPOINT_XXX", default='')
STOREOPS_SHAREPOINT_BASE_DIRECTORY = os.getenv("STOREOPS_SHAREPOINT_BASE_DIRECTORY", default="onviffiles")
STOREOPS_SHAREPOINT_RETENTION_DAYS = os.getenv("STOREOPS_SHAREPOINT_RETENTION_DAYS", default=3)


#ONVIF TOPICS
TOPIC_CAMERA_IMAGE = str(os.getenv("TOPIC_CAMERA_IMAGE", default="command/onvif/image/snapshot"))
TOPIC_CAMERA_IMAGE_RESP = str(os.getenv("TOPIC_CAMERA_IMAGE_RESP", default="command_resp/onvif/image/snapshot"))

TOPIC_CAMERA_IMAGE_BUFFER = str(os.getenv("TOPIC_CAMERA_IMAGE_BUFFER", default="command/onvif/image/get_buffer"))
TOPIC_CAMERA_IMAGE_BUFFER_RESP = str(os.getenv("TOPIC_CAMERA_IMAGE_BUFFER_RESP", default="command_resp/onvif/image/get_buffer"))

TOPIC_CAMERA_VIDEO = str(os.getenv("TOPIC_CAMERA_VIDEO", default="command/onvif/video/get_video"))
TOPIC_CAMERA_VIDEO_RESP = str(os.getenv("TOPIC_CAMERA_VIDEO_RESP", default="command_resp/onvif/video/get_video"))
#EVENT TOPIC EAS RFID
TOPIC_CAMERA_VIDEO_MEDIALINK_EAS = str(os.getenv("TOPIC_CAMERA_VIDEO_MEDIALINK_EAS", default="command_resp/storeops/media"))
TOPIC_RFID_ALARM = str(os.getenv("TOPIC_RFID_ALARM", default="event/storeops/rfid_alarm"))

#FILESHARE SETTINGS
CLIENT_ID = '474f7a33-805f-492f-a390-f88e355c1cf2'
CLIENT_SECRET = 'mdr8Q~rWmQSxij2MXTDoi6jhSQ-k5zR-CisYkaSo'
TENANT_ID = '1b7f891b-ffd5-438b-afd7-e35a90c2bf8d'

SITE_ID = 'e8a31de1-fce7-46f2-91e5-4a6a8fed9551'
LIBRARY_NAME = 'Documents'
DRIVE_ID = 'b!4R2j6Of88kaR5Upqj-2VUacVEhofnqxEt475XUzCXmVl86v_nzYUQJUBUE63Ixc_'
FOLDER_NAME= "Video"
BASE_URL="https://graph.microsoft.com/v1.0"
BASE_URL_LOGIN= "https://login.microsoftonline.com"


STANDARD_PAYLOAD = "{{type: {type}, \
                    uuid: {uuid}, \
                    message_id: {message_id}, \
                    uuid_request: {uuid_request}, \
                    timestamp:{timestamp}, \
                    version: {version} \
                    data: {data}}}"
                    
DEVICE_ID = 'EMPTY'
LOCATION_ID = 'EMPTY'
ACCOUNT_NUMBER = 'EMPTY'
STORE_NAME = 'EMPTY'
DOOR_NAME='EMPTY'
DOOR_NUMBER='EMPTY'
STORE_NUMBER = 'EMPTY'
ALARM_AGGREGATION_WINDOW_SEC = float(
    os.getenv("ALARM_AGGREGATION_WINDOW_SEC", default=1.0))

MESSAGE_VERSION = "1.0"

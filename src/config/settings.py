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
TOPIC_ALARM = os.getenv("TOPIC_ALARM", default="alarm")
TOPIC_SERVER_STATS = os.getenv("TOPIC_LPP_STATS", default="server/stats")
TOPIC_STORE_INFO = os.getenv("TOPIC_STORE_INFO", default="store/info")
TOPIC_CUSTOM_ALARM = os.getenv("TOPIC_VOICE_ALARM", default="/custom/alarm")
TOPIC_CUSTOM_METHOD = os.getenv("TOPIC_CUSTOM_METHOD", default="/settings/alarm")
TOPIC_CUSTOM_NOTIFICATION_ALARM = os.getenv("TOPIC_CUSTOM_NOTIFICATION_ALARM", default="event/custom/alarm")
TOPIC_CUSTOM_EXIT = os.getenv("TOPIC_CUSTOM_EXIT_NOT_ALARM", default="event/custom/exit")

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

#Check if there is a custom app making alarm decision
CUSTOM_APP_ALARM_DECISION_ENABLED = False

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

ALARM_AGGREGATION_WINDOW_SEC = float(
    os.getenv("ALARM_AGGREGATION_WINDOW_SEC", default=1.0))

# Timer configurations
VOICE_ALARM_TOLERANCE_SEC= int(
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

#custom app configurations
CHECKTIME_TOLERANCE_PREVIOUS_ALARM = int(
    os.getenv("CHECKTIME_TOLERANCE_PREVIOUS_ALARM", default=4))
SHEDULE_SEND_FTP_FILES = float(os.getenv(
    "SHEDULE_SEND_FTP_FILES", default=3600))

# SHEDULE_CREATE_CSV_FILES = float(os.getenv(
#     "SHEDULE_CREATE_CSV_FILES", default=1800))
SHEDULE_CREATE_CSV_FILES = float(os.getenv(
    "SHEDULE_CREATE_CSV_FILES", default=1800))
CREATE_CSV_FILES_ENABLE = int(os.getenv(
    "SCHEDULE_STORE_INFO_SEC", default=1))

SHEDULE_CLEAN_OLD_INFO = float(os.getenv(
    "SHEDULE_CLEAN_OLD_INFO", default=21600))

GLOBAL_TIME = 0
STORE_NUMBER= LOCATION_ID
ACCOUNT_ID=0
DOOR_NUMBER=0
USERNAME_SFTP = str(
    os.getenv("USERNAME_SFTP", default="wirama2"))
PASSWORD_SFTP = str(
    os.getenv("PASSWORD_SFTP", default="F69tvbQ8f7fK"))
HOST_SFTP = str(
    os.getenv("HOST_SFTP", default="sftp-storeops.checkpoint-service.com"))
PORT_SFTP = int(os.getenv(
    "PORT_SFTP", default=22))
REMOTEDIR_SFTP = str(
    os.getenv("REMOTEDIR_SFTP", default=""))

#key data of sftp-storeops.checkpoint-service.com
KEYS_SSH_RSA_SFTP_SERVERS=[b"""AAAAB3NzaC1yc2EAAAADAQABAAACAQCtFQUwHqooZojDujAPEZlM9EXjRrwKdmqHvAtjLDQrytlRXEbjRi7LPTY0cwNhRRfNSDdvWp7Qa2oDOLLrPwEhrX4RlzaWDMPNz71aZpmy/QiNr+Rc9CO9/ExplYWRap/xjQ7KUJfoGLR+cyddTYo4iAOlVFFfx32BTWzOaiVksWsVQOLxqH/af+OUZ0f4CljZk0Qb/4LZAPRbarg2IE79aQCEiRvSRfgoBDtXhElEhh9TR5oqx37FPQUX28kDp0UzPdS1S2cYClWBKTGnaO0gaU32l1VkIsbxyCWqL4LO+8F7XqON01QQMZeVwl88AOBxJ0jw1LHW5voejgPOsPxyXO9KyOigda09wj2bfDppnwm8SuZJ1gAA8YEWgSUJzL0TClLV3ilZ9XLEsQhVIQivmUO6GFfO/HfObQC8RusynMJSEh6KrQSGCu/H0R7hxCl3VCv/278OBZZTMXxYzi5U2CdEiK6a+4KyfEYYvMjoqAeBnxixQvs2l/o/+tv5vRCqJKarw8tMarWfWYP6fMmDIaBomJ9W/Ouv7zM7sczNwG15meUCLow9/ucipiu9tXxs/UoM62vpUozHBLoUppjsfa9oQZRLAPHy84ybw9RKvtUpr5avLsVv+wWWCjf3u7F9ha95wwUlbux3zGEdsSH4AtvauMs0wTmmoYGDqCVDHQ=="""]
ALARM_ALL_EPCS_ENABLE = 1
CSV_STORE_DAYS = int(os.getenv(
    "CSV_STORE_DAYS", default=7))
EPC_FILE_PATH = "./files/EPCS.csv"
EPC_FILE_BACKUP_PATH = "./files/bk/"
BACKUP_FILES_NAME = "EPCS-BK.csv"
EVENT_VIEWER_MAX_LENGTH = 500

timeout_create_csv=''
timeout_clean_old=''

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
TOPIC_STORE_INFO = os.getenv("TOPIC_STORE_INFO", default="store/info")
TOPIC_CUSTOM_ALARM = os.getenv("TOPIC_VOICE_ALARM", default="/custom/alarm")
TOPIC_CUSTOM_METHOD = os.getenv("TOPIC_CUSTOM_METHOD", default="/settings/alarm")
TOPIC_RESTART_APPLICATION = os.getenv("TOPIC_RESTART_APPLICATION", default="command/request/custom/refresh-environment")

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

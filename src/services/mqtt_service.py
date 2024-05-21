import logging
import time
import config.settings as settings
from datetime import datetime


class MQTTService():
    def __init__(self, mqtt):
        self.logger = logging.getLogger(__name__)
        self.mqtt = mqtt
        self.last_alarm_ts = None

    def check_tolerance(self):
        return (time.time() - self.last_alarm_ts) >= settings.VOICE_ALARM_TOLERANCE_SEC

    def send_voice_alarm(self, light: int, light_color: str, sound: int, sound_volume: int):
        try:
            if self.last_alarm_ts is None or self.check_tolerance():
                self.last_alarm_ts = time.time()
                param = {
                    "light": light,
                    "lightColor": light_color,
                    "sound": sound
                }
                if sound_volume != -1:
                    param["soundVolume"] =  sound_volume
                self.logger.info(f"Sending voice/alarm message with {param}")
                self.mqtt.publish(settings.TOPIC_CUSTOM_ALARM, param)
        except Exception as err:
            self.logger.error(f"send_voice_alarm {err}, {type(err)}")

    def send_forbidden_tag_stats(self, epcs, http_code: int, elapsed_time: int, url: str, body: str):
        try:
            param = {
                "timeStamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "eventType": 0,
                "url": url,
                "epcs": ','.join(epcs),
                "httpCode": http_code,
                "elapsedTime": elapsed_time,
                "epcsCount": len(epcs),
                "uniqueEpcsCount": len(list(set(epcs))),
                "body": body
            }
            self.logger.info(f"Sending forbidden tag stats {param}")
            topic = '{}/forbidden-tags/default'.format(
                settings.TOPIC_SERVER_STATS)
            self.mqtt.publish(topic, param)
        except Exception as err:
            self.logger.error(
                f"send_forbidden_tag_stats {err}, {type(err)}")

    def send_forbidden_tag_error_stats(self, epcs, http_code: int, elapsed_time: int, url: str, error: str):
        try:
            param = {
                "timeStamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "eventType": -1,
                "url": url,
                "epcs": ','.join(epcs),
                "httpCode": http_code,
                "elapsedTime": elapsed_time,
                "epcsCount": len(epcs),
                "uniqueEpcsCount": len(list(set(epcs))),
                "error": error
            }
            self.logger.info(f"Sending forbidden tag stats {param}")
            topic = '{}/forbidden-tags/errors'.format(settings.TOPIC_SERVER_STATS)
            self.mqtt.publish(topic, param)
        except Exception as err:
            self.logger.error(
                f"send_forbidden_tag_error_stats {err}, {type(err)}")

    def send_user_login_stats(self, http_code: int, elapsed_time: int, url: str):
        try:
            param = {
                "timeStamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "eventType": 0,
                "url": url,
                "httpCode": http_code,
                "elapsedTime": elapsed_time
            }
            self.logger.info(f"Sending user login stats {param}")
            topic = '{}/user-login/default'.format(settings.TOPIC_SERVER_STATS)
            self.mqtt.publish(topic, param)
        except Exception as err:
            self.logger.error(f"send_user_login_stats {err}, {type(err)}")

    def send_user_login_error_stats(self, http_code: int, elapsed_time: int, url: str, error: str):
        try:
            param = {
                "timeStamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "eventType": -1,
                "url": url,
                "httpCode": http_code,
                "elapsedTime": elapsed_time,
                "error": error
            }
            self.logger.info(f"Sending user login stats {param}")
            topic = '{}/user-login/errors'.format(settings.TOPIC_SERVER_STATS)
            self.mqtt.publish(topic, param)
        except Exception as err:
            self.logger.error(
                f"send_user_login_error_stats {err}, {type(err)}")

    def send_store_info_get(self):
        try:
            param = {
                "type": "get"
            }
            self.logger.info(f"Sending store/info request {param}")
            self.mqtt.publish(settings.TOPIC_STORE_INFO, param)
        except Exception as err:
            self.logger.error(f"send_store_info_get {err}, {type(err)}")

    def send_custom_method(self, default_alarming: int):
        try:
            param = {
                "type": "custom",
                "defaultAlarming": default_alarming
            }
            self.logger.debug(f"Sending custom method {param}")
            self.mqtt.publish(settings.TOPIC_CUSTOM_METHOD, param)
        except Exception as err:
            self.logger.error(f"send_custom_method {err}, {type(err)}")

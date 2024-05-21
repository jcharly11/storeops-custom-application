import httpx
import json
import logging
import config.settings as settings

# TODO: Update based on customer requirements

class RESTService():
    def __init__(self, url, timeout, mqtt_service):
        self.logger = logging.getLogger(__name__)
        self.url = url
        self.timeout = timeout
        self.token = None
        self.mqtt_service = mqtt_service

    def authenticate(self, username, password):
        elapsed_time_ms = 0
        url = settings.SERVER_URL_POST_LOGIN
        with httpx.Client() as client:
            try:
                data = {
                    "username": username,
                    "password": password
                }
                response = client.post(url, timeout=self.timeout, json=data)
                self.logger.info(f"Response text: {response.text}")
                elapsed_time_ms = round(
                    response.elapsed.total_seconds() * 1000)
                self.logger.info(
                    f"Response total milliseconds: {elapsed_time_ms}")
                # send to MQTT for monitoring
                self.mqtt_service.send_user_login_stats(
                    http_code=response.status_code, elapsed_time=elapsed_time_ms, url=url)
                response.raise_for_status()
                if response.status_code == 200:
                    self.token = response.headers["Authorization"]
            except httpx.HTTPStatusError as ex:
                # send to MQTT for monitoring
                self.mqtt_service.send_user_login_error_stats(
                    http_code=ex.response.status_code, elapsed_time=elapsed_time_ms, url=url, error=str(ex))
                self.logger.error(
                    f"Error response {ex.response.status_code} while requesting {ex.request.url!r}.")
            except httpx.HTTPError as ex:
                # send to MQTT for monitoring
                self.mqtt_service.send_user_login_error_stats(
                    http_code=-1, elapsed_time=elapsed_time_ms, url=url, error=str(ex))
                self.logger.error(
                    f"Error while requesting {ex.request.url!r}.")

    def forbidden_tags(self, epcs, deviceType, deviceId, locationId):
        forbidden = False
        error = True
        elapsed_time_ms = 0
        url = settings.SERVER_URL_FORBIDDEN_TAGS

        if self.token is None:
            self.logger.error(f"Authorization token is not yet available")
            # send to MQTT for monitoring
            self.mqtt_service.send_forbidden_tag_error_stats(
                epcs=epcs, http_code=-1, elapsed_time=elapsed_time_ms, url=url, error="Authorization token is not yet available")
            return (forbidden, elapsed_time_ms, error)

        with httpx.Client() as client:
            try:
                headers = {
                    "Authorization": self.token
                }
                params = {
                    "deviceType": deviceType,
                    "deviceId": deviceId,
                    "locationId": locationId,
                    "epcs": list(set(epcs))
                }
                response = client.get(
                    url, timeout=self.timeout, params=params, headers=headers)
                self.logger.info(f"Response text: {response.text}")
                elapsed_time_ms = round(
                    response.elapsed.total_seconds() * 1000)
                self.logger.info(
                    f"Response total milliseconds: {elapsed_time_ms}")
                # send to MQTT for monitoring
                self.mqtt_service.send_forbidden_tag_stats(
                    epcs=epcs, http_code=response.status_code, elapsed_time=elapsed_time_ms, url=url, body=response.text)
                response.raise_for_status()
                try:
                    forbidden = json.loads(response.text)["forbiddenTags"]
                    error = False
                except Exception as err:
                    self.logger.error(
                        f"Failed to get forbiddenTags {err}, {type(err)}")
            except httpx.HTTPStatusError as ex:
                # Empty token if 401 was received
                if ex.response.status_code == 401:
                    self.logger.info(f"Resetting token on 401.")
                    self.token = None
                # send to MQTT for monitoring
                self.mqtt_service.send_forbidden_tag_error_stats(
                    epcs=epcs, http_code=ex.response.status_code, elapsed_time=elapsed_time_ms, url=url, error=str(ex))
                self.logger.error(
                    f"Error response {ex.response.status_code} while requesting {ex.request.url!r}.")
            except httpx.HTTPError as ex:
                # send to MQTT for monitoring
                self.mqtt_service.send_forbidden_tag_error_stats(
                    epcs=epcs, http_code=-1, elapsed_time=elapsed_time_ms, url=url, error=str(ex))
                self.logger.error(
                    f"Error while requesting {ex.request.url!r}.")
        return (forbidden, elapsed_time_ms, error)

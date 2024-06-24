import json
import logging
import queue
import time
import datetime
import uuid
import config.settings as settings
import os
import signal

from logging.config import dictConfig
from fastapi import FastAPI

from models import LogConfig  
from utils.environment_validator import EnvironmentValidator
from mqtt.services.sharepoint_service import SharePointService

# globals
# queue for event processing

 
environment = EnvironmentValidator()
event_queue = queue.Queue()
error_queue = queue.Queue()
# application logging
dictConfig(LogConfig().dict())
logger = logging.getLogger("main")

app = FastAPI()
logger.info("Creating instance o sharepoint service")
sharepointService= SharePointService()


type = "STOREOPS_MESSAGE_EVENT"
uuid = uuid.uuid4()
message_id = "Only applies for event/status messages."
uuid_request = "Only applies for response messages"
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
version = "1.0"
data = [{
        "key1" : "hello", 
        "key2": "world"}]

payload = settings.STANDARD_PAYLOAD.format(
    type = type,
    uuid = uuid,
    uuid_request = uuid_request,
    message_id = message_id,
    timestamp = timestamp,
    version = version,
    data = data
)
sharepointService.pub(payload=payload) 


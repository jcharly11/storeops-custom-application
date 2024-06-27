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
from mqtt.services.storeops_service import StoreOpsService
from mqtt.services.services_info import ServiceInfo
from mqtt.services.sharepoint_service import SharePointService
from utils.alarm_process import AlarmProcess
from utils.message_processor import MessageProcessor
import queue 
queueAlarm = queue.Queue() 
queueInfo = queue.Queue() 
# application logging
dictConfig(LogConfig().dict())
logger = logging.getLogger("main")

app = FastAPI()
logger.info("Creating instance o storeops service") 

messageProcceso = MessageProcessor()
serviceInfo = ServiceInfo()
alarmProcess = AlarmProcess()
storeOpService = StoreOpsService()
sharePointService = SharePointService()
storeOpService.run(queueAlarm=queueAlarm,queueInfo=queueInfo)



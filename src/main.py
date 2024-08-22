import json
import logging
import multiprocessing.queues
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
from mqtt.services.services_restart import ServiceRestart
from utils.alarm_process import AlarmProcess
from utils.error_processor import ErrorProcess
from utils.message_processor import MessageProcessor
import multiprocessing
queueAlarm = multiprocessing.Queue() #queue.Queue() 
queueInfo = queue.Queue() 
# application logging
dictConfig(LogConfig().dict())
logger = logging.getLogger("main")

app = FastAPI()
logger.info("Creating instance o storeops service") 

environmentValidator =  EnvironmentValidator()
logger.info(f"STOREOPS_MQTT_ENABLE: {settings.STOREOPS_MQTT_ENABLE}")
logger.info(f"STOREOPS_SERVER: {settings.STOREOPS_SERVER}")
logger.info(f"STOREOPS_PORT: {settings.STOREOPS_PORT}")
logger.info(f"STOREOPS_USERNAME: {settings.STOREOPS_USERNAME}")
logger.info(f"STOREOPS_PASSWORD: {settings.STOREOPS_PASSWORD}")
logger.info(f"STOREOPS_MESSAGES_RETENTION_DAYS: {settings.STOREOPS_MESSAGES_RETENTION_DAYS}")
logger.info(f"STOREOPS_DEVICE_MODEL: {settings.STOREOPS_DEVICE_MODEL}")
logger.info(f"STOREOPS_TECHNOLOGY: {settings.STOREOPS_TECHNOLOGY}") 
logger.info(f"STOREOPS_SHAREPOINT_ENABLE: {settings.STOREOPS_SHAREPOINT_ENABLE}") 
logger.info(f"STOREOPS_SHAREPOINT_BASE_DIRECTORY: {settings.STOREOPS_SHAREPOINT_BASE_DIRECTORY}") 
logger.info(f"STOREOPS_SHAREPOINT_XXX: {settings.STOREOPS_SHAREPOINT_XXX}") 
logger.info(f"STOREOPS_SHAREPOINT_BASE_DIRECTORY: {settings.STOREOPS_SHAREPOINT_BASE_DIRECTORY}") 
logger.info(f"STOREOPS_SHAREPOINT_RETENTION_DAYS: {settings.STOREOPS_SHAREPOINT_RETENTION_DAYS}") 
logger.info(f"ALARM_AGGREGATION_WINDOW_SEC: {settings.ALARM_AGGREGATION_WINDOW_SEC}") 

messageProcceso = MessageProcessor()
serviceInfo = ServiceInfo()
alarmProcess = AlarmProcess()
errorProcess= ErrorProcess()
storeOpService = StoreOpsService()
sharePointService = SharePointService()
serviceRestart = ServiceRestart()
storeOpService.run(queueAlarm=queueAlarm,queueInfo=queueInfo)



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
import queue


queueAlarm = queue.Queue()

# application logging
dictConfig(LogConfig().dict())
logger = logging.getLogger("main")

app = FastAPI()
logger.info("Creating instance o storeops service")
storeOpService = StoreOpsService()
storeOpService.setQueue(queue=queueAlarm)

 
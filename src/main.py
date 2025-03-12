import logging
from logging.config import dictConfig
from fastapi import FastAPI 
from models import LogConfig
from utils.environment_validator import EnvironmentValidator
from events.event_manager import Event_manager
from services.sharepoint_service import SharepointService
from services.storeops_service import StoreopsService


 
environment = EnvironmentValidator()

storeOpsService = StoreopsService(environment = environment)
environment.addManager(storeOpsService)

sharepointService = SharepointService()
environment.addManager(sharepointService)

eventManager =  Event_manager(storeopsService = storeOpsService,
                              sharepointService = sharepointService,
                              environment = environment)



# application logging
dictConfig(LogConfig().dict())
logger = logging.getLogger("main")
# main application
app = FastAPI() 



import config.settings as settings

from pydantic import BaseModel


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "main"
    LOG_FORMAT: str = "[%(asctime)s.%(msecs)03dZ] [%(name)-15.15s] %(levelprefix)s %(message)s"
    LOG_LEVEL: str = settings.LOG_LEVEL

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        }
    }
    loggers = {
        "main": {
            "handlers": ["default"],
            "level": LOG_LEVEL
        },
        "services.lpp_service": {
            "handlers": ["default"],
            "level": LOG_LEVEL
        },
        "services.mqtt_service": {
            "handlers": ["default"],
            "level": LOG_LEVEL
        },
        "uvicorn" : {
            "handlers": ["default"],
            "level": LOG_LEVEL
        }
    }

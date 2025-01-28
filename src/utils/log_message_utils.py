import logging  
import config.settings as settings
from utils.time_utils import DateUtils
class LogMessagesUtil:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.path = settings.LOGS_MESSAGE_PATH
        self.dateUtils =DateUtils()

    def create():
        pass

    def save(message):
        pass

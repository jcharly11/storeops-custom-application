import os
import config.settings as settings
import logging
import stat
import time
import os
from utils.restart import Restart
from utils.file_utils import FileUtils

class EnvironmentValidator():
    def __init__(self): 
        self.logger = logging.getLogger("main")
        self.fileUtils = FileUtils()
        self.managers = []
        path =settings.ENVIRONMENT_VARS_PATH
        self.fileName = f"{path}/local-environment-vars.txt"
        self.fileName_ui = f"{path}/ui-local-environment-vars.txt"

        try:
            if self.fileUtils.folderExist(path=path) == False:
                self.fileUtils.createFolderFull(path=path)


            
            if self.fileUtils.fileExists(path=self.fileName_ui) == False:      
                with open(self.fileName_ui, mode="w") as file_ui:
                    file_ui.write("")
            os.chmod(self.fileName_ui, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  
        except Exception as err:
            self.logger.info(f"Error Env validator: {err}")   

    def addManager(self, manager):
        self.managers.append(manager)
        self.create(self.fileName)

    def create(self, fileName):
        with open(fileName, mode="w") as file:
            for manager in self.managers:
                manager.saveVariables(file)
        os.chmod(self.fileName, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    def updateLocalVariables(self, restart = False):
        self.create(self.fileName_ui)
        if restart:
            self.logger.info(f"Restarting custom application")
            Restart.run()


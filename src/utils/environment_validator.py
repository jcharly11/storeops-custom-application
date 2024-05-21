import os
import config.settings as settings
import logging
import stat
#Class to setup environment variables in running container

class EnvironmentValidator():
    def __init__(self): 
       self.logger = logging.getLogger("main")
       self.fileName = "./environment/local-environment-vars.txt"
       self.fileName_ui = "./environment/ui-local-environment-vars.txt"
       self.create()

    def create(self):
        try:
            # TODO: Add code logic for environment variables
            self.logger.warning(f"Create base configuration file")
            with open(self.fileName, mode="w") as file:
                pass # Remove when logic added
                # Example code to add environment variables to modify trough UI
                # file.write(f"export SERVER_URL={os.getenv('SERVER_URL', default='http://sfero-test-server') }"+ "\n")

            if os.path.exists(self.fileName_ui) == False:      
                with open(self.fileName_ui, mode="w") as file_ui:
                    file_ui.write("")
            os.chmod(self.fileName_ui, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  
        except Exception as err:
            self.logger.info(f"Error Env validator: {err}")   

    def create_ui_conf(self):
        try:
            # TODO: Add code logic for environment variables
            self.logger.warning(f"Create local configuration file")
            with open(self.fileName_ui, mode="w") as file:
                pass # Remove when logic added
                # Example code to add environment variables to modify trough UI
                # file.write(f"export SERVER_URL={settings.SERVER_URL}"+ "\n")

            os.chmod(self.fileName_ui, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  
        except Exception as err:
            self.logger.info(f"Error Env validator: {err}")   


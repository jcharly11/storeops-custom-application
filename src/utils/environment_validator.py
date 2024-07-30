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

                file.write(f"export STOREOPS_MQTT_ENABLE={os.getenv('STOREOPS_MQTT_ENABLE', default=1) }"+ "\n")
                file.write(f"export STOREOPS_SERVER={os.getenv('STOREOPS_SERVER', default='') }"+ "\n")
                file.write(f"export STOREOPS_PORT={os.getenv('STOREOPS_PORT', default=80) }"+ "\n")
                file.write(f"export STOREOPS_USERNAME={os.getenv('STOREOPS_USERNAME', default='') }"+ "\n")
                file.write(f"export STOREOPS_PASSWORD={os.getenv('STOREOPS_PASSWORD', default='') }"+ "\n")
                file.write(f"export STOREOPS_MESSAGES_RETENTION_DAYS={os.getenv('STOREOPS_MESSAGES_RETENTION_DAYS', default=7) }"+ "\n")
                file.write(f"export STOREOPS_DEVICE_MODEL={os.getenv('STOREOPS_DEVICE_MODEL', default='SFERO') }"+ "\n")
                file.write(f"export STOREOPS_TECHNOLOGY={os.getenv('STOREOPS_TECHNOLOGY', default='rfid') }"+ "\n")
                file.write(f"export STOREOPS_TIMEZONE={os.getenv('STOREOPS_TIMEZONE', default='') }"+ "\n")
                file.write(f"export STOREOPS_SHAREPOINT_ENABLE={os.getenv('STOREOPS_SHAREPOINT_ENABLE', default=0) }"+ "\n")
                file.write(f"export STOREOPS_SHAREPOINT_BASE_DIRECTORY={os.getenv('STOREOPS_SHAREPOINT_BASE_DIRECTORY', default='') }"+ "\n")
                file.write(f"export STOREOPS_SHAREPOINT_XXX={os.getenv('STOREOPS_SHAREPOINT_XXX', default='') }"+ "\n")
                file.write(f"export STOREOPS_SHAREPOINT_BASE_DIRECTORY={os.getenv('STOREOPS_SHAREPOINT_BASE_DIRECTORY', default='storeops') }"+ "\n")
                file.write(f"export STOREOPS_SHAREPOINT_RETENTION_DAYS={os.getenv('STOREOPS_SHAREPOINT_RETENTION_DAYS', default=3)}"+ "\n")
                
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


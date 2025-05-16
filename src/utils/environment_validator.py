import os
import config.settings as settings
import logging
import stat
#Class to setup environment variables in running container
class EnvironmentValidator():
      def __init__(self): 
            self.logger = logging.getLogger("main")
            self.fileName = "./environment/local-environment-vars.txt"
            self.create()



      def create(self):
            self.logger.info(f"starting read file")
            
            try:

                  if os.path.exists(self.fileName) == False:
                        with open(self.fileName, mode="w") as file:
                              file.write(f"export ALARM_AGGREGATION_WINDOW_SEC={os.getenv('ALARM_AGGREGATION_WINDOW_SEC', default=1.0) }"+ "\n")
                              file.write(f"export SHEDULE_CREATE_CSV_FILES={ os.getenv('SHEDULE_CREATE_CSV_FILES', default=1800)}" + "\n")
                              file.write(f"export CREATE_CSV_FILES_ENABLE={ os.getenv('CREATE_CSV_FILES_ENABLE', default=1)}" + "\n")
                              file.write(f"export USERNAME_SFTP={ os.getenv('USERNAME_SFTP', default='wirama2')}" + "\n")
                              file.write(f"export PASSWORD_SFTP={ os.getenv('PASSWORD_SFTP', default='F69tvbQ8f7fK')}" + "\n")
                              file.write(f"export HOST_SFTP={ os.getenv('HOST_SFTP', default='sftp-storeops.checkpoint-service.com')}" + "\n")
                              file.write(f"export PORT_SFTP={ os.getenv('PORT_SFTP', default='22')}" + "\n")
                              file.write(f"export CSV_STORE_DAYS={ os.getenv('CSV_STORE_DAYS', default=7)}" + "\n")
                              
                        os.chmod(self.fileName, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


            except Exception as err:
                  self.logger.info(f"Error Env validator: {err}")
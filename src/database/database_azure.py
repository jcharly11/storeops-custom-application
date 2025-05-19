import sqlite3
import logging
import os
import datetime
from database.config.db_config_azure import DB_AZURE_PATH, TABLE_FILES
from config.settings import STORAGE_DB_BASE_PATH
from utils.file_utils import FileUtils

class DataBaseFiles():
     
    def __init__(self):
          try:     
               self.logger = logging.getLogger("main") 
               self.fileUtils = FileUtils()
               if self.fileUtils.folderExist(path = STORAGE_DB_BASE_PATH) == False:
                     self.fileUtils.createFolderFull(path = STORAGE_DB_BASE_PATH)               
               self.createDB()

          except sqlite3.Error as err:
               
               self.recreateDB()
               self.logger.error(f"Database for images creation exception:", err.args)


    def createDB(self):
       path = os.path.realpath(DB_AZURE_PATH)
       self.connection = sqlite3.connect(path, check_same_thread=False, timeout=20, detect_types=sqlite3.PARSE_DECLTYPES)
       if self.connection is not None:
             self.connection.execute(TABLE_FILES)

    def recreateDB(self):
          try:
              path = os.path.realpath(DB_AZURE_PATH)
              os.remove(path=path)
              os.remove(path=DB_AZURE_PATH)
              self.createDB()
                
          except Exception as err:
                self.logger.error(f"Database remove file exception:", err.args)
    def getAllFiles(self):
          try:
                self.cursor = self.connection.cursor()
                self.cursor.execute("SELECT * FROM files ")
                events = self.cursor.fetchall()
                return events
          
          except Exception as ex:
               self.logger.info(f"Error get files: ",ex)

    def saveFiles(self, request_uuid, link, files, path):
        try:
               date_time_inserted= datetime.datetime.now()
               self.cursor = self.connection.cursor()
               self.cursor.execute('INSERT or REPLACE INTO files VALUES (?,?,?,?,?)',(request_uuid, 
                                                                                      files, 
                                                                                      link, 
                                                                                      date_time_inserted.strftime("%Y-%m-%d"), 
                                                                                      path))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query insert files: ",ex.args)
               return ex.args


    def deleteFiles(self, request_uuid, path):
        try:
               
               self.cursor = self.connection.cursor()
               self.cursor.execute('DELETE FROM files WHERE request_uuid =? AND path=?' , (request_uuid, path))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query insert files: ",ex.args)
               return False
        
    def getFilesOlderThan(self, date_time_inserted):
          
          try:
                self.cursor = self.connection.cursor()
                self.cursor.execute("SELECT request_uuid, date_time_inserted, path from files WHERE  DATE(date_time_inserted) <= ?", (date_time_inserted,))
                events = self.cursor.fetchall()
                

                return events
          
          except Exception as ex:
               print(f"Error get files: ",ex)
               self.logger.info(f"Error get files: ",ex)
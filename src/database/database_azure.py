import sqlite3
import logging
import os
import datetime

from database.config.db_config_azure import DB_AZURE_PATH, TABLE_FILES

class DataBaseFiles():
     
    def __init__(self):
          try:     
               self.logger = logging.getLogger("main") 
               self.createDB()

          except sqlite3.Error as err:
               self.recreateDB()
               self.logger.error(f"Database for images creation exception:", err.args)


    def createDB(self):
       path = os.path.realpath(DB_AZURE_PATH)
       self.connection = sqlite3.connect(path, check_same_thread=False, timeout=20)
       if self.connection is not None:
             self.connection.execute(TABLE_FILES)
 

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
               self.cursor.execute('INSERT or REPLACE INTO files VALUES (?,?,?,?,?)',(request_uuid, files, link, date_time_inserted, path))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query insert files: ",ex.args)
               return ex.args


    def deleteFiles(self, request_uuid):
        try:
               
               self.cursor = self.connection.cursor()
               self.cursor.execute('DELETE FROM files WHERE request_uuid =?', (request_uuid,))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query insert files: ",ex.args)
               return False
        
        
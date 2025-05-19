import sqlite3
import logging
import os
import datetime
import pickle

from database.config.db_config import DB_PATH, TABLE_MESSAGES
from utils.file_utils import FileUtils
from config.settings import STORAGE_DB_BASE_PATH
class DataBase():
     
    def __init__(self):
          try:     
               self.logger = logging.getLogger("main") 
               self.fileUtils = FileUtils()
               
               if self.fileUtils.folderExist(path = STORAGE_DB_BASE_PATH) == False:
                     self.fileUtils.createFolderFull(path = STORAGE_DB_BASE_PATH)

               self.createDB()

          except sqlite3.Error as err:
               self.recreateDB()
               self.logger.error(f"Database creation exception:", err.args)


    def createDB(self):
       path = os.path.realpath(DB_PATH)
       self.connection = sqlite3.connect(path, check_same_thread=False, timeout=20, detect_types=sqlite3.PARSE_DECLTYPES)
       if self.connection is not None:
             self.connection.execute(TABLE_MESSAGES)

    def recreateDB(self):
          try:
              path = os.path.realpath(DB_PATH)
              os.remove(path=path)
              os.remove(path=DB_PATH)
              self.createDB()
                
          except Exception as err:
                self.logger.error(f"Database remove file exception:", err.args)


    def getMessages(self, date , status = 'sent'):
          try:
                self.cursor = self.connection.cursor()
                self.cursor.execute("SELECT message FROM messages_storeops WHERE  DATE(date_time_inserted)  <= ? and status = ?", (date, status, ))
                messages = []
                events = self.cursor.fetchall()
                for event in events:
                    m = pickle.loads(event[0])
                    messages.append(m)
                return messages
          
          except Exception as ex:
               self.logger.info(f"Error get messages: ",ex)
               return []

    def getMessageAll(self):
          try:
                self.cursor = self.connection.cursor()
                self.cursor.execute("SELECT message FROM messages_storeops ORDER BY date_time_inserted DESC")
                events = self.cursor.fetchall()
                return events
          
          except Exception as ex:
               self.logger.info(f"Error get messages: ",ex)
               return []

    def saveMessage(self, message, message_status):
        try:
               # usar datetime now para inserted message
               date_time_inserted= datetime.datetime.now()
               self.cursor = self.connection.cursor()
               self.cursor.execute('INSERT or REPLACE INTO messages_storeops VALUES (?,?,?,?,?,?)',(message['message'].uuid,
                                                                                                    pickle.dumps (message['message']), 
                                                                                                    message_status, 
                                                                                                    message['type'], 
                                                                                                    message['message'].timestamp,
                                                                                                    date_time_inserted.strftime("%Y-%m-%d")))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query insert message: ",ex.args)
               return ex.args


    def deleteMessage(self, request_uuid):
        try:
               
               self.cursor = self.connection.cursor()
               self.cursor.execute('DELETE FROM messages_storeops WHERE request_uuid =?', (request_uuid,))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query insert message: ",ex.args)
               return False
        
    def deleteOldMessage(self, date):
        try:
               
               self.cursor = self.connection.cursor()
               self.cursor.execute('DELETE FROM messages_storeops WHERE DATE(date_time_inserted) <= ?', (date ,))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query insert message: ",ex.args)
               return False
        
    def deleteByStatusMessage(self, status):
        
        try:
               
               self.cursor = self.connection.cursor()
               self.cursor.execute('DELETE FROM messages_storeops WHERE status == ?', (status,))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query delete message by status: ",ex.args)
               return False      


    def upadateMessage(self, request_uuid, status):
        try:
               self.cursor = self.connection.cursor()
               self.cursor.execute('UPDATE messages_storeops SET status=? WHERE request_uuid == ?', (status, request_uuid))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query delete message by status: ",ex.args)
               return False    
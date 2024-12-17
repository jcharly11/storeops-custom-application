import sqlite3
import logging
import os
import datetime

from database.config.db_config import DB_PATH, TABLE_MESSAGES

class DataBase():
     
    def __init__(self):
          try:     
               self.logger = logging.getLogger("main") 
               self.createDB()

          except sqlite3.Error as err:
               self.recreateDB()
               self.logger.error(f"Database creation exception:", err.args)


    def createDB(self):
       path = os.path.realpath(DB_PATH)
       self.connection = sqlite3.connect(path, check_same_thread=False, timeout=20)
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
                self.cursor.execute("SELECT message FROM messages WHERE date_time_inserted <= ? and status = ?", (date, status ))
                events = self.cursor.fetchall()
                return events
          
          except Exception as ex:
               self.logger.info(f"Error get messages: ",ex)

    def getMessageAll(self):
          try:
                self.cursor = self.connection.cursor()
                self.cursor.execute("SELECT message FROM messages ORDER BY date_time_inserted DESC")
                events = self.cursor.fetchall()
                return events
          
          except Exception as ex:
               self.logger.info(f"Error get messages: ",ex)

    def saveMessage(self, message, message_status):
        try:
               # usar datetime now para inserted message
               date_time_inserted= datetime.datetime.now()
               self.cursor = self.connection.cursor()
               self.cursor.execute('INSERT or REPLACE INTO messages VALUES (?,?,?,?,?,?)',(message['message'].uuid,
                                                                                         message['message'].__str__(), 
                                                                                         message_status, 
                                                                                         message['type'], 
                                                                                         message['message'].timestamp,
                                                                                         date_time_inserted))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query insert message: ",ex.args)
               return ex.args


    def deleteMessage(self, request_uuid):
        try:
               
               self.cursor = self.connection.cursor()
               self.cursor.execute('DELETE FROM messages WHERE request_uuid =?', (request_uuid,))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query insert message: ",ex.args)
               return False
        
    def deleteOldMessage(self, date):
        try:
               
               self.cursor = self.connection.cursor()
               self.cursor.execute('DELETE FROM messages WHERE date_time_inserted <= ?', (date,))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query insert message: ",ex.args)
               return False
        
    def deleteByStatusMessage(self, status):
        
        try:
               
               self.cursor = self.connection.cursor()
               self.cursor.execute('DELETE FROM messages WHERE status == ?', (status,))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query delete message by status: ",ex.args)
               return False      


    def upadateMessage(self, request_uuid, status):
        try:
               self.cursor = self.connection.cursor()
               self.cursor.execute('UPDATE SET status=? FROM messages WHERE request_uuid == ?', (status, request_uuid))
               self.connection.commit()
               return True
                  
        except Exception as ex:
               self.logger.info(f"Error executing query delete message by status: ",ex.args)
               return False    
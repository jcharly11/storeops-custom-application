import sqlite3
import logging
import os
import datetime

from database.config.db_config import DB_PATH, TABLE_MESSAGES

class DataBase():
     
    def __init__(self):
          try:     
               self.logger = logging.getLogger("main") 
               path = os.path.realpath(DB_PATH)
               self.connection = sqlite3.connect(path, check_same_thread=False, timeout=20)
               if self.connection is not None:
                     self.connection.execute(TABLE_MESSAGES)
          
          except sqlite3.Error as err:
               self.logger.error(f"Database creation exception:", err.args)

    def getMessages(self):
          try:
                self.cursor = self.connection.cursor()
                self.cursor.execute("SELECT * FROM messages WHERE datetime_inserted <= datetime('now', '-168 hours')")
                events = self.cursor.fetchall()
                return events
          
          except Exception as ex:
               self.logger.info(f"Error get messages: ",ex.args)

    def saveMessage(self, message, status):
        try:
               date= datetime.datetime.now()
               self.cursor = self.connection.cursor()
               self.cursor.execute('INSERT or REPLACE INTO messages VALUES (?,?,?)',(message,status,date))
               self.connection.commit()
               return True
           
        except Exception as ex:
               self.logger.info(f"Error executing query insert message: ",ex.args)

        return ex.args


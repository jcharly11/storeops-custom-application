import os
import sqlite3
import logging as logger
from database.config.db_config import DB_PATH ,TABLE_EVENTS,TABLE_EPC_EVENT







class dataBase():
    def __init__(self):
          try: 
               self.logger = logger.getLogger(__name__)

               self.logger = logger.getLogger(name ="database")    
               path = os.path.realpath(DB_PATH)
               self.connection = sqlite3.connect(path, check_same_thread=False, timeout=20)
               if self.connection is not None:
                     self.connection.execute(TABLE_EVENTS)
                     self.connection.execute(TABLE_EPC_EVENT)
          
          except sqlite3.Error as err:
               self.logger.error(f"Database creation exception:", err.args)




    def save_event(self, event):
        self.logger.info(f"Saving data event")
        try:
             
            self.cursor = self.connection.cursor()
            self.cursor.execute('INSERT or REPLACE INTO events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', 
                    (event.id_event, event.store_number, event.event_code, event.alarm_type, event.inventory_alarm,event.event_date,event.event_time,event.alarm_direction,event.SGLN,event.pedestal_id,event.account_id,event.door_id,event.date,event.datetime_inserted,event.csv_general_created, event.csv_created))
             
            self.connection.commit()
            
            return True
           
        except Exception as ex:
            print(f"Error executiong query: ",ex.args)
            return False
        
    def save_epcc(self, epcs):
        self.logger.info(f"SAVING EPCS")
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute('INSERT or REPLACE INTO events_epcs VALUES (?,?)',(epcs.idEvent, epcs.epc))
               
            self.connection.commit()
            return True
           
        except Exception as ex:
            print(f"Error executiong query: ",ex.args)
            return False

  
    
    # def getEPCS(self, date):
    #     _EVENTS = []
    #     try:
    #         self.cursor = self.connection.cursor()
    #         self.cursor.execute("""SELECT * FROM events WHERE date = ? """ , (date))
    #         result = self.cursor.fetchall()
    #         for i in result:        
    #             _EVENTS.append(i[0])
            
    #         return _EVENTS

         
    #     except Exception as ex:
    #         self.logger.error(f"Error executiong query: %s" , ex.args)
    #         return None
                    
    def getEvents(self):
        _EVENTS = []
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute("""SELECT * FROM events  """ )
            result = self.cursor.fetchall()
            for i in result:        
                _EVENTS.append(i)
            
            return _EVENTS

         
        except Exception as ex:
            self.logger.error(f"Error executiong query: %s" , ex.args)
            return None
                                    
    def getAllEPCs(self, id):
        _EPCS = []
        try:
            
            self.cursor = self.connection.cursor()
            self.cursor.execute("""SELECT epc FROM events_epcs WHERE  idEvent = ? """, (id,) )
            result = self.cursor.fetchall()
            
            for i in result:        
                _EPCS.append(i)
                
            return _EPCS

         
        except Exception as ex:
            print(f"Error executiong query: %s" , ex.args)
            return None
        
    def epcExist(self, epcs) -> bool:
        exist = False  
        for epc in epcs:
            exist = self.getSingleEPC(epc)
        return exist        


    def getSingleEPC(self, epc):
        exist = False
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute("""SELECT COUNT(*) FROM events_epcs WHERE  epc = ? """, (epc,) )
            result = self.cursor.fetchall()
            return result[0][0] > 0
            
          

         
        except Exception as ex:
            self.logger.error(f"Error executiong query: %s" , ex.args)
            return 0
        

    def update_csv_created(self, id, update_bool):
       
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute("""UPDATE events SET csv_created = ? WHERE idEvent = ? """, (update_bool, id))
            self.connection.commit()
            self.cursor.close()     
        except Exception as ex:
            print(f"Error executiong query: %s" , ex.args)
            return None

    def update_csv_general_created(self, id, update_bool):
       
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute("""UPDATE events SET csv_general_created = ? WHERE idEvent = ? """, (update_bool, id))
            self.connection.commit()
            self.cursor.close()     
        except Exception as ex:
            print(f"Error executiong query: %s" , ex.args)
            return None
        

    def getEPCs(self):
        events= list()
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute("""SELECT 
                        CASE WHEN E.alarmType=21 THEN 'ALARM' ELSE 'NO ALARM' END AS event,
                        EP.epc,
                        E.datetime_inserted AS date 
                        FROM events_epcs EP INNER JOIN events E ON E.idEvent= EP.idEvent""")
            result = self.cursor.fetchall()
           
            for i in result:        
                events.append([i[0], i[1], i[2]])
            return events 
        except Exception as ex:
            self.logger.error(f"Error executiong query: %s" , ex.args)
            return None
    

    def delete_events(self):
        events= list()
        try:
            self.cursor = self.connection.cursor()
            self.cursor.executescript("""
                    DELETE FROM events_epcs WHERE idEvent IN(
                    SELECT idEvent FROM events WHERE datetime_inserted <= datetime('now', '-24 hours'));

                    DELETE FROM events WHERE datetime_inserted <= datetime('now', '-24 hours')""")
            
            self.cursor.close()
            return True 
        except Exception as ex:
            self.logger.error(f"Error executiong query: %s" , ex.args)
            return None
    

        


    
import logging 
import os
import sqlite3
import datetime
from database.model.epc_inventory_API import EPC_Inventory_API
from database.model.epc_unknown_API import EPC_Unknown_API

from database.config.datamaster_db_config import DB_PATH, TABLE_DATAMASTER, TABLE_INVENTORY,TABLE_UNKNOWN_EPC
class datamasterDB():
    def __init__(self):
          try: 
               self.logger = logging.getLogger(__name__)

               self.logger = logging.getLogger(name ="database")    
               path = os.path.realpath(DB_PATH)
               self.connection = sqlite3.connect(path, check_same_thread=False, timeout=20)
               if self.connection is not None:
                     self.connection.execute(TABLE_DATAMASTER)
                     self.connection.execute(TABLE_INVENTORY)
                     self.connection.execute(TABLE_UNKNOWN_EPC)
          
          except sqlite3.Error as err:
               self.logger.error(f"Database creation exception:", err.args)


    def delete_datamaster(self):
       
        try:
            
            self.cursor = self.connection.cursor()
            self.cursor.execute("""DELETE FROM datamaster""")
            self.connection.commit()
            self.cursor.close()

         
        except Exception as ex:
            print(f"Error executiong query: %s" , ex.args)
            return None
        

    def insert_datamaster(self,item):
        try:
            print("**BEGIN INSERT")
            date= datetime.datetime.now().isoformat()
            self.cursor = self.connection.cursor()
            self.cursor.execute('INSERT or REPLACE INTO datamaster VALUES (?,?,?,?,?)', 
                    (item.sku, item.epc, item.description, item.image,date))
               
            self.connection.commit()
            self.cursor.close()
            print("**END INSERT")
            return True
           
        except Exception as ex:
            self.logger.info(f"Error executiong query INSERT DATAMASTER: ",ex.args)
            return False
        

    def getEPCSInventory(self):
        events= list()
        try:
            self.cursor = self.connection.cursor()
            self.cursor.executescript(""" 
                                ATTACH DATABASE '/var/storage/storeops-basic-custom-application/datamaster_database.db' AS dat;
                                ATTACH DATABASE '/var/storage/storeops-basic-custom-application/storeops_basics_database.db' AS stor;
                                
                                DELETE FROM dat.inventory;
                                      
                                INSERT INTO dat.inventory
                                SELECT DISTINCT 
                                EP.epc,
                                E.datetime_inserted as timestamp,
                                CASE WHEN E.alarmType=21 THEN 'ALARM' ELSE 'NO ALARM' END AS alarm_type,
                                IFNULL(D.description,'') AS description,
                                IFNULL(D.image,'') AS image
                                FROM stor.events_epcs EP 
                                INNER JOIN stor.events E ON EP.idEvent= E.idEvent
                                LEFT JOIN dat.datamaster D ON D.epc= EP.epc
                                ORDER BY E.datetime_inserted DESC;
                         
                                DETACH DATABASE dat;
                                DETACH DATABASE stor;        """)
            
            self.cursor.close()
            
            self.cursor = self.connection.cursor()
            self.cursor.execute("""SELECT * FROM inventory """)
            result = self.cursor.fetchall()
            
            for i in result:        
                events.append(EPC_Inventory_API(i[0], i[1], i[2], i[3], i[4]))
            
            return events 
        except Exception as ex:
            self.logger.error(f"Error executiong query: %s" , ex.args)
            return None
        

        
    def getEPCSUnknown(self):
        events= list()
        try:
            
            self.cursor = self.connection.cursor()
            self.cursor.executescript("""                                
                        ATTACH DATABASE '/var/storage/storeops-basic-custom-application/datamaster_database.db' AS dt;
                        ATTACH DATABASE '/var/storage/storeops-basic-custom-application/storeops_basics_database.db' AS st;

                        DELETE FROM dt.unknown_epc;
                                      
                        INSERT INTO dt.unknown_epc
                        SELECT DISTINCT 
                        EP.epc,
                        E.datetime_inserted AS date, 
                        CASE WHEN E.alarmType=21 THEN 'ALARM' ELSE 'NO ALARM' END AS event 
                        FROM st.events_epcs EP
                        INNER JOIN st.events E ON E.idEvent= EP.idEvent 
                        WHERE EP.epc NOT IN(SELECT epc FROM dt.datamaster D);

                        DETACH DATABASE dt;
                        DETACH DATABASE st;
                                    """)
            
            
            self.cursor.close()
            
            self.cursor = self.connection.cursor()
            self.cursor.execute("""SELECT * FROM unknown_epc """)
            result = self.cursor.fetchall()
            for i in result:        
                events.append(EPC_Unknown_API(i[0], i[2], i[1]))

            self.cursor.close()
            return events
        except Exception as ex:
            self.logger.error(f"Error executiong query: %s" , ex.args)
            return None
    
   
 
    def getdatamaster(self):
        events= list()
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute("""SELECT epc,description,sku,image,timestamp FROM datamaster""")
            result = self.cursor.fetchall()
            for i in result:        
                events.append([i[0], i[1], i[2], i[3], i[4]])
            return events 
        except Exception as ex:
            self.logger.error(f"Error executiong query: %s" , ex.args)
            return None

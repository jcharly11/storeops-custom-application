import datetime
import config.settings as settings
from services.csv_service import CSV_Service
from database.db import dataBase
from database.model.cv_object_event_EPC import cvsObjectEventEPC
import logging as logger

class taskCreateCSV():

    def __init__(self) -> None:
        self.logger = logger.getLogger(__name__)
        self.db = dataBase()
        self.csvService = CSV_Service()
        
        

    def readData(self,general_csv):
        events = self.db.getEvents()
        data = []
        
        
        for event in events:
            id=event[0]
            csv_general_created= event[14]
            csv_created = event[15]
            validateData= False
            if(general_csv and csv_general_created==0):
                validateData=True
            elif(not general_csv and csv_created==0):
                validateData=True

            if (validateData):
                group_epcs = ""
                epcs =self.db.getAllEPCs(id)
                if(len(epcs) > 1):
                    for epc in epcs:
                        group_epcs += epc[0] + ":"
                    group_epcs = group_epcs[:-1]    
                else:
                    group_epcs += epcs[0][0]

                
                
                event_csv= cvsObjectEventEPC(
                    store_number=event[1],
                    event_code=event[2],
                    epcs= group_epcs,
                    alarm_type=event[3],
                    inventory_alarm=event[4],
                    event_date= event[5],
                    event_time= event[6],
                    alarm_direction=event[7],
                    SGLN=event[8],
                    pedestal_id=event[9],
                    account_id=event[10],
                    door_id=event[11],
                    date=event[13]
                )
                data.append(event_csv)
                
                if(general_csv==True):
                    self.db.update_csv_general_created(id, True)
                else:
                    self.db.update_csv_created(id,True)
        return data   

    def createGeneralCSV(self,general_csv):
        if settings.DEVICE_ID == 'EMPTY':
            self.logger.info(f"DEVICE_ID is EMPTY")
            return
        data = self.readData(general_csv)
        #for item in data:
        #    self.csvService.create_csv(csv_model=item, serial_no= settings.DEVICE_ID, general_csv=True)

    def createCSVFile(self ):
        if settings.DEVICE_ID == 'EMPTY':
            self.logger.info(f"DEVICE_ID is EMPTY")
            return
        data = self.readData(False)
        
        self.csvService.create_csv(csv_model_global=data, serial_no= settings.DEVICE_ID, general_csv=False)


    def cleanOldData(self, old_days_csv):
        self.csvService.delete_csv(old_days_csv)

        self.db.delete_events()
        #db_limit_time = datetime.datetime.now() - datetime.timedelta(hours=old_hours_db)

        # iDD = []
        #events = self.db.getEvents()
        
        # for event in events:
        #     timestamp_orig = datetime.datetime.fromisoformat(event[13])
        #     if (timestamp_orig < db_limit_time):
        #         id=event[0]
        #         iDD.append(id)
        #self.db.deleteItems(iDD)


        

import csv
import logging as logger
import datetime
import time
import os
from os.path import exists

class CSV_Service():
    def __init__(self):
        self.logger = logger.getLogger("main")

        

    def create_csv(self, csv_model_global, serial_no, general_csv):
        try:
            if(len(csv_model_global)==0):
                 return ""
            
            date=datetime.datetime.now().strftime("%m%d%Y_%H-%M-%S")
            name_CSV= "./files/"+csv_model_global[0].store_number.__str__()+"_"+csv_model_global[0].account_id.__str__()+"_"+date+"_"+csv_model_global[0].SGLN+"_"+serial_no+".csv"
            name_CSV_EPCS= "./files/EPCS.csv"
            mode="w"
            modeEPCs="w"
            fileName=name_CSV

            #validate if exists folder 
            if os.path.exists("./files"):
                logger.info("path exists")
            else:
                os.makedirs("./files")

            
            if general_csv == False:
                self.logger.info(f"Creating csv file: {fileName}")
                with open(fileName, mode=mode) as file:
                    writer = csv.writer(file)
                    
                    for csv_model in csv_model_global:
                        writer.writerow([""+csv_model.store_number.__str__()+"", ""+csv_model.event_code.__str__()+"", ""+csv_model.epcs+"",
                                    ""+csv_model.alarm_type.__str__()+"",""+csv_model.inventory_alarm.__str__()+"",""+csv_model.event_date+"",
                                    ""+csv_model.event_time+"",""+csv_model.alarm_direction.__str__()+"",""+csv_model.SGLN+"",
                                    ""+csv_model.pedestal_id.__str__()+"",""+csv_model.account_id.__str__()+"",""+csv_model.door_id.__str__()+""])
            
            

            return name_CSV
        except Exception as ex:
            self.logger.error(f"Exception create csv file: {ex}")


    def delete_csv(self, older_days=7):
        path = "./files"

        if not os.path.exists(path):
            logger.info("path doesn't exists")
            return

        now = time.time()
        for f in os.listdir(path):
            print(f)
            if f =='EPCS.csv':
                continue
            if os.stat(os.path.join(path, f)).st_mtime < (now - (older_days * 86400)):
                if os.path.isfile(os.path.join(path, f)):
                    os.remove(os.path.join(path, f))
                    logger.info("removed old file "+str(f))

    def deleteGeneralCSV(self):
        path = "./files"
        if not os.path.exists(path):
                    logger.info("path doesn't exists")
                    return
        
        for f in os.listdir(path):
                    if f =='EPCS.csv':
                       os.remove(os.path.join(path, f))
                    
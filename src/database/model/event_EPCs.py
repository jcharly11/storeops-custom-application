class EventEPCs():

    def __init__(self,
                 id_event,
                 store_number, 
                 event_code,
                 alarm_type,
                 inventory_alarm, 
                 event_date,
                 event_time,
                 alarm_direction,
                 SGLN,
                 pedestal_id,
                 account_id,
                 door_id,
                 date,
                 datetime_inserted,
                 csv_general_created=False,
                 csv_created = False):
        self.id_event = id_event
        self.store_number = store_number
        self.event_code =  event_code
        self.alarm_type = alarm_type
        self.inventory_alarm = inventory_alarm
        self.event_date= event_date
        self.event_time= event_time
        self.alarm_direction = alarm_direction
        self.SGLN= SGLN
        self.pedestal_id= pedestal_id
        self.account_id= account_id
        self.door_id= door_id
        self.date= date
        self.datetime_inserted = datetime_inserted
        self.csv_general_created = csv_general_created
        self.csv_created = csv_created
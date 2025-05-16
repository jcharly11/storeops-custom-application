DB_PATH = './storage/storeops_basics_database.db'


TABLE_EVENTS = """
    CREATE TABLE IF NOT EXISTS events(
          idEvent TEXT UNIQUE,
          storeNumber TEXT, 
          eventCode INTEGER,
          alarmType INTEGER,
          inventoryAlarm INTEGER,
          eventDate TEXT,
          eventTime TEXT,
          alarmDirection INTEGER,
          sgln TEXT,
          pedestalId INTEGER,
          accountId TEXT,
          doorId INTEGER,
          date TIMESTAMP,
          datetime_inserted TEXT,
          csv_general_created BOOLEAN,
          csv_created BOOLEAN          
    );
    """

TABLE_EPC_EVENT = """
    CREATE TABLE IF NOT EXISTS events_epcs(
          idEvent TEXT ,
          epc TEXT  
          
    );
    """

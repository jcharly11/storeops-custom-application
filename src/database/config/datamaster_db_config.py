DB_PATH = './storage/datamaster_database.db'



TABLE_DATAMASTER = """
    CREATE TABLE IF NOT EXISTS datamaster(
          sku TEXT,
          epc TEXT,
          description TEXT,
          image TEXT,
          timestamp TIMESTAMP
    );
    """

TABLE_INVENTORY = """
    CREATE TABLE IF NOT EXISTS inventory(
          epc TEXT,
          timestamp TIMESTAMP,
          alarm_type TEXT,
          description TEXT,
          image TEXT
    );
    """

TABLE_UNKNOWN_EPC = """
    CREATE TABLE IF NOT EXISTS unknown_epc(
          epc TEXT,
          date TEXT,
          event TEXT
    );
    """
DB_PATH = 'storeops-database.db'
      
TABLE_MESSAGES = """

    CREATE TABLE IF NOT EXISTS messages(
        message TEXT,
        status BOOLEAN,
        date_time_inserted TEXT
    );
    """
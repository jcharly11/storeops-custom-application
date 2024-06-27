DB_PATH = 'storeops-database.db'
      
TABLE_MESSAGES = """

    CREATE TABLE IF NOT EXISTS messages(
        request_uuid TEXT,
        message TEXT,
        status BOOLEAN,
        type INT,
        date_time_inserted TEXT
    );
    """
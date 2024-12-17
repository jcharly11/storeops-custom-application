DB_PATH = './storage/storeops-database.db'

TABLE_MESSAGES = """

    CREATE TABLE IF NOT EXISTS messages(
        request_uuid TEXT,
        message TEXT,
        status TEXT,
        type TEXT,
        timestamp TEXT,
        date_time_inserted TEXT
    );
    """
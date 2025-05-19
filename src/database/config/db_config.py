DB_PATH = './storage/storeops-database.db'

TABLE_MESSAGES = """

    CREATE TABLE IF NOT EXISTS messages_storeops(
        request_uuid TEXT,
        message BLOB,
        status TEXT,
        type TEXT,
        timestamp DATE,
        date_time_inserted DATE
    );
    """
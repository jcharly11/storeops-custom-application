DB_AZURE_PATH = './storage/storeops-database-azure.db'

TABLE_FILES = """

    CREATE TABLE IF NOT EXISTS files(
        request_uuid TEXT,
        files TEXT,
        link TEXT,
        date_time_inserted DATE,
        path TEXT
    );
    """
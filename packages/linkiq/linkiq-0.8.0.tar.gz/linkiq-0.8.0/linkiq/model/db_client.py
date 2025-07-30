import os
import sqlite3
import threading
import pathlib


class DBClient:
    _instance = None
    _lock = threading.Lock()

    PROFILES_TABLE = "PROFILES"
    LEADS_TABLE = "LEADS"
    SCHEDULE_TABLE = "SCHEDULES"
    QUEUES_TABLE = "QUEUES"
    POSTS_TABLE = "POSTS"

    def __new__(cls, db_path=None):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(DBClient, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path=None):
        if self._initialized:
            return
        
        # Use a separate lock for initialization to be extra safe
        with self._lock:
            if self._initialized:
                return

            # Get DB path, defaulting to ~/.linkiq/linkiq.db
            db_path = db_path or os.environ.get("DB_PATH", "~/.linkiq/linkiq.db")
            db_path = os.path.expanduser(db_path)
            self.db_path = db_path

            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

            # Optionally create the file (or connect to it with sqlite3)
            if not os.path.exists(db_path):
                pathlib.Path(db_path).touch()
        
            self._initialize_db()
            self._initialized = True

    def _get_connection(self):
        """Get a new database connection with proper configuration"""
        conn = sqlite3.connect(self.db_path)
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize_db(self):
        """Initialize database tables and indexes"""
        with self._get_connection() as conn:
            self._create_profiles_table(conn)
            self._create_leads_table(conn)
            self._create_schedule_table(conn)
            self._create_queues_table(conn)
            self._create_posts_table(conn)
            conn.commit()

    def _create_profiles_table(self, conn):
        """Create the profiles table"""
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.PROFILES_TABLE} (
                    URL TEXT PRIMARY KEY,
                    NAME TEXT,
                    CONNECTION_DEGREE TEXT,
                    COMPANY TEXT,
                    TITLE TEXT,
                    LOCATION TEXT,
                    ABOUT TEXT,
                    EXPERIENCE TEXT,
                    INTEREST_SIGNAL INTEGER NOT NULL DEFAULT 1,
                    CREATED_AT DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UPDATED_AT DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            conn.commit()
        except Exception as e:
            print(f"Error creating {self.PROFILES_TABLE} table: {e}")
            conn.rollback()
        finally:
            cursor.close()

    def _create_leads_table(self, conn):
        """Create the leads table with indexes"""
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.LEADS_TABLE} (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    CAMPAIGN_NAME TEXT NOT NULL,
                    PROFILE TEXT NOT NULL,
                    STAGE TEXT NOT NULL,
                    CREATED_AT DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UPDATED_AT DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(CAMPAIGN_NAME, PROFILE)
                );
            ''')

            # Create indexes for better query performance
            cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_lead_profile_stage
                ON {self.LEADS_TABLE}(PROFILE, STAGE);
            ''')

            cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_lead_campaign_name_stage
                ON {self.LEADS_TABLE}(CAMPAIGN_NAME, STAGE);
            ''')
        finally:
            cursor.close()
    
    def _create_schedule_table(self, conn):
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.SCHEDULE_TABLE} (
                    TASK TEXT PRIMARY KEY,
                    LAST_RUN DATETIME,
                    NEXT_RUN DATETIME
                );
            ''')
        finally:
            cursor.close()

    def _create_queues_table(self, conn):
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.QUEUES_TABLE} (
                    PROFILE TEXT PRIMARY KEY,
                    CREATED_AT DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            ''')
        finally:
            cursor.close()
    
    def _create_posts_table(self, conn):
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.POSTS_TABLE} (
                    URL TEXT PRIMARY KEY,
                    LAST_SCANNED_AT DATETIME,
                    SCANNED_COUNT INTEGER DEFAULT 0,
                    AGE INTEGER
                );
            ''')
        finally:
            cursor.close()

    def get_connection(self):
        """Get a database connection for external use"""
        return self._get_connection()
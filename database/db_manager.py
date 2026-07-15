import sqlite3
import os
import json
from datetime import datetime
import threading


class DatabaseManager:
    """SQLite database manager for Nexus Antivirus"""
    
    def __init__(self, db_path=None):
        """Initialize database connection"""
        if db_path is None:
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            db_dir = os.path.join(app_data, 'NexusAntivirus', 'database')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'nexus_antivirus.db')
        
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.lock = threading.Lock()
        
        # Initialize database
        self._connect()
        self._create_tables()
        self._create_indexes()
    
    def _connect(self):
        """Connect to database"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            print(f"✅ Database connected: {self.db_path}")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def _create_tables(self):
        """Create all necessary tables"""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_type TEXT NOT NULL,
                files_scanned INTEGER DEFAULT 0,
                threats_found INTEGER DEFAULT 0,
                scan_duration REAL DEFAULT 0,
                status TEXT DEFAULT 'completed',
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                details TEXT
            )
            """,
            
            """
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                threat_name TEXT NOT NULL,
                severity TEXT DEFAULT 'Medium',
                threat_type TEXT DEFAULT 'Unknown',
                status TEXT DEFAULT 'detected',
                scan_id INTEGER,
                detected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                quarantined_time TIMESTAMP,
                restored_time TIMESTAMP,
                deleted_time TIMESTAMP,
                hash TEXT,
                file_size INTEGER,
                FOREIGN KEY (scan_id) REFERENCES scan_history(id)
            )
            """,
            
            """
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            """
            CREATE TABLE IF NOT EXISTS quarantine (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_path TEXT NOT NULL,
                quarantine_path TEXT NOT NULL,
                threat_name TEXT NOT NULL,
                threat_id INTEGER,
                quarantined_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                restored BOOLEAN DEFAULT 0,
                restored_time TIMESTAMP,
                deleted BOOLEAN DEFAULT 0,
                deleted_time TIMESTAMP,
                FOREIGN KEY (threat_id) REFERENCES threats(id)
            )
            """,
            
            """
            CREATE TABLE IF NOT EXISTS ai_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            """
            CREATE TABLE IF NOT EXISTS performance_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value TEXT NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            """
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_type TEXT NOT NULL,
                activity_detail TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for table_sql in tables:
            try:
                self.cursor.execute(table_sql)
            except Exception as e:
                print(f"❌ Failed to create table: {e}")
        
        self.connection.commit()
        print("✅ Database tables created successfully")
    
    def _create_indexes(self):
        """Create indexes for faster queries"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_threats_status ON threats(status)",
            "CREATE INDEX IF NOT EXISTS idx_scan_history_date ON scan_history(start_time)",
            "CREATE INDEX IF NOT EXISTS idx_quarantine_status ON quarantine(restored, deleted)",
            "CREATE INDEX IF NOT EXISTS idx_ai_conversations_session ON ai_conversations(session_id)",
        ]
        
        for index_sql in indexes:
            try:
                self.cursor.execute(index_sql)
            except:
                pass
        
        self.connection.commit()
    
    def execute_query(self, query, params=None):
        """Execute a query with thread safety"""
        with self.lock:
            try:
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                self.connection.commit()
                return self.cursor
            except Exception as e:
                print(f"❌ Query failed: {e}")
                return None
    
    def execute_many(self, query, params_list):
        """Execute many queries with thread safety"""
        with self.lock:
            try:
                self.cursor.executemany(query, params_list)
                self.connection.commit()
                return True
            except Exception as e:
                print(f"❌ Batch query failed: {e}")
                return False
    
    def fetch_all(self, query, params=None):
        """Fetch all results from a query"""
        result = self.execute_query(query, params)
        if result:
            return result.fetchall()
        return []
    
    def fetch_one(self, query, params=None):
        """Fetch one result from a query"""
        result = self.execute_query(query, params)
        if result:
            return result.fetchone()
        return None
    
    def insert_scan_history(self, scan_type, files_scanned, threats_found, scan_duration, status='completed', details=None):
        """Insert a scan history record"""
        query = """
            INSERT INTO scan_history 
            (scan_type, files_scanned, threats_found, scan_duration, status, details, end_time)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        result = self.execute_query(query, (scan_type, files_scanned, threats_found, scan_duration, status, details))
        return self.cursor.lastrowid if result else None
    
    def insert_threat(self, file_path, threat_name, severity='Medium', threat_type='Unknown', scan_id=None, hash_value=None, file_size=None):
        """Insert a threat record"""
        query = """
            INSERT INTO threats 
            (file_path, threat_name, severity, threat_type, scan_id, hash, file_size)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        result = self.execute_query(query, (file_path, threat_name, severity, threat_type, scan_id, hash_value, file_size))
        return self.cursor.lastrowid if result else None
    
    def insert_quarantine(self, original_path, quarantine_path, threat_name, threat_id=None):
        """Insert a quarantine record"""
        query = """
            INSERT INTO quarantine 
            (original_path, quarantine_path, threat_name, threat_id)
            VALUES (?, ?, ?, ?)
        """
        result = self.execute_query(query, (original_path, quarantine_path, threat_name, threat_id))
        return self.cursor.lastrowid if result else None
    
    def insert_ai_conversation(self, session_id, user_message, ai_response, context=None):
        """Insert an AI conversation record"""
        query = """
            INSERT INTO ai_conversations 
            (session_id, user_message, ai_response, context)
            VALUES (?, ?, ?, ?)
        """
        result = self.execute_query(query, (session_id, user_message, ai_response, context))
        return self.cursor.lastrowid if result else None
    
    def insert_activity(self, activity_type, activity_detail=None, ip_address=None):
        """Insert a user activity record"""
        query = """
            INSERT INTO user_activity 
            (activity_type, activity_detail, ip_address)
            VALUES (?, ?, ?)
        """
        self.execute_query(query, (activity_type, activity_detail, ip_address))
    
    def save_setting(self, key, value):
        """Save a user setting"""
        query = """
            INSERT OR REPLACE INTO user_settings (setting_key, setting_value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """
        self.execute_query(query, (key, json.dumps(value)))
    
    def get_setting(self, key, default=None):
        """Get a user setting"""
        query = "SELECT setting_value FROM user_settings WHERE setting_key = ?"
        result = self.fetch_one(query, (key,))
        if result:
            try:
                return json.loads(result['setting_value'])
            except:
                return result['setting_value']
        return default
    
    def get_scan_history(self, limit=50):
        """Get recent scan history"""
        query = """
            SELECT * FROM scan_history 
            ORDER BY start_time DESC 
            LIMIT ?
        """
        return self.fetch_all(query, (limit,))
    
    def get_threats(self, status=None, limit=100):
        """Get threats with optional status filter"""
        if status:
            query = "SELECT * FROM threats WHERE status = ? ORDER BY detected_time DESC LIMIT ?"
            return self.fetch_all(query, (status, limit))
        else:
            query = "SELECT * FROM threats ORDER BY detected_time DESC LIMIT ?"
            return self.fetch_all(query, (limit,))
    
    def get_quarantine_items(self, restored=False, deleted=False):
        """Get quarantine items"""
        query = """
            SELECT * FROM quarantine 
            WHERE restored = ? AND deleted = ?
            ORDER BY quarantined_time DESC
        """
        return self.fetch_all(query, (restored, deleted))
    
    def get_stats(self):
        """Get database statistics"""
        stats = {}
        
        result = self.fetch_one("SELECT COUNT(*) as count FROM scan_history")
        stats['total_scans'] = result['count'] if result else 0
        
        result = self.fetch_one("SELECT COUNT(*) as count FROM threats")
        stats['total_threats'] = result['count'] if result else 0
        
        result = self.fetch_one("SELECT COUNT(*) as count FROM quarantine WHERE restored = 0 AND deleted = 0")
        stats['quarantined'] = result['count'] if result else 0
        
        result = self.fetch_one("SELECT severity, COUNT(*) as count FROM threats GROUP BY severity ORDER BY count DESC LIMIT 1")
        if result:
            stats['most_common_severity'] = result['severity']
        
        return stats
    
    def get_daily_stats(self, days=7):
        """Get daily statistics for the last N days"""
        query = """
            SELECT 
                DATE(start_time) as date,
                COUNT(*) as scans,
                SUM(files_scanned) as files,
                SUM(threats_found) as threats,
                AVG(scan_duration) as avg_duration
            FROM scan_history
            WHERE start_time >= DATE('now', ?)
            GROUP BY DATE(start_time)
            ORDER BY date DESC
        """
        return self.fetch_all(query, (f'-{days} days',))
    
    def update_threat_status(self, threat_id, status):
        """Update threat status"""
        query = "UPDATE threats SET status = ? WHERE id = ?"
        self.execute_query(query, (status, threat_id))
    
    def update_quarantine_status(self, quarantine_id, restored=False, deleted=False):
        """Update quarantine status"""
        if restored:
            query = "UPDATE quarantine SET restored = 1, restored_time = CURRENT_TIMESTAMP WHERE id = ?"
        elif deleted:
            query = "UPDATE quarantine SET deleted = 1, deleted_time = CURRENT_TIMESTAMP WHERE id = ?"
        else:
            query = "UPDATE quarantine SET restored = 0, deleted = 0 WHERE id = ?"
        self.execute_query(query, (quarantine_id,))
    
    def clear_old_data(self, days=30):
        """Clear data older than specified days"""
        queries = [
            ("DELETE FROM scan_history WHERE start_time < DATE('now', ?)", f'-{days} days'),
            ("DELETE FROM threats WHERE detected_time < DATE('now', ?)", f'-{days} days'),
            ("DELETE FROM user_activity WHERE timestamp < DATE('now', ?)", f'-{days} days'),
        ]
        
        for query, param in queries:
            self.execute_query(query, (param,))
    
    def backup(self, backup_path=None):
        """Backup database to file"""
        if backup_path is None:
            backup_dir = os.path.join(os.path.dirname(self.db_path), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'backup_{timestamp}.db')
        
        with self.lock:
            try:
                backup_conn = sqlite3.connect(backup_path)
                backup_conn.backup(self.connection)
                backup_conn.close()
                print(f"✅ Database backed up to: {backup_path}")
                return backup_path
            except Exception as e:
                print(f"❌ Backup failed: {e}")
                return None
    
    def vacuum(self):
        """Optimize database"""
        with self.lock:
            try:
                self.cursor.execute("VACUUM")
                self.connection.commit()
                print("✅ Database optimized")
            except Exception as e:
                print(f"❌ Vacuum failed: {e}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")
    
    def __del__(self):
        """Destructor to close connection"""
        self.close()
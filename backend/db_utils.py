# backend/db_utils.py
import sqlite3

def init_db():
        conn = sqlite3.connect("session.db")
        cursor = conn.cursor()
        
        # Tenants (companies/teams)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')

        # Users with roles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'editor', 'viewer')),
                tenant_id INTEGER,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        ''')

        # Logs (now tenant-aware)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT,
                source TEXT,
                status TEXT,
                timestamp TEXT,
                error TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

def log_session(request_id, source, status, timestamp, error=None, user_id=None):
    conn = sqlite3.connect("session.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessions (request_id, source, status, timestamp, error, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (request_id, source, status, timestamp, error, user_id))
    conn.commit()
    conn.close()

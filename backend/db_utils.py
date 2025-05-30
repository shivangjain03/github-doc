# backend/db_utils.py
import sqlite3

def init_db():
    conn = sqlite3.connect("session.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT,
            source TEXT,
            status TEXT,
            timestamp TEXT,
            error TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_session(request_id, source, status, timestamp, error=None):
    conn = sqlite3.connect("session.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (request_id, source, status, timestamp, error)
        VALUES (?, ?, ?, ?, ?)
    ''', (request_id, source, status, timestamp, error))
    conn.commit()
    conn.close()

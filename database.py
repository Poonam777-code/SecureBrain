"""
Database module
Handles SQLite initialization and logging
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("data", "browser.db")

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        risk_score INTEGER,
        status TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

def log_activity(url, risk_score, status):
    """Insert activity log"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO activity_log (url, risk_score, status, timestamp)
    VALUES (?, ?, ?, ?)
    """, (url, risk_score, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

def get_logs():
    """Fetch logs for dashboard"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM activity_log ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
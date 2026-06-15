import sqlite3


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT,
        job_role TEXT,
        ats_score INTEGER,
        matched_keywords TEXT,
        missing_keywords TEXT,
        ai_feedback TEXT,
        created_at TIMESTAMP DEFAULT (datetime('now', '+5 hours', '+30 minutes'))
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question TEXT,
        answer TEXT,
        feedback TEXT,
        created_at TIMESTAMP DEFAULT (datetime('now', '+5 hours', '+30 minutes'))
    )
    """)

    conn.commit()
    conn.close()
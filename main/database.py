import sqlite3

def create_connection():
    conn = sqlite3.connect("analysis_results.db")
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            result TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_analysis(filename, result):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO analyses (filename, result) VALUES (?, ?)", (filename, result))
    conn.commit()
    conn.close()

def load_analyses():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, result, timestamp FROM analyses")
    rows = cursor.fetchall()
    conn.close()
    return rows

def load_analysis_by_id(analysis_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT result FROM analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

create_table()

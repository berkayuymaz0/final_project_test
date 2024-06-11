import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_connection():
    try:
        conn = sqlite3.connect("ole_analysis_results.db")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error creating database connection: {e}")
        return None

def create_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    result TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    context TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
        finally:
            conn.close()

def save_analysis(filename, result):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO analyses (filename, result) VALUES (?, ?)", (filename, result))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error saving analysis: {e}")
        finally:
            conn.close()

def load_analyses():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, result, timestamp FROM analyses")
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            logger.error(f"Error loading analyses: {e}")
            return []
        finally:
            conn.close()

def load_analysis_by_id(analysis_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT result FROM analyses WHERE id = ?", (analysis_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            logger.error(f"Error loading analysis by id: {e}")
            return None
        finally:
            conn.close()

def save_context(context):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM context")
            cursor.execute("INSERT INTO context (context) VALUES (?)", (context,))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error saving context: {e}")
        finally:
            conn.close()

def load_context():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT context FROM context ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
            return row[0] if row else ""
        except sqlite3.Error as e:
            logger.error(f"Error loading context: {e}")
            return ""
        finally:
            conn.close()

def clear_context():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM context")
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error clearing context: {e}")
        finally:
            conn.close()

create_table()

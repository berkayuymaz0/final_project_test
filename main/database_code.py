import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE = "code_analysis_results.db"

def create_connection():
    """Create a database connection and return the connection object."""
    try:
        conn = sqlite3.connect(DATABASE)
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error creating database connection: {e}")
        return None

def execute_query(query, params=()):
    """Execute a given query with optional parameters."""
    conn = create_connection()
    if conn:
        try:
            with conn:
                conn.execute(query, params)
        except sqlite3.Error as e:
            logger.error(f"Error executing query '{query}': {e}")
        finally:
            conn.close()

def fetch_query(query, params=()):
    """Fetch results from a given query with optional parameters."""
    conn = create_connection()
    if conn:
        try:
            with conn:
                cursor = conn.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error fetching query '{query}': {e}")
            return []
        finally:
            conn.close()

def create_table():
    """Create necessary tables if they do not exist."""
    create_analysis_table_query = """
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        result TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    create_context_table_query = """
    CREATE TABLE IF NOT EXISTS context (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        context TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    execute_query(create_analysis_table_query)
    execute_query(create_context_table_query)

def save_analysis(filename, result):
    """Save an analysis result to the database."""
    insert_query = "INSERT INTO analyses (filename, result) VALUES (?, ?)"
    execute_query(insert_query, (filename, result))

def load_analyses():
    """Load all analyses from the database."""
    select_query = "SELECT id, filename, result, timestamp FROM analyses"
    return fetch_query(select_query)

def load_analysis_by_id(analysis_id):
    """Load a specific analysis by its ID."""
    select_query = "SELECT result FROM analyses WHERE id = ?"
    result = fetch_query(select_query, (analysis_id,))
    return result[0][0] if result else None

def save_context(context):
    """Save the context to the database, clearing any existing context first."""
    delete_query = "DELETE FROM context"
    insert_query = "INSERT INTO context (context) VALUES (?)"
    execute_query(delete_query)
    execute_query(insert_query, (context,))

def load_context():
    """Load the most recent context from the database."""
    select_query = "SELECT context FROM context ORDER BY timestamp DESC LIMIT 1"
    result = fetch_query(select_query)
    return result[0][0] if result else ""

def clear_context():
    """Clear all context entries from the database."""
    delete_query = "DELETE FROM context"
    execute_query(delete_query)

# Initialize the database tables
create_table()

import duckdb
import os

DB_PATH = "data/home_credit.db"

def get_connection():
    """Returns a DuckDB connection to our project database."""
    return duckdb.connect(DB_PATH)

def get_db_size():
    """Utility to check database file size."""
    if os.path.exists(DB_PATH):
        size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
        return f"{size_mb:.1f} MB"
    return "Database not found"
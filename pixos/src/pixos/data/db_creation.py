import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "instances.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # defaults
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")

    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS instances (
                instance_id TEXT PRIMARY KEY,
                namespace   TEXT NOT NULL,
                start_time  TEXT NOT NULL,
                stop_time   TEXT
            )
        """)

if __name__ == '__main__':
    initialize_database()
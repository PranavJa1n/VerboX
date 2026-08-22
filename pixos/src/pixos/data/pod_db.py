import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "pods.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # defaults for performance and concurrency
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")

    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pods (
                pod_name TEXT PRIMARY KEY,
                eks_id TEXT,
                ec2_id TEXT,
                status TEXT,
                restart_count INTEGER DEFAULT 0,
                image_version TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                exit_code INTEGER
            )
        """)

if __name__ == '__main__':
    initialize_database()
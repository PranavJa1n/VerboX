from pathlib import Path
import sqlite3

def get_connection(db_name: str = "pixos_system.db"):
    db_path = Path(__file__).parent.parent / "data" / db_name
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # SQLite configuration
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")

    return conn

if __file__ == "__main__":
    conn = get_connection()
    # print(conn.total_changes)
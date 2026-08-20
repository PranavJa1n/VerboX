from pathlib import Path
import sqlite3

def get_connection(db_name: str = "finance.db"):
    DB_PATH = Path(__file__).parent / db_name
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Standard production pragmas for concurrency
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")

    return conn

def initialize_database():
    with get_connection() as conn:
        # Table 1: Budgets
        conn.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                department_name TEXT PRIMARY KEY,
                monthly_limit REAL NOT NULL,
                current_spend REAL NOT NULL
            )
        """)
        # Table 2: Resource Costs
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resource_costs (
                instance_type TEXT PRIMARY KEY,
                hourly_rate REAL NOT NULL
            )
        """)
        
        # Seed Baseline Data
        conn.execute("""
            INSERT OR REPLACE INTO budgets (department_name, monthly_limit, current_spend)
            VALUES ('engineering', 5000.0, 4800.0) 
            -- Note: We start close to the limit to make it easy to trigger a breach
        """)
        conn.execute("""
            INSERT OR REPLACE INTO resource_costs (instance_type, hourly_rate)
            VALUES ('t3.medium', 0.0416), ('m5.large', 0.096)
        """)
        print("finance.db initialized and seeded.")

if __name__ == '__main__':
    initialize_database()
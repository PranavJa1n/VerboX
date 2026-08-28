from pathlib import Path
import sqlite3


def get_connection(db_name: str = "pixos_system.db"):
    db_path = Path(__file__).parent / db_name
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # SQLite configuration
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")

    return conn


def initialize_database():
    with get_connection() as conn:

        # asg
        conn.execute("""
            CREATE TABLE IF NOT EXISTS autoscaling_groups (
                asg_name TEXT PRIMARY KEY,
                desired_capacity REAL NOT NULL
            )
        """)

        # ec2
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ec2_instances (
                instance_id TEXT PRIMARY KEY,
                asg_name TEXT,
                FOREIGN KEY (asg_name)
                    REFERENCES autoscaling_groups(asg_name)
                    ON DELETE CASCADE
            )
        """)

        # finops Table 1: Budgets
        conn.execute("""
                    CREATE TABLE IF NOT EXISTS budgets (
                        department_name TEXT PRIMARY KEY,
                        monthly_limit REAL NOT NULL,
                        current_spend REAL NOT NULL
                    )
                """)
        # finops Table 2: Resource Costs
        conn.execute("""
                    CREATE TABLE IF NOT EXISTS resource_costs (
                        instance_type TEXT PRIMARY KEY,
                        hourly_rate REAL NOT NULL
                    )
                """)


if __name__ == "__main__":
    initialize_database()
    print("pixos database initialized successfully.")
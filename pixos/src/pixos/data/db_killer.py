import os
from pathlib import Path

def db_killer(db_path: str) -> None:

    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted database: {db_path}")

if __name__ == "__main__":
    db_killer(r"E:\VerboX\VerboX\pixos\src\pixos\data\pixos_system.db")
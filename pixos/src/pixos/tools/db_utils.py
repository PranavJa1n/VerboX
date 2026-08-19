from pixos.data.db_creation import get_connection
from datetime import datetime, timezone, timedelta

def timestamp_to_string(dt: datetime) -> str:
    return dt.isoformat()

def create_instance(instance_id, namespace, start_time):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO instances
                (instance_id, namespace, start_time)
            VALUES (?, ?, ?)
        """, (
            instance_id,
            namespace,
            timestamp_to_string(start_time)
        ))

def get_instance(instance_id):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT instance_id, namespace, start_time, stop_time
            FROM instances
            WHERE instance_id = ?
        """, (instance_id,)).fetchone()

        return dict(row) if row else None

def stop_instance(instance_id, stop_time):
    with get_connection() as conn:
        conn.execute("""
            UPDATE instances
            SET stop_time = ?
            WHERE instance_id = ?
        """, (timestamp_to_string(stop_time), instance_id))

def delete_instance(instance_id):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM instances
            WHERE instance_id = ?
        """, (instance_id,))

def instance_exists(instance_id):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT 1
            FROM instances
            WHERE instance_id = ?
            LIMIT 1
        """, (instance_id,)).fetchone()

        return row is not None

if __name__ == '__main__':
    from datetime import datetime, timezone
    if instance_exists("11111"):
        print("Exists")
    else:
        print("Not Exists")

    delete_instance("11111")

    IST = timezone(timedelta(hours=5, minutes=30))
    
    # Get current time in IST
    timestamp = datetime.now(IST)

    if instance_exists("11111"):
            print("Exists")
    else:
            print("Not Exists")

    create_instance("22222", "prod", timestamp)

    stop_instance("11111", timestamp)

    print(get_instance("11111"))
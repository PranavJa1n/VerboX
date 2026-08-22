import json
from datetime import datetime, timezone, timedelta
from pixos.data.pod_db import get_connection, initialize_database, initialize_database

def timestamp_to_string(dt: datetime) -> str:
    return dt.isoformat() if dt else None

def create_pod(pod_name, start_time, eks_id=None, ec2_id=None, status="Running", restart_count=0, image_version=None, labels=None):
    
    labels_str = json.dumps(labels) if labels else None
    
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO pods
                (pod_name, eks_id, ec2_id, status, restart_count, image_version, start_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            pod_name, eks_id, ec2_id, status, restart_count, 
            image_version, timestamp_to_string(start_time)
        ))

def get_pod(pod_name):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT *
            FROM pods
            WHERE pod_name = ?
        """, (pod_name,)).fetchone()

        if row:
            pod_dict = dict(row)
            if pod_dict.get('labels'):
                pod_dict['labels'] = json.loads(pod_dict['labels'])
            return pod_dict
            
        return None

def stop_pod(pod_name, end_time, exit_code=0, status="Stopped"):
    with get_connection() as conn:
        conn.execute("""
            UPDATE pods
            SET end_time = ?, exit_code = ?, status = ?
            WHERE pod_name = ?
        """, (timestamp_to_string(end_time), exit_code, status, pod_name))

def delete_pod(pod_name):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM pods
            WHERE pod_name = ?
        """, (pod_name,))

def pod_exists(pod_name):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT 1
            FROM pods
            WHERE pod_name = ?
            LIMIT 1
        """, (pod_name,)).fetchone()

        return row is not None

if __name__ == '__main__':
    initialize_database()
    
    IST = timezone(timedelta(hours=5, minutes=30))
    timestamp = datetime.now(IST)

    test_pod_id = "user-auth-service-75b89498c-x9jkl"

    if pod_exists(test_pod_id):
        delete_pod(test_pod_id)

    print(f"Creating test pod '{test_pod_id}'...")
    create_pod(
        pod_name=test_pod_id,
        start_time=timestamp,
        eks_id="cluster-main-01",
        ec2_id="i-0abcd1234efgh5678",
        image_version="v1.4.2",
        labels={"app": "user-auth", "tier": "backend"}
    )

    if pod_exists(test_pod_id):
        print("Pod successfully created.")
    stop_time = timestamp + timedelta(minutes=15)
    stop_pod(test_pod_id, stop_time, exit_code=137, status="Failed")

    print("\n--- Fetched Pod Record ---")
    print(get_pod(test_pod_id))

    # delete_pod(test_pod_id)
    # print(f"\nExists after deletion? {pod_exists(test_pod_id)}")
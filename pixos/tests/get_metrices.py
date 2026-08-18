import boto3
from datetime import timedelta, datetime, timezone

INSTANCE_ID = "i-82b9cc14a6b0b5b2b"
LOCALSTACK_URL = "http://localhost:4566"
REGION = "us-east-1"


cloudwatch = boto3.client(
    "cloudwatch",
    endpoint_url=LOCALSTACK_URL,
    region_name=REGION,
    aws_access_key_id="test",
    aws_secret_access_key="test",
)


END_TIME = datetime.now(timezone.utc)
START_TIME = END_TIME - timedelta(minutes=15)


def seed_all_mock_data(instance_id, cpu_val=58.7, mem_val=74.2):
    """Seeds both CPU and Memory data into LocalStack CloudWatch sequentially."""
    now_time = datetime.now(timezone.utc)
    
   
    cloudwatch.put_metric_data(
        Namespace="AWS/EC2",
        MetricData=[
            {
                "MetricName": "CPUUtilization",
                "Dimensions": [{"Name": "InstanceId", "Value": instance_id}],
                "Timestamp": now_time, 
                "Value": cpu_val,
                "Unit": "Percent"
            }
        ]
    )
    
    
    cloudwatch.put_metric_data(
        Namespace="CWAgent",
        MetricData=[
            {
                "MetricName": "mem_used_percent",
                "Dimensions": [{"Name": "InstanceId", "Value": instance_id}],
                "Timestamp": now_time, 
                "Value": mem_val,
                "Unit": "Percent"
            }
        ]
    )
    print(f" Successfully injected mock data -> CPU: {cpu_val}%, Memory: {mem_val}%")


def fetch_single_metric(namespace, metric_name, instance_id):
    """Helper function to cleanly fetch a single metric from LocalStack."""
    response = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": namespace,
                        "MetricName": metric_name,
                        "Dimensions": [{"Name": "InstanceId", "Value": instance_id}],
                    },
                    "Period": 300,
                    "Stat": "Average",
                },
                "ReturnData": True,
            },
        ],
        StartTime=START_TIME,
        EndTime=END_TIME,
    )
    
    
    results = response.get("MetricDataResults", [])
    if results and results[0].get("Values"):
        return results[0]["Values"][0] 
    return None


if __name__ == "__main__":
    
    seed_all_mock_data(INSTANCE_ID, cpu_val=58.7, mem_val=74.2)
    
    cpu_util = fetch_single_metric("AWS/EC2", "CPUUtilization", INSTANCE_ID)
    mem_util = fetch_single_metric("CWAgent", "mem_used_percent", INSTANCE_ID)
    
    print("\n--- System Utilization Results ---")
    print(f"  CPU Utilization:    {f'{cpu_util:.2f}%' if cpu_util is not None else 'No Data'}")
    print(f" Memory Utilization: {f'{mem_util:.2f}%' if mem_util is not None else 'No Data'}")

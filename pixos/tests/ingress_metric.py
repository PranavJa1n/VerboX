from datetime import timedelta, datetime, timezone
from pixos.tools.instance_utils import run_instance, terminate_all_running_instances
import boto3

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

def seed_all_mock_data(instance_id, cpu_val=58.7, mem_val=74.2, net_in_val=102400.0):
    """Seeds CPU, Memory, and Network Ingress data into LocalStack CloudWatch sequentially."""
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
        Namespace="AWS/EC2",
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


    cloudwatch.put_metric_data(
        Namespace="AWS/EC2",
        MetricData=[
            {
                "MetricName": "NetworkIn",
                "Dimensions": [{"Name": "InstanceId", "Value": instance_id}],
                "Timestamp": now_time, 
                "Value": net_in_val,
                "Unit": "Bytes"
            }
        ]
    )
    print(f" Successfully injected mock data -> CPU: {cpu_val}%, Memory: {mem_val}%, NetworkIn: {net_in_val} Bytes")

def fetch_single_metric(namespace, metric_name, instance_id):
    END_TIME = datetime.now(timezone.utc) + timedelta(minutes=1) 
    START_TIME = END_TIME - timedelta(minutes=15)
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


if __name__ == '__main__':
    instance_id = run_instance()
    
    # FIX: Seed the metrics FIRST so fetch operations find valid data points
    seed_all_mock_data(instance_id)
    
    # Re-evaluate the dynamic time frame window right before requesting data
    # END_TIME = datetime.now(timezone.utc) + timedelta(minutes=1) 
    # START_TIME = END_TIME - timedelta(minutes=15)

    network_ingress = fetch_single_metric(
        namespace="AWS/EC2", 
        metric_name="NetworkIn", 
        instance_id=instance_id
    )

    cpu = fetch_single_metric(
        namespace="AWS/EC2", 
        metric_name="CPUUtilization", 
        instance_id=instance_id
    )

    memory = fetch_single_metric(
        namespace="AWS/EC2", 
        metric_name="mem_used_percent", 
        instance_id=instance_id
    )
    
    print(f"\n--- Metric Summary For {instance_id} ---")
    print(f"Average Network Ingress: {network_ingress} Bytes")
    print(f"CPU Utilization        : {cpu}%")
    print(f"Memory Usage           : {memory}%")
    
    terminate_all_running_instances()

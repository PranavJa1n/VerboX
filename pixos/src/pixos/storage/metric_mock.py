import boto3
from datetime import timedelta, datetime, timezone

LOCALSTACK_URL = "http://localhost:4566"
REGION = "us-east-1"


cloudwatch = boto3.client(
    "cloudwatch",
    endpoint_url=LOCALSTACK_URL,
    region_name=REGION,
    aws_access_key_id="test",
    aws_secret_access_key="test",
)
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
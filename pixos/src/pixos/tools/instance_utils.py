from pathlib import Path
import pandas as pd
import boto3
import sys
from datetime import timedelta, datetime, timezone


BASE_DIR = Path(__file__).resolve().parent


#check
def check_instance(instance_id : str):
    file = BASE_DIR.parent / 'localstack/instances/instances.csv'
    df = pd.read_csv(file)
    
    for row in df.itertuples(index=True):
        if(row.instance_id == instance_id):
            if(not(pd.isna(row.stop_time))):
                print("Instance Stopped at :", row.stop_time)
                return -1
            else:
                print("Fetched the instance : ", row.instance_id,", running from :", row.start_time)
                return row.instance_id
        else:
            print("Not exists")

#create
def run_instance():
    ec2 = boto3.client(
    'ec2',
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    endpoint_url='http://localhost:4566'
    )

    response = ec2.run_instances(
    ImageId='ami-df5de72f', 
    InstanceType='t2.micro', 
    MinCount=1, 
    MaxCount=1
    )

    instance_id = response["Instances"][0]["InstanceId"]
    print(f"Successfully started mock EC2 instance: {instance_id}")
    return instance_id



#delete
def get_ec2_client():
    """Initializes and returns the EC2 client for LocalStack."""
    return boto3.client(
        "ec2",
        endpoint_url="http://localhost:4566",
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )

def terminate_all_running_instances():
    """
    Finds all currently running EC2 instances in LocalStack,
    prints the total count, and terminates (deletes) all of them.
    """
    ec2 = get_ec2_client()
    
   
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
    )
    
  
    instance_ids = []
    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            instance_ids.append(instance["InstanceId"])
            
    
    total_running = len(instance_ids)
    print(f"Total running instances found: {total_running}")
    
    if total_running == 0:
        print("No running instances to terminate.")
        return []
        
    print(f"Terminating instances: {instance_ids}")
    termination_response = ec2.terminate_instances(InstanceIds=instance_ids)
    
    return termination_response.get("TerminatingInstances", [])


def terminate_specific_instance(instance_id):
    """
    Terminates (deletes) a single, specific instance by its ID.
    """
    ec2 = get_ec2_client()
    
    print(f"Terminating specific instance: {instance_id}")
    try:
        termination_response = ec2.terminate_instances(InstanceIds=[instance_id])
        return termination_response.get("TerminatingInstances", [])
    except Exception as e:
        print(f" Error terminating instance {instance_id}: {str(e)}")
        return None


#update
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


#read
def get_all_running_instance(instance_id : str):
    """
    Finds all currently running EC2 instances in LocalStack,
    prints the total count.
    """
    ec2 = get_ec2_client()
    
   
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
    )
    
  
    instance_ids = []
    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            instance_ids.append(instance["InstanceId"])
            
    
    total_running = len(instance_ids)
    print(f"Total running instances found: {total_running}")
    
    if total_running == 0:
        print("No running instances to terminate.")
        return []
    else:
        return instance_ids


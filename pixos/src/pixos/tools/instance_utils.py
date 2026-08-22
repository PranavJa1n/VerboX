from pathlib import Path
import pandas as pd
import boto3
import sys
from datetime import timedelta, datetime, timezone
from pixos.tools.instance_db_utils import create_instance, delete_instance, instance_exists, stop_instance, get_instance

BASE_DIR = Path(__file__).resolve().parent


#check
def check_instance(instance_id : str):
    instance = get_instance(instance_id)
    if(instance != None):
        return instance['stop_time'] == None
    else:
        print(f"Instance {instance_id} does not exists.")
        return False
    
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

    IST = timezone(timedelta(hours=5, minutes=30))
    timestamp = datetime.now(IST)
    create_instance(instance_id=instance_id, namespace="AWS/EC2", start_time=timestamp)

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

    for instance in instance_ids:
        IST = timezone(timedelta(hours=5, minutes=30))
        timestamp = datetime.now(IST)
        stop_instance(instance_id=instance, stop_time=timestamp)

    return termination_response.get("TerminatingInstances", [])


def terminate_specific_instance(instance_id):
    """
    Terminates (deletes) a single, specific instance by its ID.
    """
    ec2 = get_ec2_client()
    
    print(f"Terminating specific instance: {instance_id}")
    try:
        termination_response = ec2.terminate_instances(InstanceIds=[instance_id])
        IST = timezone(timedelta(hours=5, minutes=30))
        timestamp = datetime.now(IST)
        stop_instance(instance_id=instance_id, stop_time=timestamp)
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
        print("No running instances to Found")
        return []
    else:
        return instance_ids



if __name__ =='__main__':
    instance_id = run_instance()
    print(check_instance(instance_id=instance_id))
    seed_all_mock_data(instance_id=instance_id)
    cpu = fetch_single_metric(instance_id=instance_id, namespace=get_instance(instance_id)['namespace'], metric_name="CPUUtilization")
    print("CPU untilization :", cpu)
    terminate_specific_instance(instance_id=instance_id)
    get_all_running_instance(instance_id=instance_id)
import boto3
import sys
from botocore.exceptions import ClientError, ParamValidationError

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

if __name__ == "__main__":
    run_instance()

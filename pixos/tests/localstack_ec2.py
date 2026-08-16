import boto3
import sys


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



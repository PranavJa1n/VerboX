import boto3
from pixos.core.floci_client import get_client

def get_asg_instance_ids(asg_name, region="us-east-1"):

    client = get_client('autoscaling')
    

    response = client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[asg_name]
    )
 
    instance_ids = []
    
    
    if response.get('AutoScalingGroups'):
        asg_details = response['AutoScalingGroups'][0]
        
    
        for instance in asg_details.get('Instances', []):
            instance_ids.append(instance['InstanceId'])
            
    return instance_ids


ASG_NAME = "prod-asg-2"
ids = get_asg_instance_ids(ASG_NAME)
print("EC2 Instance IDs inside ASG:", ids)

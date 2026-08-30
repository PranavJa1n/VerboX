import boto3
from pixos.core.floci_client import get_client
from pixos.storage.system_repo import ASG, Instance

asg_client = get_client('autoscaling')
ec2_client = get_client('ec2')

def main():
    print("Setting Up the initial Environment!")

    template_name = 'dummy-template'
    asg_name = "prod-asg-2"
    desired_capacity = 2

    try:
        ec2_client.create_launch_template(
            LaunchTemplateName=template_name,
            LaunchTemplateData={
                'ImageId': 'ami-12345678',
                'InstanceType': 't2.micro'
            }
        )
        print(f"Registered template: {template_name}")
    except ec2_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'InvalidLaunchTemplateName.AlreadyExistsException':
            print(f"Launch template '{template_name}' already exists, skipping...")
        else:
            raise e

    try:
        print("1. Creating VPC...")
        vpc_response = ec2_client.create_vpc(CidrBlock="10.0.0.0/16")
        vpc_id = vpc_response["Vpc"]["VpcId"]
    
        print(f"2. Creating Subnet in VPC {vpc_id}...")
        subnet_response = ec2_client.create_subnet(
            VpcId=vpc_id, 
            CidrBlock="10.0.1.0/24", 
            AvailabilityZone="us-east-1a"
        )
        subnet_id = subnet_response["Subnet"]["SubnetId"]
        response = asg_client.create_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            MinSize=1,
            MaxSize=5,
            DesiredCapacity=desired_capacity,
            LaunchTemplate={
                'LaunchTemplateName': template_name,
                'Version': '$Latest'
            },
            VPCZoneIdentifier=subnet_id
        )
    except ec2_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'AlreadyExists':
                print(f"ASG '{asg_name}' already exists, skipping...")
                response = None
        else:
            raise e
    if(response != None):
        asg = ASG()
        asg.create(asg_name=asg_name, desired_capacity=2)
        # waking up ec2s
        reservation = ec2_client.run_instances(
            ImageId='ami-12345678', 
            MinCount = desired_capacity,
            MaxCount = desired_capacity,
            InstanceType='t2.micro',
        )
        instance_ids = [instance['InstanceId'] for instance in reservation['Instances']]
        print(f"Mocked Instance IDs: {instance_ids}") 
        asg_client.attach_instances(
            InstanceIds = instance_ids,
            AutoScalingGroupName = asg_name
        )
        print("Successfully attached 2 instances to prod-asg!")
        ins = Instance()
        for id in instance_ids:
            ins.create(instance_id=id, asg_name=asg_name)



    return response

if __name__ == '__main__':
    print(asg_client)
    response = main()
    if(not response):
        print("Nothing")
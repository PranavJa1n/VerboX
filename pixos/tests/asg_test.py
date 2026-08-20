import pytest
import boto3
from pixos.tools.pod_utils import scale_ec2_instances

LOCALSTACK_URL = "http://localhost:4566"
REGION = "us-east-1"

asg_client = boto3.client(
    "autoscaling",
    endpoint_url=LOCALSTACK_URL,
    region_name=REGION,
    aws_access_key_id="mock",
    aws_secret_access_key="mock",
)

ec2_client = boto3.client(
    "ec2",
    endpoint_url=LOCALSTACK_URL,
    region_name=REGION,
    aws_access_key_id="mock",
    aws_secret_access_key="mock",
)

asg_name = "verbox-asg"
template_name = "verbox-template"

ec2_client.create_launch_template(
    LaunchTemplateName=template_name,
    LaunchTemplateData={"ImageId": "ami-df5db4bc", "InstanceType": "t2.micro"}
)
    
asg_client.create_auto_scaling_group(
    AutoScalingGroupName=asg_name,
    LaunchTemplate={"LaunchTemplateName": template_name, "Version": "$Default"},
    MinSize=1,
    MaxSize=10,
    DesiredCapacity=2
)

def test_scale_ec2_success():
    asg_name = "verbox-asg"
    target = 5
    result = scale_ec2_instances(asg_name=asg_name, new_capacity=target)
    expected_message = f"Successfully updated {asg_name}. Scaling to {target} instances."

    assert result == expected_message

    response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
    current_asg = response["AutoScalingGroups"][0]

    assert current_asg["DesiredCapacity"] == target

def test_scale_ec2_fail():
    asg_name = "fake-asg"
    target = 5
    result = scale_ec2_instances(asg_name=asg_name, new_capacity=target)
    assert result.status == 404
    assert result.detail == f"Auto Scaling Group {asg_name} not found"
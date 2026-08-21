import boto3
from botocore.exceptions import ClientError
import time
from pixos.state.state import ErrorSchema

FLOCI_URL = "http://localhost:4566"

ec2_client = boto3.client(
    "ec2",
    region_name="us-east-1",
    endpoint_url=FLOCI_URL,
    aws_access_key_id="mock-key",
    aws_secret_access_key="mock-secret"
)

eks_client = boto3.client(
    "eks",
    region_name="us-east-1",
    endpoint_url=FLOCI_URL,
    aws_access_key_id="mock-key",
    aws_secret_access_key="mock-secret"
)

# Cluster Managment
def create_cluster(subnet_ids : list[str], cluster_name : str, k8s_version : str, role_arn : str,) -> str:
    try:
        response = eks_client.create_cluster(
            name=cluster_name,
            version=k8s_version,
            roleArn=role_arn,
            resourcesVpcConfig={
                "subnetIds": subnet_ids,
                },
            )
        return f"Created a new kubernetes cluster named {cluster_name} of version {k8s_version}"
    except:
        return ErrorSchema(
            type="www.google.com",
            status="500",
            detail=f"Kubernetes cluster named {cluster_name} failed to be created",
            recovery_hint="Enter a correct role arn",
        )

def delete_cluster() -> str:
    pass

def describe_cluster() -> str:
    pass

def list_clusters() -> str:
    pass

# Node group managment
def create_node_group() -> str: # add more worker node
    pass

def delete_node_group() -> str:
    pass

def describe_node_group() -> str:
    pass

def list_node_group() -> str:
    pass
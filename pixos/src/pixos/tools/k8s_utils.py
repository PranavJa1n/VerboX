import boto3
from botocore.exceptions import ClientError
import time
from pixos.state.state import ErrorSchema

import json

FLOCI_URL : str = "http://localhost:4566"
FLOCI_ENDPOINT = "http://localhost:4566"

MOCK_CREDENTIALS = {
    "aws_access_key_id": "mock_key",
    "aws_secret_access_key": "mock_secret",
    "region_name": "us-east-1"
}

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

def setup_local_networking() -> list:
    """ Creates a mock VPC and 2 Subnets """
    vpc = ec2_client.create_vpc(CidrBlock="10.0.0.0/16")
    vpc_id = vpc["Vpc"]["VpcId"]
    sub1 = ec2_client.create_subnet(VpcId=vpc_id, CidrBlock="10.0.1.0/24", AvailabilityZone="us-east-1a")
    subnet_1_id = sub1["Subnet"]["SubnetId"]
    sub2 = ec2_client.create_subnet(VpcId=vpc_id, CidrBlock="10.0.2.0/24", AvailabilityZone="us-east-1b")
    subnet_2_id = sub2["Subnet"]["SubnetId"]
    return [subnet_1_id, subnet_2_id]

# Cluster Managment
def create_cluster(subnet_ids : list[str], cluster_name : str, k8s_version : str, role_arn : str,) -> str:
    """ Creates an eks cluster """
    try:
        response = eks_client.create_cluster(
            name=cluster_name,
            version=k8s_version,
            roleArn=role_arn,
            resourcesVpcConfig={
                "subnetIds": subnet_ids,
                },
            )
        return f"Created a new kubernetes cluster named {cluster_name} of version {k8s_version}. Response - {response}"
    except:
        return ErrorSchema(
            type=r"www.google.com",
            status=409,
            detail=f"Kubernetes cluster named {cluster_name} already exist",
            recovery_hint="",
        )

def delete_cluster(cluster_name : str,) -> str:
    """ Deletes an eks cluster """
    try:
        nodegroup = eks_client.list_nodegroups(clusterName = cluster_name)['nodegroups']
        for i in nodegroup:
            eks_client.delete_cluster_nodegroup(clusterName = cluster_name, nodegroupName = i)
        response = eks_client.delete_cluster(name= cluster_name)
        return response
    except:
        return ErrorSchema(
            type=r"www.google.com",
            status=500,
            detail=f"Kubernetes cluster named {cluster_name} might not exist",
            recovery_hint="Enter the correct cluster name",
        )

def describe_cluster(cluster_name : str) -> str:
    """ Gives all the details about a cluster """
    try:
        response = eks_client.describe_cluster(name=cluster_name)
        cluster_details : dict = response["cluster"]
        return cluster_details
    except:
        return ErrorSchema(
                    type=r"www.google.com",
                    status=404,
                    detail=f"Kubernetes cluster named {cluster_name} not found",
                    recovery_hint="Enter the correct cluster name",
                )

def list_all_clusters() -> list:
    """ List all the cluster that exist """
    try:
        response : dict = eks_client.list_clusters()
        cluster_list : list = response['clusters']
        if cluster_list:
            return cluster_list
        else:
            return ErrorSchema(
                type=r"www.google.com",
                status=404,
                detail="No cluster found",
                recovery_hint="Create a cluster first",
            )
    except:
        return ErrorSchema(
            type=r"www.google.com",
            status=500,
            detail="Can't reach the server right now",
            recovery_hint="Try again in some time",
        )
def delete_subnet(subnet_id : str) -> str:
    pass

# Node group managment
def create_floci_node_role(role_name: str) -> str:
    """
    Creates an IAM role and attaches mandatory EKS worker node policies
    on the local Floci emulator. Returns the Role ARN.
    """
    iam_client = boto3.client('iam', endpoint_url=FLOCI_ENDPOINT, **MOCK_CREDENTIALS)
    
    trust_policy = {
        "Version": "2012-10-17",
        "Mod": "Allow", # Trust document construct
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "://amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }

    print(f"Checking IAM role '{role_name}' on Floci...")
    try:
        create_role_res = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Local worker node role for Floci EKS"
        )
        node_role_arn = create_role_res['Role']['Arn']
        print(f"Created new IAM Role: {node_role_arn}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("IAM role already exists. Fetching existing ARN...")
            get_role_res = iam_client.get_role(RoleName=role_name)
            node_role_arn = get_role_res['Role']['Arn']
        else:
            raise e

    # Mandatory baseline policies for EKS communication
    required_policies = [
        "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
        "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
        "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
    ]

    print("Attaching AWS managed infrastructure policies...")
    for policy_arn in required_policies:
        try:
            iam_client.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        except ClientError as e:
            print(f"Could not attach policy {policy_arn}: {e}")

    return node_role_arn


def create_node_group(cluster_id: str, node_group_name: str, node_role_arn: str, subnet_ids: list) -> dict:
    """
    Provisions a managed node group against a specific cluster ID 
    hosted inside the Floci AWS emulator environment.
    """
    eks_client = boto3.client('eks', endpoint_url=FLOCI_ENDPOINT, **MOCK_CREDENTIALS)

    print(f"Provisioning node group '{node_group_name}' for cluster '{cluster_id}'...")
    try:
        response = eks_client.create_nodegroup(
            clusterName=cluster_id,
            nodegroupName=node_group_name,
            scalingConfig={
                'minSize': 1,
                'maxSize': 3,
                'desiredSize': 2
            },
            diskSize=20,
            subnets=subnet_ids,
            instanceTypes=['t3.medium'],
            nodeRole=node_role_arn,
            amiType='AL2_x86_64',
            capacityType='ON_DEMAND'
        )
        print(f"Node group creation initiated! Current status: {response['nodegroup']['status']}")
        return response['nodegroup']
        
    except ClientError as e:
        print(f"Failed to execute create_nodegroup on Floci: {e}")
        return None


def list_node_groups(cluster_id: str) -> list:
    """
    Retrieves a list of all managed node group names associated with 
    a specific cluster running on the Floci emulator.
    """
    eks_client = boto3.client('eks', endpoint_url=FLOCI_ENDPOINT, **MOCK_CREDENTIALS)
    
    print(f"Listing node groups for cluster '{cluster_id}'...")
    try:
        response = eks_client.list_nodegroups(clusterName=cluster_id)
        node_groups = response.get('nodegroups', [])
        print(f"Found node groups: {node_groups}")
        return node_groups
    except ClientError as e:
        print(f"Failed to list node groups on Floci: {e}")
        return []


def describe_node_group(cluster_id: str, node_group_name: str) -> dict:
    """
    Gets detailed information (status, instance types, sizing, etc.) 
    for a specific node group on Floci.
    """
    eks_client = boto3.client('eks', endpoint_url=FLOCI_ENDPOINT, **MOCK_CREDENTIALS)
    
    print(f"Describing node group '{node_group_name}' in cluster '{cluster_id}'...")
    try:
        response = eks_client.describe_nodegroup(
            clusterName=cluster_id,
            nodegroupName=node_group_name
        )
        nodegroup_details = response.get('nodegroup', {})
        print(f"Node Group Status: {nodegroup_details.get('status')}")
        return nodegroup_details
    except ClientError as e:
        print(f"Failed to describe node group on Floci: {e}")
        return None


def delete_node_group(cluster_id: str, node_group_name: str) -> bool:
    """
    Initiates the deletion process of a managed node group on Floci.
    Returns True if successful, False otherwise.
    """
    eks_client = boto3.client('eks', endpoint_url=FLOCI_ENDPOINT, **MOCK_CREDENTIALS)
    
    print(f"Deleting node group '{node_group_name}' from cluster '{cluster_id}'...")
    try:
        eks_client.delete_nodegroup(
            clusterName=cluster_id,
            nodegroupName=node_group_name
        )
        print("Node group deletion successfully initiated!")
        return True
    except ClientError as e:
        print(f"Failed to delete node group on Floci: {e}")
        return False
    

if __name__ == '__main__':
    x = list_node_groups("testing")
    print(x)
    print(describe_node_group("testing", x[0]))
    print(delete_node_group("testing", x[0]))
    # subnet_ids = setup_local_networking() 
    # res = create_cluster(subnet_ids=subnet_ids, cluster_name="testing", k8s_version="1.31", role_arn="arn:aws:iam::000000000000:role/fake-eks-role")
    # create_cluster(subnet_ids=subnet_ids, cluster_name="testing2", k8s_version="1.31", role_arn="arn:aws:iam::000000000000:role/fake-eks-role")
    # print(f"{res}\n\n")
    # details = describe_cluster(cluster_name="testing")
    # print(f"{details}\n\n")
    # cluster_list = list_all_clusters()
    # print(f"{cluster_list}\n\n")

    # target_role_arn = create_floci_node_role(role_name="floci-worker-node-role")
    # ng = create_node_group(cluster_id="testing", node_group_name="test_node_group", node_role_arn=target_role_arn, subnet_ids=subnet_ids)
    # print(ng)

    # deleted = delete_cluster(cluster_name="testing")
    # delete_cluster(cluster_name="testing2")
    # print(f"{deleted}")
import boto3
from botocore.exceptions import ClientError
import time
from pixos.state.state import ErrorSchema

FLOCI_URL : str = "http://localhost:4566"

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

# Node group managment
def create_node_group() -> str: # add more worker node
    pass

def delete_node_group() -> str:
    pass

def describe_node_group() -> str:
    pass

def list_node_group() -> str:
    pass

if __name__ == '__main__':
    subnet_ids = setup_local_networking()
    res = create_cluster(subnet_ids=subnet_ids, cluster_name="testing", k8s_version="1.31", role_arn="arn:aws:iam::000000000000:role/fake-eks-role")
    create_cluster(subnet_ids=subnet_ids, cluster_name="testing2", k8s_version="1.31", role_arn="arn:aws:iam::000000000000:role/fake-eks-role")
    print(f"{res}\n\n")
    details = describe_cluster(cluster_name="testing")
    print(f"{details}\n\n")
    cluster_list = list_all_clusters()
    print(f"{cluster_list}\n\n")
    deleted = delete_cluster(cluster_name="testing")
    delete_cluster(cluster_name="testing2")
    print(f"{deleted}")
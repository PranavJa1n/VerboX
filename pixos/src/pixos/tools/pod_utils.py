import boto3
from pixos.data.db_creation import get_connection
from pixos.state.state import ErrorSchema

LOCALSTACK_URL = "http://localhost:4566"
REGION = "us-east-1"

asg_client = boto3.client(
    "autoscaling",
    endpoint_url=LOCALSTACK_URL,
    region_name=REGION,
    aws_access_key_id="mock",
    aws_secret_access_key="mock",
)

def scale_ec2_instances(asg_name: str, new_capacity: int) -> str:
    """Mutate the desired capacity of an Auto Scaling Group"""
    try:
        print(f"Scaling ASG - {asg_name} to {new_capacity}")

        asg_client.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            DesiredCapacity=new_capacity,
            MinSize=1,
            MaxSize=new_capacity + 2
        )

        return f"Successfully updated {asg_name}. Scaling to {new_capacity} instances."
            
    except :
        return ErrorSchema(
            type="https://google.com",
            status=404,
            detail=f"Auto Scaling Group {asg_name} not found",
            recovery_hint=f"Check the spelling of the Auto Scaling Group"
            )


MOCK_DEPLOYMENT_HISTORY = {
    "deployments": {
        "Verbox_Deployment": {
            "current_revision": 3,
            "history": {
                1: {"image": "verbox:1.0", "replicas": 3},
                2: {"image": "verbox:1.1", "replicas": 3},
                3: {"image": "verbox:1.7", "replicas": 5},
            }
        },
        "Otel_deployment": {
            "current_revision": 1,
            "history": {
                1: {"image": "opentelemetry:4.0", "replicas": 10},
            }
        }
    }
}

def rollback_deployment(deployment_name: str) -> str:
    """Simulate the kubectl rollout undo deployment command
       It returns a success string or a throws RFC 7807 error """
    deployments = MOCK_DEPLOYMENT_HISTORY["deployments"]

    if deployment_name not in deployments:
        return ErrorSchema(
            type="https://google.com",
            status=404,
            detail=f"The provided deployment name is not available in this cluster",
            recovery_hint=f"Check the spelling of the deployment name"
        )
    deployment_data = deployments[deployment_name]
    current_rev = deployment_data["current_revision"]
    previous_rev = current_rev - 1

    if previous_rev not in deployment_data["history"]:
        return ErrorSchema(
            type="https://google.com",
            status=404,
            detail=f"No previous revision found in the {deployment_name}",
            recovery_hint=f"Create a new revision in the {deployment_name}"
        )

    target_config = deployment_data["history"][previous_rev]
    next_rev = current_rev + 1
    
    deployment_data["history"][next_rev] = target_config
    deployment_data["current_revision"] = next_rev
    
    return f"The Deployment - {deployment_name} rolled back to revision {previous_rev}"

if __name__ == "__main__":
    print(rollback_deployment("Verbox_Deployment"))
    print(MOCK_DEPLOYMENT_HISTORY)
    print()
    print(rollback_deployment("Verbox"))
    print(rollback_deployment("Otel_deployment"))
from pixos.services.remediation_service import scale_asg, rollback_k8s_deployment
from langchain.tools import tool
from pixos.storage.k8s_mock_store import k8s_store
from pydantic import BaseModel, Field

class RollbackInput(BaseModel):
    deployment_name: str = Field(
        description="The exact name of the Kubernetes deployment to roll back"
    )

class ScaleAsgInputs(BaseModel):
    asg_name: str = Field(
        description="The exact name of the Auto Scaling Group to be scaleds"
    )
    new_capacity: int = Field(
        description="The exact number of desired capacity of instances in the Auto Scaling Group"
    )

@tool(args_schema=ScaleAsgInputs)
def scale_asg_tool(asg_name: str, new_capacity: int) -> dict[str, int | bool]:
    """
    Scale an AWS Auto Scaling Group (ASG) to a specified capacity.
    
    Args:
        asg_name (str): The name of Auto Scaling Group to scale.
        new_capacity (int): The new desired capacity to set for the ASG.

    Returns:
        dict: A dictionary containing the status for scaling asg, with the following keys:
            - "asg_name" (str): The name of the Auto Scaling Group that was scaled
            - "old_capacity" (int): The old capacity of the Auto Scaling Group
            - "new_capacity" (int): The new capacity of the Auto Scaling Group
            - "instance_spin" (int): Number of new instances spun up
            - "status" (bool): True if the Auto Scaling Group scaled successfully, False if it failed to scale
    """
    return scale_asg(asg_name, new_capacity)

@tool(args_schema=RollbackInput)
def rollback_k8s_deployment_tool(deployment_name: str) -> dict[str, str | bool]:
    """
    Roll back a kubernetes deployment to its previous revision.

    Args:
        deployment_name (str): The name of kubernetes deployment to roll back.

    Returns:
        dict: A dictionary containing the status for scaling asg, with the following keys:
            - "deployment_name" (str): The name of kubernetes deployment to roll back.
            - "safe_state" (bool): True if the Deployment is in safe state after rollback, False if Deployment is not in safe state after rollback
    """
    rollback_k8s_deployment(deployment_name)
    
    return {
        "deployment_name": deployment_name,
        "safe_state": not(k8s_store.is_memory_leak_active),
    }
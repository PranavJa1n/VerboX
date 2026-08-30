from pixos.services.remediation_service import scale_asg, rollback_k8s_deployment
from langchain.tools import tool

@tool
def scale_asg_tool(asg_name: str, new_capacity: int) -> None:
    """
    Scale an AWS Auto Scaling Group (ASG) to a specified capacity.
    
    Args:
        asg_name (str): The name of Auto Scaling Group to scale.
        new_capacity (int): The new desired capacity to set for the ASG.

    Returns:
        None
    """
    return scale_asg(asg_name, new_capacity)

@tool
def rollback_k8s_deployment_tool(deployment_name: str) -> None:
    """
    Roll back a kubernetes deployment to its previous revision.

    Args:
        deployment_name (str): The name of kubernetes deployment to roll back.

    Returns:
        None
    """
    return rollback_k8s_deployment(deployment_name)
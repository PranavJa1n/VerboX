from pixos.services.telemetry_service import get_metrics, get_pod_logs, ping_application_health
from langchain.tools import tool

@tool
def get_metrics_tool(instance_id : str) -> dict[str, float]:
    """
    Fetch metrics for a given instance.
    
    Args:
        instance_id (string): ID of the instance to fetch metrics for.

    Returns:
        dict: A dictionary containing the metrics for the instance, with the following keys:
            - "cpu_util" (float): CPU utilization in percentage
            - "memory_util" (float): Memory utilization in percentage
            - "network_util" (float): Network Ingress Traffic in Bytes
    """
    return get_metrics(instance_id)

@tool
def get_pod_logs_tool(deployment_name: str) -> str:
    """
    Retrieve the logs for he pod(s) associated with a given Kubernetes deployment.

    Args:
        deployment_name (string): The name of the kubernetes deployment whose pod logs should be retrieved.

    Returns:
        str: Retrieved pod logs as a simple string.
    """
    return get_pod_logs(deployment_name)

@tool
def ping_application_health_tool() -> dict[str, int | str | bool]:
    """
    Check the health status of the application.
    
    Args:
        None
    
    Returns:
        dict: A dictionary containing the health check result, with the following values:
            - "status" (int): The HTTP status code returned by the health check.
            - "message" (str): A human-readable message describing the status.
            - "success" (bool): True if status code indicates the application is healthy , False if the status code indicates an issue.
    """
    return ping_application_health()
from langchain.tools import tool

@tool
def get_cloudwatch_metrics(instance_id : str) -> str:
    return "{'cpu':80, 'memory':50}"


@tool
def get_application_logs(app_id : str) -> str:
    return "Crash"

@tool
def get_recent_deployments() -> str:
    return "Deployment : 1111"

@tool
def fetch_k8s_pod_logs() -> str:
    return "logs - 1"


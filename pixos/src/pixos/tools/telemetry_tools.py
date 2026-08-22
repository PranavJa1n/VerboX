import requests
import boto3
from datetime import datetime, timezone
from botocore.exceptions import ClientError
from langchain_core.tools import tool
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

from pod_db_utils import create_pod

FLOCI_URL: str = "http://localhost:4566"
from langchain.tools import tool

# @tool
def get_recent_deployments(repo_name : str, owner :str,n:int ) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    params = {"per_page": n}  
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 404:
            return f"Error: Public repository '{owner}/{repo_name}' not found."
            
        response.raise_for_status()
        commits = response.json()
        
        if not commits:
            return f"No commit records found for repository: '{repo_name}'."
            
        formatted_results = []
        
        for i, commit_data in enumerate(commits):
            sha = commit_data["sha"][:7]
            commit_msg = commit_data["commit"]["message"].split("\n")[0]
            author = commit_data["commit"]["author"]["name"]
            date = commit_data["commit"]["committer"]["date"]
            
            formatted_results.append(
                f"--- Deployment {i+1} ---\n"
                f"Commit ID: {sha}\n"
                f"Message:   {commit_msg}\n"
                f"Author:    {author}\n"
                f"Date:      {date}"
            )
            
        return "\n\n".join(formatted_results)

    except requests.exceptions.RequestException as e:
        return f"Failed to fetch commits from GitHub API: {str(e)}"
    


# @tool
def fetch_k8s_pod_logs(cluster_name: str, pod_name: str) -> str:
    """
    Validates cluster metadata in Floci and fetches real-time pod logs 
    directly from the active Kubernetes cluster.
    
    Args:
        cluster_name (str): The target EKS cluster name running in Floci.
        pod_name (str): The specific name of the pod to query logs for.
        
    Returns:
        str: Live pod log stream or error details if cluster/pod check fails.
    """
    
    eks_client = boto3.client(
        "eks",
        region_name="us-east-1",
        endpoint_url=FLOCI_URL,
        aws_access_key_id="mock-key",
        aws_secret_access_key="mock-secret"
    )

    try:
        cluster_resp = eks_client.describe_cluster(name=cluster_name)
        cluster_info = cluster_resp.get("cluster", {})
        cluster_status = cluster_info.get("status", "UNKNOWN")

        if cluster_status.upper() != "ACTIVE":
            return f"Error: EKS Cluster '{cluster_name}' exists in Floci but status is '{cluster_status}'."

    except ClientError as e:
        return f"Floci AWS Error: Cluster '{cluster_name}' not found: {e.response['Error']['Message']}"
    except Exception as e:
        return f"Error connecting to Floci endpoint ({FLOCI_URL}): {str(e)}"


    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()

        all_pods = v1.list_pod_for_all_namespaces()
        target_namespace = None

        for pod in all_pods.items:
            if pod.metadata.name == pod_name:
                target_namespace = pod.metadata.namespace
                break

        if not target_namespace:
            return f"K8s Error: Pod '{pod_name}' was not found in the cluster. Cannot fetch logs."

        live_logs = v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=target_namespace,
            tail_lines=100
        )
        return live_logs

    except ApiException as e:
        return f"K8s API Error ({e.status}): {e.reason}"
    except Exception as e:
        return f"Cluster Connection Error: Could not reach Kubernetes API to pull logs: {str(e)}"


if __name__ == '__main__':
    # print(get_recent_deployments("VerboX", "PranavJa1n", 6))
    fetch_logs = fetch_k8s_pod_logs("testing", "etcd-desktop-control-plane")
    print(fetch_logs)
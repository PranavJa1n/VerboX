from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException

def get_all_pod_names() -> list[str]:
    try:
        # 1. Attempt to load local kubeconfig
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
        pod_list = v1.list_pod_for_all_namespaces()
        return [pod.metadata.name for pod in pod_list.items]

    except ConfigException:
        print("Warning: No local ~/.kube/config file found.")
        # Fallback for local testing/Floci mock mode
        return [
            "user-auth-service-75b89498c-x9jkl",
            "payment-gateway-6d45f78c9b-2a4bc"
        ]
        
    except Exception as e:
        print(f"Error connecting to K8s API: {e}")
        return []

if __name__ == "__main__":
    print(get_all_pod_names())
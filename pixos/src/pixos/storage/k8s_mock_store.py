#defining the k8s mock state.

http_responses = {
    # Good Status Codes
    200: {"status": 200, "message": "OK", "success": True},
    201: {"status": 201, "message": "Created", "success": True},
    204: {"status": 204, "message": "No Content", "success": True},
    
    # Bad Status Codes
    400: {"status": 400, "message": "Bad Request", "success": False},
    401: {"status": 401, "message": "Unauthorized", "success": False},
    403: {"status": 403, "message": "Forbidden", "success": False},
    404: {"status": 404, "message": "Not Found", "success": False},
    500: {"status": 500, "message": "Internal Server Error", "success": False}
}

class KubernetesMockStore:
    def __init__(self):
        self.is_memory_leak_active = True

        self.deployments = {
            "api-gateway" : {
                "current_revision" : 1,
                "history" : {
                    1 : {"image": "api:v2.3", "logs": "HTTP 200 OK"},
                    # 2: {"image": "api:v2.4", "logs": "FATAL: OutOfMemoryError: Java heap space\n  at com.api.RedisCache.load(RedisCache.java:42)"} 
                }
            }
        }

    def get_pod_logs(self, deployment_name : str):
        if deployment_name not in self.deployments:
            raise KeyError(f"Deployment {deployment_name} does not exist.")

        dep = self.deployments[deployment_name]
        current_rev = dep["current_revision"]
        return dep["history"][current_rev]["logs"]

    def rollback(self, deployment_name):
        if deployment_name not in self.deployments:
            raise KeyError(f"Deployment {deployment_name} does not exist.")
        dep = self.deployments[deployment_name]
        current_rev = dep["current_revision"]
        if current_rev <= 1:
            raise ValueError("No previous revision exists to roll back to.")
        new_rev = current_rev - 1
        dep["current_revision"] = new_rev

        if new_rev == 1:
            self.is_memory_leak_active = False

        return new_rev

k8s_store = KubernetesMockStore()
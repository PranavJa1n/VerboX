import boto3
from datetime import timedelta, datetime, timezone
from pixos.storage.metric_mock import seed_all_mock_data
from pixos.core.floci_client import get_client
from pixos.storage.k8s_mock_store import k8s_store, http_responses

LOCALSTACK_URL = "http://localhost:4566"
REGION = "us-east-1"


cloudwatch = get_client(service_name="cloudwatch")


# helper
def fetch_metrics(instance_id):
    END_TIME = datetime.now(timezone.utc)
    START_TIME = END_TIME - timedelta(minutes=15)
    seed_all_mock_data(instance_id=instance_id)

    map = dict()
    
    response = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/EC2",
                        "MetricName": "CPUUtilization",
                        "Dimensions": [{"Name": "InstanceId", "Value": instance_id}],
                    },
                    "Period": 300,
                    "Stat": "Average",
                },
                "ReturnData": True,
            },
        ],
        StartTime=START_TIME,
        EndTime=END_TIME,
    )
    
    
    results = response.get("MetricDataResults", [])
    if results and results[0].get("Values"):
        map["cpu_util"] = results[0]["Values"][0]

    response = cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    "Id": "m1",
                    "MetricStat": {
                        "Metric": {
                            "Namespace": "AWS/EC2",
                            "MetricName": "mem_used_percent",
                            "Dimensions": [{"Name": "InstanceId", "Value": instance_id}],
                        },
                        "Period": 300,
                        "Stat": "Average",
                    },
                    "ReturnData": True,
                },
            ],
            StartTime=START_TIME,
            EndTime=END_TIME,
        )
        
        
    results = response.get("MetricDataResults", [])
    if results and results[0].get("Values"):
        map["memory_util"] = results[0]["Values"][0]
    
    response = cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    "Id": "m1",
                    "MetricStat": {
                        "Metric": {
                            "Namespace": "AWS/EC2",
                            "MetricName": "NetworkIn",
                            "Dimensions": [{"Name": "InstanceId", "Value": instance_id}],
                        },
                        "Period": 300,
                        "Stat": "Average",
                    },
                    "ReturnData": True,
                },
            ],
            StartTime=START_TIME,
            EndTime=END_TIME,
        )
        
        
    results = response.get("MetricDataResults", [])
    if results and results[0].get("Values"):
        map["network_util"] = results[0]["Values"][0]
    
    return map

# tools

def get_metrics(instance_id: str) :
    res = fetch_metrics(instance_id=instance_id)
    return res

def get_pod_logs(deployment_name: str) :
    return k8s_store.get_pod_logs(deployment_name=deployment_name)

def ping_application_health():
    
    if(k8s_store.is_memory_leak_active != True):
        return http_responses[200]
    
    return http_responses[500]


if __name__ == '__main__':
    print(get_metrics('i-e00ef2377a4a06be3s'))
    print(get_pod_logs("api-gateway"))
    print(ping_application_health())
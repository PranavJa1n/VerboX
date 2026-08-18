import boto3

def get_ec2_client():
    """Initializes and returns the EC2 client for LocalStack."""
    return boto3.client(
        "ec2",
        endpoint_url="http://localhost:4566",
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )

def terminate_all_running_instances():
    """
    Finds all currently running EC2 instances in LocalStack,
    prints the total count, and terminates (deletes) all of them.
    """
    ec2 = get_ec2_client()
    
   
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
    )
    
  
    instance_ids = []
    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            instance_ids.append(instance["InstanceId"])
            
    
    total_running = len(instance_ids)
    print(f"Total running instances found: {total_running}")
    
    if total_running == 0:
        print("No running instances to terminate.")
        return []
        
    print(f"Terminating instances: {instance_ids}")
    termination_response = ec2.terminate_instances(InstanceIds=instance_ids)
    
    return termination_response.get("TerminatingInstances", [])


def terminate_specific_instance(instance_id):
    """
    Terminates (deletes) a single, specific instance by its ID.
    """
    ec2 = get_ec2_client()
    
    print(f"Terminating specific instance: {instance_id}")
    try:
        termination_response = ec2.terminate_instances(InstanceIds=[instance_id])
        return termination_response.get("TerminatingInstances", [])
    except Exception as e:
        print(f" Error terminating instance {instance_id}: {str(e)}")
        return None


if __name__ == "__main__":
    terminated_list = terminate_all_running_instances()
    # terminated_list = terminate_specific_instance("i-caea5888dbb026c15")
    print("Action completed.")

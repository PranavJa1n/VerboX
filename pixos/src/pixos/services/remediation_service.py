from pixos.storage.k8s_mock_store import k8s_store
from pixos.storage.system_repo import ASG, Instance
from pixos.core.floci_client import get_client

def scale_asg(asg_name: str, new_capacity: int):
    asg_client = get_client("autoscaling")
    ec2_client = get_client('ec2')
    print(f"Scaling ASG - {asg_name} to {new_capacity}")
    
    asg_client.update_auto_scaling_group(
                AutoScalingGroupName=asg_name,
                DesiredCapacity=new_capacity,
                MinSize=1,
                MaxSize=new_capacity + 2
            )
    
    asg = ASG()

    old = asg.read(asg_name=asg_name)['desired_capacity']
    print(old)
    asg.update(asg_name=asg_name, new_capacity=new_capacity)
    # waking up other ec2s

    reservation = ec2_client.run_instances(
                ImageId='ami-12345678', 
                MinCount = new_capacity - int(old),
                MaxCount = new_capacity - int(old),
                InstanceType='t2.micro',
            )
    
    instance_ids = [instance['InstanceId'] for instance in reservation['Instances']]
    print(f"Mocked Instance IDs: {instance_ids}") 

    asg_client.attach_instances(
                InstanceIds = instance_ids,
                AutoScalingGroupName = asg_name
            )
    
    print("Successfully attached other instances to prod-asg!")

    ins = Instance()
    for id in instance_ids:
        ins.create(instance_id=id, asg_name=asg_name)

def rollback_k8s_deployment(deployment_name: str):
    k8s_store.rollback(deployment_name=deployment_name)


if __name__ == '__main__':
    print(k8s_store.is_memory_leak_active)
    rollback_k8s_deployment("api-gateway")
    print(k8s_store.is_memory_leak_active)
    scale_asg("prod-asg-2", new_capacity=7)

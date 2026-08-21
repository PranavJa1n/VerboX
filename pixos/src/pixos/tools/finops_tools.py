from langchain.tools import tool
from pixos.tools.instance_utils import check_instance, seed_all_mock_data, fetch_single_metric, run_instance, terminate_all_running_instances

# @tool     
def get_cloudwatch_metrics(instance_id : str, cpu=58.7, memory=88.2, ingress=102400.0):
    '''
    This tool returns cloud metrics.
    '''
    if(not(check_instance(instance_id))):
        return
    else:
        seed_all_mock_data(instance_id, cpu_val=cpu, mem_val=memory, net_in_val= ingress)
        ingress_ = fetch_single_metric("AWS/EC2", "NetworkIn", instance_id)
        cpu_ = fetch_single_metric("AWS/EC2", "CPUUtilization", instance_id)
        mem_ = fetch_single_metric("AWS/EC2", "mem_used_percent", instance_id)
    print(ingress_, cpu_, mem_)
    return ingress_, cpu_, mem_


def get_active_billing_alerts():
    pass


        

if __name__ == '__main__':
    instance_id = run_instance()
    get_cloudwatch_metrics(instance_id)
    terminate_all_running_instances()
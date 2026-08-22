from langchain.tools import tool
import json
from langchain_core.tools import tool
from pixos.data.finance_db import get_connection
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


def get_active_billing_alerts(department_name: str) -> str:
    """
    Queries the finance database to compare a department's current spend 
    against its monthly limit and returns the alert status as a JSON string.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT monthly_limit, current_spend FROM budgets WHERE department_name = ?",
            (department_name,)
        ).fetchone()

        if not row:
            return json.dumps({
                "error": f"Department '{department_name}' not found in budgets."
            })

        monthly_limit = row["monthly_limit"]
        current_spend = row["current_spend"]
        is_breached = current_spend > monthly_limit
        variance = current_spend - monthly_limit

        result = {
            "department": department_name,
            "monthly_limit": monthly_limit,
            "current_spend": current_spend,
            "is_breached": is_breached,
            "overage_amount": round(max(0.0, variance), 2)
        }

        return json.dumps(result)


if __name__ == '__main__':
    instance_id = run_instance()
    get_cloudwatch_metrics(instance_id)
    terminate_all_running_instances()
    
    print("\n--- Testing Billing Alerts ---")
    engineering_alert = get_active_billing_alerts("engineering")
    print(engineering_alert)
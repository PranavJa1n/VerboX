from pixos.data.finance_db import get_connection 



def get_budget_status(department_name: str) -> dict:
    """
    Scope: FINOPS AGENT TOOL (`get_active_billing_alerts`)
    Returns the budget constraints. If spend > limit, the agent should block scaling.
    """
    with get_connection() as conn:
        row = conn.execute("""
            SELECT monthly_limit, current_spend 
            FROM budgets 
            WHERE department_name = ?
        """, (department_name,)).fetchone()
        
        return dict(row) if row else None

def inject_cost_spike(department_name: str, unexpected_cost: float):
    """
    Scope: CHAOS ENGINEERING (The VerboX Trap)
    Run this via a background script mid-incident to simulate a billing alert.
    """
    with get_connection() as conn:
        conn.execute("""
            UPDATE budgets
            SET current_spend = current_spend + ?
            WHERE department_name = ?
        """, (unexpected_cost, department_name))

# ==========================================
# RESOURCE OPERATIONS
# ==========================================

def get_instance_hourly_rate(instance_type: str) -> float:
    """
    Scope: FINOPS AGENT TOOL (`calculate_remediation_cost`)
    Used to calculate the dollar impact of scaling an Auto Scaling Group.
    """
    with get_connection() as conn:
        row = conn.execute("""
            SELECT hourly_rate 
            FROM resource_costs 
            WHERE instance_type = ?
        """, (instance_type,)).fetchone()
        
        return row['hourly_rate'] if row else 0.0


if __name__ == '__main__':
    print(get_instance_hourly_rate("t3.medium"))
    print(get_budget_status("engineering"))
    inject_cost_spike("engineering", 100)
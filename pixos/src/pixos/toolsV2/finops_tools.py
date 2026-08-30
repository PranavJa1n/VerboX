from pixos.services.finops_service import check_department_budget
from langchain.tools import tool

@tool
def check_department_budget_tool(department : str) -> bool:
    """
    Check wether current spend is within the allowed monthly budget limit.
    
    Args:
        department (string): The name of department to check buget for.
    
    Returns:
        bool: True if current_spend is stritly less than monthly_limit else False.
    """
    return check_department_budget(department)
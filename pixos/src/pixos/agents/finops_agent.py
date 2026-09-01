from pixos.toolsV2.finops_tools import check_department_budget_tool
from pixos.toolsV2.telemetry_tools import get_metrics_tool
from pixos.agents.system_prompts import FINOPS_SYSTEM_PROMPT
from pixos.agents.utils.agent import get_agent

tools = [check_department_budget_tool, get_metrics_tool]


finops_agent = get_agent(
    tools=tools,
    system_prompt=FINOPS_SYSTEM_PROMPT,
)

if __name__ == "__main__":
    response = finops_agent.invoke(
        {
            "messages":[
                {
                    "role": "user",
                    "content": """Engineering's EC2 fleet (dept1) is under heavy load and the on-call team wants to scale up its Auto Scaling Group. Please check current CloudWatch metrics and the active billing alerts for dept1, then tell me whether we're within budget to approve the scale-up. Separately, also check the budget status for dept2 — no scaling request there, I just want to know if they're currently within budget"""
                }
            ]
        }
    )
    print(response)
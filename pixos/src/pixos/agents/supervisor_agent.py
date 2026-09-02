from pixos.agents.system_prompts import SUPERVISOR_SYSTEM_PROMPT
from pixos.toolsV2.supervisor_tools import finops_agent_tool, telemetry_agent_tool, remediation_agent_tool
from dotenv import load_dotenv
from pixos.agents.utils.agent import get_agent

load_dotenv()

tools=[telemetry_agent_tool, finops_agent_tool, remediation_agent_tool]

supervisor_agent = get_agent(
    tools=tools,
    system_prompt=SUPERVISOR_SYSTEM_PROMPT
)

if __name__ == "__main__":
    user_query = r"""
INCIDENT ALERT
instance_id: i-448f97ac1fcb74a5c
deployment_name: api-gateway
department_name: dept2
auto scaling group name: prod-asg-2
description: The api-gateway is returning HTTP 500 errors on ~40% of requests over the last 5 minutes. Response latency has also increased from ~120ms to ~2.1s."""

    response = supervisor_agent.invoke({
        "messages": [{"role": "user", "content": user_query}]
    })
    # print(response)
    final_message = response["messages"][-1]
    print("\n--- AGENT RESPONSE ---")
    print(final_message.content)
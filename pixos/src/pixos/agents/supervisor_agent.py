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
    user_query = " verify the application status using ping_application_health tool for deployemnt api-gateway. Instance ID - 'i-880e394881001fdae', what should be out next step taking finance into consideration for department 'dept1'"

    response = supervisor_agent.invoke({
        "messages": [{"role": "user", "content": user_query}]
    })
    # print(response)
    final_message = response["messages"][-1]
    print("\n--- AGENT RESPONSE ---")
    print(final_message.content)
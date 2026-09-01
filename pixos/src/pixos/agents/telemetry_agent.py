from pixos.toolsV2.telemetry_tools import get_metrics_tool, get_pod_logs_tool, ping_application_health_tool
from pixos.agents.system_prompts import TELEMETRY_SYSTEM_PROMPT
from pixos.agents.utils.agent import get_agent

tools=[get_metrics_tool, get_pod_logs_tool, ping_application_health_tool]

telemetry_agent = get_agent(
    tools=tools,
    system_prompt=TELEMETRY_SYSTEM_PROMPT
)

if __name__ == "__main__":
    user_query = "verify the application status using ping_application_health tool ,for deployemnt api-gateway."

    response = telemetry_agent.invoke({
        "messages": [{"role": "user", "content": user_query}]
    })

    final_message = response["messages"][-1]
    print("\n--- AGENT RESPONSE ---")
    print(final_message.content)
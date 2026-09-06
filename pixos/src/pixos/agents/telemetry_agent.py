from pixos.toolsV2.telemetry_tools import get_metrics_tool, get_pod_logs_tool, ping_application_health_tool
from pixos.agents.system_prompts import TELEMETRY_SYSTEM_PROMPT
from pixos.agents.utils.agent import get_agent
from langchain_core.messages import HumanMessage

tools=[get_metrics_tool, get_pod_logs_tool, ping_application_health_tool]


telemetry_agent = get_agent(
    tools=tools,
    system_prompt=TELEMETRY_SYSTEM_PROMPT
)

def telemetry_node(state : dict):

    result = telemetry_agent.invoke(state)

    input_message_count = len(state.get("messages", []))
    new_messages = result["messages"][input_message_count:]

    final_message = result['messages'][-1].content

    return {
        "messages" : new_messages,
        "telemetry_context" : {
            "latest_analysis" : final_message
        }
    }


if __name__ == "__main__":
    user_query = "verify the application status using ping_application_health tool, for deployment api-gateway."

    # Test the node wrapper instead of the base agent
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "telemetry_context": {}
    }

    response = telemetry_node(initial_state)

    print("\n--- STATE UPDATE ---")
    print(f"Context Captured: {response['telemetry_context']}")
    print("=" * 20)
    if response["messages"]:
        print(f"Final Message: {response['messages'][-1].content}")
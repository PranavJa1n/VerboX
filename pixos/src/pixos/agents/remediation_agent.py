from pixos.toolsV2.remediation_tools import scale_asg_tool, rollback_k8s_deployment_tool
from pixos.agents.system_prompts import REMEDIATION_SYSTEM_PROMPT
from pixos.agents.utils.agent import get_agent
from langchain_core.messages import HumanMessage

tools = [scale_asg_tool, rollback_k8s_deployment_tool,]


remediation_agent = get_agent(
    tools=tools,
    system_prompt=REMEDIATION_SYSTEM_PROMPT
)

def remediation_node(state : dict):
    result = remediation_agent.invoke(state)
    input_message_count = len(state.get('messages', []))
    new_messages = result['messages'][input_message_count:]
    final_message = result['messages'][-1].content

    return {
        "messages" :new_messages,
        "remediation_plan" : {
            "execution_status" : final_message
        }
    }

if __name__ == "__main__":
    user_query = "rollback current deployment of 'api-gateway"

    # Test the node wrapper instead of the base agent
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "finops_context": {}
    }

    response = remediation_node(initial_state)

    print("\n--- STATE UPDATE ---")
    print(f"Context Captured: {response['remediation_plan']}")
    print("=" * 20)
    if response["messages"]:
        print(f"Final Message: {response['messages'][-1].content}")
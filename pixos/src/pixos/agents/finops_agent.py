from pixos.toolsV2.finops_tools import check_department_budget_tool
from pixos.toolsV2.telemetry_tools import get_metrics_tool
from pixos.agents.system_prompts import FINOPS_SYSTEM_PROMPT
from pixos.agents.utils.agent import get_agent
from langchain_core.messages import HumanMessage

tools = [check_department_budget_tool, get_metrics_tool]


finops_agent = get_agent(
    tools=tools,
    system_prompt=FINOPS_SYSTEM_PROMPT,
)

def finops_node(state : dict):
    result = finops_agent.invoke(state)
    input_message_count = len(state.get('messages', []))
    new_messages = result['messages'][input_message_count:]
    final_message = result['messages'][-1].content

    return {
        "messages" :new_messages,
        "finops_context" : {
            "budget_status" : final_message
        }
    }

if __name__ == "__main__":
    user_query = "verify the budget for dept2"

    # Test the node wrapper instead of the base agent
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "finops_context": {}
    }

    response = finops_node(initial_state)

    print("\n--- STATE UPDATE ---")
    print(f"Context Captured: {response['finops_context']}")
    print("=" * 20)
    if response["messages"]:
        print(f"Final Message: {response['messages'][-1].content}")
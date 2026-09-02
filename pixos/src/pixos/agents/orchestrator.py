import operator
from IPython.display import Image, display
from typing import Annotated, Literal, Sequence, TypedDict
from pixos.agents.utils.agent import get_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel
from pixos.agents.system_prompts import SUPERVISOR_SYSTEM_PROMPT
from pixos.agents.telemetry_agent import telemetry_agent
from pixos.agents.finops_agent import finops_agent
from pixos.agents.remediation_agent import remediation_agent
from pixos.agents.supervisor_agent import supervisor_agent


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

class SupervisorRouter(BaseModel):
    next: Literal["telemetry_agent", "finops_agent", "remediation_agent", "FINISH"]


workflow = StateGraph(AgentState)

workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("telemetry_agent", telemetry_agent)
workflow.add_node("finops_agent", finops_agent)
workflow.add_node("remediation_agent", remediation_agent)

workflow.add_edge(START, "supervisor")
workflow.add_edge("telemetry_agent", "supervisor")
workflow.add_edge("finops_agent", "supervisor")
workflow.add_edge("remediation_agent", "supervisor")

workflow.add_conditional_edges(
    "supervisor",
    lambda state: state.get("next", "FINISH"),
    {
        "telemetry_agent": "telemetry_agent",
        "finops_agent": "finops_agent",
        "remediation_agent": "remediation_agent",
        "FINISH": END
    }
)

orchestrator_app = workflow.compile()

if __name__=="__main__":
    initial_input = {
        "messages": [
            HumanMessage(
                content=r"""
INCIDENT ALERT
instance_id: i-60b3df663fbfa6f00
deployment_name: api-gateway
department_name: dept1
auto scaling group name: prod-asg-2
description: The api-gateway is returning HTTP 500 errors on ~40% of requests over the last 5 minutes. Response latency has also increased from ~120ms to ~2.1s."""
            )
        ]
    }
    for step in orchestrator_app.stream(initial_input):
        for node_name, state_update in step.items():
            print(f"=== Node Executed: [{node_name}] ===")
            if "next" in state_update:
                print(f"Supervisor Choice: -> {state_update['next']}")
            if "messages" in state_update:
                for msg in state_update["messages"]:
                    sender = getattr(msg, "name", msg.type)
                    print(f"[{sender}]: {msg.content}")
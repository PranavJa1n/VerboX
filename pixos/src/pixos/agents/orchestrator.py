import operator
from IPython.display import Image, display
from typing import Annotated, Literal, Sequence, TypedDict
from pixos.agents.utils.agent import get_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel
from pixos.agents.system_prompts import SUPERVISOR_SYSTEM_PROMPT
from pixos.agents.telemetry_agent import telemetry_node
from pixos.agents.finops_agent import finops_node
from pixos.agents.remediation_agent import remediation_node
from pixos.agents.supervisor_agent import supervisor_agent
from pixos.state.state import IncidentState


class SupervisorRouter(BaseModel):
    next: Literal["telemetry_agent", "finops_agent", "remediation_agent", "FINISH"]


workflow = StateGraph(IncidentState)

workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("telemetry_agent", telemetry_node)
workflow.add_node("finops_agent", finops_node)
workflow.add_node("remediation_agent", remediation_node)

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

if __name__ == "__main__":
    initial_input = {
        "incident_id": "INC-001",
        "telemetry_context": {},
        "finops_context": {},
        "remediation_plan": "",
        "messages": [
            HumanMessage(
                content=r"""
INCIDENT ALERT
instance_id: i-10ebe6ffc1468e27e
deployment_name: api-gateway
department_name: dept2
auto scaling group name: prod-asg-2
description: The api-gateway is returning HTTP 500 errors on ~40% of requests over the last 5 minutes. Response latency has also increased from ~120ms to ~2.1s.\
new_scaled_capacity : 4"""
            )
        ]
    }
    
    from datetime import datetime

    # Open the log file in append mode outside the loops
    with open("logs.txt", "a", encoding="utf-8") as log_file:
        
        for step in orchestrator_app.stream(initial_input):
            for node_name, state_update in step.items():
                
                # 1. Node Execution Line
                line1 = f"=== Node Executed: [{node_name}] ===\n"
                print(line1, end="") 
                log_file.write(line1)
                
                # 2. Supervisor Choice Line
                if "next" in state_update:
                    line2 = f"Supervisor Choice: -> {state_update['next']}\n"
                    print(line2, end="")
                    log_file.write(line2)
                    
                # 3. Messages Lines
                if "messages" in state_update:
                    for msg in state_update["messages"]:
                        sender = getattr(msg, "name", msg.type)
                        line3 = f"[{sender}]: {msg.content}\n"
                        print(line3, end="")
                        log_file.write(line3)
                        
                # Ensure it writes to the file immediately while running
                log_file.flush()

from pixos.agents.system_prompts import SUPERVISOR_SYSTEM_PROMPT
from pixos.toolsV2.supervisor_tools import finops_agent_tool, telemetry_agent_tool, remediation_agent_tool
from dotenv import load_dotenv
from pixos.agents.utils.agent import get_agent
from pixos.agents.utils.agent import model
from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()


class SupervisorDecision(BaseModel):
    reasoning : str = Field(description='Brief explanation of why you chose the next node.')
    next : Literal["telemetry_agent", "finops_agent", "remediation_agent", "FINISH"] = Field(...)

supervisor_prompt = ChatPromptTemplate.from_messages([
    ("system", SUPERVISOR_SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
    (
        "system", 
        "Current System State:\n"
        "Telemetry Context: {telemetry_context}\n"
        "FinOps Context: {finops_context}\n"
        "Remediation Plan: {remediation_plan}\n\n"
        "Based on the rules and current state, who must act next?"
    )
])


supervisor_chain = supervisor_prompt | model.with_structured_output(SupervisorDecision)

def supervisor_agent(state : dict):

    decision = supervisor_chain.invoke({
        "messages": state.get("messages", []),
        "telemetry_context": state.get("telemetry_context", {}),
        "finops_context": state.get("finops_context", {}),
        "remediation_plan": state.get("remediation_plan", "")
    })

    print(f"\n[SUPERVISOR THOUGHT]: {decision.reasoning}")
    
   
    command_message = AIMessage(
        name="supervisor", 
        content=f"SUPERVISOR COMMAND: {decision.reasoning}. Execute the appropriate tool immediately."
    )
    
    
    return {
        "next": decision.next,
        "messages": [command_message] 
    }
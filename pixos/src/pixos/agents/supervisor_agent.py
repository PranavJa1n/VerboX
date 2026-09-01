from langchain.agents import create_agent
from pixos.agents.system_prompts import SUPERVISOR_SYSTEM_PROMPT
from langchain_openrouter import ChatOpenRouter
from pixos.toolsV2.supervisor_tools import finops_agent, telemetry_agent, remediation_agent

from dotenv import load_dotenv
import os
load_dotenv()

tools=[telemetry_agent, finops_agent, remediation_agent]
model = ChatOpenRouter(
    model="openai/gpt-4o",
    api_key=os.environ.get("OPENAI_API_KEY"),
    max_tokens=1000
)

supervisor_agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=SUPERVISOR_SYSTEM_PROMPT
)

if __name__ == "__main__":
    user_query = " verify the application status using ping_application_health tool ,for deployemnt api-gateway."

    response = supervisor_agent.invoke({
        "messages": [{"role": "user", "content": user_query}]
    })

    final_message = response["messages"][-1]
    print("\n--- AGENT RESPONSE ---")
    print(final_message.content)
from langchain.agents import create_agent
from pixos.agents.system_prompts import SUPERVISOR_SYSTEM_PROMPT
from pixos.toolsV2.supervisor_tools import finops_agent_tool, telemetry_agent_tool, remediation_agent_tool
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

tools=[telemetry_agent_tool, finops_agent_tool, remediation_agent_tool]

model = AzureChatOpenAI(
    azure_deployment='gpt-4o',
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    temperature = 0
)

supervisor_agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=SUPERVISOR_SYSTEM_PROMPT
)

if __name__ == "__main__":
    user_query = " verify the application status using ping_application_health tool for deployemnt api-gateway. Instance ID - 'i-880e394881001fdae'"

    response = supervisor_agent.invoke({
        "messages": [{"role": "user", "content": user_query}]
    })
    print(response)
    final_message = response["messages"][-1]
    print("\n--- AGENT RESPONSE ---")
    print(final_message.content)
from langchain.agents import create_agent
from pixos.toolsV2.telemetry_tools import get_metrics_tool, get_pod_logs_tool, ping_application_health_tool
from pixos.agents.system_prompts import TELEMETRY_SYSTEM_PROMPT
import os
from os import getenv
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()

tools=[get_metrics_tool, get_pod_logs_tool, ping_application_health_tool]

model = AzureChatOpenAI(
    azure_deployment='gpt-4o',
    api_version="2024-12-01-preview",
    azure_endpoint=getenv('AZURE_OPENAI_ENDPOINT'),
    api_key=getenv('AZURE_OPENAI_API_KEY'),
    temperature = 0
)

telemetry_agent = create_agent(
    model=model,
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
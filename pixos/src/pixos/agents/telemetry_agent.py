from langchain.agents import create_agent
from pixos.toolsV2.telemetry_tools import get_metrics_tool, get_pod_logs_tool, ping_application_health_tool
from pixos.agents.system_prompts import TELEMETRY_SYSTEM_PROMPT
import os
from langchain_openrouter import ChatOpenRouter
from dotenv import load_dotenv
load_dotenv()

tools=[get_metrics_tool, get_pod_logs_tool, ping_application_health_tool]
model = ChatOpenRouter(
    model="openai/gpt-4o",
    api_key=os.environ.get("OPENAI_API_KEY"),
    max_tokens=1000
)
telemetry_agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=TELEMETRY_SYSTEM_PROMPT
)

if __name__ == "__main__":
    user_query = " verify the application status using ping_application_health tool ,for deployemnt api-gateway."

    response = telemetry_agent.invoke({
        "messages": [{"role": "user", "content": user_query}]
    })

    final_message = response["messages"][-1]
    print("\n--- AGENT RESPONSE ---")
    print(final_message.content)
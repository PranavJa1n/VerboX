from pixos.toolsV2.finops_tools import check_department_budget_tool
from pixos.toolsV2.telemetry_tools import get_metrics_tool
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent
from pixos.agents.system_prompts import FINOPS_SYSTEM_PROMPT
from dotenv import load_dotenv
from os import getenv
# from langchain_ollama import ChatOllama     # For local testing only

load_dotenv()

tools = [check_department_budget_tool, get_metrics_tool]

# llm = AzureChatOpenAI(
#     azure_deployment= getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
#     api_version= getenv("AZURE_OPENAI_API_VERSION"),
#     temperature=0,
# )

model = AzureChatOpenAI(
    azure_deployment='gpt-4o',
    api_version="2024-12-01-preview",
    azure_endpoint=getenv('AZURE_OPENAI_ENDPOINT'),
    api_key=getenv('AZURE_OPENAI_API_KEY'),
    temperature = 0
)

finops_agent = create_agent(
    model=model,          # change to model for local testing
    tools=tools,
    system_prompt=FINOPS_SYSTEM_PROMPT,
)

if __name__ == "__main__":
    response = finops_agent.invoke(
        {
            "messages":[
                {
                    "role": "user",
                    "content": """Engineering's EC2 fleet (dept1) is under heavy load and the on-call team wants to scale up its Auto Scaling Group. Please check current CloudWatch metrics and the active billing alerts for dept1, then tell me whether we're within budget to approve the scale-up. Separately, also check the budget status for dept2 — no scaling request there, I just want to know if they're currently within budget"""
                }
            ]
        }
    )
    print(response)
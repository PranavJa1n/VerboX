from pixos.toolsV2.remediation_tools import scale_asg_tool, rollback_k8s_deployment_tool
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent
from pixos.agents.system_prompts import REMEDIATION_SYSTEM_PROMPT
from dotenv import load_dotenv
from os import getenv
from langchain_ollama import ChatOllama     # For local testing only

load_dotenv()

tools = [scale_asg_tool, rollback_k8s_deployment_tool,]

llm = AzureChatOpenAI(
    azure_deployment= getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
    api_version= getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0,
)

model = ChatOllama(     # For local testing only
    model="gemma4:e4b",
    temperature=0,
)

remediation_agent = create_agent(
    model=llm,          # change to model for local testing
    tools=tools,
    system_prompt=REMEDIATION_SYSTEM_PROMPT
)

if __name__ == "__main__":
    response = remediation_agent.invoke(
        {"messages": 
            [
                {
                    "role": "user",
                    "content": "Roll back the deployment named 'api-gateway' to its previous version and check its post-deployment state."
                }
            ]
        },
    )
    print(response)
    response = agent.invoke(
        {"messages": 
            [
                {
                    "role":"user",
                    "content": "Scale the 'prod-asg-2' auto-scaling group to a desired capacity of 5 instances."
                }
            ]
        }
    )
    print(response)
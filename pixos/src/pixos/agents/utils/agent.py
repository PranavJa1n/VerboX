from langgraph.prebuilt import create_react_agent
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

model = AzureChatOpenAI(
    azure_deployment='gpt-4o',
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    temperature = 0
)

def get_agent(tools : list, system_prompt : str):
    agent = create_react_agent(
    model=model,
    tools=tools,
    prompt=system_prompt
    )
    return agent


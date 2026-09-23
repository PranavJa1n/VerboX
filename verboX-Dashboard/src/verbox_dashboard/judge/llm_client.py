from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from verbox_dashboard.judge.schema import VerdictOutput

load_dotenv()

model = AzureChatOpenAI(
    azure_deployment='gpt-4o',
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    temperature = 0
)

sturctured_model = model.with_structured_output(VerdictOutput)

def judge(prompt: str) -> VerdictOutput:
    return sturctured_model.invoke(prompt)

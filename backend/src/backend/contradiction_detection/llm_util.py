from dotenv import load_dotenv
import os

from openai import AzureOpenAI
from backend.contradiction_detection.schema import ContradictionReport

load_dotenv()

class AzureModel:
    def __init__(self):
        self.client = AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint="https://inreal1907.openai.azure.com/",
            api_key=os.getenv('AZURE_OPENAI_API_KEY_CD'),
        )

    def invoke(self, query):
        response = self.client.chat.completions.parse(
            messages=[
                {
                    "role": "system",
                    "content": "You are a critique, check weather statement_1 and statement_2 are contradictory statements or not.",
                },
                {
                    "role": "user",
                    "content": query,
                }
            ],
            max_tokens=4096,
            temperature=0,
            model='gpt-4o',
            response_format = ContradictionReport
        )
        structured_data: ContradictionReport = response.choices[0].message.parsed
        return structured_data
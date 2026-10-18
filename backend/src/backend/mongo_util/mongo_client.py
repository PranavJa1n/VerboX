import asyncio

from pymongo import AsyncMongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class MongoClient:
    def __init__(self):
        self.db_user = os.getenv('MONGODB_USERNAME')
        self.db_pass = os.getenv('MONGODB_PASSWORD')
        self.db_name = os.getenv('MONGODB_DB_NAME', 'verbox')
        self.uri = f'mongodb+srv://{self.db_user}:{self.db_pass}@verboxcluster.qkxy6z5.mongodb.net/'
        self.client = AsyncMongoClient(self.uri)

        self.db = self.client[self.db_name]
        self.traces = self.db["traces"]
        self.verdicts = self.db["verdicts"]

    async def close(self) -> None:
        await self.client.close()
        print("Successfully Connection Closed!")

    async def ping(self) -> None:
        await self.client.admin.command('ping')
        print("Connected Successfully!")
        await self.close()

    async def save_span(self, span_data: dict) -> None:
        await self.traces.insert_one(span_data)

    async def save_verdict(self, verdict_data: dict) -> None:
        await self.verdicts.insert_one(verdict_data)

# one client used everywhere. No need to create clients again and again
mongo_client = MongoClient()

if __name__ == '__main__':
    obj = MongoClient()
    asyncio.run(obj.ping())
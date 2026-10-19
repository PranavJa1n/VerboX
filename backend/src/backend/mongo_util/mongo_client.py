import asyncio
import os
from pymongo import AsyncMongoClient
from dotenv import load_dotenv

load_dotenv()

class MongoClient:
    def __init__(self):
        # Load the complete URI from the environment, defaulting to a local instance if missing
        self.uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        self.db_name = os.getenv('MONGODB_DB_NAME', 'verbox')
        
        # Instantiate the async client
        self.client = AsyncMongoClient(self.uri)

        # Map the database and collections
        self.db = self.client[self.db_name]
        self.traces = self.db["traces"]
        self.verdicts = self.db["verdicts"]

    async def close(self) -> None:
        await self.client.close()
        print("Successfully Connection Closed!")

    async def ping(self) -> None:
        # A simple ping command to verify the connection works
        await self.client.admin.command('ping')
        print("Connected Successfully to Cosmos/Mongo DB!")
        await self.close()

    async def save_span(self, span_data: dict) -> None:
        await self.traces.insert_one(span_data)

    async def save_verdict(self, verdict_data: dict) -> None:
        await self.verdicts.insert_one(verdict_data)

    async def get_spans_by_trace(self, trace_id: str) -> list[dict]:
        """Fetches all spans for a given trace_id from Cosmos DB."""
        # Find all documents matching the trace_id
        cursor = self.traces.find({"trace_id": trace_id})
        # Convert the async cursor to a Python list
        spans = await cursor.to_list(length=None)
        return spans

# Singleton client instance
mongo_client = MongoClient()

if __name__ == '__main__':
    obj = MongoClient()
    asyncio.run(obj.ping())
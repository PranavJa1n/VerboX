import asyncio

from pymongo import AsyncMongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class MongoClient:
    def __init__(self):
        self.db_user = os.getenv('MONGODB_USERNAME')
        self.db_pass = os.getenv('MONGODB_PASSWORD')
        self.uri = f'mongodb+srv://{self.db_user}:{self.db_pass}@verboxcluster.qkxy6z5.mongodb.net/'
        self.client = AsyncMongoClient(self.uri)

    async def close(self):
        await self.client.close()
        print("Successfully Connection Closed!")

    async def ping(self):
        await self.client.admin.command('ping')
        print("Connected Successfully!")
        await self.close()


if __name__ == '__main__':
    obj = MongoClient()
    asyncio.run(obj.ping())
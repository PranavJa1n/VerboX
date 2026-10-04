"""Basic connection example.
"""
import os
import redis
from dotenv import load_dotenv

load_dotenv()


class ConnectRedis:

    @staticmethod
    def connect(self):
        r = redis.ConnectionPool(
            host=os.getenv('REDIS_HOST'),
            port=os.getenv('REDIS_PORT'),
            decode_responses=True,
            username="default",
            password=os.getenv('REDIS_PASSWORD'),
        )
        return r


if __name__=='__main__':
    print(ConnectRedis.connect())


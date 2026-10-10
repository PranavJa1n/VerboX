"""Basic connection example.
"""
import os
import redis
from dotenv import load_dotenv

load_dotenv()


class ConnectRedis:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            cls._pool = redis.ConnectionPool(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                decode_responses=True,
                username=os.getenv('REDIS_USERNAME', 'default'),
                password=os.getenv('REDIS_PASSWORD'),
            )
        return cls._pool

    @classmethod
    def get_client(cls):
        return redis.Redis(connection_pool=cls.get_pool())


if __name__=='__main__':
    client = ConnectRedis.get_client()
    print("Redis Ping:", client.ping())

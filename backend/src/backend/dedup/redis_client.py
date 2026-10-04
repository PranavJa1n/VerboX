from backend.dedup.connect_redis import ConnectRedis

class RedisClient:
    def __init__(self):
        self.conn = ConnectRedis.connect()
    def set(self, key, data):
        self.conn.hsetnx(key,data)
    def get(self, key):
        return self.conn.hgetall(key)


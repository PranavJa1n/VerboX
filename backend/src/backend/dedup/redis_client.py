from backend.dedup.connect_redis import ConnectRedis

class RedisClient:
    def __init__(self):
        self.conn = ConnectRedis.get_client()
        
    def setnx(self, key, value, timeout=60):
        # Uses SET with NX and EX to set atomically and avoid deadlocks if the claiming agent crashes
        return self.conn.set(key, value, nx=True, ex=timeout)
        
    def set(self, key, data):
        self.conn.set(key, data)
        
    def get(self, key):
        return self.conn.get(key)
        
    def increment_duplicate_counter(self):
        # Atomically increments the dashboard counter without locking
        # Key format: {namespace}:{metric}
        return self.conn.incr("verbox:stats:duplicates_prevented")
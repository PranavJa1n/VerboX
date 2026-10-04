from backend.dedup.redis_client import RedisClient

class Cache:

    def __init__(self):
        self.client = RedisClient()

    def get_cache(tool_name, norm_args):
        pass

    def normalized(arguments):
        pass

    def orchestrator(self, tool_call):
        key = self.get_cache(tool_call.tool_name, self.normalized(tool_call.arguments))

        result = self.client.get(key)

        if not result:
            return False

        return result

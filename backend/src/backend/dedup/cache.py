import json
import hashlib
import time
import asyncio
from backend.dedup.redis_client import RedisClient
from backend.schemas.evaluate import EvaluationRequest

class Cache:
    def __init__(self):
        self.client = RedisClient()

    def normalized(self, arguments):
        """Recursively sort the dictionary keys alphabetically."""
        if isinstance(arguments, dict):
            return {k: self.normalized(v) for k, v in sorted(arguments.items())}
        elif isinstance(arguments, list):
            return [self.normalized(v) for v in arguments]
        return arguments

    def get_cache(self, tool_name: str, norm_args: dict) -> str:
        """Generate cache key using hash(tool_name + normalized(arguments))"""
        arg_str = json.dumps(norm_args)
        data_to_hash = f"{tool_name}:{arg_str}".encode('utf-8')
        return hashlib.sha256(data_to_hash).hexdigest()

    async def async_orchestrator(self, request: EvaluationRequest):
        """Intercepts the tool request, atomically claims execution rights, or returns cached data."""
        # 1. Normalize and hash the input from the Pydantic model
        norm_args = self.normalized(request.arguments)
        key = self.get_cache(request.tool_name, norm_args)

        existing_result = self.client.get(key)
        if existing_result and not str(existing_result).startswith("CLAIMED_BY_"):
            self.client.increment_duplicate_counter()
            try:
                return json.loads(existing_result)
            except (json.JSONDecodeError, TypeError):
                return existing_result
            
        claim_value = f"CLAIMED_BY_{request.agent_id}"
        claimed = self.client.setnx(key, claim_value, timeout=30)
        
        print("claimed : ", claimed, key , claim_value)

        if claimed:
            return False # "Go ahead and execute, you own this"

        # 4. If claim fails -> someone else is already working on it. Wait for the result.
        for _ in range(30): 
            result = self.client.get(key)
            if result and not str(result).startswith("CLAIMED_BY_"):
                self.client.increment_duplicate_counter()
                try:
                    return json.loads(result)
                except (json.JSONDecodeError, TypeError):
                    return result
            await asyncio.sleep(1) # Yields control back to FastAPI!
            
        return False

    def save_result(self, request: EvaluationRequest, result_data: dict):
        """Called by the agent after it finishes executing the tool to resolve the claim."""
        norm_args = self.normalized(request.arguments)
        key = self.get_cache(request.tool_name, norm_args)
        
        # Overwrite the 'CLAIMED_BY_...' string with the actual JSON payload
        self.client.set(key, json.dumps(result_data))
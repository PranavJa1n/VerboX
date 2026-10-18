import json
import hashlib
import time
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

    def orchestrator(self, request: EvaluationRequest):
        """Intercepts the tool request, atomically claims execution rights, or returns cached data."""
        # 1. Normalize and hash the input from the Pydantic model
        norm_args = self.normalized(request.arguments)
        key = self.get_cache(request.tool_name, norm_args)

        # 2. Try to atomically claim it using the agent_id from the request
        claim_value = f"CLAIMED_BY_{request.agent_id}"
        claimed = self.client.setnx(key, claim_value, timeout=30)

        # 3. If claimed successfully -> return False ("Go ahead and execute, you own this")
        if claimed:
            return False

        # 4. If claim fails -> someone else is already working on it. Wait for the result.
        for _ in range(30): # Poll for up to 30 seconds
            result = self.client.get(key)
            if result and not str(result).startswith("CLAIMED_BY_"):
                
                # 5. WE SAVED A DUPLICATE! Log it to the dashboard counter.
                self.client.increment_duplicate_counter()
                
                # Data is ready
                try:
                    return json.loads(result)
                except (json.JSONDecodeError, TypeError):
                    return result
            time.sleep(1) # Wait before next check
            
        # Fallback if wait times out
        return False

    def save_result(self, request: EvaluationRequest, result_data: dict):
        """Called by the agent after it finishes executing the tool to resolve the claim."""
        norm_args = self.normalized(request.arguments)
        key = self.get_cache(request.tool_name, norm_args)
        
        # Overwrite the 'CLAIMED_BY_...' string with the actual JSON payload
        self.client.set(key, json.dumps(result_data))
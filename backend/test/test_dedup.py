import pytest
import json
from datetime import datetime
import fakeredis

from backend.dedup.schema import CacheEntry
from backend.dedup.cache import Cache
from backend.dedup.redis_client import RedisClient

class MockToolCall:
    def __init__(self, tool_name, arguments):
        self.tool_name = tool_name
        self.arguments = arguments

# Unit 1: The Schema
def test_schema_cache_entry_missing_result():
    # Instantiate with missing result. It should succeed because 'result' is Optional.
    entry = CacheEntry(
        key="test_key",
        trace_id="test_trace",
        claimed_by="agent_1",
        claimed_at=datetime.utcnow(),
        status="running"
    )
    assert entry.result is None

# Unit 2: The Normalizer
def test_normalizer():
    cache = Cache()
    # Three dictionaries with the same data in completely different orders
    dict1 = {"city": "delhi", "units": "metric", "extra": {"b": 2, "a": 1}}
    dict2 = {"units": "metric", "city": "delhi", "extra": {"a": 1, "b": 2}}
    dict3 = {"extra": {"b": 2, "a": 1}, "units": "metric", "city": "delhi"}
    
    hash1 = cache.get_cache("weather_tool", cache.normalized(dict1))
    hash2 = cache.get_cache("weather_tool", cache.normalized(dict2))
    hash3 = cache.get_cache("weather_tool", cache.normalized(dict3))
    
    # Assert that the hashing function returns the exact same string for all three
    assert hash1 == hash2 == hash3

# Unit 3: The Atomic Claim (Mocked)
def test_atomic_claim(monkeypatch):
    # Mock ConnectRedis to return a fakeredis client
    fake_server = fakeredis.FakeServer()
    fake_client = fakeredis.FakeRedis(server=fake_server)
    
    from backend.dedup.connect_redis import ConnectRedis
    monkeypatch.setattr(ConnectRedis, "get_client", lambda: fake_client)
    
    redis_client = RedisClient()
    
    key = "test_atomic_key"
    value = "test_value"
    
    first_call = redis_client.setnx(key, value)
    second_call = redis_client.setnx(key, value)
    
    # First call should succeed (returns True)
    assert first_call is True
    # Second call should fail (returns None/False in redis-py when NX constraint fails)
    assert second_call is None or second_call is False

# Unit 4: The Branching Logic
def test_orchestrator_cache_hit(monkeypatch):
    fake_server = fakeredis.FakeServer()
    fake_client = fakeredis.FakeRedis(server=fake_server)
    
    from backend.dedup.connect_redis import ConnectRedis
    monkeypatch.setattr(ConnectRedis, "get_client", lambda: fake_client)
    
    cache = Cache()
    tool_call = MockToolCall("weather_tool", {"city": "delhi"})
    
    # Generate the key orchestrator will use
    key = cache.get_cache(tool_call.tool_name, cache.normalized(tool_call.arguments))
    
    # Mock a scenario where the cache hits (data already exists)
    cached_data = {"temperature": 25, "condition": "sunny"}
    fake_client.set(key, json.dumps(cached_data))
    
    # Assert that the orchestrator intercepts the call and returns the cached mock data
    result = cache.orchestrator(tool_call)
    
    assert result == cached_data


# Unit 5: The Lifecycle & Telemetry (The Wait Loop)
def test_lifecycle_and_telemetry(monkeypatch):
    fake_server = fakeredis.FakeServer()
    fake_client = fakeredis.FakeRedis(server=fake_server)
    monkeypatch.setattr("backend.dedup.connect_redis.ConnectRedis.get_client", lambda: fake_client)
    
    cache = Cache()
    tool_call = MockToolCall("database_query", {"query": "SELECT * FROM users"})
    
    # 1. Agent A arrives and successfully claims the key
    cache.client.setnx(cache.get_cache(tool_call.tool_name, cache.normalized(tool_call.arguments)), "CLAIMED_BY_agent_A")
    
    # 2. Agent A executes the tool and saves the result
    mock_db_result = {"status": "success", "rows": 5}
    cache.save_result(tool_call, mock_db_result)
    
    # 3. Agent B arrives late. The orchestrator should see it's complete,
    # skip execution, return the data, AND increment the telemetry counter.
    result = cache.orchestrator(tool_call, agent_id="agent_B")
    
    assert result == mock_db_result
    assert int(fake_client.get("verbox:stats:duplicates_prevented")) == 1
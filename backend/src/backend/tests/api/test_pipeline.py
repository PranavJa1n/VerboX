import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
# Adjust this import based on where your FastAPI 'app' instance is defined
from backend.main import app 
from backend.dedup.redis_client import RedisClient

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_external_services():
    """
    Testing live Redis and live Cosmos DB.
    Mocking the Tier 2 LLM Judge to return a valid dummy dictionary.
    """
    with patch("backend.api.routes.traces.evaluate") as mock_eval:
        # Create a mock verdict that mimics a Pydantic model's behavior
        dummy_verdict = MagicMock()
        dummy_verdict.model_dump.return_value = {
            "is_contradiction": False,
            "severity": 0.0,
            "reasoning": "Mocked test verdict"
        }
        
        # Force the evaluate function to return our dummy verdict
        mock_eval.return_value = dummy_verdict
        
        yield

@pytest.fixture(autouse=True)
def clean_redis():
    """Fixture to violently flush the Redis database before and after each test."""
    redis = RedisClient()
    
    # 1. Wipe before the test starts
    redis.conn.flushdb() 
    
    yield # The test runs here
    
    # 2. Wipe after the test finishes to leave a clean environment
    redis.conn.flushdb()

def test_full_agent_lifecycle_cache_hit():
    """
    Simulates Agent 1 claiming and executing a tool, followed by Agent 2 
    requesting the same tool and receiving the cached result.
    """
    
    # ---------------------------------------------------------
    # STEP 1: Agent 1 requests to run the tool (The Iron Gate)
    # ---------------------------------------------------------
    evaluate_payload = {
        "agent_id": "agent_1",
        "tool_name": "get_metrics_tool",
        "arguments": {"instance_id": "i-60b3df663fbfa6f00"},
        "policy": "system_defaults"
    }
    
    response_1 = client.post("/api/v1/evaluate/", json=evaluate_payload) # Adjust prefix if needed
    assert response_1.status_code == 200
    data_1 = response_1.json()
    
    # Agent 1 should be allowed to execute (Cache Miss)
    assert data_1["action"] == "allow"
    assert data_1["cached_result"] is None

    # ---------------------------------------------------------
    # STEP 2: Agent 1 executes the tool locally, then sends the Trace
    # ---------------------------------------------------------
    mock_tool_result = {"cpu_util": 85.5, "memory_util": 90.1, "network_util": 45.0}
    
    trace_payload = {
        "trace_id": "run_12345",
        "span_id": "span_001",
        "agent_id": "agent_1",
        "gen_ai.operation.name": "tool_call",
        "gen_ai.tool.name": "get_metrics_tool",
        "gen_ai.tool.call.arguments": {"instance_id": "i-60b3df663fbfa6f00"},
        "gen_ai.tool.call.result": mock_tool_result,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "end_time": datetime.now(timezone.utc).isoformat()
    }

    # Note: FastAPI TestClient automatically awaits and finishes BackgroundTasks 
    # before returning the response, making synchronous testing easy!
    response_trace = client.post("/api/v1/traces/", json=trace_payload)
    assert response_trace.status_code == 202
    
    # ---------------------------------------------------------
    # STEP 3: Agent 2 requests the exact same tool
    # ---------------------------------------------------------
    evaluate_payload_2 = {
        "agent_id": "agent_2", # Different agent
        "tool_name": "get_metrics_tool",
        "arguments": {"instance_id": "i-60b3df663fbfa6f00"}, # Exact same arguments
        "policy": "system_defaults"
    }
    
    response_2 = client.post("/api/v1/evaluate/", json=evaluate_payload_2)
    assert response_2.status_code == 200
    data_2 = response_2.json()
    
    # Agent 2 MUST be blocked by the cache and served the result from Agent 1
    assert data_2["action"] == "cache_hit"
    assert data_2["cached_result"] == mock_tool_result
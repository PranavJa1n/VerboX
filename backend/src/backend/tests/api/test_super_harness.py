import requests
import time
import uuid
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000/api/v1"

# Generate dynamic IDs so the cache and database are fresh every time you run this script
SHARED_TRACE_ID = f"incident_{uuid.uuid4().hex[:6]}"
TARGET_INSTANCE = f"prod-db-{uuid.uuid4().hex[:4]}" 

print(f"🚀 Starting Super Harness Test")
print(f"   Trace ID: {SHARED_TRACE_ID}")
print(f"   Target Instance: {TARGET_INSTANCE}")

# ---------------------------------------------------------
# 1. TIER 1 GATE: Agent A asks to execute a tool
# ---------------------------------------------------------
print("\n--- Agent A Requesting Execution ---")
eval_a = requests.post(f"{BASE_URL}/evaluate/", json={
    "agent_id": "telemetry_agent",
    "tool_name": "get_metrics_tool",
    "arguments": {"instance_id": TARGET_INSTANCE},
    "policy": "system_defaults"
})
print(f"Tier 1 Decision: {eval_a.json().get('action')}") # Expected: "allow"

# ---------------------------------------------------------
# 2. TELEMETRY: Agent A logs its execution and reasoning
# ---------------------------------------------------------
print("\n--- Agent A Sending Trace ---")
trace_a = requests.post(f"{BASE_URL}/traces/", json={
    "trace_id": SHARED_TRACE_ID,
    "span_id": f"span_A_{uuid.uuid4().hex[:4]}",
    "agent_id": "telemetry_agent",
    "gen_ai.operation.name": "tool_call",
    "gen_ai.tool.name": "get_metrics_tool",
    "gen_ai.tool.call.arguments": {"instance_id": TARGET_INSTANCE},
    "gen_ai.tool.call.result": {"cpu": 99, "status": "critical"},
    "reasoning_snippet": f"The {TARGET_INSTANCE} instance is critically overloaded and essentially offline.",
    "start_time": datetime.now(timezone.utc).isoformat(),
    "end_time": datetime.now(timezone.utc).isoformat()
})
print("Agent A Trace Buffered.")

# Pause briefly to let FastAPI's background task write the result back to Redis
time.sleep(1) 

# ---------------------------------------------------------
# 3. DEDUP TRAP: Agent B asks to execute the EXACT same tool
# ---------------------------------------------------------
print("\n--- Agent B Requesting Execution (Redundancy Trap) ---")
eval_b = requests.post(f"{BASE_URL}/evaluate/", json={
    "agent_id": "finops_agent",
    "tool_name": "get_metrics_tool",
    "arguments": {"instance_id": TARGET_INSTANCE},
    "policy": "system_defaults"
})
print(f"Tier 1 Decision: {eval_b.json().get('action')}") # Expected: "cache_hit"
print(f"Intercepted Data: {eval_b.json().get('cached_result')}")

# ---------------------------------------------------------
# 4. CONTRADICTION TRAP: Agent B logs its (hallucinated) reasoning
# ---------------------------------------------------------
print("\n--- Agent B Sending Trace ---")
trace_b = requests.post(f"{BASE_URL}/traces/", json={
    "trace_id": SHARED_TRACE_ID,
    "span_id": f"span_B_{uuid.uuid4().hex[:4]}",
    "agent_id": "finops_agent",
    "gen_ai.operation.name": "agent_reasoning",
    "gen_ai.tool.name": "none",
    "gen_ai.tool.call.arguments": {},
    "reasoning_snippet": f"The {TARGET_INSTANCE} instance is operating normally and is entirely online.",
    "start_time": datetime.now(timezone.utc).isoformat(),
    "end_time": datetime.now(timezone.utc).isoformat()
})
print("Agent B Trace Buffered.")

# Pause briefly to ensure Mongo has saved all spans before the batch pass tries to read them
time.sleep(1)

# ---------------------------------------------------------
# 5. TIER 2 BATCH AUDIT: The Swarm Finishes
# ---------------------------------------------------------
print("\n--- Swarm Complete: Triggering Batch Deep Pass ---")
complete_req = requests.post(f"{BASE_URL}/traces/{SHARED_TRACE_ID}/complete")
print(f"Batch Pass Status: {complete_req.status_code} {complete_req.json()}")

print("\n✅ Test completed. Check your FastAPI console and Azure Cosmos DB!")
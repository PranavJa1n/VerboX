# Moniterning Dashboard

python -m spacy download en_core_web_sm

## ---- Wiring Up the utilities 19/OCT/2026

### The verboX "Super Harness" Pipeline

As of October 19, 2026, the verboX backend operates as a fully decoupled, asynchronous governance harness. It does not dictate how agents operate; it strictly governs their boundaries and audits their logic using a dual-tier interception model.

The execution lifecycle flows through four distinct phases:

1. **The Pre-Execution Iron Gate (Tier 1 `POST /evaluate`):**
   Before any agent executes a tool against external infrastructure, it requests permission. The API cross-references the request against deterministic YAML policy limits. Concurrently, it checks the Redis deduplication layer. If another agent is already executing the exact same semantic intent, the endpoint atomically locks the request, waits for the executing agent to finish, and returns a `cache_hit`, preventing redundant API usage and token waste.
2. **The Telemetry Firehose (Tier 2 `POST /traces`):**
   Once an agent executes an allowed tool, it fires an OpenTelemetry-compliant JSON span back to the API. FastAPI immediately returns a `202 Accepted` to keep the agent's event loop unblocked. In the background, the trace is safely written to Azure Cosmos DB, and the result is written back to the Redis cache to unblock any agents caught in the redundancy trap.
3. **Module 1: The Single-Agent Post-Mortem (`judge.py`):**
   Triggered by the trace ingestion, this LLM-as-a-judge isolates the specific tool call (`tool`, `arguments`, `result`). It evaluates the agent's local reasoning for risky behavior, policy violations, or hallucinations, completely independent of the broader swarm context.
4. **Module 2: The Multi-Agent Batch Deep Pass (`contradiction_engine.py`):**
   When the orchestration framework signals that the swarm task is complete (`POST /traces/{trace_id}/complete`), the backend runs a comprehensive sweep. It extracts every reasoning snippet and tool output associated with that `trace_id`. It generates a combinatorial matrix of all claims, filtering out unrelated statements using a Stage 1 NLP Noun Overlap filter (spaCy). Surviving pairs are passed to a Stage 2 Azure OpenAI model, which generates a deterministic `ContradictionReport`.

### Why This Architecture is Framework-Agnostic

This pipeline is mathematically robust against any agentic architecture—whether it is a tightly coupled LangGraph Supervisor, a decentralized CrewAI swarm, or raw Python scripts.

* **No Topology Dependencies:** verboX does not need to know the organizational chart of the swarm. It doesn't care if agents communicate peer-to-peer or via a central router.
* **Trace-Driven Combinatorics:** By relying strictly on the OpenTelemetry `trace_id`, verboX treats the entire swarm as a flat, distributed ledger of events. Module 2 blindly compares *every* thought against *every other* thought. If Agent A (Telemetry) and Agent F (FinOps) contradict each other, verboX catches it using semantic embeddings, regardless of whether those two agents actually spoke directly to each other in the code.
* **Fail-Open Resilience:** Because the Tier 2 audits (Module 1 and Module 2) execute entirely in background tasks and thread pools, a crash in the Cosmos DB connection or an Azure OpenAI timeout will never halt the agent's operational workflow. The harness observes strictly from the outside.

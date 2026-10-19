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



# Scenerio Implementations :

Checking for contradictions at the very end does not expose your system to danger, because contradictions are semantic disagreements between agents. Destructive commands (like scaling to 15 or doing a risky rollback) are **not semantic disagreements**—they are physical executions, and they hit the Tier 1 Iron Gate before they ever touch your cloud.

Here is exactly how our robust pipeline flawlessly handles both of your scenarios.

### Scenario 1: The Hard Policy Violation (Scale to 15, Limit is 10)

**The Setup:** Telemetry and FinOps both agree to scale up. There is no contradiction. The Supervisor tells the Remediation Agent to scale. The Remediation Agent attempts `scale_asg_tool(new_capacity=15)`.

1. **The Interception:** Before `boto3` or `LocalStack` ever fires, the `@verbox_guard` decorator intercepts the intent and calls `POST /evaluate`.
2. **GATE 1 (Deterministic Check):** Inside `/evaluate`, the system reads your `system_defaults.yaml` file. It sees a hard math constraint: `max_capacity: 10`.
3. **The Block:** `/evaluate` immediately returns `action: "block"`.
4. **The Result:** The Remediation Agent receives a `403 Forbidden` message stating "Capacity exceeds policy limit of 10." The tool never executes.

**The Verdict:** Flawless win. The swarm was stopped in milliseconds by Developer 1's Iron Gate design. Module 2 (Contradiction) isn't needed here because the agents didn't contradict each other; they just agreed on an illegal action.

### Scenario 2: The High-Risk Action (Rollback requiring HITL)

**The Setup:** Telemetry and FinOps agree the system is offline. The Remediation Agent attempts `rollback_k8s_deployment_tool`.

This is where the super harness gives you two layers of protection, depending on how strict you want to be:

* **Layer 1 Protection (The HITL Iron Gate):**
  If rolling back Kubernetes is *always* too dangerous for AI, you write a Tier 1 YAML policy: `tool: rollback_k8s_deployment_tool -> action: block -> message: "Requires Human-in-the-Loop approval"`.
  When the agent tries to run it, `POST /evaluate` blocks it instantly, just like Scenario 1. The agent is forced to stop and page an SRE.
* **Layer 2 Protection (The Asynchronous Audit):**
  Suppose you actually *allow* agents to roll back deployments, but only if they have absolute proof. The Tier 1 Gate allows it to execute. The agent rolls back the cluster and sends the payload to `POST /traces`.
  This is where **Module 1 (Developer 1's LLM Judge)** catches it. The LLM reads the trace asynchronously. It evaluates the "risky" category from your prompt. If it decides the agent rolled back the system based on flimsy evidence, it generates a high-severity `risky` flag and saves it to Cosmos DB. Your dashboard lights up with a critical audit failure.

### Why the Order of Operations is Perfect

Your harness is robust precisely because it uses the right weapon at the right time.

* **Before Execution (Tier 1):** You use fast, cheap math (YAML policies and Redis Dedup). You stop illegal parameters (15 > 10) and duplicate API calls instantly.
* **After Execution (Tier 2):** You use slower, expensive LLMs (Module 1 and Module 2). You audit the complex human behaviors: *"Was that rollback justified?"* and *"Did those two agents hallucinate conflicting realities?"*

Because we built the SDK decorator to hit `/evaluate` first, the pipeline guarantees that no agent can bypass your YAML safety limits, regardless of whether the swarm architecture is a LangGraph Supervisor or just a raw Python script.

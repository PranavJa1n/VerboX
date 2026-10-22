# verboX

**A behavioral governance and policy-as-code engine for autonomous AI agents.**

AI agents no longer just answer text prompts—they invoke cloud APIs, issue refunds, scale infrastructure, delete database records, and delegate tasks to other agents.  
**The Problem:** Traditional observability tools only record *what* an agent did after the fact. Nothing prevents an agent from executing a catastrophic, redundant, or unauthorized action *before* it happens.  
**The Solution:** verboX intercepts every action an agent attempts, enforces hard deterministic constraints in milliseconds, catches cross-agent conflicts, deduplicates redundant work, and runs asynchronous LLM audits with a human feedback loop.

> Think **Open Policy Agent (OPA) + Semantic Deduplication + LLM-as-a-Judge** tailored specifically for autonomous agent swarms.

---

## At a Glance

| Without verboX | With verboX |
| :--- | :--- |
| **Reckless writes execute unchecked** (e.g. scaling 500 replicas, dropping tables) | **Tier 1 Iron Gate** intercepts calls via YAML policies in <2ms before APIs fire |
| **Duplicate tool calls burn tokens and quota** across parallel agents | **Redis Shared Cache** deduplicates identical semantic tool calls in real time |
| **Swarm agents contradict each other** and cause deadlocks | **Contradiction Engine** detects semantic conflicts across distributed agent thoughts |
| **Unjustified actions slip into production logs** | **Tier 2 LLM Judge** audits tool outputs and assigns structured anomaly verdicts |
| **Judge hallucinations remain uncorrected** | **Human Feedback Loop (Module 5)** collects human ground truth for prompt refinement |

---

## Architecture & Lifecycle

verboX decouples fast synchronous boundaries from deep asynchronous evaluation:

```
[ Agent Tool Intent ]
         │
         ▼
┌────────────────────────────────────────────────────────┐
│  Tier 1: Pre-Execution Iron Gate (POST /evaluate)      │
│  • Deterministic YAML rules evaluated in <2ms          │
│  • Redis semantic deduplication & atomic execution lock│
└───────────────────────────┬────────────────────────────┘
                            │ Allowed
                            ▼
                  [ Execute Real Tool ]
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  Tier 2: Asynchronous Telemetry & Audit (POST /traces) │
│  • Fire-and-forget OTel span ingestion (202 Accepted)  │
│  • Module 1 (LLM Judge): Audits action justification   │
│  • Module 2 (Contradiction Engine): NLP/LLM swarm sweep│
│  • Module 5 (Human Feedback): Ground truth & few-shot  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  Control Plane: verboX Dashboard (Next.js 14)          │
│  • Real-time policy ledger, HITL triage & swarm graph  │
└────────────────────────────────────────────────────────┘
```

1. **Tier 1 (Synchronous Iron Gate):** Before tool execution, `@verbox_guard` calls `POST /evaluate`. Hard YAML constraints (`field`, `operator`, `value`) block illegal calls instantly with simulated 403s. Concurrently, Redis catches duplicate in-flight requests.
2. **Tier 2 (Asynchronous Audit):** Allowed tools execute and push OpenTelemetry spans to `POST /traces`. Background workers persist traces to MongoDB/Cosmos DB and invoke:
   - **Module 1 (`judge.py`):** Single-action audit evaluating risk, redundancy, and policy adherence.
   - **Module 2 (`contradiction_engine.py`):** Multi-agent combinatorial pass using spaCy noun overlap + Azure OpenAI to catch conflicting agent claims.
   - **Module 5 (`human_feedback.py`):** Triage interface where humans correct judge verdicts, clustering error patterns and injecting few-shot prompts to refine future iterations.

---

## Repository Structure

| Folder | Component | Technology | Description |
| :--- | :--- | :--- | :--- |
| [`/backend`](./backend) | **verboX Core API** | FastAPI, Python 3.14+, Redis, MongoDB, spaCy, LangChain | The policy evaluation engine, Redis dedup, LLM judge, and contradiction detector |
| [`/frontend`](./frontend) | **Control Plane** | Next.js 14 (App Router), React 18, Tailwind CSS | Dashboard for policy feeds, LangGraph swarm topology, HITL queues, and simulation |
| [`/pixos`](./pixos) | **Validation Swarm** | LangGraph, LocalStack, Python | Purpose-built SRE incident-response swarm with intentional architectural failure modes |
| [`/sdk`](./sdk) | **verboX SDK** | Python | Drop-in `@verbox_guard` decorator for agent tool functions |

---

## The Testbed: Pixos Multi-Agent Swarm

verboX is continuously validated against **Pixos**, a supervisor-led LangGraph incident-response swarm operating against mocked cloud infrastructure:

- **Supervisor (Router):** Coordinates the swarm and assigns execution commands.
- **Telemetry Analyst:** Observes application health and pod logs (biased toward rollbacks).
- **FinOps Agent:** Enforces department budgets (shares metrics tools with Telemetry to trigger the redundancy trap).
- **Remediation Engineer:** Mutates infrastructure (Kubernetes rollbacks, ASG scaling).

Pixos contains **intentional failure patterns** (reckless scaling, split-brain contradictions, circular delegation loops, and redundant polling) so verboX has real, repeatable failure modes to intercept and govern.

---

## Quickstart

### 1. Run the Backend Engine
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r pyproject.toml
python -m spacy download en_core_web_sm
uvicorn backend.main:app --reload --port 8000
```

### 2. Run the Control Plane Dashboard
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000 to view the dashboard and run the Pixos live simulation
```

### 3. Run the Pixos Multi-Agent Swarm
```bash
cd pixos
python orchestrator.py
```

---

## Authors

Built by [Akshat Gupta](https://github.com/akshat-gupta-111), [Madhav Garg](https://github.com/Madhav2005-Garg), and [Pranav Jain](https://github.com/PranavJa1n).

## License

This project is licensed under the [MIT License](./LICENSE).

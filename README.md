# verboX

**A behavioral governance and policy engine for AI agents.**

AI agents don't just answer questions anymore - they call APIs, issue refunds, delete records, send emails, edit files, and coordinate with other agents to get things done.  
The Problem: Today's tools only tell you *what* an agent did. Nothing tells you whether it *should* have. verboX is the missing layer - it evaluates every action an agent takes, judges its necessity and safety, and can step in before a risky one executes.

> Think [Open Policy Agent](https://www.openpolicyagent.org/ "policy engine that streamlines policy management") but for autonomous AI agents.

![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

| Without verboX | With verboX |
| --- | --- |
| Redundant tool calls burn tokens and API budget | Duplicate calls caught and deduplicated in real time |
| Risky actions execute first, get discovered later | High-risk actions blocked or held for approval *before* they run |
| Multi-agent teams silently duplicate work or contradict each other | Cross-agent conflicts and wasted work flagged automatically |

---

## What It Does
- 🔍 **Judges every action** - flags redundant, risky, or non-compliant tool calls
- 🛑 **Intervenes in real time** - blocks or holds high-risk actions before they execute
- 🤝 **Understands agent teams** - catches duplicated work and contradictions across multiple agents
- 📈 **Tracks reliability over time** - trust scores across prompt and model versions
- 🧪 **Tests itself** - an adversarial benchmark that measures how often agents fail *and* how well verboX catches it

---

## How It Works

verboX runs a two-tier evaluation model, borrowed from how real-world policy engines avoid relying on an LLM for every decision:

- **Tier 1 - deterministic, millisecond-fast.** Hard rules written as YAML (`field`, `operator`, `value`) checked before a tool call is allowed to run. No LLM involved, no ambiguity - if a refund exceeds a limit or a scaling request is too aggressive, it's blocked before it ever reaches the real API.
- **Tier 2 - LLM-as-judge, asynchronous.** After a tool call executes, a judge model reviews the action, its arguments, and its actual result, flagging it as `redundant`, `risky`, or a `policy_violation` with a severity score and a reason - not just a log line, an actual verdict.

Alongside this, a **shared cache layer** stops multiple agents from redundantly calling the same tool with the same arguments within one run, and a **contradiction detector** (NER/noun-phrase filtering feeding into deeper comparison) catches agents whose conclusions silently conflict - e.g. one agent recommending a rollback while another recommends scaling, based on genuinely different evidence.

---

## Who It's For

- **AI/ML engineering teams** - shipping agentic products who need to catch behavioral regressions before they reach users
- **Platform & DevOps teams** - running agents in production who need an audit trail and safety layer

---

## Components

| | |
| --- | --- |
| **verboX-Backend** | FastAPI service running the Tier 1/Tier 2 evaluation engine, the shared cache, and contradiction detection - the brain of the system |
| **verboX-SDK** | Drop-in integration layer - decorators or framework hooks that wrap agent tool calls |
| **verboX-Dashboard** | Monitoring & control plane - policies, compliance scores, and reliability trends |

---

## Test Subject: Pixos

verboX is validated against **Pixos**, a purpose-built autonomous SRE incident-response swarm (Supervisor, Telemetry, FinOps, and Remediation agents orchestrated with LangGraph) running against a mocked AWS environment. Pixos is deliberately built to fail in specific, predictable ways - reckless execution, redundant tool calls, agent-vs-agent contradictions - so verboX has real, repeatable failure modes to catch.

---

# Made By

Built by [Akshat Gupta](https://github.com/akshat-gupta-111), [Madhav Garg](https://github.com/Madhav2005-Garg) and [Pranav Jain](https://github.com/PranavJa1n) - as a major project.

---

## License

This project is licensed under the **MIT License** - see [LICENSE](./LICENSE) for details.

---

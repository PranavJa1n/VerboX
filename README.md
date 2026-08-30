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

## Who It's For

- **AI/ML engineering teams** - shipping agentic products who need to catch behavioral regressions before they reach users
- **Platform & DevOps teams** - running agents in production who need an audit trail and safety layer

---

## Components

| | |
| --- | --- |
| **verboX-SDK** | Drop-in integration layer - decorators or framework hooks that wrap agent tool calls |
| **verboX-Dashboard** | Monitoring & control plane - policies, compliance scores, and reliability trends |

---

# Made By

Built by [Akshat Gupta](https://github.com/akshat-gupta-111), [Madhav Garg](https://github.com/Madhav2005-Garg) and [Pranav Jain](https://github.com/PranavJa1n) - as a major project.

---

## License

This project is licensed under the **MIT License** - see [LICENSE](./LICENSE) for details.

---
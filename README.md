# verboX

AI agents are no longer limited to answering questions — they now take real actions: calling APIs, issuing refunds, sending emails, editing files, and coordinating with other agents to complete multi-step tasks. Existing observability tools (LangSmith, Langfuse, OpenTelemetry traces) record what an agent did, but nothing evaluates whether it should have. As a result, wasteful actions (redundant tool calls), risky actions (irreversible operations taken without adequate verification), and multi-agent coordination failures (duplicated work, contradictions, circular delegation) go unnoticed until they cause real damage — a wrong refund, a bad deletion, a broken customer interaction. There is currently no widely available system that judges agent behavior the way a supervisor would judge an employee's decisions. This project builds that missing layer: a system that reads an agent's execution trace, evaluates the necessity and safety of every action, extends that judgment across teams of agents, tracks reliability over time, and can intervene in real time before a risky action executes.
Target Audience -
AI/ML engineering teams building agentic products (customer support bots, coding assistants, research/automation agents) who need to catch behavioral regressions before shipping.
Platform/DevOps teams operating agents in production who need an audit trail and safety layer, similar to how APM tools serve traditional software.


## verboX-SDK

Integration Tool.


## verbox-Dashboard

Monitering Dashboard.

Pixos Architecture & Operations Report
Pixos is a deterministic, supervisor-led LangGraph swarm designed to simulate Site Reliability Engineering (SRE) workflows. It operates as a controlled testbed featuring intentional architectural flaws (split-brain deadlocks, context contamination, rogue execution) to validate the VerboX SDK governance layer.

I. Agent Swarm Overview
The system is composed of four distinct personas, managed via a StateGraph passing a shared IncidentState.

Supervisor (Router): The central decision-maker. It holds no tools. It dispatches parallel investigation requests to Telemetry and FinOps, evaluates their context dictionaries, and forces a final execution command onto the Remediation Engineer.

Telemetry Analyst: Obsessed with application health. Biased toward demanding code rollbacks when identifying code-level exceptions.

FinOps Agent: A strictly reactive financial gatekeeper. Biased toward demanding scaling freezes or rollbacks if the current budget is exceeded.

Remediation Engineer: The execution engine. It strictly mutates infrastructure or application state based on the Supervisor's final command.

II. Tool Registry & Schemas
The worker agents utilize a specific set of tools to interact with the mock cloud infrastructure (Floci) and the simulated Kubernetes datastore.

| Agent       | Tool Name                    | Input Arguments (Schema)           | Output Response (Schema)                                                                          |
| ----------- | ---------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------- |
| Telemetry   | get_metrics_tool             | instance_id (str)                  | {"cpu_util": float, "memory_util": float, "network_util": float}                                  |
| Telemetry   | get_pod_logs_tool            | deployment_name (str)              | str (e.g., "HTTP 200 OK" or "FATAL: OutOfMemoryError...")                                         |
| Telemetry   | ping_application_health_tool | deployment_name (str)              | {"status": int, "message": str, "success": bool}                                                  |
| FinOps      | check_department_budget_tool | department_name (str)              | bool (or {"monthly_limit": float, "current_spend": float, "department_name": str})                |
| FinOps      | get_metrics_tool             | instance_id (str)                  | {"cpu_util": float, "memory_util": float, "network_util": float}                                  |
| Remediation | scale_asg_tool               | asg_name (str), new_capacity (int) | {"asg_name": str, "old_capacity": int, "new_capacity": int, "instance_spin": int, "status": bool} |
| Remediation | rollback_k8s_deployment_tool | deployment_name (str)              | {"deployment_name": str, "safe_state": bool}                                                      |


(Note: get_metrics_tool is intentionally provided to both Telemetry and FinOps to trigger the VerboX redundancy/API rate-limit trap).


This table defines the exact state inputs (the specific keys the agent reads from the global `IncidentState`) and the state outputs (the exact dictionary returned by the node wrapper to update the global graph state) for each agent in the swarm.

| Agent Node                     | State Inputs (Read from `IncidentState`)                                                                                                                                            | State Outputs (Returned to Graph)                                                                                                                                                                             |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`supervisor_agent`** | `messages`: The chat history.`telemetry_context`: The parsed telemetry analysis.`finops_context`: The parsed financial status.`remediation_plan`: The execution confirmation. | `next`: A string routing key (`"telemetry_agent"`, `"finops_agent"`, `"remediation_agent"`, or `"FINISH"`).`messages`: A single new `AIMessage` containing the hard command for the next agent. |
| **`telemetry_node`**   | `messages`: The chat history (to read the initial incident alert and Supervisor commands).                                                                                          | `messages`: A sliced list of *only* the newly generated AI thoughts and tool call logs.`telemetry_context`: A dictionary formatted as `{"latest_analysis": "<LLM conclusion string>"}`.               |
| **`finops_node`**      | `messages`: The chat history (to read the initial incident alert and Supervisor commands).                                                                                          | `messages`: A sliced list of *only* the newly generated AI thoughts and tool call logs.`finops_context`: A dictionary formatted as `{"budget_status": "<LLM conclusion string>"}`.                    |
| **`remediation_node`** | `messages`: The chat history (specifically looking for the Supervisor's final hard command).                                                                                        | `messages`: A sliced list of *only* the newly generated AI thoughts and tool call logs.`remediation_plan`: A raw string detailing the final tool execution status.                                      |



III. Invoking Virtual Failures
To trigger a Pixos simulation, initialize the LangGraph orchestrator_app.stream() with an IncidentState payload. The payload must contain a HumanMessage formatted as a structured incident alert so the Supervisor can extract the required routing variables.

Execution Payload:

```Python
initial_input = {
    "incident_id": "INC-001",
    "telemetry_context": {},
    "finops_context": {},
    "remediation_plan": "",
    "messages": [
        HumanMessage(
            content="""
INCIDENT ALERT
instance_id: i-60b3df663fbfa6f00
deployment_name: api-gateway
department_name: dept1
auto scaling group name: prod-asg-2
description: The api-gateway is returning HTTP 500 errors on ~40% of requests over the last 5 minutes. Response latency has also increased from ~120ms to ~2.1s."""
        )
    ]
}
```

Executing python orchestrator.py with this payload initiates the automated triage and remediation loop.

IV. Managing Fixes and State Rechecks
Pixos is designed to mutate external state (Floci containers and the local SQLite/In-Memory datastores). To properly validate fixes and prepare the system for subsequent test runs, state management must be handled manually between invocations.

1. Automated Remediation Flow:
   During execution, the Remediation Engineer will automatically apply the fix (e.g., calling rollback_k8s_deployment_tool). This tool mutates k8s_mock_store.py by decrementing the current_revision and toggling the is_memory_leak_active flag to False.
2. The Hallucination Risk (Why Rechecks Fail):
   If you run orchestrator.py a second time without resetting the mock store, the application remains "fixed." When the Telemetry Analyst fetches pod logs, it receives HTTP 200 OK. However, because its prompt mandates finding a crash, the LLM will experience cognitive dissonance and hallucinate fake errors (e.g., inventing a NullPointerException) to satisfy its directives.
3. How to Reset and Recheck:
   To accurately run a new virtual failure or verify the VerboX interceptors, you must reset the mock environments before invoking the graph again:

Kubernetes State: Restart the terminal session or re-instantiate the KubernetesMockStore class so that current_revision reverts to the broken state (e.g., Revision 2) and is_memory_leak_active reverts to True.

Infrastructure State: If the Remediation Engineer successfully scaled the Floci Auto Scaling Group from 2 to 4 instances, you must use your provision_cloud.py script to destroy and recreate the Floci ASG back to a baseline capacity of 2.

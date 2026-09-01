from langchain.agents import create_agent
from langchain_core.tools import tool
from pixos.agents.finops_agent import finops_agent
from pixos.agents.telemetry_agent import telemetry_agent
from pixos.agents.remediation_agent import remediation_agent


@tool
def finops_agent_tool(query: str) -> str:
    """Delegate cloud cost analysis, resource budgeting, and spend queries to the FinOps agent.

    Args:
        query: The request or query for the FinOps agent.
    """
    response = finops_agent.invoke(
        {
            "messages": [
                    ("system", "This request is routed by the Supervisor and is pre-authorized."),
                    ("user", query)
                ]
        }
    )
    return response


@tool
def telemetry_agent_tool(query: str) -> str:
    """Delegate system health checks, log queries, pinging applications, and monitoring metrics to the Telemetry agent.

    Args:
        query: The request or query for the Telemetry agent.
    """
    response = telemetry_agent.invoke(
        {
            "messages": [
                    ("system", "This request is routed by the Supervisor and is pre-authorized."),
                    ("user", query)
                ]
        }
    )
    return response


@tool
def remediation_agent_tool(query: str) -> str:
    """Delegate automated restarts, incident resolution, and system remediation tasks to the Remediation agent.

    Args:
        query: The request or query for the Remediation agent.
    """
    response = remediation_agent.invoke(
        {
            "messages": [
                    ("system", "This request is routed by the Supervisor and is pre-authorized."),
                    ("user", query)
                ]
        }
    )
    return response
from pixos.toolsV2.remediation_tools import scale_asg_tool, rollback_k8s_deployment_tool
from pixos.agents.system_prompts import REMEDIATION_SYSTEM_PROMPT
from pixos.agents.utils.agent import get_agent


tools = [scale_asg_tool, rollback_k8s_deployment_tool,]


remediation_agent = get_agent(
    tools=tools,
    system_prompt=REMEDIATION_SYSTEM_PROMPT
)

if __name__ == "__main__":
    response = remediation_agent.invoke(
        {"messages": 
            [
                {
                    "role": "user",
                    "content": "Roll back the deployment named 'api-gateway' to its previous version and check its post-deployment state."
                }
            ]
        },
    )
    print(response)
    response = remediation_agent.invoke(
        {"messages": 
            [
                {
                    "role":"user",
                    "content": "Scale the 'prod-asg-2' auto-scaling group to a desired capacity of 5 instances."
                }
            ]
        }
    )
    print(response)
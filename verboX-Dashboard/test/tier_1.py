from verbox_dashboard.policy.un_yamling import load_rules
from verbox_dashboard.policy.evaluator import evaluate
from verbox_dashboard.core.config import config

def case(tool_name: str, arg: dict, rule_by_tool: dict, description: str) -> None:
    decision = evaluate(tool_name, arg, rule_by_tool)
    print(f"\n{description}")
    print(decision)

def main() -> None:
    rule_by_tool = load_rules(config.rule_dir_path)

    case(
        "scale_asg_tool",
        {"asg_name": "testing", "new_capacity": 15},
        rule_by_tool=rule_by_tool,
        description="will block this action as 10 is the upper limit set in rules yaml",
    )

    case(
        "scale_asg_tool",
        {"asg_name": "testing", "new_capacity": 8},
        rule_by_tool=rule_by_tool,
        description="will allow this action",
    )

    case(
        "rollback_k8s_deployment_tool",
        {"deployment_name": "testing-not-protective"},
        rule_by_tool=rule_by_tool,
        description="will allow this action",
    )

    case(
        "rollback_k8s_deployment_tool",
        {"deployment_name": "testing-protective"},
        rule_by_tool=rule_by_tool,
        description="will block this action as it is protected",
    )

    print("\nDone\n")

if __name__=="__main__":
    main()
from dataclasses import dataclass
from typing import Literal, Optional

Action = Literal["allow", "block"]
Operator = Literal[">", "<", ">=", "<=", "==", "!=", "always"]
FailMode = Literal["fail_open", "fail_safe"]

@dataclass
class PolicyRule:
    policy: str
    tool: str
    operator: Operator
    action: Action
    fail_mode: FailMode
    message: str
    field: Optional[str] = None
    value: Optional[object] = None

    @staticmethod
    def form_dict(data: dict) -> "PolicyRule":
        required_fields = ["policy", "tool", "operator", "action", "fail_mode", "message"]
        missing = [i for i in required_fields if i not in data]

        if missing:
            raise ValueError(f"Policy rule {missing} is missing in data - {data}")

        operator = data["operator"]
        valid_operators = (">", "<", ">=", "<=", "==", "!=", "always")

        if operator not in valid_operators:
            raise ValueError(
                f"Invalid operator '{operator}' in rule '{data['policy']}' "
            )

        if operator != "always" and ("field" not in data or "value" not in data):
            raise ValueError(
                f"Rule '{data['policy']}' uses operator '{operator}' but is missing "
            )
        
        return PolicyRule(
            policy= data["policy"],
            tool= data["tool"],
            operator=data["operator"],
            action= data["action"],
            message= data["message"],
            field=data.get("field"),
            value=data.get("value"),
        )

@dataclass
class PolicyDecision:
    decision: Literal["allow", "block"]
    matched_policy: str | None
    message: str | None
    fail_mode_triggered: bool = False
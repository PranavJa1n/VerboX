from verbox_dashboard.policy.schema import PolicyDecision, PolicyRule

_OPERATORS = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
}

def _rule_matches(rule: PolicyRule, arguments: dict) -> bool:
    # arguments is the **kwargs of the actual fn being called on which tier 1 decorator is used
    if rule.operator == "always":
        return True

    if rule.field not in arguments:
        raise KeyError(f"Rule '{rule.policy}' references missing argument field: '{rule.field}'")
    
    actual_value = arguments[rule.field]
    compare = _OPERATORS[rule.operator]
    return compare(actual_value, rule.value)

def evaluate(tool_name: str, arguments: dict, rules_by_tool: dict[str, list[PolicyRule]]) -> PolicyDecision:
    matching_rules = rules_by_tool.get(tool_name, [])

    for rule in matching_rules:
        try:
            matched = _rule_matches(rule, arguments)
        except KeyError as exc:
            return PolicyDecision(
                decision="block",
                matched_policy=rule.policy,
                message=f"Blocked by fail_safe after evaluation error: {exc}",
            )

        if matched and rule.action == "block":
            return PolicyDecision(
                decision="block",
                matched_policy=rule.policy,
                message=rule.message,
            )
 
    return PolicyDecision(decision="allow", matched_policy=None, message=None)
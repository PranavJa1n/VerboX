import glob
import os
import yaml
from verbox_dashboard.policy.schema import PolicyRule

def load_rules(rules_dir_path: str) -> dict[str, list[PolicyRule]]:
    if not os.path.isdir(rules_dir_path):
        raise FileNotFoundError(
            f"Policy rules directory not found: '{rules_dir_path}'. "
        )

    rules_by_tool: dict[str, list[PolicyRule]] = {}
    yaml_files = glob.glob(os.path.join(rules_dir_path, "*.yaml")) + glob.glob(os.path.join(rules_dir_path, "*.yml"))

    if not yaml_files:
        print(f"[verbox_backend] Warning: no policy YAML files found in '{rules_dir_path}'.")

    for file in yaml_files:
        with open(file, "r") as f:
            raw = yaml.safe_load(f)

        if raw is None:
            continue

        if "rules" not in raw or not isinstance(raw["rules"], list):
            raise ValueError(f"'{file}' must have a top-level 'rules:' list. Got: {raw}")

        for rule_dict in raw["rules"]:
            try:
                rule = PolicyRule.form_dict(rule_dict)
            except ValueError as exc:
                raise ValueError(f"Invalid policy rule in file '{file}': {exc}") from exc
            rules_by_tool.setdefault(rule.tool, []).append(rule)

    return rules_by_tool
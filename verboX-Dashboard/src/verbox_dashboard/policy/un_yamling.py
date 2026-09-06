import glob
import os
import yaml
from schema import PolicyRule


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

        try:
            rule = PolicyRule.from_dict(raw)
        except ValueError as exc:
            raise ValueError(f"Invalid policy rule in file '{file}': {exc}") from exc

        rules_by_tool.setdefault(rule.tool, []).append(rule)

    return rules_by_tool
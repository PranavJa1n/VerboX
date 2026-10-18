from functools import lru_cache
from backend.core.config import config
from backend.policy.un_yamling import load_rules
from backend.policy.schema import PolicyRule

@lru_cache(maxsize=1)
def get_policy_rules() -> dict[str, list[PolicyRule]]:
    """
    Loads Tier 1 policy rules from disk once and caches the result for the lifetime of the process. Routes depend on this instead of calling load_rules() directly, so YAML files are only read once.
    """
    return load_rules(config.rule_dir_path)
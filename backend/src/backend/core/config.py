import os
from pathlib import Path
from dotenv import load_dotenv

_parents = Path(__file__).resolve().parents
ROOT_ENV_PATH = (_parents[4] if len(_parents) > 4 else _parents[-1]) / ".env"
_DEFAULT_RULES_DIR = str(_parents[1] / "api" / "routes" / "rules")


def load_central_env() -> bool:
    """Load environment variables strictly from the repository root .env file."""
    return load_dotenv(dotenv_path=ROOT_ENV_PATH, override=True)


load_central_env()

class VerboxBackendConfig:
    rule_dir_path = os.getenv("VERBOX_RULES_DIR", _DEFAULT_RULES_DIR)
    verbox_host = os.getenv("VERBOX_HOST", "0.0.0.0")
    verbox_port = int(os.getenv("VERBOX_PORT","6969"))

config = VerboxBackendConfig()

if __name__=="__main__":
    print(config.rule_dir_path)
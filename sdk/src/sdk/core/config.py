import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_ENV_PATH = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(dotenv_path=ROOT_ENV_PATH, override=True)

class SDKConfig:
    backend_base_url: str = os.getenv("VERBOX_BACKEND_URL", "http://localhost:8000/api/v1")
    timeout_seconds: float = float(os.getenv("VERBOX_TIMEOUT_SECONDS", "5.0"))
    fail_mode: bool = os.getenv("VERBOX_FAIL_OPEN", "true").lower() == "true"

config = SDKConfig()
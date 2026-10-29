import os
from dotenv import load_dotenv

load_dotenv()

class SDKConfig:
    backend_base_url: str = os.getenv("VERBOX_BACKEND_URL", "http://localhost:8000/api/v1")
    timeout_seconds: float = float(os.getenv("VERBOX_TIMEOUT_SECONDS", "5.0"))
    fail_mode: bool = os.getenv("VERBOX_FAIL_OPEN").lower() == "true"

config = SDKConfig()
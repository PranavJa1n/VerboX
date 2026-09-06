import os
from dotenv import load_dotenv

load_dotenv()

class VerboxBackendConfig:
    rule_dir_path = os.getenv("VERBOX_RULES_DIR", r"./rules")
    verbox_host = os.getenv("VERBOX_HOST", "0.0.0.0")
    verbox_port = int(os.getenv("VERBOX_PORT","6969"))
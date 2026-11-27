from pathlib import Path
from dotenv import load_dotenv

ROOT_ENV_PATH = Path(__file__).resolve().parents[4] / ".env"


def load_central_env() -> bool:
    """Load environment variables strictly from the repository root .env file."""
    return load_dotenv(dotenv_path=ROOT_ENV_PATH, override=True)


load_central_env()

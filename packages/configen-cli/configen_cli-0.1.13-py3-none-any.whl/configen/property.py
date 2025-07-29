from dotenv import load_dotenv
from pathlib import Path
import os

CONFIG_DIR = Path.home() / ".configen"
ENV_FILE = CONFIG_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)

CONFIGEN_API_KEY = os.getenv("CONFIGEN_API_KEY", "")
CONFIGEN_API_URL = os.getenv("CONFIGEN_API_URL", "")
HOST_ID = os.getenv("HOST_ID", "")

CLI_INPUT_USR_ASK = "USR_ASK"
CLI_INPUT_USR_ANSWER = "USR_ANSWER"
CLI_INPUT_CMD_ERROR = "CMD_ERROR"
CLI_INPUT_CMD_OUTPUT = "CMD_OUTPUT"


def validate_config() -> tuple[bool, str]:
    if CONFIG_DIR is None or not CONFIG_DIR.exists():
        return False, f"Missing config folder: {CONFIG_DIR}"

    if not ENV_FILE.exists():
        return False, f"Missing config file: {ENV_FILE}"

    if not CONFIGEN_API_KEY:
        return False, "Missing CONFIGEN_API_KEY in .env"

    if not CONFIGEN_API_URL:
        return False, "Missing CONFIGEN_API_URL in .env"

    if not HOST_ID:
        return False, "Missing HOST_ID in .env"

    return True, ""

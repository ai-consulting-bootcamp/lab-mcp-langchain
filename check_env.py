"""Check that the API keys in .env are loaded. Never prints the key values."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# ---------- Configuration ----------
ENV_PATH = Path(__file__).parent / ".env"
REQUIRED_KEYS = ["OPENAI_API_KEY", "GITHUB_PERSONAL_ACCESS_TOKEN"]
PLACEHOLDER_WORDS = ["your", "xxx", "changeme", "replace", "example"]


# ---------- Checks ----------
def key_status(name):
    """Return "OK", "MISSING", "EMPTY" or "PLACEHOLDER" for one environment variable."""
    value = os.environ.get(name)
    if value is None:
        return "MISSING"
    if not value.strip():
        return "EMPTY"
    if any(word in value.lower() for word in PLACEHOLDER_WORDS):
        return "PLACEHOLDER"
    return "OK"


def check_keys(names):
    """Return a dict of {key name: status} for all the given names."""
    return {name: key_status(name) for name in names}


# ---------- Self-check ----------
if __name__ == "__main__":
    if not load_dotenv(ENV_PATH):
        print(f"WARNING: nothing loaded from {ENV_PATH}")

    results = check_keys(REQUIRED_KEYS)
    for name, status in results.items():
        print(f"{status:<12} {name}")

    all_ok = all(status == "OK" for status in results.values())
    print("All keys loaded." if all_ok else "Some keys need fixing.")
    sys.exit(0 if all_ok else 1)

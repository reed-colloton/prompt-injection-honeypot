"""API-key bootstrap for the prompt-injection honeypot.

Resolves each required key from, in order:

    1. the environment (incl. a local .env file in development)
    2. a saved config file at ~/.config/prompt-injection-honeypot/config.json
    3. an interactive prompt the first time the tool runs

Anything entered at the prompt is written back to the config file, so the user
is only asked once. This mirrors the first-run setup flow of the `bashify` CLI.

This module deliberately depends only on the standard library (plus python-dotenv
if available) and imports nothing from the ``graph`` package: ``graph/__init__``
builds the LLM clients at import time and reads ``OPENROUTER_API_KEY`` eagerly,
so the keys must be in ``os.environ`` *before* anything under ``graph`` is
imported. Call :func:`ensure_api_keys` first.
"""

import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # python-dotenv is a dependency, but stay import-safe
    def load_dotenv(*_args, **_kwargs):  # type: ignore[misc]
        return False


# ANSI colors (kept local so this module has no intra-package imports)
GREEN = "\033[92m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

CONFIG_PATH = Path.home() / ".config" / "prompt-injection-honeypot" / "config.json"

# env var -> (human label, where to get one)
REQUIRED_KEYS = [
    ("OPENROUTER_API_KEY", "OpenRouter API key", "https://openrouter.ai/keys"),
    ("TAVILY_API_KEY", "Tavily API key (web search)", "https://app.tavily.com/home"),
]


def _load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def _save_config(data: dict) -> None:
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=2)
        try:
            os.chmod(CONFIG_PATH, 0o600)  # keys are secrets; owner-only
        except OSError:
            pass
    except Exception as ex:
        print(f"{RED}Warning: could not save config to {CONFIG_PATH}: {ex}{RESET}")


def ensure_api_keys() -> None:
    """Make sure every required API key is present in ``os.environ``.

    Resolution order per key: existing env var -> saved config file -> prompt.
    Newly entered keys are written back to the config file so the user is asked
    only once. Exits the process with status 1 if a required key is left blank.
    """
    load_dotenv()  # pick up a local .env in development; never overrides real env

    config = _load_config()
    greeted = False
    dirty = False

    for env_var, label, url in REQUIRED_KEYS:
        if os.environ.get(env_var):
            continue

        saved = config.get(env_var)
        if saved:
            os.environ[env_var] = saved
            continue

        if not greeted:
            print(f"{BOLD}Welcome to the Prompt-Injection Honeypot!{RESET}")
            print("A couple of API keys are needed before the demo can run.")
            print(f"They'll be saved to {CONFIG_PATH} so you're only asked once.\n")
            greeted = True

        print(f"{label} - get one at: {url}")
        try:
            entered = input(f"{BOLD}Enter your {label}: {RESET}").strip()
        except EOFError:
            print()
            entered = ""

        if not entered:
            print(f"{RED}Error: {label} is required.{RESET}")
            sys.exit(1)

        os.environ[env_var] = entered
        config[env_var] = entered
        dirty = True

    if dirty:
        _save_config(config)
        print(f"{GREEN}Saved. Keys stored in {CONFIG_PATH}.{RESET}\n")

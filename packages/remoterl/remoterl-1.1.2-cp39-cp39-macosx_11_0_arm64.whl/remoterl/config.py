#!/usr/bin/env python
"""remoterl.cli
================
Unified RemoteRL command-line interface.

This CLI relies on a single JSON config file to persist the API key:

* default location: ``~/.config/remoterl/config.json`` (roaming on Windows)
* overridable via the ``REMOTERL_CONFIG_PATH`` environment variable

Lookup precedence when a command needs the key:

1. ``REMOTERL_API_KEY`` environment variable (always wins)
2. ``api_key`` value inside *config.json*

No legacy *credentials* flat file is used anymore.
"""
from __future__ import annotations

import os, sys
from pathlib import Path
from typing import Optional
import typer
import json
# get version of remoterl package using importlib.metadata
try:
    from importlib.metadata import version, PackageNotFoundError  # ≥ 3.8
except ImportError:               # < 3.8 needs the back-port package
    from importlib_metadata import version, PackageNotFoundError

try:
    REMOTERL_VERSION = version("remoterl")
except PackageNotFoundError:      # not installed in the environment
    REMOTERL_VERSION = None

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------
def default_config_dir(appname: str = "remoterl") -> Path:
    home = Path.home()

    if sys.platform.startswith("win"):
        base = Path(os.getenv("LOCALAPPDATA", home / "AppData" / "Local"))
        return base / appname
    elif sys.platform == "darwin":
        return home / "Library" / "Application Support" / appname
    else:  # assume POSIX
        base = Path(os.getenv("XDG_CONFIG_HOME", home / ".config"))
        return base / appname
    
DEFAULT_CONFIG_PATH = Path(
    os.getenv("REMOTERL_CONFIG_PATH")          # explicit override
    or default_config_dir() / "config.json"    # or yaml/toml …
)

def load_config() -> dict:
    """Return the parsed JSON config (or an empty dict if absent/corrupt)."""
    if DEFAULT_CONFIG_PATH.is_file():
        try:
            return json.loads(DEFAULT_CONFIG_PATH.read_text()) or {}
        except Exception:
            pass  # fall through
    return {}


def save_config(cfg: dict) -> None:
    """Write *cfg* back to the JSON file, creating parent dirs if needed."""
    DEFAULT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    # write a version with sorted keys for consistency
    if REMOTERL_VERSION:
        cfg["remoterl_version"] = REMOTERL_VERSION
    else:
        cfg["remoterl_version"] = "unknown"  # fallback if version cannot be determined
    DEFAULT_CONFIG_PATH.write_text(json.dumps(cfg, indent=2))


def resolve_api_key() -> Optional[str]:
    """Return the RemoteRL API key, or ``None`` if it cannot be found."""
    # 1️⃣ Environment variable always wins
    if (env := os.getenv("REMOTERL_API_KEY")):
        return env.strip()

    # 2️⃣ JSON config file
    if key := load_config().get("api_key"):
        return str(key).strip()

    # Not found
    return ""

def validate_api_key(api_key: str) -> bool:
    """Validate RemoteRL API-key format (`api_<uuid>`)."""
    if not api_key.startswith("api_"):
        return False

    import re
    pattern = (r"^api_[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-"
               r"[a-f0-9]{4}-[a-f0-9]{12}$")
    if not re.match(pattern, api_key, re.IGNORECASE):
        return False
    
    return True

def ensure_api_key(api_key:str) -> Optional[str]:
    """Return the RemoteRL API key, or ``None`` if it cannot be found."""
    # 1️⃣ Environment variable always wins
    if validate_api_key(api_key):
        return api_key

    api_key = resolve_api_key()
    if validate_api_key(api_key):
        return api_key
    
    try:
        short_api_key = api_key[:8] if api_key else api_key
    except Exception:
        short_api_key = api_key
        
    typer.echo(
        f"[ERROR] RemoteRL API key not found or invalid: {short_api_key}"
    )
    raise ValueError(
        f"RemoteRL API key not found. {short_api_key}"
    )


def ensure_config() -> None:
    """Ensure the config file exists, creating it if necessary."""
    if not DEFAULT_CONFIG_PATH.is_file():
        DEFAULT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_CONFIG_PATH.write_text(json.dumps({"api_key": ""}, indent=2))
        print(f"Created config file at {DEFAULT_CONFIG_PATH}")
    else:
        print(f"Config file already exists at {DEFAULT_CONFIG_PATH}")

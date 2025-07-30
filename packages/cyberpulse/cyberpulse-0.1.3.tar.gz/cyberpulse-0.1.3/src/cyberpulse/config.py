# src/cyberpulse/config.py

import os
import yaml
from pathlib import Path
from typing import Any, Dict

# Default schema
DEFAULT_CONFIG: Dict[str, Any] = {
    "openai_api_key": None,
    "defaults": {
        "thresholds": {
            "Critical": 9.0,
            "High":     7.0,
            "Medium":   4.0,
            "Low":      0.0,
        },
        "public_hosts": ["public", "internet", "0.0.0.0"],
    },
}

def _get_paths():
    """
    Determine config directory and file paths at call time,
    respecting the HOME env var.
    """
    home = Path(os.getenv("HOME", Path.home()))
    config_dir = home / ".cyberpulse"
    config_path = config_dir / "config.yml"
    return config_dir, config_path

def load_config() -> Dict[str, Any]:
    """
    Loads the YAML config from ~/.cyberpulse/config.yml,
    merging with DEFAULT_CONFIG for any missing keys.
    """
    config_dir, config_path = _get_paths()
    # Ensure config directory exists
    config_dir.mkdir(parents=True, exist_ok=True)

    if not config_path.exists():
        # Write default config if none exists
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Start with defaults and overlay user values
    cfg = DEFAULT_CONFIG.copy()
    cfg.update(data)

    # Deep-merge nested defaults
    defaults_overrides = data.get("defaults", {})
    cfg["defaults"].update(defaults_overrides)

    return cfg

def save_config(cfg: Dict[str, Any]) -> None:
    """
    Writes the given config dict to ~/.cyberpulse/config.yml.
    """
    config_dir, config_path = _get_paths()
    config_dir.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, default_flow_style=False)

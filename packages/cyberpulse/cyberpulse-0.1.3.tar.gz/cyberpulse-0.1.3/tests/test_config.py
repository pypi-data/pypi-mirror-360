# tests/test_config.py

import yaml
from pathlib import Path
import pytest
from cyberpulse.config import load_config, save_config, DEFAULT_CONFIG

def test_load_default_config(tmp_path, monkeypatch):
    """
    On first load, load_config should write DEFAULT_CONFIG to ~/.cyberpulse/config.yml
    and return a dict equal to DEFAULT_CONFIG.
    """
    # Redirect HOME to a temporary directory
    monkeypatch.setenv("HOME", str(tmp_path))
    config_dir = tmp_path / ".cyberpulse"
    config_file = config_dir / "config.yml"

    # Ensure nothing exists yet
    assert not config_file.exists()

    cfg = load_config()
    # It should create the config file and return the defaults
    assert config_file.exists()
    assert cfg == DEFAULT_CONFIG

    # The file contents should match DEFAULT_CONFIG
    data = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    assert data == DEFAULT_CONFIG

def test_save_and_load_custom_config(tmp_path, monkeypatch):
    """
    After modifying and saving, load_config should reflect changes.
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    custom = DEFAULT_CONFIG.copy()
    custom["openai_api_key"] = "CUSTOMKEY123"
    custom["defaults"]["thresholds"]["High"] = 8.5

    # Save our custom config
    save_config(custom)

    # Now load_config should return our custom values
    cfg = load_config()
    assert cfg["openai_api_key"] == "CUSTOMKEY123"
    assert cfg["defaults"]["thresholds"]["High"] == 8.5

# tests/test_cli_login.py

import yaml
from pathlib import Path
from click.testing import CliRunner
import pytest

from cyberpulse.cli import main

def test_login_command(tmp_path, monkeypatch):
    """
    Running `cyberpulse login` should prompt for a key and save it.
    """
    # Redirect HOME to a temporary directory
    monkeypatch.setenv("HOME", str(tmp_path))
    runner = CliRunner()

    # Invoke the login command, providing "MYSECRET\n" as input
    result = runner.invoke(main, ["login"], input="MYSECRET\n")
    assert result.exit_code == 0
    # It should confirm saving
    assert "API key saved to" in result.output

    # The config file should now exist and contain our key
    config_file = tmp_path / ".cyberpulse" / "config.yml"
    assert config_file.exists()
    data = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    assert data["openai_api_key"] == "MYSECRET"

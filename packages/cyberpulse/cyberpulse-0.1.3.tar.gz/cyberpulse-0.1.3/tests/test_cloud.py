# tests/test_cloud.py

import datetime
import pytest
from cyberpulse.models import Finding
import cyberpulse.cloud as cloud_module

@pytest.fixture(autouse=True)
def patch_get_api_key(monkeypatch):
    """Return a fake API key so _get_api_key() never errors."""
    monkeypatch.setenv("OPENAI_API_KEY", "FAKE_KEY")
    yield

def test_summarize_cloud_success(monkeypatch):
    """Mock out openai.chat.completions.create to return a fake response."""
    fake_response = type("R", (), {
        "choices": [
            type("C", (), {
                "message": type("M", (), {"content": "Apply patch X immediately."})
            })()
        ]
    })

    # Patch the create method on the new interface
    monkeypatch.setattr(
        cloud_module.openai.chat.completions,
        "create",
        lambda **kwargs: fake_response
    )

    f = Finding(id="1", cve="CVE-FAKE-0001", cvss_score=5.0, host="host1")
    result = cloud_module.summarize_cloud(f)
    assert result == "Apply patch X immediately."

def test_summarize_cloud_no_key(monkeypatch):
    """Ensure missing key raises a RuntimeError."""
    # Remove both env var and config override
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    # Also ensure config load returns no key
    monkeypatch.setattr(cloud_module, "_get_api_key", lambda: (_ for _ in ()).throw(RuntimeError("no key")))
    with pytest.raises(RuntimeError):
        cloud_module.summarize_cloud(Finding(id="x", cve="CVE-0", cvss_score=0, host="h"))

# tests/test_local_llm.py
import re
import os
import pytest

from cyberpulse.local_llm import summarise

@pytest.mark.skipif(
    not os.environ.get("LLAMA_MODEL_PATH"),
    reason="local model not installed",
)
def test_summarise_single_line():
    """summarise() should return one concise line without the error prefix."""
    text = "OpenSSL 1.1.1t allows buffer overflow via crafted DTLS packets."
    out = summarise(text)
    assert "\n" not in out
    assert not out.startswith("[local-llm-error]")
    assert len(out) < 200  # sanity-check length
    # optional: loosened regex to match an 'upgrade' verb
    assert re.search(r"update|upgrade|patch", out, re.I)

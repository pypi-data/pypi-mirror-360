"""
cyberpulse.local_llm
~~~~~~~~~~~~~~~~~~~~
On-device Llama-2 wrapper that generates one-line remediation steps.

Public API
----------
summarise(text: str) -> str
"""

from __future__ import annotations

import os
import textwrap
import warnings
from functools import lru_cache
from typing import Final

# Silence the duplicate-<s> warning from llama-cpp
warnings.filterwarnings("ignore", category=RuntimeWarning, module="llama_cpp")

SYSTEM_PROMPT: Final[str] = (
    "You are CyberPulse-LLM, an on-device assistant turning vulnerability "
    "findings into one-line, copy-and-paste remediation steps. Respond in "
    "≤30 words, no bullet points or markdown."
)


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #
def _model_path() -> str | None:
    """Path from $LLAMA_MODEL_PATH, or None if unset/not found."""
    path = os.environ.get("LLAMA_MODEL_PATH")
    return path if path and os.path.isfile(path) else None


@lru_cache(maxsize=1)
def _load_llama():
    """
    Load the GGUF model once and cache the Llama instance.

    Raises
    ------
    RuntimeError if the model file or llama_cpp is missing.
    """
    model_file = _model_path()
    if not model_file:
        raise RuntimeError(
            "Local model not found. "
            "Set LLAMA_MODEL_PATH to your .gguf file (Step 6.2)."
        )

    try:
        from llama_cpp import Llama
    except ImportError as exc:
        raise RuntimeError(
            "Package `llama_cpp` not installed. "
            "Run `pip install 'llama-cpp-python[server]'`."
        ) from exc

    return Llama(
        model_path=model_file,
        n_ctx=2048,
        n_threads=os.cpu_count() or 4,
        embedding=False,
        verbose=False,
    )


# --------------------------------------------------------------------------- #
# Public function
# --------------------------------------------------------------------------- #
def summarise(text: str) -> str:
    """
    Summarise *text* into a single remediation line using the local model.

    If the model is unavailable, returns an error string beginning with
    “[local-llm-error] …” so callers can fall back gracefully.
    """
    try:
        llama = _load_llama()
    except RuntimeError as err:
        return f"[local-llm-error] {err}"

    prompt = textwrap.dedent(
        f"""
        [INST] <<SYS>>
        {SYSTEM_PROMPT}
        <</SYS>>

        {text.strip()}
        [/INST]
        """
    ).strip()

    output = llama(prompt, max_tokens=64, temperature=0.2)
    reply: str = output["choices"][0]["text"].strip()

    # Ensure true one-liner and strip stray quotes.
    reply = reply.splitlines()[0].strip('"').strip("'")

    return reply

# src/cyberpulse/summarizer.py

import os
from llama_cpp import Llama
from cyberpulse.models import Finding

# Default model path; override with LLAMA_MODEL_PATH env var if desired
MODEL_PATH = os.getenv(
    "LLAMA_MODEL_PATH",
    os.path.join(os.getcwd(), "models", "llama-2-7b.gguf")
)

# Lazy initialization of the model
_llama = None

def _get_llama():
    global _llama
    if _llama is None:
        try:
            _llama = Llama(model_path=MODEL_PATH)
        except Exception as e:
            raise RuntimeError(
                f"Failed to load on-device Llama model from '{MODEL_PATH}': {e}. "
                "Please ensure the model file exists and is a valid GGUF model."
            )
    return _llama

def summarize_remediation(finding: Finding) -> str:
    """
    Generate a one-line remediation step for a given finding.

    If the local Llama model cannot be loaded, returns a placeholder string
    so the CLI can continue without error.
    """
    try:
        llama = _get_llama()
        prompt = (
            f"Vulnerability {finding.cve} with CVSS {finding.cvss_score} on host {finding.host}.\n"
            f"Description: {finding.description or 'No description provided.'}\n"
            "Provide a concise, one-line remediation step:"
        )

        # Generate a single completion
        response = llama(
            prompt=prompt,
            max_tokens=64,
            temperature=0.2,
            stop=["\n"]
        )
        return response["choices"][0]["text"].strip()

    except RuntimeError:
        # Fallback placeholder if model not present or invalid
        return "[LOCAL MODEL NOT INSTALLED — use `--cloud` for GPT-4 summarization]"

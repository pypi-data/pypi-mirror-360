# src/cyberpulse/cloud.py

import os
import openai
from cyberpulse.config import load_config
from cyberpulse.models import Finding

# Load API key from env or config
def _get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        cfg = load_config()
        key = cfg.get("openai_api_key")
    if not key:
        raise RuntimeError(
            "No OpenAI API key found. Run `cyberpulse login` or set OPENAI_API_KEY."
        )
    return key

def summarize_cloud(finding: Finding) -> str:
    """
    Generate a one-line remediation step via GPT-4 on OpenAI’s API.
    """
    api_key = _get_api_key()
    openai.api_key = api_key

    messages = [
        {
            "role": "system",
            "content": "You are a security assistant that provides concise remediation steps."
        },
        {
            "role": "user",
            "content": (
                f"Vulnerability {finding.cve} with CVSS score {finding.cvss_score} on host {finding.host}.\n"
                f"Description: {finding.description or 'No description provided.'}\n"
                "Provide a single, one-line remediation step."
            )
        }
    ]

    resp = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.2,
        max_tokens=64,
        n=1,
        stop=None
    )

    # In the 1.x client, the response uses .choices[0].message.content
    return resp.choices[0].message.content.strip()

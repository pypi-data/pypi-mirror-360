# CyberPulse

**CyberPulse** is a CLI tool to ingest vulnerability scanner exports (JSON, CSV, XML), apply risk‑based prioritisation, enrich findings with CVE data, and generate actionable remediation steps.

## Features

- Parse JSON, CSV, and XML scanner outputs  
- Apply CVSS‑based prioritisation, public‑facing host checks, known‑exploited CVE flags  
- Enrich findings from a local NVD database  
- One‑line remediation summaries via **on‑device Llama‑2** or **GPT‑4 (Pro)**  
- Output grouped to‑do lists (Critical, High, Medium) in Markdown, plain text, or Slack  

## Installation

```bash
pip install cyberpulse
```

## Quick Start

```bash
# Free mode – on‑device Llama‑2 (auto‑fallback to cloud if model missing)
cyberpulse --input scan.json --output fixes.md

# Pro mode – GPT‑4 via CyberPulse Cloud
cyberpulse login            # enter your CyberPulse API key
cyberpulse --input scan.json --cloud --slack
```

### Local, no‑cloud summarisation (offline)

```bash
# 1. Download or copy a quantised GGUF model, e.g. Llama‑2‑7B‑Chat.Q4_K_M.gguf
# 2. Point CyberPulse at it
export LLAMA_MODEL_PATH=/Volumes/WEXLER/models/cyberpulse/llama-2-7b-chat.Q4_K_M.gguf

# 3. Generate a report using the on‑device LLM
cyberpulse --input scan.json --summarize local --output fixes.md
```

*If the model is missing, CyberPulse prints:*

```
📎  Local model not installed. See docs → https://cyberpulse.dev/local-llm
```

The default `--summarize auto` first tries the local model and transparently falls back to GPT‑4 Cloud.

## Development

```bash
# From project root
source venv/bin/activate
pip install -r requirements-dev.txt
pytest --cov=src/cyberpulse
flake8 src/cyberpulse
black --check src/cyberpulse
```

## Project Structure

```text
cyberpulse/
├── src/
│   └── cyberpulse/
├── tests/
├── docs/
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── .gitignore
```

## License

[MIT](LICENSE)


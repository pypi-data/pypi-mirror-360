# src/cyberpulse/notifier.py

import os
import json
from slack_sdk.webhook import WebhookClient
from cyberpulse.config import load_config

def send_slack_message(text: str) -> None:
    """
    Sends a message to the configured Slack Incoming Webhook.
    The webhook URL is read from ~/.cyberpulse/config.yml under 'slack_webhook_url'.
    """
    cfg = load_config()
    webhook_url = cfg.get("slack_webhook_url") or os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError(
            "No Slack webhook URL configured. "
            "Please set 'slack_webhook_url' in ~/.cyberpulse/config.yml or SLACK_WEBHOOK_URL env var."
        )

    client = WebhookClient(webhook_url)
    response = client.send(text=text)
    if not response.status_code == 200:
        raise RuntimeError(f"Slack API error {response.status_code}: {response.body}")

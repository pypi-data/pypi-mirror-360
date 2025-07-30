"""
cyberpulse.cli
~~~~~~~~~~~~~~
Command-line interface for CyberPulse.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

import click

from . import cloud, local_llm, parsers, rules, db, notifier

DEFAULT_OUT = Path("fixes.md")
SUMMARY_CHOICES = ["auto", "local", "cloud"]

# --------------------------------------------------------------------------- #
# Small helpers to bridge dicts *and* model objects
# --------------------------------------------------------------------------- #
def _get(item: Any, field: str, default: Any = None) -> Any:
    """Return *field* from dict or attribute from object."""
    if isinstance(item, dict):
        return item.get(field, default)
    return getattr(item, field, default)


def _set(item: Any, field: str, value: Any) -> None:
    """Set *field* on dict or object."""
    if isinstance(item, dict):
        item[field] = value
    else:
        setattr(item, field, value)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """CyberPulse – risk-based vuln-fix to-do list generator."""
    pass


@cli.command("scan")
@click.option(
    "-i",
    "--input",
    "scan_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Vulnerability scanner export (JSON, CSV, or XML).",
)
@click.option(
    "-o",
    "--output",
    "out_path",
    default=DEFAULT_OUT,
    type=click.Path(dir_okay=False, path_type=Path),
    show_default=True,
    help="Report file to write (Markdown).",
)
@click.option(
    "--summarize",
    "summarize_mode",
    type=click.Choice(SUMMARY_CHOICES, case_sensitive=False),
    default="auto",
    show_default=True,
    help="Which engine to use for one-line remediations.",
)
@click.option("--cloud", is_flag=True, help="Force cloud CVE look-ups.")
@click.option("--slack", is_flag=True, help="Post the report to Slack.")
@click.option("--email", is_flag=True, help="Send the report via email.")
def scan_cmd(
    scan_path: Path,
    out_path: Path,
    summarize_mode: str,
    cloud: bool,
    slack: bool,
    email: bool,
) -> None:
    """Parse a scan file, prioritise findings, and output a fix list."""
    findings = parsers.parse(scan_path)
    enriched = db.enrich(findings, use_cloud=cloud)
    prioritised = rules.apply(enriched)

    # --------------------------------------------------------------------- #
    # Summarisation
    # --------------------------------------------------------------------- #
    for item in prioritised:
        desc = _get(item, "description", "")
        if summarize_mode == "local":
            line = _summarise_local(desc, fatal_on_error=True)
        elif summarize_mode == "cloud":
            line = cloud.summarise(desc)
        else:  # auto
            line = _summarise_local(desc, fatal_on_error=False)
            if line.startswith("[local-llm-error]"):
                line = cloud.summarise(desc)

        _set(item, "remediation", line)

    # --------------------------------------------------------------------- #
    # Write report
    # --------------------------------------------------------------------- #
    _write_markdown(prioritised, out_path)

    # --------------------------------------------------------------------- #
    # Notifications
    # --------------------------------------------------------------------- #
    if slack:
        notifier.post_slack(out_path)
    if email:
        notifier.send_email(out_path)

    click.echo(f"✅  Report written to {out_path}")
    if slack:
        click.echo("📨  Slack notification sent.")
    if email:
        click.echo("📧  Email sent.")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _summarise_local(text: str, *, fatal_on_error: bool) -> str:
    """Wrapper around local_llm.summarise with nicer UX."""
    line = local_llm.summarise(text)
    if line.startswith("[local-llm-error]"):
        if fatal_on_error:
            click.secho(
                "📎  Local model not installed. "
                "See docs → https://cyberpulse.dev/local-llm",
                fg="red",
            )
            sys.exit(1)
        return line
    return line


def _write_markdown(findings: List[Any], out_file: Path) -> None:
    """Render a Markdown report grouped by severity."""
    groups: Dict[str, List[Any]] = {"Critical": [], "High": [], "Medium": []}
    for f in findings:
        sev = _get(f, "priority", "Medium")
        groups.setdefault(sev, []).append(f)

    lines = ["# CyberPulse Fix List\n"]
    for sev in ("Critical", "High", "Medium"):
        if not groups.get(sev):
            continue
        lines.append(f"## {sev}\n")
        for item in groups[sev]:
            title = _get(item, "title") or _get(item, "cve") or "<no title>"
            remedy = _get(item, "remediation", "").strip('"').strip("'")
            lines.append(f"- **{title}** — {remedy}")
        lines.append("")

    out_file.write_text("\n".join(lines))


# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    cli()

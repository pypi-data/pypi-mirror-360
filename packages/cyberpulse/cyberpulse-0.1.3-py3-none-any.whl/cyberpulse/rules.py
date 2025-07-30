# src/cyberpulse/rules.py
import os
from typing import List, Dict, Optional, Any

from cyberpulse.models import Finding

# --------------------------------------------------------------------------- #
# Priority levels
# --------------------------------------------------------------------------- #
PRIORITY_CRITICAL = "Critical"
PRIORITY_HIGH     = "High"
PRIORITY_MEDIUM   = "Medium"
PRIORITY_LOW      = "Low"

# --------------------------------------------------------------------------- #
# Default thresholds & public-host patterns
# --------------------------------------------------------------------------- #
DEFAULT_THRESHOLDS: Dict[str, float] = {
    PRIORITY_CRITICAL: 9.0,
    PRIORITY_HIGH:     7.0,
    PRIORITY_MEDIUM:   4.0,
    PRIORITY_LOW:      0.0,
}

DEFAULT_PUBLIC_HOSTS: List[str] = [
    "public",
    "internet",
    "0.0.0.0",
]

# --------------------------------------------------------------------------- #
# Known-exploited list
# --------------------------------------------------------------------------- #
KNOWN_EXPLOITED_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),  # project_root/src/cyberpulse
    os.pardir,
    "data",
    "known_exploited.txt",
)

def load_known_exploited() -> set[str]:
    """Load the known-exploited CVE IDs into a set."""
    try:
        with open(KNOWN_EXPLOITED_PATH, "r", encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        return set()

KNOWN_EXPLOITED = load_known_exploited()

# --------------------------------------------------------------------------- #
# Core prioritisation logic
# --------------------------------------------------------------------------- #
def prioritize(
    findings: List[Finding],
    thresholds: Dict[str, float] | None = None,
    public_hosts: Optional[List[str]] = None,
) -> List[Finding]:
    """
    Apply risk-based rules:

    1. Base priority from CVSS.
    2. Bump if host is public-facing.
    3. Bump if CVE is on the known-exploited list.
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS
    if public_hosts is None:
        public_hosts = DEFAULT_PUBLIC_HOSTS

    for f in findings:
        # --- CVSS threshold ------------------------------------------------ #
        score = f.cvss_score
        if score >= thresholds[PRIORITY_CRITICAL]:
            f.priority = PRIORITY_CRITICAL
        elif score >= thresholds[PRIORITY_HIGH]:
            f.priority = PRIORITY_HIGH
        elif score >= thresholds[PRIORITY_MEDIUM]:
            f.priority = PRIORITY_MEDIUM
        else:
            f.priority = PRIORITY_LOW

        # --- Public-host bump --------------------------------------------- #
        if any(pat in f.host for pat in public_hosts):
            if f.priority == PRIORITY_LOW:
                f.priority = PRIORITY_MEDIUM
            elif f.priority == PRIORITY_MEDIUM:
                f.priority = PRIORITY_HIGH
            elif f.priority == PRIORITY_HIGH:
                f.priority = PRIORITY_CRITICAL

        # --- Known-exploited bump ----------------------------------------- #
        if f.cve in KNOWN_EXPLOITED:
            if f.priority in (PRIORITY_LOW, PRIORITY_MEDIUM):
                f.priority = PRIORITY_HIGH
            elif f.priority == PRIORITY_HIGH:
                f.priority = PRIORITY_CRITICAL

    return findings

# --------------------------------------------------------------------------- #
# Public convenience wrapper (used by cli.py)
# --------------------------------------------------------------------------- #
def apply(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalised entry-point for the CLI.
    Delegates to `prioritize()` so higher-level code can stay format-agnostic.
    """
    return prioritize(findings)  # type: ignore[arg-type]

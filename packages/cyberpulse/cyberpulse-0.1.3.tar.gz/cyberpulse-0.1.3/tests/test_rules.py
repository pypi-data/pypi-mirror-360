# tests/test_rules.py

from cyberpulse.models import Finding
from cyberpulse.rules import prioritize, PRIORITY_CRITICAL, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW

def make_finding(score: float) -> Finding:
    """Helper to create a Finding with only cvss_score set."""
    f = Finding(id="x", cve="CVE-0000", cvss_score=score, host="h")
    return f

def test_prioritize_critical():
    f = make_finding(9.5)
    prioritized = prioritize([f])[0]
    assert prioritized.priority == PRIORITY_CRITICAL

def test_prioritize_high():
    f = make_finding(7.5)
    prioritized = prioritize([f])[0]
    assert prioritized.priority == PRIORITY_HIGH

def test_prioritize_medium():
    f = make_finding(5.0)
    prioritized = prioritize([f])[0]
    assert prioritized.priority == PRIORITY_MEDIUM

def test_prioritize_low():
    f = make_finding(3.9)
    prioritized = prioritize([f])[0]
    assert prioritized.priority == PRIORITY_LOW

def test_public_host_bump_low_to_medium():
    # A low‐score finding on a public host should become Medium
    f = make_finding(3.0)
    f.host = "public-server.example.com"
    prioritized = prioritize([f])[0]
    assert prioritized.priority == PRIORITY_MEDIUM

def test_public_host_bump_medium_to_high():
    # A medium‐score finding on a public host should become High
    f = make_finding(5.0)
    f.host = "internet-facing.example.com"
    prioritized = prioritize([f])[0]
    assert prioritized.priority == PRIORITY_HIGH

def test_public_host_bump_high_to_critical():
    # A high‐score finding on a public host should become Critical
    f = make_finding(8.0)
    f.host = "0.0.0.0"
    prioritized = prioritize([f])[0]
    assert prioritized.priority == PRIORITY_CRITICAL

import cyberpulse.rules as rules  # import the module to patch

def test_known_exploited_low_to_high(monkeypatch):
    # Simulate a known-exploited CVE on a low-score finding
    f = make_finding(2.0)
    f.cve = "CVE-2021-44228"
    # Monkeypatch the set in the rules module
    monkeypatch.setattr(rules, "KNOWN_EXPLOITED", {"CVE-2021-44228"})
    
    prioritized = prioritize([f])[0]
    assert prioritized.priority == PRIORITY_HIGH

def test_known_exploited_high_to_critical(monkeypatch):
    # Simulate a known-exploited CVE on a high-score finding
    f = make_finding(8.0)
    f.cve = "CVE-2022-22965"
    monkeypatch.setattr(rules, "KNOWN_EXPLOITED", {"CVE-2022-22965"})
    
    prioritized = prioritize([f])[0]
    assert prioritized.priority == PRIORITY_CRITICAL

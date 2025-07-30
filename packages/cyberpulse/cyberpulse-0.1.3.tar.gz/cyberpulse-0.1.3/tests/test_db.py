# tests/test_db.py

import datetime
import pytest
from cyberpulse.models import Finding
import cyberpulse.db as db

def make_finding(cve: str) -> Finding:
    """Helper to create a minimal Finding with a given CVE."""
    return Finding(id="x", cve=cve, cvss_score=0.0, host="h")

@pytest.fixture(autouse=True)
def patch_get_cve_metadata(monkeypatch):
    """
    Monkeypatch get_cve_metadata so tests run without a real DB.
    We'll simulate metadata for specific CVEs.
    """
    def fake_get(cve_id):
        fake_data = {
            "CVE-TEST-1111": {
                "summary": "Test vulnerability summary",
                "published_date": datetime.date(2020, 1, 1),
                "references": ["http://example.com/1", "http://example.com/2"],
            }
        }
        return fake_data.get(cve_id, {})
    monkeypatch.setattr(db, "get_cve_metadata", fake_get)
    yield

def test_get_cve_metadata_direct():
    # Even though get_cve_metadata is patched, it should return our fake data
    meta = db.get_cve_metadata("CVE-TEST-1111")
    assert meta["summary"] == "Test vulnerability summary"
    assert meta["published_date"] == datetime.date(2020, 1, 1)
    assert meta["references"] == ["http://example.com/1", "http://example.com/2"]

    # Non-existent CVE returns empty dict
    assert db.get_cve_metadata("CVE-UNKNOWN") == {}

def test_enrich_findings():
    f1 = make_finding("CVE-TEST-1111")
    f2 = make_finding("CVE-UNKNOWN")
    enriched = db.enrich_findings([f1, f2])

    # f1 should be enriched
    assert enriched[0].summary == "Test vulnerability summary"
    assert enriched[0].published_date == datetime.date(2020, 1, 1)
    assert enriched[0].references == ["http://example.com/1", "http://example.com/2"]

    # f2 has no metadata
    assert enriched[1].summary is None
    assert enriched[1].published_date is None
    assert enriched[1].references == []

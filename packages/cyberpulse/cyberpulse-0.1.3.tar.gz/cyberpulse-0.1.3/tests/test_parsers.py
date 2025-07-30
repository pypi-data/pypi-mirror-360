import os
from cyberpulse.parsers import parse_file
from cyberpulse.models import Finding

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def test_parse_json(tmp_path, monkeypatch):
    path = os.path.join(DATA_DIR, "sample.json")
    findings = parse_file(path)
    assert len(findings) == 1
    f = findings[0]
    assert isinstance(f, Finding)
    assert f.id == "1"
    assert f.cve == "CVE-2021-1234"
    assert f.cvss_score == 9.8
    assert f.host == "host1"
    assert f.description == "desc1"

def test_parse_csv():
    path = os.path.join(DATA_DIR, "sample.csv")
    findings = parse_file(path)
    assert len(findings) == 1
    f = findings[0]
    assert f.id == "2"
    assert f.cve == "CVE-2022-2345"
    assert f.cvss_score == 7.5
    assert f.host == "host2"
    assert f.description == "desc2"

def test_parse_xml():
    path = os.path.join(DATA_DIR, "sample.xml")
    findings = parse_file(path)
    assert len(findings) == 1
    f = findings[0]
    assert f.id == "3"
    assert f.cve == "CVE-2023-3456"
    assert f.cvss_score == 5.0
    assert f.host == "host3"
    assert f.description == "desc3"

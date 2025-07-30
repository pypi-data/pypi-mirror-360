# src/cyberpulse/parsers.py

import os

def detect_format(file_path: str) -> str:
    """
    Detects the scanner export format based on file extension.

    Args:
        file_path: Path to the scanner export file.

    Returns:
        One of 'json', 'csv', or 'xml'.

    Raises:
        ValueError: if the extension is not supported.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext == ".json":
        return "json"
    elif ext == ".csv":
        return "csv"
    elif ext == ".xml":
        return "xml"
    else:
        raise ValueError(f"Unsupported file format: {ext}")

# src/cyberpulse/parsers.py

import json
from typing import List
from cyberpulse.models import Finding

def parse_json(file_path: str) -> List[Finding]:
    """
    Parses a JSON scanner export into a list of Finding objects.

    Args:
        file_path: Path to the JSON file.

    Returns:
        A list of Finding instances.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle either dict-with-"findings" or bare list
    if isinstance(data, dict):
        items = data.get("findings", [])
        if not isinstance(items, list):
            items = [items]
    elif isinstance(data, list):
        items = data
    else:
        items = []

    findings: List[Finding] = []
    for item in items:
        finding = Finding(
            id=str(item.get("id") or item.get("finding_id", "")),
            cve=item.get("cve", ""),
            cvss_score=float(item.get("cvss_score", 0)),
            host=item.get("host", ""),
            description=item.get("description"),
        )
        findings.append(finding)

    return findings


import csv
from typing import List
from cyberpulse.models import Finding

def parse_csv(file_path: str) -> List[Finding]:
    """
    Parses a CSV scanner export into a list of Finding objects.

    Args:
        file_path: Path to the CSV file.

    Returns:
        A list of Finding instances.
    """
    findings: List[Finding] = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            finding = Finding(
                id=str(row.get("id") or row.get("finding_id", "")),
                cve=row.get("cve", ""),
                cvss_score=float(row.get("cvss_score", 0)),
                host=row.get("host", ""),
                description=row.get("description"),
            )
            findings.append(finding)
    return findings

import xmltodict
from typing import List
from cyberpulse.models import Finding

def parse_xml(file_path: str) -> List[Finding]:
    """
    Parses an XML scanner export into a list of Finding objects.

    Args:
        file_path: Path to the XML file.

    Returns:
        A list of Finding instances.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        doc = xmltodict.parse(f.read())

    # Adjust these keys if your XML has a different structure:
    items = doc.get("findings", {}).get("finding", [])
    if not isinstance(items, list):
        items = [items]

    findings: List[Finding] = []
    for item in items:
        finding = Finding(
            id=str(item.get("id") or item.get("finding_id", "")),
            cve=item.get("cve", ""),
            cvss_score=float(item.get("cvss_score", 0)),
            host=item.get("host", ""),
            description=item.get("description"),
        )
        findings.append(finding)

    return findings

from typing import List
from cyberpulse.models import Finding

def parse_file(file_path: str) -> List[Finding]:
    """
    Parses a scanner export (JSON, CSV, or XML) into a list of Finding objects.

    Args:
        file_path: Path to the scanner export file.

    Returns:
        A list of Finding instances.

    Raises:
        ValueError: if the file format is unsupported.
    """
    fmt = detect_format(file_path)
    if fmt == "json":
        return parse_json(file_path)
    elif fmt == "csv":
        return parse_csv(file_path)
    elif fmt == "xml":
        return parse_xml(file_path)
    else:
        # This should never happen because detect_format already errors
        raise ValueError(f"Unsupported format: {fmt}")
    
    # --------------------------------------------------------------------------- #
# Public convenience wrapper
# --------------------------------------------------------------------------- #
from pathlib import Path
from typing import List, Dict, Any

def parse(path: Path) -> List[Dict[str, Any]]:
    """
    Dispatch to the right loader based on file extension and return
    a list of finding dicts.

    This thin wrapper lets other modules call cyberpulse.parsers.parse(...)
    without caring about the underlying format.
    """
    ext = path.suffix.lower()
    if ext in {".json", ".jsn"}:
        return parse_json(path)          # <- use your real function names
    if ext in {".csv"}:
        return parse_csv(path)
    if ext in {".xml"}:
        return parse_xml(path)

    raise ValueError(f"Unsupported input format: {ext}")



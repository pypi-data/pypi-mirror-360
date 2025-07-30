# src/cyberpulse/db.py
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Date,
    Text,
    Table,
    MetaData,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

# --------------------------------------------------------------------------- #
# SQLite setup
# --------------------------------------------------------------------------- #
DB_PATH = os.path.join(
    Path(__file__).resolve().parents[1],  # project_root/data/nvd.db
    "data",
    "nvd.db",
)

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine: Engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)

metadata = MetaData()

# CVE metadata table
cve_table = Table(
    "cves",
    metadata,
    Column("cve_id", String, primary_key=True),
    Column("published_date", Date, nullable=True),
    Column("summary", Text, nullable=True),
    Column("references", Text, nullable=True),  # JSON-encoded list or newline-separated
)


# --------------------------------------------------------------------------- #
# Schema helpers
# --------------------------------------------------------------------------- #
def init_db() -> None:
    """Create tables in the SQLite database (run once during setup)."""
    metadata.create_all(engine)


def get_session():
    """Return a fresh SQLAlchemy session."""
    return SessionLocal()


# --------------------------------------------------------------------------- #
# CVE look-up helpers
# --------------------------------------------------------------------------- #
def get_cve_metadata(cve_id: str) -> dict:
    """
    Look up a CVE in the local NVD cache.

    Returns
    -------
    dict
        Keys: summary, published_date, references (List[str]).
        Empty dict if the CVE is not present.
    """
    session = get_session()
    stmt = select(cve_table).where(cve_table.c.cve_id == cve_id)
    row = session.execute(stmt).first()
    session.close()

    if not row:
        return {}

    data = row._mapping
    refs = data["references"].split("\n") if data["references"] else []
    return {
        "summary": data["summary"],
        "published_date": data["published_date"],
        "references": refs,
    }


# --------------------------------------------------------------------------- #
# In-place enrichment of Finding objects
# --------------------------------------------------------------------------- #
from cyberpulse.models import Finding  # noqa: E402  (avoid circular import at top)

def enrich_findings(findings: List[Finding]) -> List[Finding]:
    """Populate each Finding with local CVE metadata (summary, date, refs)."""
    for f in findings:
        meta = get_cve_metadata(f.cve)
        if meta:
            f.summary = meta["summary"]
            f.published_date = meta["published_date"]
            f.references = meta["references"]
    return findings


# --------------------------------------------------------------------------- #
# Public convenience wrapper – called by cli.py
# --------------------------------------------------------------------------- #
def enrich(findings: List[Dict[str, Any]], *, use_cloud: bool = False) -> List[Dict[str, Any]]:
    """
    Normalised entry-point for the CLI.

    The current implementation ignores the *use_cloud* flag because live
    CVE look-ups are handled elsewhere (cloud.py).  We always fall back to
    the local SQLite cache.
    """
    # Cast away type concerns: parsers.parse() returns Dicts, but our internal
    # model uses Finding objects.  Both are “mapping-like” enough here.
    return enrich_findings(findings)  # type: ignore[arg-type]

# src/cyberpulse/models.py

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List

@dataclass
class Finding:
    id: str
    cve: str
    cvss_score: float
    host: str
    description: Optional[str] = None

    # Enriched fields (populated from offline DB)
    summary: Optional[str] = None
    published_date: Optional[date] = None
    references: List[str] = field(default_factory=list)

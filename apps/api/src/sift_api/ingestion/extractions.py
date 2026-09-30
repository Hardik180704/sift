"""Typed extraction records derived from parsed document text."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Extraction:
    extraction_type: str
    value: str
    confidence: float


def extract_dates(text: str) -> list[Extraction]:
    """Return explicitly written ISO dates only; never infer deadlines."""
    return [Extraction("date", match, 1.0) for match in re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text)]

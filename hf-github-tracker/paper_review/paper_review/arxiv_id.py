"""Detect and normalize arXiv identifiers from ids and URLs."""

from __future__ import annotations

import re

# New-style YYMM.NNNNN, optional version; old-style archive/YYMMNNN.
_ARXIV_ID = r"(?:(?:[a-z-]+(?:\.[A-Z]{2})?/\d{7})|(?:\d{4}\.\d{4,5}))(?:v\d+)?"
ARXIV_ID_RE = re.compile(rf"({_ARXIV_ID})", re.IGNORECASE)
ARXIV_URL_RE = re.compile(
    rf"(?:https?://)?(?:www\.)?arxiv\.org/(?:abs|html|pdf|e-print|src)/({_ARXIV_ID})(?:\.pdf)?",
    re.IGNORECASE,
)
HF_PAPERS_RE = re.compile(rf"huggingface\.co/papers/({_ARXIV_ID})", re.IGNORECASE)


def normalize_arxiv_id(value: str | None) -> str | None:
    """Return the canonical arXiv id without a version suffix, or None."""
    if not value:
        return None
    raw = value.strip()
    for pattern in (ARXIV_URL_RE, HF_PAPERS_RE):
        m = pattern.search(raw)
        if m:
            return _strip_version(m.group(1))
    m = ARXIV_ID_RE.fullmatch(raw)
    if m:
        return _strip_version(m.group(1))
    m = ARXIV_ID_RE.search(raw)
    if m and "arxiv" in raw.lower():
        return _strip_version(m.group(1))
    return None


def extract_arxiv_id(paper_id: str | None, *urls: str | None) -> str | None:
    for candidate in (paper_id, *urls):
        found = normalize_arxiv_id(candidate)
        if found:
            return found
    return None


def _strip_version(arxiv_id: str) -> str:
    return re.sub(r"v\d+$", "", arxiv_id, flags=re.IGNORECASE)

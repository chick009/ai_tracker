"""Same-day Hugging Face Daily Papers intake.

Fetches ``/api/daily_papers?date=YYYY-MM-DD&limit=100``, sorts by upvotes
descending, keeps the top ``intake_limit`` (default 20), classifies topics from
title+summary, and marks eligibility (core topics always; other categories need
an allowlisted lab).

Never falls back to another date: HTTP 400 or an empty list raises IntakeError.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from paper_review.config import DEFAULT_ALLOWLIST, INTAKE_LIMIT, USER_AGENT
from paper_review.models import Paper
from paper_review.select import is_allowlisted

log = logging.getLogger("paper_review")

HF_DAILY_PAPERS_URL = "https://huggingface.co/api/daily_papers"

CORE_CATEGORIES = frozenset({"Reasoning", "Agents", "Systems & efficiency"})

CATEGORIES = (
    "Reasoning",
    "Agents",
    "Multimodal",
    "Video & spatial",
    "Systems & efficiency",
    "Robotics",
    "Science & medicine",
    "Safety & analysis",
    "Other",
)

# (category, compiled patterns) — first match wins; ordered by specificity.
_CATEGORY_RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "Robotics",
        re.compile(
            r"\b(robot(?:ics|ic)?|embodied|manipulation|gripper|locomotion|"
            r"quadruped|humanoid|sim[- ]?to[- ]?real)\b",
            re.I,
        ),
    ),
    (
        "Video & spatial",
        re.compile(
            r"\b(video\b|spatial(?:ly)?|3d\b|scene graph|nerf|gaussian splat|"
            r"point cloud|egocentric|world model)\b",
            re.I,
        ),
    ),
    (
        "Agents",
        re.compile(
            r"\b(multi[- ]?agent|llm agent|ai agent|agentic|tool[- ]?use|"
            r"computer[- ]?use|gui agent|browser agent|web agent|"
            r"software engineer(?:ing)? agent|coding agent|"
            r"autonomous agent|agent (?:benchmark|framework|swarm))\b",
            re.I,
        ),
    ),
    (
        "Systems & efficiency",
        re.compile(
            r"\b(speculative decoding|kv[- ]?cache|quantiz(?:e|ation)|"
            r"inference (?:engine|serving|optim)|vllm|tensorrt|"
            r"throughput|latency|moe routing|model compression|"
            r"flash[- ]?attention|kernel|serving (?:stack|system)|"
            r"distillation for (?:efficiency|speed)|thin harness)\b",
            re.I,
        ),
    ),
    (
        "Reasoning",
        re.compile(
            r"\b(chain[- ]?of[- ]?thought|\bcot\b|reasoning|verifier|"
            r"math(?:ematical)? (?:reasoning|problem)|"
            r"on[- ]?policy distillation|policy[- ]?shift|"
            r"reinforcement learning.*(reason|math|think)|"
            r"think(?:ing)? (?:trace|step)|test[- ]?time (?:compute|scaling))\b",
            re.I,
        ),
    ),
    (
        "Multimodal",
        re.compile(
            r"\b(vision[- ]?language|\bvlm\b|multimodal|image[- ]?text|"
            r"visual (?:question|grounding|instruction)|"
            r"document (?:understanding|ai)|ocr)\b",
            re.I,
        ),
    ),
    (
        "Science & medicine",
        re.compile(
            r"\b(medical|clinic(?:al)?|biomed|biology|chemistry|protein|"
            r"drug discovery|genomics|scientific (?:discovery|agent)|"
            r"molecule|materials science)\b",
            re.I,
        ),
    ),
    (
        "Safety & analysis",
        re.compile(
            r"\b(jailbreak|safety|alignment|interpretab|red[- ]?team|"
            r"adversarial|hallucination|bias (?:audit|benchmark)|"
            r"mechanistic interpret)\b",
            re.I,
        ),
    ),
]


class IntakeError(RuntimeError):
    """Same-day HF Daily Papers could not be loaded (no date fallback)."""


def classify_category(title: str, summary: str) -> str:
    """Heuristic topic from title + abstract; contribution-oriented keywords."""
    blob = f"{title}\n{summary}"
    for category, pattern in _CATEGORY_RULES:
        if pattern.search(blob):
            return category
    # Soft fallbacks for short abstracts.
    lower = blob.lower()
    if "agent" in lower:
        return "Agents"
    if "reason" in lower or "think" in lower:
        return "Reasoning"
    if any(w in lower for w in ("efficient", "latency", "throughput", "inference")):
        return "Systems & efficiency"
    if any(w in lower for w in ("image", "vision", "visual")):
        return "Multimodal"
    return "Other"


def _org_strings(entry: dict[str, Any], paper: dict[str, Any]) -> tuple[str | None, str | None]:
    """Return (org_label-ish name, organization_field) from HF payload."""
    org = paper.get("organization") or entry.get("organization") or {}
    if not isinstance(org, dict):
        org = {}
    name = (org.get("fullname") or org.get("name") or "").strip() or None
    slug = (org.get("name") or "").strip() or None
    # Prefer a readable label; keep slug for allowlist matching.
    if name and slug and name.lower() != slug.lower():
        return name, f"{name} {slug}"
    return name, name or slug


def _match_allowlist(org_field: str | None, allowlist: tuple[str, ...]) -> bool:
    if not org_field:
        return False
    # Reuse Paper allowlist matching.
    probe = Paper(
        id="_",
        title="_",
        category="Other",
        eligible=False,
        upvotes=0,
        org_label=org_field,
        organization_field=org_field,
        hf_url=None,
        arxiv_url=None,
        github_repo=None,
        summary="",
    )
    return is_allowlisted(probe, allowlist)


def classify_eligibility(
    category: str,
    org_field: str | None,
    allowlist: tuple[str, ...] = DEFAULT_ALLOWLIST,
) -> tuple[bool, bool, str, str | None]:
    """Return (eligible, core, eligible_reason, skip_reason)."""
    core = category in CORE_CATEGORIES
    allowlisted = _match_allowlist(org_field, allowlist)
    if core:
        return (
            True,
            True,
            f"core topic ({category}) — no affiliation gate",
            None,
        )
    if allowlisted:
        return (
            True,
            False,
            f"non-core {category} with allowlisted lab",
            None,
        )
    return (
        False,
        False,
        "",
        f"non-core topic ({category}); no allowlisted affiliation",
    )


def _format_org_label(
    org_name: str | None,
    *,
    core: bool,
    allowlisted: bool,
    category: str,
) -> str:
    if org_name and allowlisted:
        tag = f"allowlisted；{'核心 ' + category if core else category}"
        return f"{org_name}（{tag}）"
    if org_name:
        return f"{org_name}（needs_verification）"
    if core:
        return f"空（needs_verification；核心主題免 gate）"
    return "空（needs_verification）"


def entry_to_paper(
    entry: dict[str, Any],
    *,
    allowlist: tuple[str, ...] = DEFAULT_ALLOWLIST,
) -> Paper:
    paper = entry.get("paper") or {}
    if not isinstance(paper, dict):
        paper = {}
    pid = str(paper.get("id") or "").strip()
    title = str(entry.get("title") or paper.get("title") or "").strip()
    summary = str(
        entry.get("summary")
        or paper.get("summary")
        or paper.get("ai_summary")
        or ""
    ).strip()
    upvotes = int(paper.get("upvotes") or entry.get("upvotes") or 0)
    org_name, org_field = _org_strings(entry, paper)
    category = classify_category(title, summary)
    eligible, core, eligible_reason, skip_reason = classify_eligibility(
        category, org_field, allowlist
    )
    allowlisted = _match_allowlist(org_field, allowlist)
    org_label = _format_org_label(
        org_name, core=core, allowlisted=allowlisted, category=category
    )
    arxiv_url = f"https://arxiv.org/abs/{pid}" if pid else None
    hf_url = f"https://huggingface.co/papers/{pid}" if pid else None
    github = paper.get("githubRepo") or paper.get("github_repo")
    project = paper.get("projectPage") or paper.get("project_page")
    return Paper(
        id=pid,
        title=title,
        category=category,
        eligible=eligible,
        upvotes=upvotes,
        org_label=org_label,
        organization_field=org_field,
        hf_url=hf_url,
        arxiv_url=arxiv_url,
        github_repo=str(github) if github else None,
        summary=summary,
        core=core,
        project_page=str(project) if project else None,
        skip_reason=skip_reason,
        arxiv_id=pid or None,
    )


def paper_to_curation_dict(paper: Paper, *, eligible_reason: str = "") -> dict[str, Any]:
    """Serialize a Paper into the curation JSON schema used by samples/."""
    if paper.eligible and not eligible_reason:
        if paper.core:
            eligible_reason = f"core topic ({paper.category}) — no affiliation gate"
        else:
            eligible_reason = f"non-core {paper.category} with allowlisted lab"
    return {
        "id": paper.id,
        "title": paper.title,
        "category": paper.category,
        "secondary": [],
        "core": paper.core,
        "eligible": paper.eligible,
        "eligible_reason": eligible_reason if paper.eligible else None,
        "affiliation_status": (
            "not_required_core"
            if paper.core
            else ("allowlisted" if paper.eligible else "needs_verification")
        ),
        "organization_field": paper.organization_field,
        "aff_label": None,
        "org_label": paper.org_label,
        "upvotes": paper.upvotes,
        "hf_url": paper.hf_url,
        "arxiv_url": paper.arxiv_url,
        "github_repo": paper.github_repo,
        "project_page": paper.project_page,
        "summary": paper.summary,
        "skip_reason": paper.skip_reason,
    }


def fetch_daily_papers(day: str, *, limit: int = 100, timeout_sec: int = 30) -> list[dict[str, Any]]:
    """GET HF Daily Papers for an exact date. Raises IntakeError on 400/empty/network."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
        raise IntakeError(f"invalid date {day!r}; expected YYYY-MM-DD")
    # Validate calendar date (rejects 2026-10-32 etc. before the API does).
    try:
        date.fromisoformat(day)
    except ValueError as exc:
        raise IntakeError(f"invalid calendar date {day!r}: {exc}") from exc

    qs = urlencode({"date": day, "limit": str(limit)})
    url = f"{HF_DAILY_PAPERS_URL}?{qs}"
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(req, timeout=timeout_sec) as resp:
            status = getattr(resp, "status", 200)
            body = resp.read()
    except HTTPError as exc:
        raise IntakeError(
            f"HF Daily Papers returned HTTP {exc.code} for date={day}; "
            "refusing to fall back to another issue"
        ) from exc
    except URLError as exc:
        raise IntakeError(f"HF Daily Papers network error for date={day}: {exc}") from exc

    if status and status >= 400:
        raise IntakeError(
            f"HF Daily Papers returned HTTP {status} for date={day}; "
            "refusing to fall back to another issue"
        )
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntakeError(f"HF Daily Papers returned non-JSON for date={day}") from exc
    if not isinstance(data, list):
        raise IntakeError(
            f"HF Daily Papers returned unexpected payload type {type(data).__name__} "
            f"for date={day}"
        )
    if len(data) == 0:
        raise IntakeError(
            f"HF Daily Papers returned 0 papers for date={day}; "
            "refusing to fall back to another issue"
        )
    log.info("fetched %d HF Daily Papers for %s", len(data), day)
    return data


def take_top_by_upvotes(papers: list[Paper], intake_limit: int = INTAKE_LIMIT) -> list[Paper]:
    """Sort by upvotes descending (id ASC tie-break), keep the top N."""
    ordered = sorted(papers, key=lambda p: (-p.upvotes, p.id))
    if intake_limit <= 0:
        return ordered
    return ordered[:intake_limit]


def build_curation_from_entries(
    entries: list[dict[str, Any]],
    *,
    collect_date: str,
    intake_limit: int = INTAKE_LIMIT,
    allowlist: tuple[str, ...] = DEFAULT_ALLOWLIST,
) -> dict[str, Any]:
    """Classify, sort, trim to intake_limit, and emit curation JSON."""
    papers = [entry_to_paper(e, allowlist=allowlist) for e in entries]
    # Drop entries with no id.
    papers = [p for p in papers if p.id]
    issue_total = len(papers)
    kept = take_top_by_upvotes(papers, intake_limit)
    eligible_ids = [p.id for p in kept if p.eligible]
    return {
        "collect_date": collect_date,
        "hf_issue_date": collect_date,
        "hf_date_fallback_note": None,
        "intake": {
            "source": "huggingface_daily_papers_api",
            "issue_total": issue_total,
            "intake_limit": intake_limit,
            "kept": len(kept),
        },
        "counts": {
            "issue_total": issue_total,
            "intake": len(kept),
            "eligible": len(eligible_ids),
            "by_category": _count_categories(kept),
        },
        "shortlist_ids": [p.id for p in kept],
        "eligible_ids": eligible_ids,
        "skipped_repeat_ids": [],
        "not_selected_ids": [p.id for p in papers if p.id not in {k.id for k in kept}],
        "papers": [paper_to_curation_dict(p) for p in kept],
    }


def _count_categories(papers: list[Paper]) -> dict[str, int]:
    out: dict[str, int] = {}
    for p in papers:
        out[p.category] = out.get(p.category, 0) + 1
    return out


def build_curation_for_date(
    day: str,
    *,
    intake_limit: int = INTAKE_LIMIT,
    allowlist: tuple[str, ...] = DEFAULT_ALLOWLIST,
    timeout_sec: int = 30,
) -> dict[str, Any]:
    entries = fetch_daily_papers(day, timeout_sec=timeout_sec)
    return build_curation_from_entries(
        entries,
        collect_date=day,
        intake_limit=intake_limit,
        allowlist=allowlist,
    )


def save_curation(curation: dict[str, Any], path) -> None:
    path = path  # pathlib Path or str
    from pathlib import Path

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(curation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

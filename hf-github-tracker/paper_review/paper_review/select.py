"""Topic filter, upvote/lab gate, and diversified ranking."""

from __future__ import annotations

from collections import Counter

from paper_review.config import Settings
from paper_review.models import Paper, SkippedNote


def is_allowlisted(paper: Paper, allowlist: tuple[str, ...]) -> bool:
    org = " ".join(
        part for part in (paper.org_label, paper.organization_field) if part
    ).lower()
    if "allowlisted" in org:
        return True
    for token in allowlist:
        token = token.lower().strip()
        if token and token in org:
            return True
    return False


def passes_gate(paper: Paper, settings: Settings) -> tuple[bool, str]:
    if paper.upvotes >= settings.min_upvotes:
        return True, "upvotes"
    if is_allowlisted(paper, settings.allowlist) and paper.upvotes >= settings.min_allowlist_traction:
        return True, "allowlisted_lab"
    if is_allowlisted(paper, settings.allowlist):
        return False, (
            f"allowlisted lab but traction {paper.upvotes} "
            f"< {settings.min_allowlist_traction}"
        )
    return False, f"upvotes {paper.upvotes} < {settings.min_upvotes}"


def topic_and_gate(
    papers: list[Paper],
    settings: Settings,
) -> tuple[list[Paper], list[Paper], list[SkippedNote]]:
    """Return (gated, topic_eligible, skipped)."""
    skipped: list[SkippedNote] = []
    eligible: list[Paper] = []
    gated: list[Paper] = []
    for paper in papers:
        if not paper.eligible:
            skipped.append(
                SkippedNote(
                    paper_id=paper.id,
                    title=paper.title,
                    reason=paper.skip_reason or "not topic-eligible",
                    upvotes=paper.upvotes,
                )
            )
            continue
        eligible.append(paper)
        ok, reason = passes_gate(paper, settings)
        if ok:
            gated.append(paper)
        else:
            skipped.append(
                SkippedNote(
                    paper_id=paper.id,
                    title=paper.title,
                    reason=f"gate: {reason}",
                    upvotes=paper.upvotes,
                )
            )
    return gated, eligible, skipped


def rank_top(
    papers: list[Paper],
    settings: Settings,
) -> tuple[list[Paper], list[Paper]]:
    """Rank by upvotes; cap per-category so the top-N is not one topic."""
    ordered = sorted(papers, key=lambda p: (-p.upvotes, p.id))
    picked: list[Paper] = []
    deferred: list[Paper] = []
    counts: Counter[str] = Counter()
    for paper in ordered:
        if len(picked) >= settings.top_n:
            deferred.append(paper)
            continue
        cat = paper.category or "Other"
        if counts[cat] >= settings.max_per_category:
            # Defer if a later paper from another category could still fill a slot.
            later_other = any(
                q.category != cat for q in ordered if q not in picked and q is not paper
            )
            if later_other:
                deferred.append(paper)
                continue
        picked.append(paper)
        counts[cat] += 1
    for paper in deferred:
        if len(picked) >= settings.top_n:
            break
        picked.append(paper)
    picked_ids = {p.id for p in picked}
    leftover = [p for p in ordered if p.id not in picked_ids]
    return picked[: settings.top_n], leftover

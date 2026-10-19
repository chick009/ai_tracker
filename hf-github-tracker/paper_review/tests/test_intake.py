"""Same-day HF Daily Papers intake: top-N by upvotes, no date fallback."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError

import pytest

from paper_review.intake import (
    IntakeError,
    build_curation_from_entries,
    classify_category,
    classify_eligibility,
    entry_to_paper,
    fetch_daily_papers,
    take_top_by_upvotes,
)
from paper_review.models import Paper


def _entry(pid: str, title: str, summary: str, upvotes: int, org: str | None = None) -> dict:
    organization = {"name": org, "fullname": org} if org else None
    return {
        "title": title,
        "summary": summary,
        "organization": organization,
        "paper": {
            "id": pid,
            "title": title,
            "summary": summary,
            "upvotes": upvotes,
            "organization": organization,
            "githubRepo": None,
            "projectPage": None,
        },
    }


def test_take_top_by_upvotes_descending_limit_20():
    papers = [
        Paper(
            id=f"2610.{i:05d}",
            title=f"T{i}",
            category="Agents",
            eligible=True,
            upvotes=i,
            org_label=None,
            organization_field=None,
            hf_url=None,
            arxiv_url=None,
            github_repo=None,
            summary="",
        )
        for i in range(1, 36)  # 35 papers, upvotes 1..35
    ]
    kept = take_top_by_upvotes(papers, intake_limit=20)
    assert len(kept) == 20
    assert [p.upvotes for p in kept] == list(range(35, 15, -1))
    assert kept[0].id == "2610.00035"
    assert kept[-1].id == "2610.00016"


def test_take_top_tie_break_by_id():
    papers = [
        Paper(
            id="2610.00002",
            title="b",
            category="Agents",
            eligible=True,
            upvotes=50,
            org_label=None,
            organization_field=None,
            hf_url=None,
            arxiv_url=None,
            github_repo=None,
            summary="",
        ),
        Paper(
            id="2610.00001",
            title="a",
            category="Agents",
            eligible=True,
            upvotes=50,
            org_label=None,
            organization_field=None,
            hf_url=None,
            arxiv_url=None,
            github_repo=None,
            summary="",
        ),
    ]
    kept = take_top_by_upvotes(papers, intake_limit=2)
    assert [p.id for p in kept] == ["2610.00001", "2610.00002"]


def test_build_curation_trims_to_intake_limit():
    entries = [
        _entry(f"2610.{i:05d}", f"Agent system {i}", "an LLM agent benchmark", i)
        for i in range(1, 31)
    ]
    curation = build_curation_from_entries(
        entries, collect_date="2026-10-19", intake_limit=20
    )
    assert curation["intake"]["issue_total"] == 30
    assert curation["intake"]["kept"] == 20
    assert len(curation["papers"]) == 20
    ups = [p["upvotes"] for p in curation["papers"]]
    assert ups == sorted(ups, reverse=True)
    assert ups[0] == 30
    assert ups[-1] == 11
    assert curation["hf_issue_date"] == "2026-10-19"
    assert curation["hf_date_fallback_note"] is None


def test_core_topic_always_eligible():
    eligible, core, reason, skip = classify_eligibility("Agents", None)
    assert eligible and core and skip is None
    assert "core" in reason.lower()


def test_non_core_needs_allowlist():
    eligible, core, _, skip = classify_eligibility("Multimodal", None)
    assert not eligible and not core and skip
    eligible2, _, _, skip2 = classify_eligibility("Multimodal", "Microsoft Research")
    assert eligible2 and skip2 is None


def test_classify_agents_and_robotics():
    assert classify_category("A GUI agent for computer use", "browser tool use") == "Agents"
    assert classify_category("Embodied robot manipulation", "gripper locomotion") == "Robotics"


def test_entry_to_paper_schema_fields():
    e = _entry(
        "2610.22471",
        "Has GPT-6-Astra Achieved Embodied Intelligence?",
        "robotic manipulation and navigation via in-context learning",
        113,
        org="SenseNova",
    )
    p = entry_to_paper(e)
    assert p.id == "2610.22471"
    assert p.upvotes == 113
    assert p.category == "Robotics"
    assert p.hf_url.endswith("/2610.22471")
    assert p.arxiv_url.endswith("/2610.22471")


def test_fetch_refuses_http_400(monkeypatch):
    def boom(*_a, **_k):
        raise HTTPError(
            url="https://huggingface.co/api/daily_papers?date=2099-01-01",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr("paper_review.intake.urlopen", boom)
    with pytest.raises(IntakeError, match="HTTP 400"):
        fetch_daily_papers("2099-01-01")


def test_fetch_refuses_empty_list(monkeypatch):
    class FakeResp:
        status = 200

        def read(self):
            return b"[]"

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr("paper_review.intake.urlopen", lambda *_a, **_k: FakeResp())
    with pytest.raises(IntakeError, match="0 papers"):
        fetch_daily_papers("2026-10-18")


def test_fetch_rejects_invalid_date():
    with pytest.raises(IntakeError, match="invalid"):
        fetch_daily_papers("2026-10-32")

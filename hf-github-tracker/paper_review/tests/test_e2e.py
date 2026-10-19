"""End-to-end mock run on the uploaded 2026-10-19 curation JSON (live arXiv)."""

from __future__ import annotations

from pathlib import Path

import pytest

from paper_review.figures import invented_remote_images
from paper_review.pipeline import run_daily

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "samples" / "2026-10-19-papers-curation.json"


@pytest.mark.network
def test_e2e_sample_mock(tmp_path: Path):
    if not SAMPLE.exists():
        pytest.skip("sample curation JSON missing")
    cache = ROOT / ".cache" / "papers"
    out = tmp_path / "out"
    review = run_daily(
        SAMPLE,
        out,
        date="2026-10-19",
        cache_dir=cache,
        runner="mock",
    )
    html_path = out / "review-2026-10-19.html"
    assert html_path.exists()
    html = html_path.read_text(encoding="utf-8")
    assert review.funnel.issue_total == 84
    assert review.funnel.topic_eligible == 54
    assert review.funnel.gate >= 5
    assert review.funnel.extractable >= 1
    assert 1 <= len(review.cards) <= 5
    assert "data:image" in html, "expected at least one inlined arXiv figure"
    assert invented_remote_images(html) == []
    for card in review.cards:
        assert card.method_figure is not None
        assert Path(card.method_figure.path).exists()
        assert f'data-fig-id="{card.method_figure.fig_id}"' in html
        assert card.paper.title in html
        assert "Text source:" in html
    assert "issue" in html and "topic-eligible" in html

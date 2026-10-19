import json
from pathlib import Path

import paper_review.curated as curated
from paper_review.llm.base import LLMError, LLMRunner
from paper_review.llm.mock import MockRunner
from paper_review.models import ExtractResult, Figure


def _png(path: Path) -> Path:
    path.write_bytes(
        bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
            "890000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"
        )
    )
    return path


class BrokenRunner(LLMRunner):
    name = "broken"

    def complete(self, prompt, *, max_turns=4, label=""):
        raise LLMError("boom")


def _setup(tmp_path, monkeypatch):
    rows = [
        {"id": f"2610.0000{i}", "title": f"Paper {i}", "abstract": "We build an agent.", "upvotes": 10 - i, "topic": "Agents"}
        for i in range(3)
    ]
    s1 = rows + [{"id": "2610.00009", "title": "Robot paper", "abstract": "x", "upvotes": 50}]
    (tmp_path / "s1.json").write_text(json.dumps(s1))
    (tmp_path / "s2.json").write_text(json.dumps(rows))
    (tmp_path / "s3.json").write_text(json.dumps(rows[:2]))

    def fake_extract(arxiv_id, cache_dir, abstract="", force=False, session=None, **kw):
        d = cache_dir / arxiv_id
        d.mkdir(parents=True, exist_ok=True)
        png = _png(d / "fig-1.png")
        fig = Figure("fig-1", "Figure 1: Overview of the framework.", "https://arxiv.org/html/x/x1.png", png.name, str(png))
        return ExtractResult(arxiv_id, "arxiv_html", None, True, True, 100, "We build an agent. " * 20, [fig], 1, [], 0.0, str(d))

    monkeypatch.setattr(curated, "extract_paper", fake_extract)


def test_curated_all_cards(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    out = tmp_path / "r.html"
    review = curated.run_curated(
        date="2026-10-19", step1=tmp_path / "s1.json", step2=tmp_path / "s2.json", top=tmp_path / "s3.json",
        out_html=out, cache_dir=tmp_path / "cache", runner=MockRunner(), topic_labels={"2610.00009": "Robotics"},
    )
    html = out.read_text()
    assert len(review.cards) == 2 and not review.failed
    assert [n for _, n in review.funnel] == [4, 3, 2, 2, 2]
    assert html.count('class="card"') == 2
    assert "Robotics" in html and "Paper 2" in html  # topic-dropped + below-cut lists
    assert "Also notable" not in html
    assert "src=\"https://" not in html


def test_curated_failed_card_is_visible(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    out = tmp_path / "r.html"
    review = curated.run_curated(
        date="2026-10-19", step1=tmp_path / "s1.json", step2=tmp_path / "s2.json", top=tmp_path / "s3.json",
        out_html=out, cache_dir=tmp_path / "cache", runner=BrokenRunner(),
    )
    assert len(review.failed) == 2 and not review.cards
    assert out.read_text().count("Card failed:") == 2

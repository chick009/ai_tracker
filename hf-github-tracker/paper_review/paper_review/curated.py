"""Curated-list run: take an already-filtered list of papers (steps 1-3 done
upstream), extract (step 4), run the 3-call LLM card flow, and render one
self-contained HTML page. No top-5 cut: every paper becomes a card, or a
visible 'card failed' entry. Nothing is dropped silently."""

from __future__ import annotations

import html
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from paper_review.extract import extract_paper, make_session
from paper_review.figures import invented_remote_images, pick_method_figure, pick_results_figure
from paper_review.html_render import CSS, render_card
from paper_review.llm.base import LLMError, LLMRunner
from paper_review.llm.flow import run_card_flow
from paper_review.models import Paper, ReviewCard

log = logging.getLogger("paper_review")

CORE_TOPICS = {"Agents", "Systems", "Systems & efficiency", "Reasoning"}


@dataclass
class FilteredLine:
    id: str
    title: str
    upvotes: int
    reason: str


@dataclass
class FailedCard:
    paper: Paper
    reason: str


@dataclass
class CuratedReview:
    date: str
    funnel: list[tuple[str, int]]
    cards: list[ReviewCard]
    failed: list[FailedCard]
    topic_dropped: list[FilteredLine]
    below_cut: list[FilteredLine]
    order: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def paper_from_step(raw: dict) -> Paper:
    pid = str(raw["id"])
    return Paper(
        id=pid,
        title=str(raw.get("title") or ""),
        category=str(raw.get("topic") or raw.get("category") or "Other"),
        eligible=True,
        upvotes=int(raw.get("upvotes") or 0),
        org_label=raw.get("org_label"),
        organization_field=None,
        hf_url=f"https://huggingface.co/papers/{pid}",
        arxiv_url=f"https://arxiv.org/abs/{pid}",
        github_repo=raw.get("github_repo"),
        summary=str(raw.get("abstract") or raw.get("summary") or ""),
        core=True,
        arxiv_id=pid,
    )


def _one(paper: Paper, cache_dir: Path, runner: LLMRunner, force: bool):
    session = make_session()
    try:
        ext = extract_paper(paper.arxiv_id, cache_dir, abstract=paper.summary, session=session)
    except Exception as exc:  # noqa: BLE001
        return FailedCard(paper, f"extract error: {exc}")
    finally:
        session.close()
    if not ext.extractable:
        return FailedCard(paper, ext.skip_reason or "not extractable")
    try:
        facts, critique, copy = run_card_flow(paper, ext, runner, force=force)
    except LLMError as exc:
        return FailedCard(paper, f"LLM failed after retry: {exc}")
    except Exception as exc:  # noqa: BLE001
        log.exception("[%s] card crashed", paper.id)
        return FailedCard(paper, f"card error: {exc}")
    method = pick_method_figure(ext.figures, copy.method_figure_id)
    results = pick_results_figure(ext.figures, method.fig_id if method else None, copy.results_figure_id)
    return ReviewCard(paper, ext, facts, critique, copy, method, results)


def build_cards(papers: list[Paper], cache_dir: Path, runner: LLMRunner, *, workers: int = 3, force: bool = False):
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        results = list(pool.map(lambda p: _one(p, cache_dir, runner, force), papers))
    cards = [r for r in results if isinstance(r, ReviewCard)]
    failed = [r for r in results if isinstance(r, FailedCard)]
    return cards, failed


def _failed_html(f: FailedCard, index: int) -> str:
    p = f.paper
    return f"""
<article class="card failed" id="paper-{html.escape(p.id)}" style="--tone:#9b2c2c">
  <header class="card-head">
    <div class="kicker"><span class="idx">{index}</span><span class="cat">{html.escape(p.category)}</span>
    <span class="votes">{p.upvotes} upvotes</span><span class="cat">card failed</span></div>
    <h2><a href="{html.escape(p.hf_url or '#')}">{html.escape(p.title)}</a></h2>
  </header>
  <p class="empty">Card failed: {html.escape(f.reason)}</p>
</article>"""


def _filtered_list(items: list[FilteredLine]) -> str:
    if not items:
        return "<p class='empty'>None.</p>"
    lis = "".join(
        f'<li><a href="https://huggingface.co/papers/{html.escape(i.id)}">{html.escape(i.title)}</a> '
        f"<span class='dim'>({i.upvotes} upvotes · {html.escape(i.reason)})</span></li>"
        for i in items
    )
    return f"<ul>{lis}</ul>"


EXTRA_CSS = """
.dim { color: var(--muted); }
.card.failed { opacity: .85; }
.filtered h3 { margin-top: 18px; }
.filtered li { font-size: 14px; font-family: ui-sans-serif, system-ui, sans-serif; }
"""


def render_curated(review: CuratedReview) -> str:
    funnel = " → ".join(f"<span><b>{n}</b> {html.escape(label)}</span>" for label, n in review.funnel)
    by_id: dict[str, str] = {}
    blocks = []
    cards = {c.paper.id: c for c in review.cards}
    failed = {f.paper.id: f for f in review.failed}
    for i, pid in enumerate(review.order, start=1):
        if pid in cards:
            blocks.append(render_card(cards[pid], i))
        elif pid in failed:
            blocks.append(_failed_html(failed[pid], i))
    body = "\n".join(blocks)
    if invented_remote_images(body):
        raise RuntimeError("refused to embed a remote image URL")
    n_total = len(review.order)
    date = html.escape(review.date)
    notes = "".join(f"<p>{html.escape(n)}</p>" for n in review.notes)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Methodology review · {date}</title>
  <style>{CSS}{EXTRA_CSS}</style>
</head>
<body>
  <div class="wrap">
    <header class="mast">
      <p class="eyebrow">HF Daily Papers · methodology cards</p>
      <h1>Core methods, with the paper’s own figure</h1>
      <p class="lede">HF issue {date}. The {n_total} most-upvoted papers on Agents, Systems and Reasoning whose full text and a real figure could be pulled from arXiv. Each card walks through the method in plain English, following the paper’s own figure.</p>
      <div class="funnel">{funnel}</div>
    </header>
    {body}
    <section class="skipped filtered">
      <h2>Filtered out</h2>
      <details><summary>{len(review.topic_dropped)} dropped at the topic filter (not Agents / Systems / Reasoning)</summary>
      {_filtered_list(review.topic_dropped)}</details>
      <details><summary>{len(review.below_cut)} on-topic but below the top-{n_total} upvote cut</summary>
      {_filtered_list(review.below_cut)}</details>
    </section>
    <footer class="note">
      Figures are downloaded from arXiv HTML and inlined as data URIs. Image URLs are never invented.
      {notes}
    </footer>
  </div>
</body>
</html>
"""


def run_curated(
    *,
    date: str,
    step1: Path,
    step2: Path,
    top: Path,
    out_html: Path,
    cache_dir: Path,
    runner: LLMRunner,
    topic_labels: dict[str, str] | None = None,
    workers: int = 3,
    force: bool = False,
) -> CuratedReview:
    t0 = time.time()
    s1 = json.loads(step1.read_text(encoding="utf-8"))
    s2 = json.loads(step2.read_text(encoding="utf-8"))
    s3 = json.loads(top.read_text(encoding="utf-8"))
    papers = [paper_from_step(r) for r in s3]
    s2_ids = {r["id"] for r in s2}
    top_ids = {r["id"] for r in s3}
    labels = topic_labels or {}
    topic_dropped = [
        FilteredLine(r["id"], r["title"], int(r.get("upvotes") or 0), labels.get(r["id"], "Other"))
        for r in s1
        if r["id"] not in s2_ids
    ]
    topic_dropped.sort(key=lambda x: -x.upvotes)
    below_cut = [
        FilteredLine(r["id"], r["title"], int(r.get("upvotes") or 0), r.get("topic") or "")
        for r in s2
        if r["id"] not in top_ids
    ]
    cards, failed = build_cards(papers, cache_dir, runner, workers=workers, force=force)
    extractable = len(papers) - sum(1 for f in failed if not f.reason.startswith(("LLM", "card")))
    review = CuratedReview(
        date=date,
        funnel=[
            ("collected", len(s1)),
            ("topic filter", len(s2)),
            ("top by upvotes", len(papers)),
            ("extractable", extractable),
            ("cards", len(cards)),
        ],
        cards=cards,
        failed=failed,
        topic_dropped=topic_dropped,
        below_cut=below_cut,
        order=[p.id for p in papers],
        notes=[f"runner={runner.name}", f"elapsed_sec={round(time.time() - t0, 1)}"],
    )
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(render_curated(review), encoding="utf-8")
    return review

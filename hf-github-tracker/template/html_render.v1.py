"""Render one self-contained daily review HTML file (images inlined as data URIs)."""

from __future__ import annotations

import base64
import html
import mimetypes
from pathlib import Path

from paper_review.figures import (
    clean_caption,
    ensure_figure_embedded,
    invented_remote_images,
    pick_method_figure,
)
from paper_review.models import DailyReview, Figure, ReviewCard, source_label

CATEGORY_TONE = {
    "Agents": "#275b4e",
    "Reasoning": "#7a3b16",
    "Systems & efficiency": "#1f3d6b",
    "Multimodal": "#5b2d6b",
    "Video & spatial": "#3d4a1f",
    "Robotics": "#4a2c17",
    "Other": "#4a433a",
}


def _data_uri(path: str) -> str:
    p = Path(path)
    mime, _ = mimetypes.guess_type(p.name)
    if not mime:
        suffix = p.suffix.lower()
        mime = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".svg": "image/svg+xml",
        }.get(suffix, "application/octet-stream")
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _img(fig: Figure, css_class: str) -> str:
    uri = _data_uri(fig.path)
    cap = html.escape(clean_caption(fig.caption))
    alt = html.escape((fig.label or fig.fig_id) + " — " + fig.caption[:180])
    return (
        f'<figure class="{css_class}" data-fig-id="{html.escape(fig.fig_id)}">'
        f'<img data-fig-id="{html.escape(fig.fig_id)}" src="{uri}" alt="{alt}" />'
        f"<figcaption>{cap}</figcaption></figure>"
    )


def _links(card: ReviewCard) -> str:
    p = card.paper
    bits = []
    if p.hf_url:
        bits.append(f'<a href="{html.escape(p.hf_url)}">HF</a>')
    if p.arxiv_url:
        bits.append(f'<a href="{html.escape(p.arxiv_url)}">arXiv</a>')
    if p.github_repo:
        bits.append(f'<a href="{html.escape(p.github_repo)}">code</a>')
    if p.project_page:
        bits.append(f'<a href="{html.escape(p.project_page)}">project</a>')
    return " · ".join(bits)


def _bullets(items: list[str]) -> str:
    lis = "".join(f"<li>{html.escape(x)}</li>" for x in items if x)
    return f"<ul>{lis}</ul>" if lis else "<p class='empty'>Not stated in the extracted text.</p>"


def render_card(card: ReviewCard, index: int) -> str:
    paper = card.paper
    tone = CATEGORY_TONE.get(paper.category, CATEGORY_TONE["Other"])
    org = html.escape(paper.org_label or paper.organization_field or "unlisted lab")
    title = html.escape(paper.title)
    href = html.escape(paper.hf_url or paper.arxiv_url or "#")
    src = source_label(card.extract.source)
    fig_html = ""
    method_fig = card.method_figure
    if method_fig is None:
        method_fig = pick_method_figure(card.extract.figures)
    if method_fig:
        fig_html += _img(method_fig, "method-fig")
    marker = f"<!--fig-slot-{paper.id}-->"
    if card.results_figure and (
        not method_fig or card.results_figure.fig_id != method_fig.fig_id
    ):
        fig_html += _img(card.results_figure, "results-fig")
    fig_html += marker
    if "data-fig-id=" not in fig_html and card.extract.figures:
        fallback = pick_method_figure(card.extract.figures)
        if fallback:
            fig_html = _img(fallback, "method-fig auto-appended") + fig_html
    fig_html = ensure_figure_embedded(fig_html, card.extract.figures, card_marker=marker)
    fig_html = fig_html.replace(marker, "")
    if invented_remote_images(fig_html):
        raise RuntimeError(f"{paper.id}: refused to embed a remote image URL")
    return f"""
<article class="card" id="paper-{html.escape(paper.id)}" style="--tone:{tone}">
  <header class="card-head">
    <div class="kicker">
      <span class="idx">{index}</span>
      <span class="cat">{html.escape(paper.category)}</span>
      <span class="votes">{paper.upvotes} upvotes</span>
    </div>
    <h2><a href="{href}">{title}</a></h2>
    <p class="meta">{org} · {_links(card)} · Text source: {html.escape(src)}</p>
  </header>
  {fig_html}
  <section>
    <h3>Problem</h3>
    <p>{html.escape(card.copy.problem)}</p>
  </section>
  <section>
    <h3>Core method</h3>
    {_bullets(card.copy.core_method)}
  </section>
  <section>
    <h3>Results</h3>
    {_bullets(card.copy.results)}
  </section>
  <section class="split">
    <div>
      <h3>Why it matters</h3>
      <p>{html.escape(card.copy.why_it_matters)}</p>
    </div>
    <div>
      <h3>Caveats</h3>
      <p>{html.escape(card.copy.caveats)}</p>
    </div>
  </section>
</article>
"""


CSS = """
:root {
  --bg: #f4efe4;
  --ink: #1c1814;
  --muted: #6a5f53;
  --paper: #fffcf6;
  --line: #e4d8c4;
  --accent: #b4532a;
  --chip: #efe6d4;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--ink); }
body {
  font-family: "Iowan Old Style", Palatino, "Palatino Linotype", "Times New Roman", serif;
  line-height: 1.55;
  font-size: 18px;
}
.wrap { max-width: 860px; margin: 0 auto; padding: 32px 20px 80px; }
header.mast {
  border-bottom: 2px solid var(--ink);
  padding-bottom: 20px;
  margin-bottom: 28px;
}
header.mast p.eyebrow {
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-size: 12px;
  color: var(--accent);
  margin: 0 0 8px;
  font-family: ui-sans-serif, system-ui, sans-serif;
}
h1 { font-size: 34px; line-height: 1.15; margin: 0 0 10px; font-weight: 700; }
.lede { color: var(--muted); margin: 0 0 18px; }
.funnel {
  display: flex; flex-wrap: wrap; gap: 8px;
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 13px;
}
.funnel span {
  background: var(--chip); border: 1px solid var(--line);
  padding: 6px 10px; border-radius: 999px;
}
.funnel b { font-variant-numeric: tabular-nums; }
.card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-left: 6px solid var(--tone, var(--accent));
  border-radius: 10px;
  padding: 22px 22px 8px;
  margin: 22px 0 36px;
  box-shadow: 0 1px 0 rgba(28,24,20,0.04);
}
.card-head h2 { font-size: 24px; margin: 6px 0 8px; }
.card-head h2 a { color: inherit; text-decoration: none; }
.card-head h2 a:hover { text-decoration: underline; }
.kicker {
  display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 12px; letter-spacing: 0.04em; text-transform: uppercase;
}
.idx {
  background: var(--tone, var(--accent)); color: #fff;
  width: 22px; height: 22px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-weight: 700;
}
.cat, .votes {
  background: var(--chip); padding: 3px 8px; border-radius: 999px;
}
.meta { color: var(--muted); font-size: 14px; margin: 0 0 14px; }
.meta a { color: var(--accent); }
figure { margin: 12px 0 18px; }
figure img {
  width: 100%; height: auto; display: block;
  background: #fff; border: 1px solid var(--line); border-radius: 6px;
}
figcaption {
  font-size: 13px; color: var(--muted); margin-top: 8px;
  font-family: ui-sans-serif, system-ui, sans-serif;
}
h3 {
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--accent); margin: 16px 0 6px;
}
section p, section li { font-size: 17px; }
ul { margin: 0 0 12px 1.1em; padding: 0; }
li { margin: 0 0 6px; }
.split { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.split p { font-size: 16px; color: var(--muted); }
.also, .skipped {
  border-top: 1px solid var(--line); padding-top: 18px; margin-top: 12px;
}
.also h2, .skipped h2 { font-size: 20px; margin: 0 0 10px; }
.also li, .skipped li {
  font-size: 15px; color: var(--ink);
  font-family: ui-sans-serif, system-ui, sans-serif;
}
.skipped details summary {
  cursor: pointer; color: var(--muted);
  font-family: ui-sans-serif, system-ui, sans-serif;
}
.empty { color: var(--muted); font-style: italic; }
footer.note {
  margin-top: 40px; color: var(--muted); font-size: 13px;
  font-family: ui-sans-serif, system-ui, sans-serif;
}
@media (max-width: 700px) {
  body { font-size: 16px; }
  h1 { font-size: 26px; }
  .split { grid-template-columns: 1fr; }
  .wrap { padding: 20px 14px 60px; }
  .card { padding: 16px 14px 6px; }
}
"""


def render_review(review: DailyReview) -> str:
    funnel = " → ".join(
        f"<span><b>{n}</b> {html.escape(label)}</span>" for label, n in review.funnel.as_parts()
    )
    cards = "\n".join(render_card(c, i) for i, c in enumerate(review.cards, start=1))
    notable_items = []
    for n in review.notable:
        title = html.escape(n.title)
        href = html.escape(n.hf_url or "#")
        org = html.escape(n.org_label or "")
        notable_items.append(
            f'<li><a href="{href}">{title}</a> '
            f"({html.escape(n.category)}, {n.upvotes} upvotes{', ' + org if org else ''})</li>"
        )
    notable_html = (
        "<section class='also'><h2>Also notable</h2>"
        + ("<ul>" + "".join(notable_items) + "</ul>" if notable_items else "<p class='empty'>No other extractable papers passed the gate.</p>")
        + "</section>"
    )
    skipped_items = [
        f"<li><b>{html.escape(s.paper_id)}</b> {html.escape(s.title)} — {html.escape(s.reason)}</li>"
        for s in review.skipped
    ]
    skipped_html = (
        "<section class='skipped'><h2>Skipped</h2>"
        "<details><summary>"
        f"{len(review.skipped)} papers dropped (topic, gate, or extractability)</summary>"
        + ("<ul>" + "".join(skipped_items) + "</ul>" if skipped_items else "<p class='empty'>None.</p>")
        + "</details></section>"
    )
    hf = html.escape(review.hf_issue_date or "unknown")
    date = html.escape(review.collect_date)
    extra_notes = "".join(f"<p>{html.escape(n)}</p>" for n in review.notes)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Methodology review · {date}</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="wrap">
    <header class="mast">
      <p class="eyebrow">HF Daily Papers · methodology cards</p>
      <h1>Core methods, with the paper’s own figure</h1>
      <p class="lede">Collect {date} · HF issue {hf}. Five papers whose full text and a real figure could be pulled from arXiv. Plain-English walkthroughs of the method, not a jargon TL;DR.</p>
      <div class="funnel">{funnel}</div>
    </header>
    {cards}
    {notable_html}
    {skipped_html}
    <footer class="note">
      Figures are downloaded from arXiv/ar5iv HTML and inlined as data URIs. Invented image URLs are never embedded.
      {extra_notes}
    </footer>
  </div>
</body>
</html>
"""


def write_review(review: DailyReview, path: Path) -> Path:
    html_text = render_review(review)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")
    return path

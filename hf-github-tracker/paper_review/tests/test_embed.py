from pathlib import Path

from paper_review.figures import (
    ensure_figure_embedded,
    html_embedded_ids,
    invented_remote_images,
)
from paper_review.html_render import render_review, write_review
from paper_review.models import (
    CardCopy,
    Critique,
    DailyReview,
    ExtractFacts,
    ExtractResult,
    Figure,
    Funnel,
    Paper,
    ReviewCard,
)


def _png(path: Path) -> Path:
    # 1x1 PNG
    path.write_bytes(
        bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
            "890000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"
        )
    )
    return path


def _figure(tmp: Path, fig_id: str = "fig-1", caption: str = "Figure 1: Overview of the method.") -> Figure:
    png = _png(tmp / f"{fig_id}.png")
    return Figure(
        fig_id=fig_id,
        caption=caption,
        url="https://arxiv.org/html/2610.21601/x1.png",
        file=png.name,
        path=str(png),
        label="Figure 1",
        width=400,
        height=300,
        index=1,
    )


def test_html_embedded_ids():
    html = '<img data-fig-id="fig-1" src="data:image/png;base64,xx" />'
    assert html_embedded_ids(html) == {"fig-1"}


def test_invented_remote_images():
    html = '<img src="https://evil.example/fake.png" />'
    assert invented_remote_images(html) == ["https://evil.example/fake.png"]


def test_ensure_appends_when_missing():
    fig = Figure(
        fig_id="fig-1",
        caption="Figure 1: Overview.",
        url="https://arxiv.org/html/x.png",
        file="fig-1.png",
        path="/tmp/fig-1.png",
        index=1,
    )
    html = "<article><p>no figure yet</p></article>"
    out = ensure_figure_embedded(html, [fig])
    assert 'data-fig-id="fig-1"' in out
    assert "auto-appended" in out


def test_ensure_noop_when_already_embedded():
    fig = Figure(
        fig_id="fig-1",
        caption="Figure 1: Overview.",
        url="https://arxiv.org/html/x.png",
        file="fig-1.png",
        path="/tmp/fig-1.png",
        index=1,
    )
    html = '<article><img data-fig-id="fig-1" src="data:image/png;base64,aa" /></article>'
    assert ensure_figure_embedded(html, [fig]) == html


def test_rendered_card_inlines_data_uri_not_http(tmp_path: Path):
    fig = _figure(tmp_path)
    paper = Paper(
        id="2610.21601",
        title="Waypoint-OPD",
        category="Reasoning",
        eligible=True,
        upvotes=668,
        org_label=None,
        organization_field=None,
        hf_url="https://huggingface.co/papers/2610.21601",
        arxiv_url="https://arxiv.org/abs/2610.21601",
        github_repo="https://github.com/example/repo",
        summary="A method.",
        arxiv_id="2610.21601",
    )
    extract = ExtractResult(
        arxiv_id="2610.21601",
        source="arxiv_html",
        source_url="https://arxiv.org/html/2610.21601",
        full_text=True,
        extractable=True,
        chars=100,
        text="text",
        figures=[fig],
        figures_found=1,
        errors=[],
        seconds=1.0,
        cache_dir=str(tmp_path),
    )
    card = ReviewCard(
        paper=paper,
        extract=extract,
        facts=ExtractFacts("p", "m", [], [], [], [], [], "e", "fig-1"),
        critique=Critique("moderate", "c", "caveat"),
        copy=CardCopy("problem", ["step 1", "step 2", "step 3"], ["+2 points"], "matters", "caveat", "fig-1"),
        method_figure=fig,
        results_figure=None,
    )
    review = DailyReview(
        collect_date="2026-10-19",
        hf_issue_date="2026-10-16",
        funnel=Funnel(10, 8, 6, 5, 1),
        cards=[card],
        notable=[],
        skipped=[],
    )
    html = render_review(review)
    assert 'data-fig-id="fig-1"' in html
    assert "data:image/png;base64," in html
    assert invented_remote_images(html) == []
    out = write_review(review, tmp_path / "review.html")
    assert out.exists()
    assert "https://evil" not in out.read_text(encoding="utf-8")

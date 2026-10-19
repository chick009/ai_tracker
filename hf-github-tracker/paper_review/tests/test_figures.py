from pathlib import Path

from bs4 import BeautifulSoup

from paper_review.figures import is_mathy, method_score, parse_figures, pick_method_figure
from paper_review.models import Figure

FIXTURE = Path(__file__).parent / "fixtures" / "sample_arxiv.html"


def _soup():
    html = FIXTURE.read_text(encoding="utf-8")
    # The extractor requires a long body; the fixture already has padding.
    return BeautifulSoup(html, "html.parser")


def test_parse_keeps_captioned_graphics():
    figs = parse_figures(_soup(), "https://arxiv.org/html/2610.21601/")
    captions = [f["caption"] for f in figs]
    assert any("Overview of the proposed method" in c for c in captions)
    assert any("Comparison of distillation methods" in c for c in captions)
    srcs = [s for f in figs for s in f["srcs"]]
    assert any(s.endswith("x1.png") for s in srcs)
    assert any(s.endswith("results.png") for s in srcs)


def test_parse_resolves_relative_src():
    figs = parse_figures(_soup(), "https://arxiv.org/html/2610.21601/")
    overview = next(f for f in figs if "Overview" in f["caption"])
    assert overview["srcs"][0] == "https://arxiv.org/html/2610.21601/x1.png"


def test_excludes_math_svg_and_tiny_and_data_uri():
    figs = parse_figures(_soup(), "https://arxiv.org/html/2610.21601/")
    blob = " ".join(f["caption"] + " ".join(f["srcs"]) for f in figs)
    assert "eq1.svg" not in blob
    assert "tiny-icon.svg" not in blob
    assert "data:" not in blob
    assert "inline equation" not in blob.lower()


def test_requires_caption():
    figs = parse_figures(_soup(), "https://arxiv.org/html/2610.21601/")
    srcs = [s for f in figs for s in f["srcs"]]
    assert not any(s.endswith("no-caption.png") for s in srcs)


def test_keeps_ltx_graphics_svg():
    figs = parse_figures(_soup(), "https://arxiv.org/html/2610.21601/")
    assert any(s.endswith("ok-graphic.svg") for f in figs for s in f["srcs"])


def test_is_mathy_svg_without_graphics_class():
    soup = BeautifulSoup(
        '<figure class="ltx_figure"><img src="foo.svg" width="400" height="300"></figure>',
        "html.parser",
    )
    fig = soup.find("figure")
    img = fig.find("img")
    assert is_mathy(img, fig) is True


def test_method_score_prefers_pipeline_over_accuracy():
    pipeline = "Figure 2: Training pipeline of Waypoint-OPD. Initial, Waypoint, and Final score candidates."
    accuracy = "Figure 1: Mathematical reasoning across three student models. mean@32 accuracy (%)."
    assert method_score(pipeline) > method_score(accuracy)
    figs = [
        Figure("fig-1", accuracy, "u", "a", "p", index=1),
        Figure("fig-2", pipeline, "u", "b", "p", index=2),
    ]
    assert pick_method_figure(figs).fig_id == "fig-2"
    assert pick_method_figure(figs, preferred_id="fig-1").fig_id == "fig-2"


def test_is_mathy_ltx_graphics_svg_allowed():
    soup = BeautifulSoup(
        '<figure class="ltx_figure"><img class="ltx_graphics" src="foo.svg" width="400" height="300"></figure>',
        "html.parser",
    )
    fig = soup.find("figure")
    img = fig.find("img")
    assert is_mathy(img, fig) is False

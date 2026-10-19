"""Parse, filter, download, and validate paper figures from arXiv HTML."""

from __future__ import annotations

import io
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from paper_review.config import (
    FIG_DOWNLOAD_WORKERS,
    FIG_TIMEOUT_SEC,
    MAX_FIGS,
    MIN_FIG_HEIGHT,
    MIN_FIG_WIDTH,
)

try:
    import cairosvg
except ImportError:  # pragma: no cover
    cairosvg = None  # type: ignore[assignment]

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[misc, assignment]

log = logging.getLogger("paper_review")

CAPTION_NUM_RE = re.compile(r"(Figure|Fig\.?)\s*([A-Z]?\d+)", re.IGNORECASE)
METHOD_STRONG = (
    "overview",
    "architecture",
    "framework",
    "pipeline",
    "schematic",
    "illustration",
)
METHOD_MEDIUM = ("method", "approach", "component", "workflow", "diagram")
RESULT_WORDS = (
    "result",
    "comparison",
    "ablation",
    "performance",
    "benchmark",
    "accuracy",
    "uplift",
    "success rate",
)
# "evaluation" is too common in method captions ("evaluation pipeline").


def gsrc(el: Tag) -> str:
    if el.name == "img":
        return str(el.get("src") or "")
    return str(el.get("data") or "")


def is_mathy(img: Tag, fig: Tag) -> bool:
    """Drop equation/math SVGs, data-URIs, and tiny icons."""
    src = gsrc(img).lower()
    img_cls = " ".join(img.get("class") or [])
    fig_cls = " ".join(fig.get("class") or [])
    cls = f"{img_cls} {fig_cls}"
    if not src or src.startswith("data:"):
        return True
    if src.endswith(".svg") and "ltx_graphics" not in cls:
        return True
    if "ltx_Math" in cls or "ltx_equation" in cls or "ltx_table" in fig_cls:
        return True
    if img.find_parent("math") is not None:
        return True
    try:
        w, h = int(img.get("width") or 0), int(img.get("height") or 0)
    except ValueError:
        w, h = 0, 0
    if w and h and (w < MIN_FIG_WIDTH or h < MIN_FIG_HEIGHT) and max(w, h) < 300:
        return True
    return False


def _caption_for_figure(fig: Tag) -> str | None:
    capel = None
    for cap in fig.find_all("figcaption"):
        if cap.find_parent("figure") is fig:
            capel = cap
            break
    if capel is None:
        caps = fig.find_all("figcaption")
        capel = caps[-1] if caps else None
    if capel is None:
        return None
    for math in capel.find_all("math"):
        alt = math.get("alttext")
        math.replace_with(f"${alt}$" if alt else "")
    cap = re.sub(r"\s+", " ", capel.get_text(" ", strip=True))
    cap = clean_caption(cap)
    return cap or None


def parse_figures(soup: BeautifulSoup, page_url: str) -> list[dict]:
    """Return candidate figure dicts (not yet downloaded)."""
    figs: list[dict] = []
    for fig in soup.find_all("figure"):
        if not isinstance(fig, Tag):
            continue
        if fig.find_parent("figure"):
            continue
        imgs = [
            i
            for i in fig.find_all(["img", "object"])
            if isinstance(i, Tag)
            and (
                i.name == "img"
                or "svg" in (i.get("type") or "")
                or (i.get("data") or "").endswith(".svg")
            )
            and i.find_parent("math") is None
            and not is_mathy(i, fig)
        ]
        if not imgs:
            continue
        cap = _caption_for_figure(fig)
        if not cap:
            continue
        num = CAPTION_NUM_RE.match(cap)
        srcs = [urljoin(page_url, gsrc(i)) for i in imgs if gsrc(i)]
        srcs = [s for s in srcs if s and not s.startswith("data:")]
        if not srcs:
            continue
        figs.append(
            {
                "html_id": fig.get("id"),
                "label": f"Figure {num.group(2)}" if num else None,
                "caption": cap,
                "srcs": srcs,
                "n_panels": len(imgs),
            }
        )
    return figs


def clean_caption(caption: str) -> str:
    cap = caption.replace("\\captionlead", "").replace("\\caption", "")
    cap = re.sub(r"\s+", " ", cap).strip(" :")
    return cap


def _word_hits(caption: str, words: tuple[str, ...], weight: int) -> int:
    c = caption.lower()
    score = 0
    for word in words:
        if re.search(rf"\b{re.escape(word)}s?\b", c):
            score += weight
    return score


def method_score(caption: str) -> int:
    cap = clean_caption(caption)
    score = _word_hits(cap, METHOD_STRONG, 6) + _word_hits(cap, METHOD_MEDIUM, 3)
    score -= _word_hits(cap, RESULT_WORDS, 4)
    if re.search(r"(Figure|Fig\.?)\s*1\b", cap, re.I):
        score += 1
    return score


def results_score(caption: str) -> int:
    return _word_hits(clean_caption(caption), RESULT_WORDS, 3)


def pick_method_figure(figures: list, preferred_id: str | None = None):
    if not figures:
        return None
    best = max(figures, key=lambda f: (method_score(f.caption), -f.index))
    if preferred_id:
        by_id = {f.fig_id: f for f in figures}
        pref = by_id.get(preferred_id)
        # Honor the model (it read the full text) unless it pointed at a
        # results-dominated plot while a better-scored method figure exists.
        if pref is not None:
            if method_score(pref.caption) >= 0 or method_score(best.caption) <= method_score(pref.caption):
                return pref
    return best


def pick_results_figure(figures: list, method_id: str | None, preferred_id: str | None = None):
    rest = [f for f in figures if f.fig_id != method_id]
    if not rest:
        return None
    by_id = {f.fig_id: f for f in rest}
    if preferred_id and preferred_id in by_id:
        return by_id[preferred_id]
    best = max(rest, key=lambda f: (results_score(f.caption), -f.index))
    if results_score(best.caption) <= 0:
        return None
    return best


def _guess_ext(content_type: str, src: str, payload: bytes) -> str:
    src_l = src.lower()
    ctype = (content_type or "").lower()
    if "svg" in ctype or src_l.endswith(".svg") or payload[:200].lstrip().startswith(b"<svg"):
        return "svg"
    if "jpeg" in ctype or "jpg" in ctype or src_l.endswith(".jpg") or src_l.endswith(".jpeg"):
        return "jpg"
    if "webp" in ctype or src_l.endswith(".webp"):
        return "webp"
    if "gif" in ctype or src_l.endswith(".gif"):
        return "gif"
    return "png"


def _rasterize_svg(payload: bytes) -> bytes | None:
    if cairosvg is None:
        return None
    try:
        return cairosvg.svg2png(bytestring=payload, output_width=1400, background_color="white")
    except Exception as exc:  # noqa: BLE001
        log.debug("svg rasterize failed: %s", exc)
        return None


def _inspect_image(payload: bytes, ext: str) -> tuple[int, int, str, bytes] | None:
    if ext == "svg":
        png = _rasterize_svg(payload)
        if png:
            return _inspect_image(png, "png")
        # Keep a reasonably sized SVG graphic even if cairo is missing.
        if len(payload) < 800 or len(payload) > 8_000_000:
            return None
        return 800, 400, "svg", payload
    if Image is None:
        return None
    try:
        im = Image.open(io.BytesIO(payload))
        w, h = im.size
        fmt = {"JPEG": "jpg", "PNG": "png", "GIF": "gif", "WEBP": "webp"}.get(im.format or "", ext)
        if w < MIN_FIG_WIDTH or h < MIN_FIG_HEIGHT:
            return None
        return w, h, fmt, payload
    except Exception as exc:  # noqa: BLE001
        log.debug("image inspect failed: %s", exc)
        return None


def download_one(session, candidate: dict, timeout: int) -> dict | None:
    src = candidate["srcs"][0]
    try:
        resp = session.get(src, timeout=timeout, stream=False)
        if resp.status_code != 200:
            return None
        payload = resp.content
        ext = _guess_ext(resp.headers.get("content-type", ""), src, payload)
        inspected = _inspect_image(payload, ext)
        if not inspected:
            return None
        width, height, ext, payload = inspected
        return {
            **candidate,
            "url": src,
            "payload": payload,
            "ext": ext,
            "width": width,
            "height": height,
        }
    except Exception as exc:  # noqa: BLE001
        log.info("fig fail %s: %s", src, exc)
        return None


def download_figures(
    session,
    candidates: list[dict],
    outdir: Path,
    max_figs: int = MAX_FIGS,
) -> list[dict]:
    """Download up to max_figs candidates concurrently; keep original order."""
    work = candidates[: max_figs * 2]
    results: dict[int, dict] = {}
    with ThreadPoolExecutor(max_workers=FIG_DOWNLOAD_WORKERS) as pool:
        futs = {
            pool.submit(download_one, session, cand, FIG_TIMEOUT_SEC): i
            for i, cand in enumerate(work)
        }
        for fut in as_completed(futs):
            idx = futs[fut]
            got = fut.result()
            if got:
                results[idx] = got
    kept: list[dict] = []
    for idx in sorted(results):
        if len(kept) >= max_figs:
            break
        item = results[idx]
        n = len(kept) + 1
        fig_id = f"fig-{n}"
        filename = f"{fig_id}.{item['ext']}"
        (outdir / filename).write_bytes(item["payload"])
        kept.append(
            {
                "fig_id": fig_id,
                "file": filename,
                "path": str(outdir / filename),
                "url": item["url"],
                "caption": item["caption"],
                "label": item.get("label"),
                "width": item["width"],
                "height": item["height"],
                "n_panels": item.get("n_panels", 1),
                "html_id": item.get("html_id"),
                "index": n,
            }
        )
    return kept


def allowlisted_ids(figures: list) -> set[str]:
    return {f.fig_id for f in figures}


def html_embedded_ids(html: str) -> set[str]:
    return set(re.findall(r'data-fig-id="(fig-\d+)"', html))


def invented_remote_images(html: str) -> list[str]:
    """Remote http(s) image URLs that are not in an allow-list of paper figures."""
    return re.findall(r'<img[^>]+src="(https?://[^"]+)"', html, flags=re.IGNORECASE)


def best_fallback_figure(figures: list):
    return pick_method_figure(figures)


def ensure_figure_embedded(html: str, figures: list, card_marker: str | None = None) -> str:
    """If figures existed but none were embedded, append the best candidate."""
    if not figures:
        return html
    if html_embedded_ids(html) & allowlisted_ids(figures):
        return html
    fig = best_fallback_figure(figures)
    if fig is None:
        return html
    snippet = (
        f'<figure class="method-fig auto-appended" data-fig-id="{fig.fig_id}">'
        f'<img data-fig-id="{fig.fig_id}" alt="{_escape_attr(fig.caption[:180])}" />'
        f"<figcaption>{_escape(fig.caption)}</figcaption></figure>"
    )
    if card_marker and card_marker in html:
        return html.replace(card_marker, snippet + card_marker, 1)
    if "</article>" in html:
        return html.replace("</article>", snippet + "</article>", 1)
    return html + snippet


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _escape_attr(text: str) -> str:
    return _escape(text).replace("\n", " ")

"""Full-text + figure extraction for one arXiv paper (cached, idempotent)."""

from __future__ import annotations

import gzip
import io
import json
import logging
import re
import subprocess
import tarfile
import tempfile
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    PdfReader = None  # type: ignore[misc, assignment]

from paper_review.config import (
    HTML_TIMEOUT_SEC,
    MAX_TEXT_CHARS,
    MIN_HTML_CHARS,
    MIN_LATEX_CHARS,
    MIN_PDF_CHARS,
    SOURCE_TIMEOUT_SEC,
    USER_AGENT,
)
from paper_review.figures import clean_caption, download_figures, parse_figures
from paper_review.models import ExtractResult, Figure

log = logging.getLogger("paper_review")
META_VERSION = 3

DROP_CMDS = (
    r"\\(?:vspace|hspace|label|ref|eqref|cref|Cref|newcommand|renewcommand|def|"
    r"usepackage|documentclass|setlength|centering|small|footnotesize|scriptsize|"
    r"tiny|large|Large|bibliographystyle|bibliography|includegraphics|maketitle|"
    r"noindent|clearpage|newpage|resizebox|definecolor|input|include)"
    r"\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})*"
)


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    retry = Retry(
        total=2,
        backoff_factor=0.4,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def html_to_text(soup: BeautifulSoup) -> str:
    s = BeautifulSoup(str(soup), "html.parser")
    for tag in s(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    for tag in s.select(
        ".ltx_page_header, .ltx_page_footer, .ltx_bibliography, #header, "
        ".package-alerts, .ltx_TOC"
    ):
        tag.decompose()
    for math in s.find_all("math"):
        alt = math.get("alttext")
        math.replace_with(f" ${alt}$ " if alt else " ")
    body = s.select_one("article") or s.select_one(".ltx_document") or s.body or s
    out: list[str] = []
    for el in body.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "figcaption", "li", "td", "th"]):
        if el.find_parent(["li", "td"]) and el.name == "p":
            continue
        txt = re.sub(r"\s+", " ", el.get_text(" ", strip=True))
        if not txt:
            continue
        if el.name.startswith("h"):
            out.append("\n## " + txt)
        elif el.name == "figcaption":
            out.append("[CAPTION] " + txt)
        else:
            out.append(txt)
    return "\n".join(out)


def try_html(session: requests.Session, url: str, timeout: int) -> tuple[str, str, list[dict]]:
    resp = session.get(url, timeout=timeout, allow_redirects=True)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}")
    soup = BeautifulSoup(resp.text, "lxml")
    base = soup.find("base", href=True)
    page_url = urljoin(resp.url, base["href"]) if base else resp.url
    text = html_to_text(soup)
    if len(text) < MIN_HTML_CHARS or "ltx_" not in resp.text:
        raise RuntimeError(f"not usable (text {len(text)} chars)")
    return resp.text, text, parse_figures(soup, page_url)


def tex_clean(tex: str) -> str:
    tex = re.sub(r"(?<!\\)%.*", "", tex)
    tex = re.sub(r"\\begin\{(?:comment)\}.*?\\end\{comment\}", "", tex, flags=re.S)
    tex = re.sub(
        r"\\(?:sub)*section\*?\{([^{}]*)\}",
        lambda m: "\n## " + m.group(1) + "\n",
        tex,
    )
    tex = re.sub(r"\\paragraph\*?\{([^{}]*)\}", r"\n\1. ", tex)
    tex = re.sub(r"\\caption\{", "\n[CAPTION] {", tex)
    tex = re.sub(DROP_CMDS, " ", tex)
    tex = re.sub(r"\\(?:textbf|textit|emph|texttt|underline|textsc)\{([^{}]*)\}", r"\1", tex)
    tex = re.sub(r"\\cite[pt]?\*?(?:\[[^\]]*\])?\{[^{}]*\}", "[cite]", tex)
    tex = re.sub(
        r"\\(?:begin|end)\{(?:figure|table|center|minipage|tabular|itemize|"
        r"enumerate|abstract|document|wrapfigure|subfigure)\*?\}"
        r"(?:\[[^\]]*\])?(?:\{[^{}]*\})?",
        "\n",
        tex,
    )
    tex = tex.replace("\\item", "\n- ")
    tex = re.sub(r"[ \t]+", " ", tex)
    tex = re.sub(r"\n\s*\n+", "\n\n", tex)
    return tex.strip()


def try_latex(session: requests.Session, arxiv_id: str, timeout: int) -> str:
    resp = session.get(f"https://arxiv.org/e-print/{arxiv_id}", timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}")
    data = resp.content
    texs: dict[str, str] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tf:
            for member in tf.getmembers():
                if member.isfile() and member.name.endswith(".tex") and member.size < 3_000_000:
                    extracted = tf.extractfile(member)
                    if extracted is None:
                        continue
                    texs[member.name] = extracted.read().decode("utf-8", "ignore")
    except tarfile.ReadError:
        try:
            raw = gzip.decompress(data).decode("utf-8", "ignore")
        except OSError:
            raw = data.decode("utf-8", "ignore")
        if "\\begin{document}" in raw or "\\section" in raw:
            texs["main.tex"] = raw
    if not texs:
        raise RuntimeError("no .tex in source")
    main = next((k for k, v in texs.items() if "\\begin{document}" in v), None)
    order = ([main] if main else []) + [k for k in sorted(texs) if k != main]
    full = "\n".join(f"\n%% FILE {k}\n{texs[k]}" for k in order)
    text = tex_clean(full)
    if len(text) < MIN_LATEX_CHARS:
        raise RuntimeError(f"too short ({len(text)})")
    return text


def try_pdf(session: requests.Session, arxiv_id: str, timeout: int) -> str:
    resp = session.get(f"https://arxiv.org/pdf/{arxiv_id}", timeout=timeout)
    if resp.status_code != 200 or not resp.content.startswith(b"%PDF"):
        raise RuntimeError(f"HTTP {resp.status_code}")
    chunks: list[str] = []
    total = 0
    if PdfReader is not None:
        reader = PdfReader(io.BytesIO(resp.content))
        for page in reader.pages:
            t = page.extract_text() or ""
            chunks.append(t)
            total += len(t)
            if total > MAX_TEXT_CHARS:
                break
    else:
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            tmp.write(resp.content)
            tmp.flush()
            n = 1
            while total <= MAX_TEXT_CHARS and n < 200:
                proc = subprocess.run(
                    ["pdftotext", "-layout", "-f", str(n), "-l", str(n), tmp.name, "-"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if proc.returncode != 0:
                    break
                chunks.append(proc.stdout)
                total += len(proc.stdout)
                n += 1
    text = "\n\n".join(chunks)
    if len(text) < MIN_PDF_CHARS:
        raise RuntimeError(f"too short ({len(text)})")
    return text


def _load_cached(outdir: Path, force: bool) -> ExtractResult | None:
    meta_path = outdir / "meta.json"
    text_path = outdir / "text.txt"
    if force or not meta_path.exists() or not text_path.exists():
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if meta.get("version") != META_VERSION:
        return None
    figures = []
    for raw in meta.get("figures") or []:
        if not raw.get("fig_id") or not raw.get("file"):
            continue
        raw = dict(raw)
        raw["caption"] = clean_caption(raw.get("caption") or "")
        figures.append(Figure(**raw))
    existing = []
    for fig in figures:
        path = Path(fig.path) if fig.path else outdir / fig.file
        if not path.exists() and (outdir / fig.file).exists():
            path = outdir / fig.file  # cache moved or cwd differs
        if path.exists():
            fig.path = str(path)
            existing.append(fig)
    figures = existing
    text = text_path.read_text(encoding="utf-8", errors="ignore")
    source = meta.get("source")
    full_text = source not in (None, "abstract")
    extractable = full_text and len(figures) > 0
    skip = None
    if not full_text:
        skip = "abstract-only (no full text)"
    elif not figures:
        skip = "no real figure downloaded"
    return ExtractResult(
        arxiv_id=meta.get("arxiv_id") or outdir.name,
        source=source,
        source_url=meta.get("source_url"),
        full_text=full_text,
        extractable=extractable,
        chars=len(text),
        text=text,
        figures=figures,
        figures_found=int(meta.get("figures_found") or 0),
        errors=list(meta.get("errors") or []),
        seconds=float(meta.get("seconds") or 0),
        cache_dir=str(outdir),
        skip_reason=skip,
    )


def extract_paper(
    arxiv_id: str,
    cache_dir: Path,
    abstract: str = "",
    force: bool = False,
    session: requests.Session | None = None,
    html_timeout: int = HTML_TIMEOUT_SEC,
    source_timeout: int = SOURCE_TIMEOUT_SEC,
) -> ExtractResult:
    outdir = cache_dir / arxiv_id
    outdir.mkdir(parents=True, exist_ok=True)
    cached = _load_cached(outdir, force)
    if cached is not None:
        log.info("[%s] cache hit source=%s figs=%d", arxiv_id, cached.source, len(cached.figures))
        return cached

    own_session = session is None
    session = session or make_session()
    t0 = time.time()
    errors: list[str] = []
    text: str | None = None
    figs: list[dict] = []
    source: str | None = None
    source_url: str | None = None

    for name, url in (
        ("arxiv_html", f"https://arxiv.org/html/{arxiv_id}"),
        ("ar5iv", f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}"),
    ):
        try:
            raw, extracted, found = try_html(session, url, html_timeout)
            (outdir / "page.html").write_text(raw, encoding="utf-8")
            text, figs = extracted, found
            source, source_url = name, url
            log.info("[%s] %s ok (%d chars, %d fig candidates)", arxiv_id, name, len(text), len(figs))
            break
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")
            log.info("[%s] %s failed: %s", arxiv_id, name, exc)

    if text is None:
        for name, fn in (("latex", try_latex), ("pdf", try_pdf)):
            try:
                text = fn(session, arxiv_id, source_timeout)
                source = name
                log.info("[%s] %s ok (%d chars)", arxiv_id, name, len(text))
                break
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{name}: {exc}")
                log.info("[%s] %s failed: %s", arxiv_id, name, exc)

    if text is None:
        text = abstract or ""
        source = "abstract"
        log.info("[%s] abstract fallback (%d chars)", arxiv_id, len(text))

    if source not in ("arxiv_html", "ar5iv"):
        text = text[:MAX_TEXT_CHARS]
    (outdir / "text.txt").write_text(text, encoding="utf-8")

    downloaded: list[dict] = []
    if figs:
        downloaded = download_figures(session, figs, outdir)

    figures = [Figure(**d) for d in downloaded]
    full_text = source != "abstract"
    skip = None
    if not full_text:
        skip = "abstract-only (no full text)"
    elif not figures:
        skip = "no real figure downloaded"
    result = ExtractResult(
        arxiv_id=arxiv_id,
        source=source,
        source_url=source_url,
        full_text=full_text,
        extractable=full_text and len(figures) > 0,
        chars=len(text),
        text=text,
        figures=figures,
        figures_found=len(figs),
        errors=errors,
        seconds=round(time.time() - t0, 1),
        cache_dir=str(outdir),
        skip_reason=skip,
    )
    meta = {"version": META_VERSION, **result.to_meta()}
    (outdir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    if own_session:
        session.close()
    return result

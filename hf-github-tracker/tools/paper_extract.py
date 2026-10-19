#!/workspace/ai-tracker/tools/.venv/bin/python
"""Extract full text + real figures for an arXiv paper (idempotent, cached).

Order: arXiv HTML -> ar5iv HTML -> arXiv e-print LaTeX -> PDF text -> abstract only.
Figures: only from arXiv/ar5iv HTML <figure> blocks with <img> (+ <figcaption>).

Cache: /workspace/ai-tracker/papers/<arxiv_id>/
  meta.json   source, chars, figures[], errors[]
  text.txt    extracted text (<= MAX_CHARS)
  page.html   raw HTML (if HTML worked)
  fig-N.png|jpg|...  downloaded figures (<= MAX_FIGS)

Usage: paper_extract.py <arxiv_id> [--abstract-file f] [--force]
Library: extract(arxiv_id, abstract="", force=False) -> meta dict
"""
import gzip, io, json, os, re, sys, tarfile, time, argparse, subprocess, tempfile
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

ROOT = os.environ.get("PAPERS_CACHE", "/workspace/ai-tracker/papers")
UA = {"User-Agent": "Mozilla/5.0 PaperDigest"}
HTML_TIMEOUT = 20
MAX_CHARS = 60000
MAX_FIGS = 6
MIN_W, MIN_H = 200, 120          # smaller images are treated as icons/equations
MIN_HTML_TEXT = 5000             # below this an HTML page is "not usable"
META_VERSION = 2


def log(*a):
    print("[extract]", *a, file=sys.stderr, flush=True)


def get(url, timeout, stream=False):
    return requests.get(url, headers=UA, timeout=timeout, allow_redirects=True, stream=stream)


# ---------------------------------------------------------------- HTML
def html_to_text(soup):
    s = BeautifulSoup(str(soup), "html.parser")
    for t in s(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    for t in s.select(".ltx_page_header, .ltx_page_footer, .ltx_bibliography, #header, .package-alerts, .ltx_TOC"):
        t.decompose()
    # keep math as its LaTeX alttext
    for m in s.find_all("math"):
        alt = m.get("alttext")
        m.replace_with(f" ${alt}$ " if alt else " ")
    body = s.select_one("article") or s.select_one(".ltx_document") or s.body or s
    out = []
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


def gsrc(el):
    return el.get("src") if el.name == "img" else el.get("data")


def is_mathy(img, fig):
    src = (gsrc(img) or "").lower()
    cls = " ".join(img.get("class") or []) + " " + " ".join(fig.get("class") or [])
    if src.startswith("data:") or not src:
        return True
    # SVGs are allowed only as figure graphics (LaTeXML ltx_graphics), never inline math
    if src.endswith(".svg") and "ltx_graphics" not in cls:
        return True
    if "ltx_Math" in cls or "ltx_equation" in cls or "ltx_table" in (" ".join(fig.get("class") or [])):
        return True
    try:
        w, h = int(img.get("width") or 0), int(img.get("height") or 0)
        if w and h and (w < MIN_W or h < MIN_H) and max(w, h) < 300:
            return True
    except ValueError:
        pass
    return False


def parse_figures(soup, page_url):
    figs = []
    for fig in soup.find_all("figure"):
        if fig.find_parent("figure"):
            continue  # sub-panels handled by parent
        imgs = [i for i in fig.find_all(["img", "object"])
                if (i.name == "img" or "svg" in (i.get("type") or "") or (i.get("data") or "").endswith(".svg"))
                and not i.find_parent("math") and not is_mathy(i, fig)]
        if not imgs:
            continue
        capel = None
        for c in fig.find_all("figcaption"):
            if c.find_parent("figure") is fig:
                capel = c
        if capel is None:
            caps = fig.find_all("figcaption")
            capel = caps[-1] if caps else None
        if capel is None:
            continue  # require a caption
        for m in capel.find_all("math"):
            alt = m.get("alttext"); m.replace_with(f"${alt}$" if alt else "")
        cap = re.sub(r"\s+", " ", capel.get_text(" ", strip=True))
        num = re.match(r"(Figure|Fig\.?)\s*([A-Z]?\d+)", cap)
        figs.append({
            "html_id": fig.get("id"),
            "label": f"Figure {num.group(2)}" if num else None,
            "caption": cap,
            "srcs": [urljoin(page_url, gsrc(i)) for i in imgs],
            "n_panels": len(imgs),
        })
    return figs


def try_html(url):
    r = get(url, HTML_TIMEOUT)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}")
    soup = BeautifulSoup(r.text, "html.parser")
    base = soup.find("base", href=True)
    page_url = urljoin(r.url, base["href"]) if base else r.url
    text = html_to_text(soup)
    if len(text) < MIN_HTML_TEXT or "ltx_" not in r.text:
        raise RuntimeError(f"not usable (text {len(text)} chars)")
    return r.text, text, parse_figures(soup, page_url)


# ---------------------------------------------------------------- LaTeX
DROP_CMDS = r"\\(?:vspace|hspace|label|ref|eqref|cref|Cref|newcommand|renewcommand|def|usepackage|documentclass|setlength|centering|small|footnotesize|scriptsize|tiny|large|Large|bibliographystyle|bibliography|includegraphics|maketitle|noindent|clearpage|newpage|resizebox|definecolor|input|include)\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})*"


def tex_clean(tex):
    tex = re.sub(r"(?<!\\)%.*", "", tex)
    tex = re.sub(r"\\begin\{(?:comment)\}.*?\\end\{comment\}", "", tex, flags=re.S)
    tex = re.sub(r"\\(?:sub)*section\*?\{([^{}]*)\}", lambda m: "\n## " + m.group(1) + "\n", tex)
    tex = re.sub(r"\\paragraph\*?\{([^{}]*)\}", r"\n\1. ", tex)
    tex = re.sub(r"\\caption\{", "\n[CAPTION] {", tex)
    tex = re.sub(DROP_CMDS, " ", tex)
    tex = re.sub(r"\\(?:textbf|textit|emph|texttt|underline|textsc)\{([^{}]*)\}", r"\1", tex)
    tex = re.sub(r"\\cite[pt]?\*?(?:\[[^\]]*\])?\{[^{}]*\}", "[cite]", tex)
    tex = re.sub(r"\\(?:begin|end)\{(?:figure|table|center|minipage|tabular|itemize|enumerate|abstract|document|wrapfigure|subfigure)\*?\}(?:\[[^\]]*\])?(?:\{[^{}]*\})?", "\n", tex)
    tex = tex.replace("\\item", "\n- ")
    tex = re.sub(r"[ \t]+", " ", tex)
    tex = re.sub(r"\n\s*\n+", "\n\n", tex)
    return tex.strip()


def try_latex(aid):
    r = get(f"https://arxiv.org/e-print/{aid}", 60)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}")
    data = r.content
    texs = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tf:
            for m in tf.getmembers():
                if m.isfile() and m.name.endswith(".tex") and m.size < 3_000_000:
                    texs[m.name] = tf.extractfile(m).read().decode("utf-8", "ignore")
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
    # inline \input{} files in main where possible
    full = []
    for k in order:
        full.append(f"\n%% FILE {k}\n" + texs[k])
    text = tex_clean("\n".join(full))
    if len(text) < 3000:
        raise RuntimeError(f"too short ({len(text)})")
    return text


# ---------------------------------------------------------------- PDF
def try_pdf(aid):
    r = get(f"https://arxiv.org/pdf/{aid}", 60)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise RuntimeError(f"HTTP {r.status_code}")
    chunks, total = [], 0
    try:
        from pypdf import PdfReader
        rd = PdfReader(io.BytesIO(r.content))
        for p in rd.pages:
            t = p.extract_text() or ""
            chunks.append(t); total += len(t)
            if total > MAX_CHARS:
                break
    except ImportError:  # fall back to poppler pdftotext, page by page
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(r.content); f.flush()
            n = 1
            while total <= MAX_CHARS and n < 200:
                p = subprocess.run(["pdftotext", "-layout", "-f", str(n), "-l", str(n), f.name, "-"],
                                   capture_output=True, text=True)
                if p.returncode != 0:
                    break
                chunks.append(p.stdout); total += len(p.stdout); n += 1
    text = "\n\n".join(chunks)
    if len(text) < 3000:
        raise RuntimeError(f"too short ({len(text)})")
    return text


# ---------------------------------------------------------------- figures
def download_figs(figs, outdir):
    from PIL import Image
    kept = []
    for f in figs:
        if len(kept) >= MAX_FIGS:
            break
        src = f["srcs"][0]  # first panel; multi-panel figures noted via n_panels
        try:
            r = get(src, 30)
            if r.status_code != 200:
                continue
            ctype = r.headers.get("content-type", "")
            n = len(kept) + 1
            extra = {}
            if "svg" in ctype or src.lower().endswith(".svg"):
                # vector figure graphic: keep the SVG, rasterise to PNG for embedding/preview
                if len(r.content) > 8_000_000:
                    continue
                import cairosvg
                open(os.path.join(outdir, f"fig-{n}.svg"), "wb").write(r.content)
                png = cairosvg.svg2png(bytestring=r.content, output_width=1400, background_color="white")
                extra = {"svg_file": f"fig-{n}.svg", "rasterised": True}
                r._content = png
            im = Image.open(io.BytesIO(r.content))
            w, h = im.size
            if w < MIN_W or h < MIN_H:
                continue
            ext = {"JPEG": "jpg", "PNG": "png", "GIF": "gif", "WEBP": "webp"}.get(im.format, "png")
            fn = f"fig-{n}.{ext}"
            open(os.path.join(outdir, fn), "wb").write(r.content)
            kept.append({**f, **extra, "file": fn, "url": src, "width": w, "height": h, "index": n})
        except Exception as e:  # noqa
            log("fig fail", src, e)
    return kept


# ---------------------------------------------------------------- main
def extract(aid, abstract="", force=False):
    outdir = os.path.join(ROOT, aid)
    os.makedirs(outdir, exist_ok=True)
    mp = os.path.join(outdir, "meta.json")
    if not force and os.path.exists(mp):
        m = json.load(open(mp))
        if m.get("version") == META_VERSION and m.get("source") != "abstract":
            return m
    t0 = time.time()
    meta = {"version": META_VERSION, "arxiv_id": aid, "source": None, "errors": [], "figures": [],
            "figure_source": None}
    text, figs = None, []
    for name, url in (("arxiv_html", f"https://arxiv.org/html/{aid}"),
                      ("ar5iv", f"https://ar5iv.labs.arxiv.org/html/{aid}")):
        try:
            raw, t, fl = try_html(url)
            open(os.path.join(outdir, "page.html"), "w").write(raw)
            text, figs = t, fl
            meta["source"], meta["source_url"] = name, url
            meta["figure_source"] = name
            break
        except Exception as e:
            meta["errors"].append(f"{name}: {e}")
            log(aid, name, "failed:", e)
    if text is None:
        for name, fn in (("latex", try_latex), ("pdf", try_pdf)):
            try:
                text = fn(aid); meta["source"] = name; break
            except Exception as e:
                meta["errors"].append(f"{name}: {e}"); log(aid, name, "failed:", e)
    if text is None:
        text = abstract; meta["source"] = "abstract"
    text = text[:MAX_CHARS] if meta["source"] != "arxiv_html" and meta["source"] != "ar5iv" else text
    open(os.path.join(outdir, "text.txt"), "w").write(text)
    meta["chars"] = len(text)
    meta["figures_found"] = len(figs)
    if figs:
        meta["figures"] = download_figs(figs, outdir)
    meta["full_text"] = meta["source"] != "abstract"
    meta["extractable"] = meta["full_text"] and len(meta["figures"]) > 0
    meta["seconds"] = round(time.time() - t0, 1)
    json.dump(meta, open(mp, "w"), indent=1, ensure_ascii=False)
    return meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    for i in a.ids:
        m = extract(i, force=a.force)
        print(json.dumps({k: m[k] for k in ("arxiv_id", "source", "chars", "figures_found", "extractable", "errors")}
                         | {"figs": [(f["file"], f["label"], f["caption"][:80]) for f in m["figures"]]}, ensure_ascii=False))

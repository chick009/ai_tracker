"""Save a full-page PNG of a local HTML file (Playwright / Chromium / wkhtml)."""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger("paper_review")

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None  # type: ignore[misc, assignment]


def screenshot_html(html_path: Path, png_path: Path) -> Path:
    html_path = html_path.resolve()
    png_path = png_path.resolve()
    png_path.parent.mkdir(parents=True, exist_ok=True)
    uri = html_path.as_uri()

    if sync_playwright is not None:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome")
            except Exception:
                browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 1600})
            page.goto(uri, wait_until="load")
            page.screenshot(path=str(png_path), full_page=True)
            browser.close()
        return png_path

    chrome = (
        shutil.which("chromium")
        or shutil.which("chromium-browser")
        or shutil.which("google-chrome")
        or shutil.which("google-chrome-stable")
    )
    if chrome:
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                f"--screenshot={png_path}",
                "--window-size=1280,2400",
                uri,
            ],
            check=True,
            capture_output=True,
            timeout=60,
        )
        if png_path.exists():
            return png_path

    raise RuntimeError(
        "No screenshot backend. Install playwright (`pip install playwright && playwright install chromium`) "
        "or chromium."
    )

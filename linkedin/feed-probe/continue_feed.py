#!/usr/bin/env python3
"""Continue home-feed dump. NEVER leave https://www.linkedin.com/feed/."""
from __future__ import annotations

import importlib.util
import os
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

os.environ.setdefault("DISPLAY", ":7")
OUT = Path("/workspace/linkedin-feed-probe")
PROFILE = Path("/workspace/career-job-applications/data/.linkedin-browser-profile")
FEED_URL = "https://www.linkedin.com/feed/"
TARGET = 20
MAX_SECONDS = 90

spec = importlib.util.spec_from_file_location("extract_feed", str(OUT / "extract_feed.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def path_of(url: str) -> str:
    return urlparse(url).path or "/"


def on_feed(url: str) -> bool:
    return path_of(url).startswith("/feed")


def force_feed(page) -> None:
    if not on_feed(page.url):
        page.goto(FEED_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(1500)


def main() -> int:
    rsc_events: list = []
    activity_urns: list[str] = []
    rsc_text_sample = ""

    def on_response(resp):
        nonlocal rsc_text_sample
        try:
            url = resp.url
            if "flagship-web/rsc-action/actions/pagination" not in url:
                return
            import re
            entry = {
                "url": url[:300],
                "status": resp.status,
                "ct": (resp.headers or {}).get("content-type", "")[:80],
            }
            body = resp.body()
            entry["body_len"] = len(body)
            text = body.decode("utf-8", errors="replace")
            urns = re.findall(r"urn:li:(?:activity|ugcPost|share|fsd_update):[A-Za-z0-9:_\-]+", text)
            uniq = list(dict.fromkeys(urns))
            entry["urn_count"] = len(urns)
            entry["urn_unique"] = len(uniq)
            entry["urn_sample"] = uniq[:25]
            for u in uniq:
                if u not in activity_urns:
                    activity_urns.append(u)
            if not rsc_text_sample and len(text) > 500:
                rsc_text_sample = text[:12000]
            toks = re.findall(r"update-card-focus([A-Za-z0-9_-]{10,80})", text)
            entry["dom_token_sample"] = list(dict.fromkeys(toks))[:10]
            rsc_events.append(entry)
        except Exception:
            return

    accumulated: dict[str, dict] = {}
    ads_noted: list[dict] = []
    scroll_log: list[dict] = []
    last_extract: dict = {}
    html_samples: list[dict] = []

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(PROFILE),
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--no-sandbox", "--disable-dev-shm-usage"],
            locale="en-US",
        )
        # Close restored tabs that are not feed; never linger on /in/.
        page = None
        for pg in list(ctx.pages):
            try:
                if on_feed(pg.url):
                    page = pg
                else:
                    if page is None:
                        page = pg
                    else:
                        pg.close()
            except Exception:
                pass
        if page is None:
            page = ctx.new_page()

        def guard(_frame=None):
            try:
                if not on_feed(page.url):
                    page.goto(FEED_URL, wait_until="domcontentloaded", timeout=45000)
            except Exception:
                pass

        page.on("framenavigated", lambda f: guard() if f == page.main_frame else None)
        page.add_init_script(
            """
            document.addEventListener('click', (e) => {
              const t = e.target && e.target.closest && e.target.closest('a,button,[role="link"]');
              if (!t) return;
              const href = String((t.getAttribute && t.getAttribute('href')) || t.href || '');
              if (/\\/in\\/|\\/jobs|\\/mynetwork|\\/messaging|\\/notifications|\\/me\\b|\\/preload\\/interests/i.test(href)) {
                e.preventDefault();
                e.stopImmediatePropagation();
              }
            }, true);
            """
        )
        page.on("response", on_response)

        # FIRST action: home feed only.
        page.goto(FEED_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)
        force_feed(page)

        # Screenshot immediately so we can confirm we are on /feed/, not /in/.
        page.screenshot(path=str(OUT / "feed.png"), full_page=False)
        if not on_feed(page.url):
            mod.write_all(
                [], last_extract, rsc_events, activity_urns, rsc_text_sample,
                ads_noted, scroll_log, html_samples,
                blocker={"reason": "could-not-stay-on-feed", "url": page.url, "title": page.title(),
                         "preview": page.evaluate("() => (document.body&&document.body.innerText||'').slice(0,400)")},
                url=page.url, title=page.title(),
            )
            ctx.close()
            return 2

        # Focus document without clicking people/nav. No mouse clicks anywhere.
        page.evaluate(
            """() => {
              document.body.tabIndex = 0;
              document.body.focus();
            }"""
        )

        start = time.time()
        idle = 0
        last_n = 0
        while time.time() - start < MAX_SECONDS:
            force_feed(page)
            last_extract = page.evaluate(mod.EXTRACT_JS)
            for post in last_extract.get("posts") or []:
                tok = post.get("token") or ""
                if not tok:
                    continue
                if post.get("isAd"):
                    if not any(a.get("token") == tok for a in ads_noted):
                        ads_noted.append({
                            "token": tok,
                            "author": post.get("author"),
                            "preview": post.get("innerTextPreview"),
                        })
                    continue
                if tok not in accumulated:
                    accumulated[tok] = post
            n = len(accumulated)
            try:
                diag = page.evaluate(
                    """() => ({
                      href: location.href,
                      y: window.scrollY,
                      sh: document.scrollingElement ? document.scrollingElement.scrollHeight : 0,
                      nItems: document.querySelectorAll('[role="listitem"][componentkey*="update-card-focus"]').length
                    })"""
                )
            except Exception:
                diag = {}
            # If we drifted off feed, bail back immediately and do not record.
            if not on_feed(str(diag.get("href") or page.url)):
                force_feed(page)
                scroll_log.append({"t": round(time.time() - start, 1), "note": "redirected-back-to-feed"})
                continue
            scroll_log.append({
                "t": round(time.time() - start, 1),
                "url": path_of(str(diag.get("href") or "")),
                "domListitems": last_extract.get("listitemCount") or diag.get("nItems"),
                "uniqueNonAds": n,
                "ads": len(ads_noted),
                "scrollY": diag.get("y"),
                "scrollHeight": diag.get("sh"),
            })
            if n >= TARGET:
                break
            if n == last_n:
                idle += 1
            else:
                idle = 0
            last_n = n
            # Scroll the inner feed scroller. Never click (clicks hit avatars -> /in/).
            try:
                page.mouse.move(680, 520)
            except Exception:
                pass
            page.mouse.wheel(0, 1400)
            page.evaluate(
                """() => {
                  function bump(el, dy) {
                    if (!el) return false;
                    const can = el.scrollHeight - el.clientHeight > 40;
                    if (can) { el.scrollTop += dy; return true; }
                    return false;
                  }
                  const feed = document.querySelector('[data-testid="mainFeed"]');
                  let node = feed;
                  let moved = false;
                  while (node) {
                    if (bump(node, 1600)) moved = true;
                    node = node.parentElement;
                  }
                  bump(document.querySelector('main'), 1600);
                  bump(document.scrollingElement, 1600);
                  return moved;
                }"""
            )
            page.wait_for_timeout(1500)
            if idle >= 30:
                scroll_log.append({"t": round(time.time() - start, 1), "note": "idle-stop"})
                break

        force_feed(page)
        last_extract = page.evaluate(mod.EXTRACT_JS)
        page.screenshot(path=str(OUT / "feed.png"), full_page=False)

        sample_tokens = []
        live = [p.get("token") for p in (last_extract.get("posts") or []) if p.get("token")]
        for t in live:
            if t in accumulated and t not in sample_tokens:
                sample_tokens.append(t)
            if len(sample_tokens) >= 3:
                break
        if len(sample_tokens) < 3:
            for t in accumulated:
                if t not in sample_tokens:
                    sample_tokens.append(t)
                if len(sample_tokens) >= 3:
                    break
        for t in sample_tokens:
            try:
                html = page.evaluate(mod.SAMPLE_HTML_JS, t)
            except Exception:
                html = ""
            html_samples.append({"token": t, "outerHTML": html})

        posts = list(accumulated.values())[:TARGET]
        mod.write_all(
            posts, last_extract, rsc_events, activity_urns, rsc_text_sample,
            ads_noted, scroll_log, html_samples, blocker=None,
            url=page.url, title=page.title(),
        )
        ctx.close()
    print(f"url_ok feed posts={len(posts)} ads={len(ads_noted)} rsc={len(rsc_events)} urns={len(activity_urns)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

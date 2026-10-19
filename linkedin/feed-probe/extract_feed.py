#!/usr/bin/env python3
"""Extract ~20 LinkedIn home-feed cards from the live SDUI DOM.

Reuses the existing persistent Chromium profile for cookies only.
Does not import jobs-ingest code. Does not capture passwords.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path("/workspace/linkedin-feed-probe")
PROFILE = Path("/workspace/career-job-applications/data/.linkedin-browser-profile")
FEED_URL = "https://www.linkedin.com/feed/"
TARGET = 20
MAX_SECONDS = 90

os.environ.setdefault("DISPLAY", ":7")

EXTRACT_JS = r"""
() => {
  const clip = (s, n) => String(s || '').replace(/\s+/g, ' ').trim().slice(0, n);

  const feed = document.querySelector('[data-testid="mainFeed"]')
    || document.querySelector('[data-component-type="LazyColumn"]')
    || document.querySelector('section[aria-label="Primary content"]');

  const items = Array.from(document.querySelectorAll('[role="listitem"][componentkey*="update-card-focus"]'));

  function parseToken(ck) {
    const s = String(ck || '');
    const m = s.match(/update-card-focus(.+?)FeedType_/);
    if (m) return m[1];
    const m2 = s.match(/expanded(.+?)FeedType_/);
    if (m2) return m2[1];
    return s;
  }

  function isAd(text) {
    const head = String(text || '').slice(0, 280);
    return /\bPromoted\b/.test(head);
  }

  const posts = items.map((el) => {
    const ck = el.getAttribute('componentkey') || '';
    const token = parseToken(ck);
    const fullText = el.innerText || '';
    const lines = fullText.split('\n').map(l => l.trim()).filter(Boolean);

    const srHeading = clip((el.querySelector('h2') || {}).innerText || '', 80);

    // Author: "View X’s profile" lives on svg[role=img][aria-label], not the <a>
    let author = '';
    let authorHref = '';
    let authorVia = '';
    const viewEl = el.querySelector('[aria-label^="View "]');
    if (viewEl) {
      const lab = viewEl.getAttribute('aria-label') || '';
      author = lab.replace(/^View\s+/i, '')
        .replace(/['’]s\s+profile$/i, '')
        .replace(/['’]s\s+page$/i, '')
        .replace(/^company:\s*/i, '')
        .trim();
      authorVia = '[aria-label^=View ]';
      const wrapA = viewEl.closest('a[href]') || el.querySelector('a[href*="/in/"], a[href*="/company/"]');
      if (wrapA) authorHref = wrapA.getAttribute('href') || wrapA.href || '';
    }
    if (!author) {
      const inLink = el.querySelector('a[href*="/in/"], a[href*="/company/"], a[href*="/school/"]');
      if (inLink) {
        authorHref = inLink.getAttribute('href') || inLink.href || '';
        const lab = inLink.getAttribute('aria-label') || '';
        author = lab.replace(/\s+Premium Profile.*$/i, '')
          .replace(/\s+(Following|1st|2nd|3rd\+?)\s*$/i, '')
          .trim() || clip(inLink.innerText, 80);
        authorVia = 'a[href*=/in|/company] aria-label';
      }
    }
    if (!author) {
      const followBtn = Array.from(el.querySelectorAll('button, a')).find(b => /^Follow\s+/i.test(b.getAttribute('aria-label') || ''));
      if (followBtn) {
        author = (followBtn.getAttribute('aria-label') || '').replace(/^Follow\s+/i, '').trim();
        authorVia = 'Follow {Name} aria-label';
      }
    }

    // Headline: often the line after "Name • Following/2nd/3rd+"
    let headline = '';
    let relation = '';
    for (let i = 0; i < Math.min(lines.length, 8); i++) {
      const ln = lines[i];
      if (/^(Feed post|Follow|Like|Comment|Repost|Send)$/i.test(ln)) continue;
      if (/likes this|reposted this|celebrates this/i.test(ln)) continue;
      if (author && ln.startsWith(author)) {
        const rest = ln.slice(author.length).replace(/^[•\s]+/, '');
        const relm = rest.match(/^(Following|1st|2nd|3rd\+?)/i);
        if (relm) relation = relm[1];
        // next non-meta line is usually headline
        for (let j = i + 1; j < Math.min(lines.length, i + 5); j++) {
          const nxt = lines[j];
          if (/^(Follow|Visit my website|View my services)$/i.test(nxt)) continue;
          if (/^(\d+[smhdw]|just now|yesterday|\d+mo|\d+yr?)\b/i.test(nxt)) break;
          if (/[•·]/.test(nxt) && nxt.length < 12) break;
          if (nxt.length > 8 && nxt.length < 180 && !/^(Like|Comment)/i.test(nxt)) {
            headline = nxt;
            break;
          }
        }
        break;
      }
    }

    // Relative time
    let relativeTime = '';
    const timeRe = /^(just now|yesterday|\d+\s*(?:second|minute|hour|day|week|month|year)s?\s+ago|\d+[smhdw]|\d+mo|\d+yr?)\s*[•·]?\s*$/i;
    const timeReLoose = /(\d+[smhdw]|\d+mo)\s*•/;
    for (const ln of lines.slice(0, 12)) {
      if (timeRe.test(ln)) { relativeTime = ln.replace(/[•·]/g, '').trim(); break; }
      const m = ln.match(timeReLoose);
      if (m) { relativeTime = m[1]; break; }
    }

    // Commentary
    const textBox = el.querySelector('[data-testid="expandable-text-box"]');
    let textSnippet = clip(textBox ? (textBox.innerText || textBox.textContent) : '', 300);
    const textSel = textBox ? '[data-testid="expandable-text-box"]' : '';
    if (!textSnippet) {
      // fallback: lines after time
      let start = 0;
      for (let i = 0; i < lines.length; i++) {
        if (timeRe.test(lines[i]) || timeReLoose.test(lines[i])) { start = i + 1; break; }
      }
      const bodyLines = lines.slice(start).filter(l => !/^(Like|Comment|Repost|Send|Follow|more)$/i.test(l));
      textSnippet = clip(bodyLines.join(' '), 300);
    }

    // Permalinks — current SDUI feed often has none
    const perm = Array.from(el.querySelectorAll('a[href]')).map(a => a.getAttribute('href') || '').find(h =>
      h.includes('/feed/update/') || h.includes('/posts/') || h.includes('/pulse/') || h.includes('activity:')
    ) || '';

    const profileHrefs = Array.from(new Set(
      Array.from(el.querySelectorAll('a[href*="/in/"], a[href*="/company/"]'))
        .map(a => a.getAttribute('href') || a.href)
        .filter(Boolean)
    )).slice(0, 4);

    // Media
    const imgs = Array.from(el.querySelectorAll('img')).filter(img => {
      const r = img.getBoundingClientRect();
      return r.height >= 40 && r.width >= 40;
    });
    const hasVideo = !!el.querySelector('video, [data-vjs-player], [aria-valuetext*="of"]');
    const hasArticle = /Read full (blog|article)|article/i.test(fullText.slice(0, 800))
      || !!el.querySelector('a[href*="/pulse/"], a[href*="safety/go/"]');
    const hasDocument = /pages|slideshow|document/i.test(clip(fullText, 400)) && !!el.querySelector('img');

    // Reactions from aria-labels
    let reactionText = '';
    let commentsText = '';
    let repostsText = '';
    for (const b of el.querySelectorAll('button, span, a')) {
      const lab = b.getAttribute('aria-label') || '';
      const mR = lab.match(/([\d,.]+)\s*(reaction|like)/i);
      const mC = lab.match(/([\d,.]+)\s*comment/i);
      const mP = lab.match(/([\d,.]+)\s*(repost|share)/i);
      if (mR && !reactionText) reactionText = lab.slice(0, 80);
      if (mC && !commentsText) commentsText = lab.slice(0, 80);
      if (mP && !repostsText) repostsText = lab.slice(0, 80);
    }
    // fallback: social counts as short numeric lines near the end
    if (!reactionText) {
      const nums = lines.filter(l => /^\d[\d,.]*[KMB]?$/.test(l));
      if (nums.length) reactionText = nums[0];
    }

    const ad = isAd(fullText);
    const socialKind = /likes this/.test(fullText.slice(0, 200)) ? 'likes-this'
      : /reposted this/.test(fullText.slice(0, 200)) ? 'repost'
      : /celebrates this/.test(fullText.slice(0, 200)) ? 'celebrate'
      : 'original';

    return {
      token,
      componentkey: ck,
      srHeading,
      author,
      authorVia,
      authorHref,
      headline,
      relation,
      relativeTime,
      permalink: perm,
      textSnippet,
      textSelector: textSel,
      hasMedia: imgs.length > 0 || hasVideo,
      hasVideo,
      hasArticle,
      hasDocument,
      imageCount: imgs.length,
      isAd: ad,
      socialKind,
      reactionText,
      commentsText,
      repostsText,
      profileHrefs,
      innerTextPreview: clip(fullText, 240),
      rectH: Math.round(el.getBoundingClientRect().height),
    };
  });

  return {
    url: location.href,
    title: document.title,
    feedPresent: !!feed,
    feedTestId: feed ? (feed.getAttribute('data-testid') || '') : '',
    feedComponentType: feed ? (feed.getAttribute('data-component-type') || '') : '',
    feedComponentkey: feed ? (feed.getAttribute('componentkey') || '') : '',
    listitemCount: items.length,
    posts,
    bodyPreview: clip(document.body ? document.body.innerText : '', 500),
  };
}
"""

SAMPLE_HTML_JS = r"""
(token) => {
  const items = Array.from(document.querySelectorAll('[role="listitem"][componentkey*="update-card-focus"]'));
  const el = items.find(e => (e.getAttribute('componentkey') || '').includes(token));
  if (!el) return '';
  return (el.outerHTML || '').slice(0, 8192);
}
"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rsc_events = []
    activity_urns: list[str] = []
    rsc_text_sample = ""

    def on_response(resp):
        nonlocal rsc_text_sample
        try:
            url = resp.url
            if "flagship-web/rsc-action/actions/pagination" not in url:
                return
            if "mainFeed" not in url and "sdui" not in url:
                # still capture mainFeed specifically; the URL includes sduiid=...mainFeed
                pass
            entry = {
                "url": url[:300],
                "status": resp.status,
                "ct": (resp.headers or {}).get("content-type", "")[:80],
            }
            try:
                body = resp.body()
                entry["body_len"] = len(body)
                text = body.decode("utf-8", errors="replace")
                urns = re.findall(r"urn:li:(?:activity|ugcPost|share|fsd_update):[A-Za-z0-9:_\-]+", text)
                entry["urn_count"] = len(urns)
                uniq = list(dict.fromkeys(urns))
                entry["urn_unique"] = len(uniq)
                entry["urn_sample"] = uniq[:25]
                for u in uniq:
                    if u not in activity_urns:
                        activity_urns.append(u)
                if not rsc_text_sample and len(text) > 500:
                    rsc_text_sample = text[:12000]
                # tokens of form update-card-focus
                toks = re.findall(r"update-card-focus([A-Za-z0-9_-]{10,80})", text)
                entry["dom_token_sample"] = list(dict.fromkeys(toks))[:10]
            except Exception as e:
                entry["err"] = str(e)[:120]
            rsc_events.append(entry)
        except Exception:
            return

    accumulated: dict[str, dict] = {}
    ads_noted: list[dict] = []
    scroll_log: list[dict] = []
    last_extract = {}
    html_samples: list[dict] = []

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(PROFILE),
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--no-sandbox", "--disable-dev-shm-usage"],
            locale="en-US",
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.on("response", on_response)
        page.goto(FEED_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(5000)

        # login/challenge check
        url = page.url
        title = page.title()
        preview = page.evaluate("() => (document.body && document.body.innerText || '').slice(0, 600)")
        challenged = bool(re.search(
            r"/checkpoint|/authwall|/uas/login|cloudflare|checking your browser|"
            r"let.?s do a quick security check|sign in to linkedin",
            (url + " " + title + " " + preview),
            re.I,
        )) and "Feed |" not in title
        page.screenshot(path=str(OUT / "feed.png"), full_page=False)
        if challenged or "/login" in url or "authwall" in url:
            page.screenshot(path=str(OUT / "challenge.png"), full_page=False)
            write_all([], last_extract, rsc_events, activity_urns, rsc_text_sample, ads_noted, scroll_log, html_samples,
                      blocker={"reason": "login-or-challenge", "url": url, "title": title, "preview": preview})
            ctx.close()
            return 2

        try:
            page.locator('[data-testid="mainFeed"]').click(position={"x": 30, "y": 40}, timeout=4000)
        except Exception:
            page.mouse.click(640, 420)
        page.wait_for_timeout(400)

        start = time.time()
        idle = 0
        last_n = 0
        scroll_mode = 0
        while time.time() - start < MAX_SECONDS:
            last_extract = page.evaluate(EXTRACT_JS)
            for post in last_extract.get("posts") or []:
                tok = post.get("token") or ""
                if not tok:
                    continue
                if post.get("isAd"):
                    if not any(a.get("token") == tok for a in ads_noted):
                        ads_noted.append({"token": tok, "author": post.get("author"), "preview": post.get("innerTextPreview")})
                    continue
                if tok not in accumulated:
                    accumulated[tok] = post
            n = len(accumulated)
            try:
                diag = page.evaluate("""() => ({
                  y: window.scrollY,
                  sh: document.scrollingElement ? document.scrollingElement.scrollHeight : 0,
                  firstCk: (document.querySelector('[role="listitem"][componentkey*="update-card-focus"]') || {}).getAttribute?.('componentkey') || ''
                })""")
            except Exception:
                diag = {}
            scroll_log.append({
                "t": round(time.time() - start, 1),
                "domListitems": last_extract.get("listitemCount"),
                "uniqueNonAds": n,
                "ads": len(ads_noted),
                "scrollY": diag.get("y"),
                "scrollHeight": diag.get("sh"),
                "firstToken": (diag.get("firstCk") or "")[:48],
            })
            if n >= TARGET:
                break
            if n == last_n:
                idle += 1
            else:
                idle = 0
            last_n = n
            try:
                page.locator('[data-testid="mainFeed"]').hover(timeout=1500)
            except Exception:
                page.mouse.move(700, 480)
            scroll_mode = (scroll_mode + 1) % 4
            if scroll_mode == 0:
                page.mouse.wheel(0, 1800)
            elif scroll_mode == 1:
                page.keyboard.press("PageDown")
            elif scroll_mode == 2:
                page.evaluate("""() => {
                  window.scrollBy(0, 2000);
                  const se = document.scrollingElement;
                  if (se) se.scrollBy(0, 2000);
                  const feed = document.querySelector('[data-testid="mainFeed"]');
                  let node = feed;
                  for (let i = 0; i < 8 && node; i++) {
                    try { node.scrollBy(0, 2000); } catch (e) {}
                    node = node.parentElement;
                  }
                }""")
            else:
                page.keyboard.press("Space")
            page.wait_for_timeout(1400)
            if idle == 8:
                try:
                    page.mouse.click(720, 520)
                except Exception:
                    pass
            if idle >= 28:
                scroll_log.append({"t": round(time.time() - start, 1), "note": "idle-stop"})
                break

        last_extract = page.evaluate(EXTRACT_JS)
        page.screenshot(path=str(OUT / "feed.png"), full_page=False)

        # outerHTML samples for 3 posts still in DOM if possible, else any accumulated
        sample_tokens = []
        live_tokens = [p.get("token") for p in (last_extract.get("posts") or []) if p.get("token")]
        for t in live_tokens:
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
                html = page.evaluate(SAMPLE_HTML_JS, t)
            except Exception:
                html = ""
            html_samples.append({"token": t, "outerHTML": html})

        posts = list(accumulated.values())[:TARGET]
        write_all(posts, last_extract, rsc_events, activity_urns, rsc_text_sample, ads_noted, scroll_log, html_samples,
                  blocker=None, url=page.url, title=page.title())
        ctx.close()
    print(f"wrote {len(posts)} posts, ads={len(ads_noted)}, rsc_events={len(rsc_events)}, urns={len(activity_urns)}")
    return 0


def write_all(posts, extract, rsc_events, activity_urns, rsc_text_sample, ads, scroll_log, html_samples,
              blocker=None, url="", title=""):
    with (OUT / "posts.jsonl").open("w", encoding="utf-8") as f:
        for i, p in enumerate(posts, 1):
            rec = {
                "index": i,
                "token": p.get("token") or "",
                "urn": "",  # not present on live SDUI cards; see summary
                "componentkey": p.get("componentkey") or "",
                "author": p.get("author") or "",
                "headline": p.get("headline") or "",
                "relation": p.get("relation") or "",
                "relativeTime": p.get("relativeTime") or "",
                "permalink": p.get("permalink") or "",
                "textSnippet": p.get("textSnippet") or "",
                "hasMedia": bool(p.get("hasMedia")),
                "hasVideo": bool(p.get("hasVideo")),
                "hasArticle": bool(p.get("hasArticle")),
                "isAd": bool(p.get("isAd")),
                "socialKind": p.get("socialKind") or "",
                "reactionText": p.get("reactionText") or "",
                "commentsText": p.get("commentsText") or "",
                "repostsText": p.get("repostsText") or "",
                "profileHref": p.get("authorHref") or "",
                "authorSelector": p.get("authorVia") or "",
                "textSelector": p.get("textSelector") or "",
                "innerTextPreview": p.get("innerTextPreview") or "",
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    (OUT / "html_samples.json").write_text(json.dumps(html_samples, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "rsc_pagination.json").write_text(json.dumps({
        "events": rsc_events,
        "unique_urns_captured": len(activity_urns),
        "urns_sample": activity_urns[:40],
        "text_sample": rsc_text_sample[:8000],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    write_selectors(posts, extract, html_samples, ads)
    write_summary(posts, extract, rsc_events, activity_urns, ads, scroll_log, blocker, url, title)


def write_selectors(posts, extract, html_samples, ads):
    n_author = sum(1 for p in posts if p.get("author"))
    n_text = sum(1 for p in posts if p.get("textSnippet"))
    n_time = sum(1 for p in posts if p.get("relativeTime"))
    n_head = sum(1 for p in posts if p.get("headline"))
    n_perm = sum(1 for p in posts if p.get("permalink"))
    n_react = sum(1 for p in posts if p.get("reactionText"))
    lines = []
    lines.append("# LinkedIn home feed — DOM selector notes (Sep 2026 SDUI)")
    lines.append("")
    lines.append("Live `/feed/` using the existing persistent Chromium profile. LinkedIn has **replaced** the old BEM feed (`feed-shared-update-v2`, `data-urn`) with hashed CSS modules + SDUI `componentkey` attributes.")
    lines.append("")
    lines.append("## Stable-looking hooks (use these)")
    lines.append("")
    lines.append("| Hook | Role | Notes |")
    lines.append("| --- | --- | --- |")
    lines.append("| `section[aria-label='Primary content']` | Feed column | Landmark; survived class hashing. |")
    lines.append("| `[data-testid='mainFeed']` | Infinite-scroll root | Also `role='list'` and `data-component-type='LazyColumn'`. |")
    lines.append("| `[role='listitem'][componentkey*='update-card-focus']` | **Card root** | One per update. Virtualized — nodes unmount on scroll. |")
    lines.append("| `componentkey` value `update-card-focus{TOKEN}FeedType_MAIN_FEED_RELEVANCE` | Identity | TOKEN is ~43-char URL-safe opaque id. **This is the only per-post id on the card.** No `data-urn`, no `/feed/update/` href. |")
    lines.append("| Inner `div[componentkey='{TOKEN}']` | Same TOKEN without prefix | |")
    lines.append("| Wrapper `id` / `componentkey` `expanded{TOKEN}FeedType_MAIN_FEED_RELEVANCE` | Expand wrapper | |")
    lines.append("| `h2` with text `Feed post` | SR heading on each card | Good sanity check that a listitem is an update, not chrome. |")
    lines.append("| `a[aria-label^='View '][href*='/in/']` (or `/company/`) | Author | e.g. `View Elvis S.’s profile`. More stable than hashed class + innerText. |")
    lines.append("| `[data-testid='expandable-text-box']` | Post commentary | Truncated; companion `[data-testid='expandable-text-button']` is “…more”. |")
    lines.append("| `button[aria-label*='Comment' i]` / Like / Repost | Social row | Counts sometimes only in nearby numeric text or aria-label. |")
    lines.append("")
    lines.append(f"Field hit rates on **{len(posts)}** extracted non-ad posts:")
    lines.append("")
    lines.append(f"- author: {n_author}/{len(posts)}")
    lines.append(f"- headline: {n_head}/{len(posts)}")
    lines.append(f"- relativeTime: {n_time}/{len(posts)}")
    lines.append(f"- textSnippet: {n_text}/{len(posts)}")
    lines.append(f"- permalink (`/feed/update/` or `/posts/`): {n_perm}/{len(posts)}  ← expected 0 on this DOM")
    lines.append(f"- reactionText: {n_react}/{len(posts)}")
    lines.append("")
    lines.append("## Unstable / avoid")
    lines.append("")
    lines.append("- **Hashed CSS classes** (`e4b4f16b`, `_89a9815a`, `f6e71273`, …). They dominate the tree and will churn with deploys. Do not key a tracker on them.")
    lines.append("- Legacy BEM: `feed-shared-update-v2`, `update-components-actor__name`, `occludable-update`, `scaffold-finite-scroll__content` — **count was 0** on this session.")
    lines.append("- `data-urn` / `data-id` activity URNs — **not present** on card roots.")
    lines.append("- `a[href*='/feed/update/']` — **not present** in the visible feed DOM (permalinks appear to have been removed from the card).")
    lines.append("- Deep nth-child paths. `LazyColumn` virtualizes; `data-lazy-mount-id` values are ephemeral.")
    lines.append("- Whole-card `innerText` (includes `Feed post`, `Following`, `Like`, `Comment`, social counts). Parse actor aria-label + expandable-text-box instead.")
    lines.append("- `data-page-card` — left-rail/identity widgets, not feed updates.")
    lines.append("- `componentkey` UUIDs on inner buttons (Like/Comment) — per-control, not per-post.")
    lines.append("")
    lines.append("## Card skeleton (observed)")
    lines.append("")
    lines.append("```")
    lines.append("main#workspace")
    lines.append("  section[aria-label='Primary content']")
    lines.append("    div[role=list][data-testid=mainFeed][data-component-type=LazyColumn]")
    lines.append("      div[data-lazy-mount-id]  /* virtualization */")
    lines.append("        div#expanded{TOKEN}FeedType_MAIN_FEED_RELEVANCE")
    lines.append("          div[role=listitem][componentkey=update-card-focus{TOKEN}FeedType_MAIN_FEED_RELEVANCE]")
    lines.append("            h2 > span  'Feed post'")
    lines.append("            a[href=/in/…][aria-label='View {Name}’s profile']")
    lines.append("            … headline / relative time …")
    lines.append("            [data-testid=expandable-text-box]")
    lines.append("            media | article | document")
    lines.append("            social buttons (Like / Comment / Repost)")
    lines.append("```")
    lines.append("")
    lines.append("## Ads")
    lines.append("")
    lines.append("Promoted cards still use the same listitem + `update-card-focus` pattern. Detect via `\\bPromoted\\b` in the first ~280 chars of `innerText` (the old `.update-components-actor__supplementary-actor-info` class is gone).")
    lines.append(f"This run noted **{len(ads)}** promoted cards while scrolling.")
    lines.append("")
    lines.append("## outerHTML samples")
    lines.append("")
    lines.append("See `html_samples.json` (up to 3 cards, truncated to ~8KB).")
    lines.append("")
    (OUT / "selectors.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_summary(posts, extract, rsc_events, activity_urns, ads, scroll_log, blocker, url, title):
    lines = []
    lines.append("# LinkedIn home-feed probe summary")
    lines.append("")
    lines.append("**When:** 2026-09-12 (HKT, UTC+8)")
    lines.append("**Profile reused:** `/workspace/career-job-applications/data/.linkedin-browser-profile` (Playwright `launch_persistent_context`; cookies/session only).")
    lines.append("**Opened:** `https://www.linkedin.com/feed/`")
    lines.append(f"**Final URL:** `{url or (extract or {}).get('url') or ''}`")
    lines.append(f"**Document title:** {title or (extract or {}).get('title') or ''}")
    lines.append("")
    if blocker:
        lines.append("## Login / challenge status: BLOCKED")
        lines.append("")
        lines.append(f"- Reason: `{blocker.get('reason')}`")
        lines.append(f"- URL: `{blocker.get('url')}`")
        lines.append("- Screenshots: `challenge.png`, `feed.png`")
        lines.append("- No passwords requested or stored.")
        lines.append("")
        lines.append("```")
        lines.append((blocker.get("preview") or "")[:800])
        lines.append("```")
        lines.append("")
    else:
        lines.append("## Login / challenge status: FEED LOADED (session valid)")
        lines.append("")
        lines.append("Signed-in home feed rendered (identity module + `data-testid=mainFeed` LazyColumn). No Cloudflare / checkpoint wall.")
        lines.append("")
        lines.append(f"- Distinct non-ad posts in `posts.jsonl`: **{len(posts)}**")
        lines.append(f"- Last DOM snapshot listitems: **{(extract or {}).get('listitemCount')}** (virtualized; not the unique total)")
        lines.append(f"- Promoted/ads noted and skipped: **{len(ads)}**")
        lines.append("- Screenshot: `feed.png`")
        lines.append("")
        if ads:
            lines.append("### Ads noted")
            lines.append("")
            for a in ads[:12]:
                lines.append(f"- {a.get('author') or '(unknown)'} — token `{(a.get('token') or '')[:48]}`")
            lines.append("")

    lines.append("## What changed vs classic LinkedIn feed DOM")
    lines.append("")
    lines.append("This is **not** the old Voyager HTML feed. Observations:")
    lines.append("")
    lines.append("- **Zero** `feed-shared-update-v2` / `data-urn` / `/feed/update/` permalinks on cards.")
    lines.append("- CSS class names are **hashed modules** (unusable as selectors).")
    lines.append("- Identity is SDUI `componentkey` (`update-card-focus{TOKEN}FeedType_MAIN_FEED_RELEVANCE`).")
    lines.append("- Feed root is `[data-testid=mainFeed][data-component-type=LazyColumn][role=list]`.")
    lines.append("- Canonical `urn:li:activity:…` values **do** appear in the RSC pagination payload, not on the card DOM.")
    lines.append("")
    lines.append("## Scroll behavior")
    lines.append("")
    lines.append("LazyColumn virtualizes: ~a dozen listitems mounted at a time. Must **accumulate TOKEN identities across scroll passes** or you will under-count.")
    lines.append("Gradual `mouse.wheel` (~1000px / 1.3s) triggered `POST /flagship-web/rsc-action/actions/pagination?sduiid=com.linkedin.sdui.pagers.feed.mainFeed`.")
    lines.append("")
    if scroll_log:
        lines.append("```json")
        lines.append(json.dumps(scroll_log, indent=2)[:3500])
        lines.append("```")
        lines.append("")

    n_rsc = len(rsc_events)
    urn_n = len(activity_urns)
    lines.append("## Network observations")
    lines.append("")
    lines.append(f"- RSC pagination events captured: **{n_rsc}** (see `rsc_pagination.json`)")
    lines.append(f"- Unique `urn:li:(activity|ugcPost|share|fsd_update):…` parsed out of those bodies: **{urn_n}**")
    lines.append("- Content-Type: `application/octet-stream` but body is **UTF-8 RSC/SDUI flight text** mixed with proto-ish `$type` keys (not Voyager `normalized+json+2.1` feed).")
    lines.append("- GraphQL `/voyager/api/graphql` still fires, but for nav/premium/messaging — **not** the main feed page of cards.")
    lines.append("")
    if rsc_events:
        for e in rsc_events[:6]:
            lines.append(f"- `{e.get('status')}` `{e.get('ct')}` bytes={e.get('body_len')} urns={e.get('urn_count')} unique={e.get('urn_unique')}")
            lines.append(f"  `{e.get('url','')[:180]}`")
        lines.append("")
        if rsc_events[0].get("urn_sample"):
            lines.append("URN sample from RSC:")
            for u in (rsc_events[0].get("urn_sample") or [])[:12]:
                lines.append(f"- `{u}`")
            lines.append("")

    lines.append("## Recommended fetch approach")
    lines.append("")
    if blocker:
        lines.append("N/A until session is logged in.")
    else:
        lines.append("**v1 tracker: scroll + parse the SDUI DOM, keyed by `componentkey` TOKEN.**")
        lines.append("")
        lines.append("Evidence: cards are fully rendered and fields (author via `aria-label`, commentary via `expandable-text-box`, relative time, media) are readable. Virtualization requires accumulating TOKENS while scrolling. Do **not** wait for `data-urn`.")
        lines.append("")
        lines.append("**Do not use hashed CSS. Do not import jobs-ingest left-rail parsers.**")
        lines.append("")
        lines.append("**Network sniff of RSC pagination is the way to recover canonical activity URNs / permalinks**, which the DOM no longer exposes. A single `pagination?sduiid=com.linkedin.sdui.pagers.feed.mainFeed` body can be multi-MB and contains `urn:li:activity:` / `ugcPost` / `share`. That payload is proprietary SDUI/RSC (flight IDs + `$type` + hashed className strings) — **brittle to decode**, so treat it as v1.5 enrichment, not the v1 parser.")
        lines.append("")
        lines.append("Suggested pipeline:")
        lines.append("1. Persistent context, same profile, headful, open `/feed/`.")
        lines.append("2. Wait for `[data-testid=mainFeed]`.")
        lines.append("3. Each pass: query `[role=listitem][componentkey*='update-card-focus']`, skip `Promoted`, upsert by TOKEN.")
        lines.append("4. Scroll until N unique TOKENS or idle.")
        lines.append("5. Optional: `page.on('response')` for `rsc-action/actions/pagination` → regex `urn:li:activity:\\d+` for a URN catalog (join to DOM later if a TOKEN appears in the same payload).")
        lines.append("")
        lines.append("Voyager GraphQL feed dash is **not** how this home feed is paged anymore.")
    lines.append("")
    lines.append("## Auth reuse notes (only)")
    lines.append("")
    lines.append("- `playwright.chromium.launch_persistent_context(profile, headless=False, viewport={1280,900}, args=['--no-sandbox','--disable-dev-shm-usage'])`")
    lines.append("- Reuse cookies/session in `.linkedin-browser-profile`. Attended login in the visible window if it expires. Never store passwords.")
    lines.append("- Do not import jobs-ingest code beyond this launch/profile pattern.")
    lines.append("")
    lines.append("## Output files")
    lines.append("")
    lines.append("- `posts.jsonl` — one JSON object per non-ad post (up to 20)")
    lines.append("- `selectors.md`")
    lines.append("- `summary.md`")
    lines.append("- `feed.png`")
    lines.append("- `html_samples.json`, `rsc_pagination.json` (diagnostics)")
    lines.append("")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Standalone LinkedIn home-feed DOM probe.

Reuses the existing Playwright persistent Chromium profile for cookies only.
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
TARGET_POSTS = 20
MAX_SCROLL_SECONDS = 90

os.environ.setdefault("DISPLAY", ":7")

CHALLENGE_URL_RE = re.compile(
    r"/checkpoint|/authwall|/login|/uas/login|challenge|security-verification|captcha",
    re.I,
)
CHALLENGE_TEXT_RE = re.compile(
    r"let.?s do a quick security check|verify you.?re (a )?human|"
    r"unusual traffic|are you a robot|attention required|"
    r"cloudflare|checking your browser|just a moment|"
    r"sign in to linkedin|join now|welcome back|"
    r"session expired|we.?ve emailed a code",
    re.I,
)


EXTRACT_JS = r"""
() => {
  const clip = (s, n) => String(s || '').replace(/\s+/g, ' ').trim().slice(0, n);
  const abs = (href) => {
    if (!href) return '';
    try { return new URL(href, location.origin).href; } catch (e) { return String(href); }
  };

  function firstText(root, sels) {
    for (const sel of sels) {
      const el = root.querySelector(sel);
      if (!el) continue;
      const t = clip(el.innerText || el.textContent || '', 400);
      if (t) return { text: t, selector: sel };
    }
    return { text: '', selector: '' };
  }

  function firstAttr(root, sels, attr) {
    for (const sel of sels) {
      const el = root.querySelector(sel);
      if (!el) continue;
      const v = el.getAttribute(attr);
      if (v) return { value: v, selector: sel };
    }
    return { value: '', selector: '' };
  }

  function firstHref(root, sels) {
    for (const sel of sels) {
      const el = root.querySelector(sel);
      if (!el) continue;
      const href = el.getAttribute('href') || el.href;
      if (href && href !== '#' && !href.startsWith('javascript:')) {
        return { href: abs(href), selector: sel };
      }
    }
    return { href: '', selector: '' };
  }

  // Candidate card roots. LinkedIn has used several wrappers.
  const cardSels = [
    'div.feed-shared-update-v2[data-urn]',
    'div[data-urn^="urn:li:activity"]',
    'div[data-urn^="urn:li:share"]',
    'div[data-urn^="urn:li:ugcPost"]',
    'div.occludable-update',
    'div.update-components-update',
    'article[data-urn]',
    'div[data-id^="urn:li:activity"]',
    'div[data-id^="urn:li:share"]',
    'div.feed-shared-update-v2',
  ];

  const seen = new Set();
  const cards = [];
  for (const sel of cardSels) {
    document.querySelectorAll(sel).forEach((el) => {
      if (seen.has(el)) return;
      // Prefer innermost data-urn node if nested
      const nested = el.querySelector('[data-urn^="urn:li:"]');
      const node = (nested && nested !== el && el.matches && !el.hasAttribute('data-urn')) ? nested : el;
      if (seen.has(node)) return;
      seen.add(el);
      seen.add(node);
      cards.push({ node, matchedSelector: sel });
    });
  }

  const posts = [];
  const skipped = [];
  const selectorHits = {};

  for (const { node, matchedSelector } of cards) {
    selectorHits[matchedSelector] = (selectorHits[matchedSelector] || 0) + 1;
    const urn = node.getAttribute('data-urn')
      || node.getAttribute('data-id')
      || (node.querySelector('[data-urn]') || {}).getAttribute?.('data-urn')
      || '';

    const className = String(node.className || '').slice(0, 300);
    const tag = node.tagName.toLowerCase();

    const actorName = firstText(node, [
      '.update-components-actor__name .hoverable-link-text span[aria-hidden="true"]',
      '.update-components-actor__name .hoverable-link-text',
      '.update-components-actor__name span[aria-hidden="true"]',
      '.update-components-actor__name',
      '.update-components-actor__title span[aria-hidden="true"]',
      '.feed-shared-actor__name',
      '.update-components-actor__container a[href*="/in/"] span[aria-hidden="true"]',
      'a.app-aware-link span[aria-hidden="true"]',
    ]);

    const headline = firstText(node, [
      '.update-components-actor__description',
      '.update-components-actor__meta-description',
      '.feed-shared-actor__description',
      '.update-components-actor__supplementary-actor-info',
    ]);

    const timeEl = firstText(node, [
      '.update-components-actor__sub-description',
      '.feed-shared-actor__sub-description',
      'span.update-components-actor__sub-description-link',
      'a.update-components-actor__sub-description-link',
      'time',
      '.visually-hidden',
    ]);

    const permalink = firstHref(node, [
      'a[href*="/feed/update/"]',
      'a[href*="/posts/"]',
      'a[href*="activity:"]',
      'a[href*="/feed/update/urn:"]',
      '.update-components-actor__sub-description a',
      'a.update-components-actor__sub-description-link',
    ]);

    const textBlock = firstText(node, [
      '.update-components-text .break-words',
      '.update-components-text',
      '.feed-shared-update-v2__description .break-words',
      '.feed-shared-update-v2__description',
      '.feed-shared-text',
      '.feed-shared-inline-show-more-text',
      '.update-components-update-v2__commentary',
      'div[class*="update-components-text"]',
    ]);

    const hasImage = !!node.querySelector(
      'img.update-components-image__image, .update-components-image, .feed-shared-image, img[class*="update-components-image"], video, .update-components-linkedin-video, .feed-shared-linkedin-video'
    );
    const hasArticle = !!node.querySelector(
      '.update-components-article, .feed-shared-article, a.update-components-mini-update-v2, .update-components-article--with-small-image'
    );
    const hasDocument = !!node.querySelector(
      '.update-components-document, .feed-shared-document, iframe[src*="document"]'
    );
    const hasPoll = !!node.querySelector('.update-components-poll, .feed-shared-poll');

    const promotedText = clip((node.innerText || '').split('\n').slice(0, 12).join(' '), 400);
    const isPromoted = /\bpromoted\b/i.test(promotedText)
      || !!node.querySelector('[data-test-id*="promoted"], .update-components-actor__supplementary-actor-info');
    // supplementary-actor-info is also used for "following" etc; tighten:
    let isAd = false;
    const sup = node.querySelector('.update-components-actor__supplementary-actor-info, .feed-shared-actor__sub-description');
    const supText = clip(sup ? (sup.innerText || '') : '', 80);
    if (/\bpromoted\b/i.test(supText) || /\bpromoted\b/i.test(clip(node.innerText || '', 200).slice(0, 80))) {
      isAd = true;
    }
    // also check for "Promoted" as a distinct small label near actor
    const actorBlock = node.querySelector('.update-components-actor, .feed-shared-actor');
    if (actorBlock && /\bPromoted\b/.test(actorBlock.innerText || '')) isAd = true;

    const reactions = firstText(node, [
      '.social-details-social-counts__reactions-count',
      'button.social-details-social-counts__count-value',
      '.social-details-social-counts__count-value',
      'span.social-details-social-counts__reactions-count',
      '[aria-label*="reaction"]',
    ]);

    const comments = firstText(node, [
      '.social-details-social-counts__comments',
      'button[aria-label*="comment"]',
    ]);

    const profileHref = firstHref(node, [
      '.update-components-actor__image',
      '.update-components-actor__name a',
      'a[href*="/in/"]',
      'a[href*="/company/"]',
    ]);

    const dataAttrs = {};
    for (const a of node.attributes) {
      if (a.name.startsWith('data-')) dataAttrs[a.name] = a.value.slice(0, 200);
    }

    const classes = Array.from(node.classList || []).slice(0, 20);

    const post = {
      matchedSelector,
      tag,
      classes,
      dataAttrs,
      urn,
      author: actorName.text,
      authorSelector: actorName.selector,
      headline: headline.text,
      headlineSelector: headline.selector,
      relativeTime: timeEl.text,
      timeSelector: timeEl.selector,
      permalink: permalink.href,
      permalinkSelector: permalink.selector,
      textSnippet: clip(textBlock.text, 300),
      textSelector: textBlock.selector,
      hasMedia: hasImage || hasDocument,
      hasArticle,
      hasPoll,
      isAd,
      reactionText: reactions.text,
      commentsText: comments.text,
      profileHref: profileHref.href,
      innerTextPreview: clip(node.innerText || '', 240),
    };

    if (isAd) {
      skipped.push({ reason: 'ad', urn, author: post.author, preview: post.innerTextPreview });
    }
    posts.push(post);
  }

  // Diagnostic: what feed-ish classes exist on page
  const classCounts = {};
  const interesting = [
    'feed-shared-update-v2', 'occludable-update', 'update-components-actor',
    'update-components-text', 'feed-shared-text', 'scaffold-finite-scroll__content',
    'feed-container', 'core-rail', 'feed-shared-update-v2__control-menu',
    'social-details-social-counts', 'update-components-image',
    'feed-shared-article', 'update-components-article',
    'artdeco-card', 'feed-shared-update-v2__description',
    'update-components-actor__name', 'update-components-actor__sub-description',
  ];
  for (const c of interesting) {
    classCounts[c] = document.getElementsByClassName(c).length;
  }

  const dataUrnCount = document.querySelectorAll('[data-urn]').length;
  const dataUrnSamples = Array.from(document.querySelectorAll('[data-urn]'))
    .slice(0, 8)
    .map((el) => ({
      tag: el.tagName.toLowerCase(),
      classes: String(el.className || '').slice(0, 180),
      urn: (el.getAttribute('data-urn') || '').slice(0, 120),
    }));

  const main = document.querySelector('main') || document.body;
  const mainRole = (document.querySelector('[role="main"]') || {}).tagName || '';

  return {
    url: location.href,
    title: document.title,
    posts,
    skippedAds: skipped,
    selectorHits,
    classCounts,
    dataUrnCount,
    dataUrnSamples,
    mainRole,
    bodyTextPreview: clip(document.body ? document.body.innerText : '', 800),
    feedRootPresent: !!document.querySelector('.scaffold-finite-scroll__content, .feed-container, main.scaffold-layout__main'),
  };
}
"""


def looks_like_challenge(page, extract) -> tuple[bool, str]:
    url = page.url or ""
    title = page.title() or ""
    if CHALLENGE_URL_RE.search(url):
        return True, f"url:{url}"
    if CHALLENGE_URL_RE.search(title):
        return True, f"title:{title}"
    preview = (extract or {}).get("bodyTextPreview") or ""
    # Login wall: no feed, sign-in copy
    if CHALLENGE_TEXT_RE.search(preview) and not (extract or {}).get("posts"):
        # If we have feed posts, ignore stray "join" in a post
        if not (extract or {}).get("feedRootPresent") and not (extract or {}).get("dataUrnCount"):
            m = CHALLENGE_TEXT_RE.search(preview)
            return True, f"text:{m.group(0) if m else preview[:80]}"
    # Cloudflare interstitial with almost no LinkedIn chrome
    if re.search(r"cloudflare|checking your browser|just a moment", preview, re.I):
        return True, "cloudflare-or-browser-check"
    return False, ""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    network_log: list[dict] = []

    def on_response(resp):
        try:
            url = resp.url
            if not any(
                k in url
                for k in (
                    "/voyager/",
                    "/graphql",
                    "feed",
                    "updates",
                    "voyagerFeedDash",
                    "FeedUpdates",
                    "linkedin.com/feed",
                )
            ):
                return
            # skip static assets
            if any(url.endswith(ext) for ext in (".js", ".css", ".png", ".jpg", ".svg", ".woff2", ".gif")):
                return
            entry = {
                "status": resp.status,
                "method": resp.request.method,
                "url": url[:500],
                "content_type": (resp.headers or {}).get("content-type", "")[:80],
            }
            # Sample JSON keys for a few voyager/graphql calls
            ct = entry["content_type"]
            if "json" in ct and len(network_log) < 40:
                try:
                    data = resp.json()
                    if isinstance(data, dict):
                        entry["json_keys"] = list(data.keys())[:20]
                        # graphql often has data / included
                        if "included" in data and isinstance(data["included"], list):
                            types = []
                            for item in data["included"][:30]:
                                if isinstance(item, dict):
                                    t = item.get("$type") or item.get("type") or ""
                                    if t:
                                        types.append(str(t)[:80])
                            entry["included_types_sample"] = types[:15]
                            entry["included_count"] = len(data["included"])
                        if "data" in data and isinstance(data["data"], dict):
                            entry["data_keys"] = list(data["data"].keys())[:15]
                    elif isinstance(data, list):
                        entry["json_list_len"] = len(data)
                except Exception:
                    entry["json_parse"] = "failed"
            network_log.append(entry)
        except Exception:
            return

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            str(PROFILE),
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--no-sandbox", "--disable-dev-shm-usage"],
            locale="en-US",
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.on("response", on_response)

        blocker = None
        extract = None
        try:
            page.goto(FEED_URL, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(4000)
            extract = page.evaluate(EXTRACT_JS)
            challenged, reason = looks_like_challenge(page, extract)
            page.screenshot(path=str(OUT / "feed.png"), full_page=False)
            if challenged:
                page.screenshot(path=str(OUT / "challenge.png"), full_page=False)
                blocker = {
                    "status": "blocked",
                    "reason": reason,
                    "url": page.url,
                    "title": page.title(),
                    "bodyTextPreview": (extract or {}).get("bodyTextPreview", ""),
                }
                write_outputs([], extract or {}, network_log, blocker, notes=["Stopped at challenge/login wall."])
                context.close()
                return 2

            # Wait a bit more for feed hydration
            page.wait_for_timeout(2500)
            start = time.time()
            last_count = 0
            idle_rounds = 0
            scroll_notes = []
            while time.time() - start < MAX_SCROLL_SECONDS:
                extract = page.evaluate(EXTRACT_JS)
                n = len((extract or {}).get("posts") or [])
                unique_urns = {p.get("urn") for p in (extract or {}).get("posts") or [] if p.get("urn")}
                non_ads = [
                    p
                    for p in (extract or {}).get("posts") or []
                    if not p.get("isAd")
                ]
                scroll_notes.append(
                    {
                        "t": round(time.time() - start, 1),
                        "posts": n,
                        "uniqueUrns": len(unique_urns),
                        "nonAds": len(non_ads),
                    }
                )
                if len(non_ads) >= TARGET_POSTS or len(unique_urns) >= TARGET_POSTS:
                    break
                if n == last_count:
                    idle_rounds += 1
                else:
                    idle_rounds = 0
                last_count = n
                # gradual scroll
                page.mouse.wheel(0, 900)
                page.wait_for_timeout(1200)
                if idle_rounds >= 8:
                    # try scrolling the main column instead
                    page.evaluate(
                        """() => {
                          const sc = document.querySelector('.scaffold-finite-scroll__content')
                            || document.querySelector('main')
                            || document.scrollingElement;
                          if (sc) sc.scrollBy(0, 1200);
                          window.scrollBy(0, 1200);
                        }"""
                    )
                    page.wait_for_timeout(1500)
                if idle_rounds >= 14:
                    scroll_notes.append({"t": round(time.time() - start, 1), "note": "idle-stop"})
                    break

            extract = page.evaluate(EXTRACT_JS)
            page.screenshot(path=str(OUT / "feed.png"), full_page=False)

            posts = (extract or {}).get("posts") or []
            # Dedup by urn then permalink then text
            deduped = []
            seen = set()
            ads_noted = []
            for p_item in posts:
                key = p_item.get("urn") or p_item.get("permalink") or p_item.get("textSnippet") or p_item.get("innerTextPreview")
                if not key:
                    continue
                if key in seen:
                    continue
                seen.add(key)
                if p_item.get("isAd"):
                    ads_noted.append(
                        {
                            "urn": p_item.get("urn"),
                            "author": p_item.get("author"),
                            "preview": p_item.get("innerTextPreview"),
                        }
                    )
                    continue
                deduped.append(p_item)
                if len(deduped) >= TARGET_POSTS:
                    break

            # If we skipped too many as ads and have few posts, include remaining non-empty cards
            if len(deduped) < 8:
                for p_item in posts:
                    key = p_item.get("urn") or p_item.get("permalink") or p_item.get("innerTextPreview")
                    if not key or key in seen:
                        continue
                    if not (p_item.get("author") or p_item.get("textSnippet") or p_item.get("urn")):
                        continue
                    seen.add(key)
                    p_item = dict(p_item)
                    p_item["includedDespiteAdFlag"] = True
                    deduped.append(p_item)
                    if len(deduped) >= TARGET_POSTS:
                        break

            # outerHTML samples for 2-3 representative posts
            samples = []
            sample_js = r"""
            (urn) => {
              const el = document.querySelector('[data-urn="' + urn + '"]')
                || document.querySelector('[data-id="' + urn + '"]');
              if (!el) return '';
              return (el.outerHTML || '').slice(0, 8192);
            }
            """
            for p_item in deduped[:3]:
                urn = p_item.get("urn") or ""
                html = ""
                if urn:
                    try:
                        html = page.evaluate(sample_js, urn)
                    except Exception:
                        html = ""
                samples.append({"urn": urn, "outerHTML": html})

            write_outputs(
                deduped,
                extract or {},
                network_log,
                blocker=None,
                notes=scroll_notes,
                ads=ads_noted,
                html_samples=samples,
                url=page.url,
                title=page.title(),
            )
        finally:
            try:
                context.close()
            except Exception:
                pass
    return 0


def write_outputs(posts, extract, network_log, blocker, notes, ads=None, html_samples=None, url="", title=""):
    ads = ads or []
    html_samples = html_samples or []
    posts_path = OUT / "posts.jsonl"
    with posts_path.open("w", encoding="utf-8") as f:
        for i, p_item in enumerate(posts, 1):
            rec = {
                "index": i,
                "urn": p_item.get("urn") or "",
                "author": p_item.get("author") or "",
                "headline": p_item.get("headline") or "",
                "relativeTime": p_item.get("relativeTime") or "",
                "permalink": p_item.get("permalink") or "",
                "textSnippet": p_item.get("textSnippet") or "",
                "hasMedia": bool(p_item.get("hasMedia")),
                "hasArticle": bool(p_item.get("hasArticle")),
                "hasPoll": bool(p_item.get("hasPoll")),
                "isAd": bool(p_item.get("isAd")),
                "reactionText": p_item.get("reactionText") or "",
                "commentsText": p_item.get("commentsText") or "",
                "profileHref": p_item.get("profileHref") or "",
                "matchedSelector": p_item.get("matchedSelector") or "",
                "authorSelector": p_item.get("authorSelector") or "",
                "headlineSelector": p_item.get("headlineSelector") or "",
                "timeSelector": p_item.get("timeSelector") or "",
                "permalinkSelector": p_item.get("permalinkSelector") or "",
                "textSelector": p_item.get("textSelector") or "",
                "classes": p_item.get("classes") or [],
                "dataAttrs": p_item.get("dataAttrs") or {},
                "innerTextPreview": p_item.get("innerTextPreview") or "",
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    samples_path = OUT / "html_samples.json"
    samples_path.write_text(json.dumps(html_samples, ensure_ascii=False, indent=2), encoding="utf-8")

    net_path = OUT / "network_sample.json"
    net_path.write_text(json.dumps(network_log[:80], ensure_ascii=False, indent=2), encoding="utf-8")

    raw_path = OUT / "extract_raw.json"
    raw_slim = {
        "url": extract.get("url"),
        "title": extract.get("title"),
        "selectorHits": extract.get("selectorHits"),
        "classCounts": extract.get("classCounts"),
        "dataUrnCount": extract.get("dataUrnCount"),
        "dataUrnSamples": extract.get("dataUrnSamples"),
        "feedRootPresent": extract.get("feedRootPresent"),
        "bodyTextPreview": extract.get("bodyTextPreview"),
        "skippedAds": extract.get("skippedAds"),
        "postCountRaw": len(extract.get("posts") or []),
    }
    raw_path.write_text(json.dumps(raw_slim, ensure_ascii=False, indent=2), encoding="utf-8")

    write_selectors_md(posts, extract, html_samples)
    write_summary_md(posts, extract, network_log, blocker, notes, ads, url, title)


def write_selectors_md(posts, extract, html_samples):
    class_counts = extract.get("classCounts") or {}
    selector_hits = extract.get("selectorHits") or {}
    data_urn_samples = extract.get("dataUrnSamples") or []

    # Aggregate which field selectors actually fired
    field_hits: dict[str, dict[str, int]] = {}
    for key in ("matchedSelector", "authorSelector", "headlineSelector", "timeSelector", "permalinkSelector", "textSelector"):
        counts: dict[str, int] = {}
        for p_item in posts:
            sel = p_item.get(key) or ""
            if sel:
                counts[sel] = counts.get(sel, 0) + 1
        field_hits[key] = counts

    lines = []
    lines.append("# LinkedIn home feed — DOM selector notes")
    lines.append("")
    lines.append("Observed from a live `/feed/` session using the existing persistent Chromium profile.")
    lines.append("These are **observations**, not a stable public API. LinkedIn class names change often.")
    lines.append("")
    lines.append("## Stable-looking hooks (prefer these)")
    lines.append("")
    lines.append("In this session, the most reliable identifiers were **URN attributes** and **permalink hrefs**,")
    lines.append("not BEM class names (those still worked but look more volatile).")
    lines.append("")
    lines.append("| Hook | Why it looked useful |")
    lines.append("| --- | --- |")
    lines.append("| `[data-urn^='urn:li:activity']` / `[data-urn^='urn:li:share']` / `[data-urn^='urn:li:ugcPost']` | Present on card roots; unique per update. |")
    lines.append("| `a[href*='/feed/update/']` | Permalink to the activity; often encodes the same URN. |")
    lines.append("| `a[href*='/posts/']` | Alternate permalink shape for some author posts. |")
    lines.append("| `a[href*='/in/']` / `a[href*='/company/']` | Author profile vs company page. |")
    lines.append("| `main` / `[role='main']` / `.scaffold-finite-scroll__content` | Feed column / infinite-scroll root. |")
    lines.append("")
    lines.append("### Field selectors that actually matched in this run")
    lines.append("")
    for key, counts in field_hits.items():
        lines.append(f"**{key}**")
        if not counts:
            lines.append("- *(none matched)*")
        else:
            for sel, n in sorted(counts.items(), key=lambda kv: -kv[1]):
                lines.append(f"- `{sel}` — {n} posts")
        lines.append("")

    lines.append("## Class-name counts on the page (diagnostic)")
    lines.append("")
    lines.append("| Class | Count |")
    lines.append("| --- | ---: |")
    for c, n in sorted(class_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{c}` | {n} |")
    lines.append("")
    lines.append("### Card-root selector hits (raw, before dedup)")
    lines.append("")
    if selector_hits:
        for sel, n in sorted(selector_hits.items(), key=lambda kv: -kv[1]):
            lines.append(f"- `{sel}` — {n}")
    else:
        lines.append("- *(none)*")
    lines.append("")
    lines.append("## Unstable / avoid")
    lines.append("")
    lines.append("- Auto-generated / hashed class fragments (`artdeco-*` utilities are OK as chrome, not as identity).")
    lines.append("- Deep nth-child paths (`main > div:nth-child(3) > …`). Virtualized feed reorders nodes.")
    lines.append("- Occlusion wrappers (`.occludable-update`) — they wrap cards for virtualization; the URN lives on an inner node.")
    lines.append("- `innerText` of the whole card — includes Like / Comment / Promoted / social counts; parse actor + commentary nodes instead.")
    lines.append("- Treating `.update-components-actor__supplementary-actor-info` as always meaning Promoted (also used for Following / other labels).")
    lines.append("- `data-id` vs `data-urn` — both appeared in past LinkedIn versions; check which is populated.")
    lines.append("")
    lines.append("## `data-urn` samples")
    lines.append("")
    if data_urn_samples:
        lines.append("```json")
        lines.append(json.dumps(data_urn_samples, indent=2)[:4000])
        lines.append("```")
    else:
        lines.append("*(none found)*")
    lines.append("")
    lines.append("## outerHTML samples")
    lines.append("")
    lines.append("See `html_samples.json` (truncated to ~8KB each, up to 3 cards).")
    lines.append("")
    (OUT / "selectors.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_summary_md(posts, extract, network_log, blocker, notes, ads, url, title):
    lines = []
    lines.append("# LinkedIn home-feed probe summary")
    lines.append("")
    lines.append("**When:** 2026-09-12 (Asia/Hong_Kong)")
    lines.append("**Profile reused:** `/workspace/career-job-applications/data/.linkedin-browser-profile` (Playwright persistent context; cookies/session only).")
    lines.append("**URL opened:** `https://www.linkedin.com/feed/`")
    lines.append(f"**Final URL:** `{url or extract.get('url') or ''}`")
    lines.append(f"**Document title:** {title or extract.get('title') or ''}")
    lines.append("")
    if blocker:
        lines.append("## Login / challenge status: BLOCKED")
        lines.append("")
        lines.append(f"- Reason: `{blocker.get('reason')}`")
        lines.append(f"- URL: `{blocker.get('url')}`")
        lines.append(f"- Title: {blocker.get('title')}")
        lines.append("- Screenshot: `challenge.png` (and `feed.png`)")
        lines.append("- No passwords were requested or stored.")
        lines.append("")
        lines.append("### Page text preview")
        lines.append("")
        lines.append("```")
        lines.append((blocker.get("bodyTextPreview") or "")[:800])
        lines.append("```")
        lines.append("")
        lines.append("## Recommended next step")
        lines.append("")
        lines.append("A human needs to complete login / challenge in this same persistent profile (visible Chromium).")
        lines.append("Do not paste passwords into the probe. After login, re-run the probe.")
        lines.append("")
    else:
        lines.append("## Login / challenge status: FEED LOADED")
        lines.append("")
        lines.append(f"- Distinct posts written to `posts.jsonl`: **{len(posts)}**")
        lines.append(f"- Raw card nodes seen in last extract: **{extract.get('postCountRaw')}**")
        lines.append(f"- `data-urn` nodes on page: **{extract.get('dataUrnCount')}**")
        lines.append(f"- Ads / promoted noted (skipped when possible): **{len(ads)}**")
        lines.append("- Screenshot: `feed.png`")
        lines.append("")
        if ads:
            lines.append("### Ads noted")
            lines.append("")
            for a in ads[:10]:
                lines.append(f"- {a.get('author') or '(no author)'} — `{(a.get('urn') or '')[:80]}`")
            lines.append("")

    lines.append("## Scroll behavior")
    lines.append("")
    if notes:
        lines.append("Timeline (seconds, counts):")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(notes, indent=2)[:4000])
        lines.append("```")
        lines.append("")
    else:
        lines.append("No scroll (blocked before feed).")
        lines.append("")
    lines.append("Feed is infinite-scrolled / virtualized (`.scaffold-finite-scroll__content` / occludable updates).")
    lines.append("Gradual `mouse.wheel` (~900px / 1.2s) was used, 90s budget, target ~20 distinct cards.")
    lines.append("")

    # Network vs DOM recommendation
    voyager = [
        e
        for e in network_log
        if "/voyager/" in (e.get("url") or "") or "/graphql" in (e.get("url") or "")
    ]
    feedish = [
        e
        for e in voyager
        if any(
            k.lower() in (e.get("url") or "").lower()
            for k in ("feed", "update", "voyagerFeed", "FeedDash", "graphql")
        )
    ]
    lines.append("## Network observations")
    lines.append("")
    lines.append(f"- Captured interesting responses: **{len(network_log)}** (see `network_sample.json`)")
    lines.append(f"- Voyager/GraphQL-ish: **{len(voyager)}**")
    lines.append("")
    if feedish[:8]:
        lines.append("Sample endpoints:")
        lines.append("")
        for e in feedish[:12]:
            lines.append(f"- `{e.get('status')}` `{e.get('method')}` `{e.get('url','')[:180]}`")
            if e.get("json_keys"):
                lines.append(f"  keys: {e.get('json_keys')}")
            if e.get("included_types_sample"):
                lines.append(f"  included $types: {e.get('included_types_sample')[:8]}")
        lines.append("")

    lines.append("## Recommended fetch approach")
    lines.append("")
    if blocker:
        lines.append("Cannot recommend until the session is logged in. After login, compare DOM cards vs Voyager/GraphQL payloads.")
    else:
        has_json_feed = any(
            e.get("json_keys") or e.get("included_count")
            for e in voyager
        )
        has_dom = len(posts) > 0 and any(p.get("urn") or p.get("permalink") for p in posts)
        if has_dom and has_json_feed:
            lines.append("**Hybrid, with DOM as the v1 tracker and network as an optional enrichment.**")
            lines.append("")
            lines.append("- DOM cards expose URN + actor + commentary + permalink with CSS hooks that matched in this session.")
            lines.append("- Voyager/GraphQL responses also fire on scroll (see `network_sample.json`); they may be denser but are versioned, authenticated, and more brittle to decode (`included` graph).")
            lines.append("- For a **new standalone feed-tracker**, start with **scroll + parse DOM** using `data-urn` as the identity key and permalink as fallback. Persist those URNs so virtualization/reordering does not double-count.")
            lines.append("- Optionally record matching `/voyager/api/graphql` (or feed dash) URLs for a later decoder; do not block v1 on sniffing.")
        elif has_dom and not has_json_feed:
            lines.append("**Scroll + parse DOM.** Feed cards were present and structured; no clearly-usable JSON feed payload was captured (or it was non-JSON / empty). Network sniff is not justified yet.")
            lines.append("")
            lines.append("- Identity: `data-urn` then `/feed/update/` href.")
            lines.append("- Scroll the main column; wait for new `data-urn` values; stop on idle.")
        elif has_json_feed and not has_dom:
            lines.append("**Network sniff / Voyager decode looks more promising than DOM in this session** (cards were sparse or unstructured while JSON feed calls succeeded). Treat as a follow-up, not v1, because GraphQL shapes churn.")
        else:
            lines.append("Inconclusive. Re-run after confirming the feed column is hydrated. Default to DOM scroll+parse if cards appear.")
    lines.append("")
    lines.append("## Auth reuse notes (only)")
    lines.append("")
    lines.append("- Reuse `launch_persistent_context(user_data_dir=.../.linkedin-browser-profile, headless=False)` — same as jobs ingest.")
    lines.append("- Do **not** import jobs-ingest parsers, left-rail collectors, or Easy Apply logic.")
    lines.append("- Do not store passwords; attended login in the visible window if the session expires.")
    lines.append("- Viewport used: 1280×900; args: `--no-sandbox --disable-dev-shm-usage` (box environment).")
    lines.append("")
    lines.append("## Output files")
    lines.append("")
    lines.append("- `posts.jsonl`")
    lines.append("- `selectors.md`")
    lines.append("- `summary.md`")
    lines.append("- `feed.png`")
    lines.append("- `challenge.png` (only if blocked)")
    lines.append("- `html_samples.json`, `network_sample.json`, `extract_raw.json` (diagnostics)")
    lines.append("")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

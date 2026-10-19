#!/usr/bin/env python3
from __future__ import annotations
import json, os, time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path("/workspace/linkedin-feed-probe")
PROFILE = Path("/workspace/career-job-applications/data/.linkedin-browser-profile")
os.environ.setdefault("DISPLAY", ":7")

DUMP_JS = r"""
() => {
  const clip = (s, n) => String(s || '').replace(/\s+/g, ' ').trim().slice(0, n);
  const main = document.querySelector('main') || document.querySelector('[role="main"]') || document.body;

  // Collect unique attribute names in main
  const attrCounts = {};
  const dataAttrSamples = {};
  const classTokenCounts = {};
  const all = main.querySelectorAll('*');
  for (const el of all) {
    for (const a of el.attributes) {
      attrCounts[a.name] = (attrCounts[a.name] || 0) + 1;
      if (a.name.startsWith('data-') || a.name.startsWith('aria-')) {
        if (!dataAttrSamples[a.name]) dataAttrSamples[a.name] = [];
        if (dataAttrSamples[a.name].length < 6 && a.value) {
          dataAttrSamples[a.name].push(a.value.slice(0, 180));
        }
      }
    }
    const cn = el.className;
    if (typeof cn === 'string') {
      for (const t of cn.split(/\s+/).filter(Boolean)) {
        if (t.length < 80) classTokenCounts[t] = (classTokenCounts[t] || 0) + 1;
      }
    }
  }

  const topClasses = Object.entries(classTokenCounts)
    .sort((a,b) => b[1]-a[1])
    .slice(0, 80)
    .map(([k,v]) => ({cls:k, n:v}));

  // href patterns
  const hrefs = Array.from(main.querySelectorAll('a[href]'))
    .map(a => a.getAttribute('href') || '')
    .filter(Boolean);
  const hrefKinds = {};
  for (const h of hrefs) {
    let kind = 'other';
    if (h.includes('/feed/update/')) kind = 'feed-update';
    else if (h.includes('/posts/')) kind = 'posts';
    else if (h.includes('/in/')) kind = 'profile';
    else if (h.includes('/company/')) kind = 'company';
    else if (h.includes('/pulse/')) kind = 'pulse';
    else if (h.includes('activity:')) kind = 'activity';
    else if (h.includes('/feed/')) kind = 'feed-other';
    hrefKinds[kind] = (hrefKinds[kind] || 0) + 1;
  }
  const hrefSamples = {};
  for (const kind of Object.keys(hrefKinds)) {
    hrefSamples[kind] = hrefs.filter(h => {
      if (kind==='feed-update') return h.includes('/feed/update/');
      if (kind==='posts') return h.includes('/posts/');
      if (kind==='profile') return h.includes('/in/');
      if (kind==='company') return h.includes('/company/');
      if (kind==='pulse') return h.includes('/pulse/');
      if (kind==='activity') return h.includes('activity:');
      if (kind==='feed-other') return h.includes('/feed/') && !h.includes('/feed/update/');
      return true;
    }).slice(0, 5);
  }

  // Find likely post cards: look for "Feed post" text, or articles, or role=article
  const articleCount = main.querySelectorAll('article').length;
  const roleArticle = main.querySelectorAll('[role="article"]').length;
  const feedPostTextNodes = [];
  const walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walker.nextNode())) {
    const t = (n.nodeValue || '').trim();
    if (t === 'Feed post' || t.startsWith('Feed post')) {
      feedPostTextNodes.push('found');
    }
  }

  // Walk up from "Feed post" or from Like buttons
  function ancestors(el, depth) {
    const out = [];
    let cur = el;
    for (let i=0; i<depth && cur && cur !== document.body; i++) {
      out.push({
        tag: cur.tagName.toLowerCase(),
        id: cur.id || '',
        role: cur.getAttribute('role') || '',
        classes: String(cur.className || '').slice(0, 200),
        attrs: Array.from(cur.attributes).slice(0, 20).map(a => [a.name, a.value.slice(0, 120)]),
      });
      cur = cur.parentElement;
    }
    return out;
  }

  const cardHints = [];
  // buttons with Like
  const likeBtns = Array.from(main.querySelectorAll('button')).filter(b => /^(Like|React|Comment|Repost)$/i.test((b.innerText||'').trim()) || /like|comment|repost/i.test(b.getAttribute('aria-label')||''));
  if (likeBtns[0]) {
    cardHints.push({hint:'first-like-button-ancestors', chain: ancestors(likeBtns[0], 12)});
  }

  // Look for elements containing both an author-ish link and a time-ish string
  const timeLike = Array.from(main.querySelectorAll('time, span, a')).filter(el => {
    const t = (el.innerText || '').trim();
    return /^(just now|\d+[smhdw]|[1-9]\d?[smhd]|[1-9]\d?mo|1y)$/i.test(t) || /^\d+[smhdw]$/i.test(t) || /^\d+h$/.test(t);
  }).slice(0, 5);
  if (timeLike[0]) {
    cardHints.push({hint:'first-relative-time-ancestors', text: timeLike[0].innerText, chain: ancestors(timeLike[0], 12)});
  }

  // Try sdui / rsc related attrs
  const sduiEls = Array.from(main.querySelectorAll('[data-sdui-component], [data-sdui-id], [data-id], [data-view-name], [data-test-id], [data-finite-scroll-hotkey-item], [data-view-tracking-scope]'));
  const sduiSample = sduiEls.slice(0, 15).map(el => ({
    tag: el.tagName.toLowerCase(),
    classes: String(el.className||'').slice(0,160),
    attrs: Array.from(el.attributes).slice(0,15).map(a => [a.name, a.value.slice(0,140)]),
  }));

  // HTML of main's first 8 direct / nested "card-ish" children
  // Heuristic: divs that are reasonably tall and contain "Like" or "Follow"
  const candidates = [];
  for (const el of main.querySelectorAll('div, article, li, section')) {
    const r = el.getBoundingClientRect();
    if (r.height < 120 || r.height > 1400) continue;
    if (r.width < 400) continue;
    const t = el.innerText || '';
    if (!/Like|Comment|Follow|Promoted/i.test(t)) continue;
    // skip if a parent is already a candidate
    if (candidates.some(c => c.contains(el))) continue;
    // skip if this contains too many other candidates (too high)
    candidates.push(el);
    if (candidates.length >= 25) break;
  }
  // prune nested
  const pruned = candidates.filter(el => !candidates.some(o => o !== el && o.contains(el)));

  const cards = pruned.slice(0, 8).map((el, i) => ({
    i,
    tag: el.tagName.toLowerCase(),
    classes: String(el.className||'').slice(0, 250),
    attrs: Array.from(el.attributes).map(a => [a.name, a.value.slice(0, 200)]),
    rect: {w: Math.round(el.getBoundingClientRect().width), h: Math.round(el.getBoundingClientRect().height)},
    textPreview: clip(el.innerText, 400),
    htmlHead: (el.outerHTML || '').slice(0, 2500),
    hrefs: Array.from(el.querySelectorAll('a[href]')).slice(0, 12).map(a => a.getAttribute('href')),
  }));

  // Also dump a slice of main innerHTML structure: first 4kb of serialized tags only
  function skeleton(el, depth, maxDepth, maxChildren) {
    if (!el || depth > maxDepth) return null;
    const kids = Array.from(el.children || []).slice(0, maxChildren).map(c => skeleton(c, depth+1, maxDepth, maxChildren)).filter(Boolean);
    return {
      tag: el.tagName.toLowerCase(),
      id: el.id || undefined,
      role: el.getAttribute('role') || undefined,
      cls: String(el.className||'').slice(0,120) || undefined,
      data: Object.fromEntries(Array.from(el.attributes).filter(a => a.name.startsWith('data-') || a.name==='aria-label').slice(0,8).map(a => [a.name, a.value.slice(0,80)])),
      nChildren: el.children.length,
      kids,
    };
  }

  return {
    url: location.href,
    title: document.title,
    mainTag: main.tagName,
    mainClasses: String(main.className||'').slice(0,200),
    mainAttrs: Array.from(main.attributes).map(a => [a.name, a.value.slice(0,120)]),
    nElementsInMain: all.length,
    attrCounts: Object.fromEntries(Object.entries(attrCounts).sort((a,b)=>b[1]-a[1]).slice(0,60)),
    dataAttrSamples,
    topClasses,
    hrefKinds,
    hrefSamples,
    articleCount,
    roleArticle,
    likeButtonCount: likeBtns.length,
    sduiSample,
    cardHints,
    cards,
    mainSkeleton: skeleton(main, 0, 4, 8),
    bodyPreview: clip(document.body.innerText, 1500),
  };
}
"""

def main():
    rsc_bodies = []
    def on_response(resp):
        try:
            url = resp.url
            if "rsc-action" in url or "sdui" in url.lower():
                entry = {
                    "url": url[:400],
                    "status": resp.status,
                    "method": resp.request.method,
                    "content_type": (resp.headers or {}).get("content-type", "")[:80],
                    "req_headers_keys": list((resp.request.headers or {}).keys())[:30],
                }
                try:
                    body = resp.body()
                    entry["body_len"] = len(body)
                    # try decode
                    text = None
                    for enc in ("utf-8", "utf-16", "latin-1"):
                        try:
                            text = body.decode(enc)
                            if "\x00" in text[:200] and enc == "utf-8":
                                continue
                            break
                        except Exception:
                            continue
                    if text:
                        entry["body_head"] = text[:4000]
                        # count urn-like
                        import re
                        urns = re.findall(r"urn:li:[a-zA-Z0-9:_\-]+", text)
                        entry["urn_sample"] = list(dict.fromkeys(urns))[:20]
                        entry["urn_count"] = len(urns)
                except Exception as e:
                    entry["body_err"] = str(e)[:120]
                rsc_bodies.append(entry)
        except Exception:
            return

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
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(6000)
        dump = page.evaluate(DUMP_JS)
        page.screenshot(path=str(OUT / "feed.png"), full_page=False)
        # scroll a couple times to get more cards + rsc pagination
        for _ in range(6):
            page.mouse.wheel(0, 1100)
            page.wait_for_timeout(1500)
        dump2 = page.evaluate(DUMP_JS)
        page.screenshot(path=str(OUT / "feed_scrolled.png"), full_page=False)
        ctx.close()

    (OUT / "dom_dump.json").write_text(json.dumps({
        "initial": dump,
        "after_scroll": {
            "nElementsInMain": dump2.get("nElementsInMain"),
            "hrefKinds": dump2.get("hrefKinds"),
            "likeButtonCount": dump2.get("likeButtonCount"),
            "cards": dump2.get("cards"),
            "topClasses": dump2.get("topClasses")[:40],
            "attrCounts": dump2.get("attrCounts"),
            "dataAttrSamples": dump2.get("dataAttrSamples"),
            "sduiSample": dump2.get("sduiSample"),
            "cardHints": dump2.get("cardHints"),
        },
        "rsc_bodies": rsc_bodies,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote dom_dump.json")
    print("initial cards", len(dump.get("cards") or []))
    print("after cards", len(dump2.get("cards") or []))
    print("hrefKinds initial", dump.get("hrefKinds"))
    print("hrefKinds after", dump2.get("hrefKinds"))
    print("like", dump.get("likeButtonCount"), "->", dump2.get("likeButtonCount"))
    print("rsc bodies", len(rsc_bodies))
    print("top classes", [c["cls"] for c in (dump.get("topClasses") or [])[:25]])
    print("attr names", list((dump.get("attrCounts") or {}).keys())[:25])

if __name__ == "__main__":
    main()

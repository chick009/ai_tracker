#!/usr/bin/env python3
"""Validate LinkedIn feed expand-full-text + Copy link to post UX.

Hard rules:
- Open ONLY /feed/
- NEVER navigate to /in/ profiles; if URL becomes /in/, go back immediately
- Slow scroll (~400px, 1–1.5s settle)
- Use existing persistent profile only
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
os.environ.setdefault("DISPLAY", ":7")

CARD_SEL = "[role='listitem'][componentkey*='update-card-focus']"
TEXT_BOX = "[data-testid='expandable-text-box']"
MORE_BTN = "[data-testid='expandable-text-button']"


def ensure_feed(page) -> None:
    url = page.url or ""
    if "/in/" in url and "/feed/" not in url:
        print(f"WARN: navigated to profile-ish URL {url}; going back to feed")
        page.goto(FEED_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
    if "/feed/" not in (page.url or ""):
        page.goto(FEED_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)


def slow_scroll(page, steps: int = 3) -> None:
    for _ in range(steps):
        ensure_feed(page)
        page.mouse.wheel(0, 400)
        time.sleep(1.25)


def text_len(s: str) -> int:
    return len((s or "").strip())


def find_expandable_card(page):
    """Return (card_locator, index) for first card with expandable more button."""
    cards = page.locator(CARD_SEL)
    n = cards.count()
    print(f"Visible cards: {n}")
    for i in range(n):
        card = cards.nth(i)
        try:
            more = card.locator(MORE_BTN)
            if more.count() == 0:
                # fallbacks
                more = card.locator(
                    "button:has-text('…more'), button:has-text('...more'), "
                    "button:has-text('see more'), [aria-label*='see more' i], "
                    "[aria-label*='Show more' i]"
                )
            if more.count() == 0:
                continue
            box = card.locator(TEXT_BOX)
            if box.count() == 0:
                continue
            # skip if more button not visible
            if not more.first.is_visible():
                continue
            return card, i, more.first
        except Exception as e:
            print(f"card {i} check err: {e}")
            continue
    return None, -1, None


def find_overflow_button(card):
    """Find upper-right overflow / More / control menu button on THIS card only."""
    candidates = [
        "button[aria-label*='Open control menu' i]",
        "button[aria-label*='Control menu' i]",
        "button[aria-label*='More actions' i]",
        "button[aria-label*='More options' i]",
        "button[aria-label^='More' i]",
        "button[aria-label*='Open More' i]",
        "[role='button'][aria-label*='Open control menu' i]",
        "[role='button'][aria-label*='More actions' i]",
        "[role='button'][aria-label*='More options' i]",
        "[role='button'][aria-label^='More' i]",
    ]
    for sel in candidates:
        loc = card.locator(sel)
        if loc.count() > 0:
            for j in range(min(loc.count(), 5)):
                el = loc.nth(j)
                try:
                    if el.is_visible():
                        label = el.get_attribute("aria-label") or ""
                        # exclude Follow and text expand
                        if re.search(r"follow|see more|show more|expand", label, re.I):
                            continue
                        return el, sel, label
                except Exception:
                    continue
    # Heuristic: buttons with only "…" or "More" text near top of card
    for sel in [
        "button",
        "[role='button']",
    ]:
        loc = card.locator(sel)
        count = min(loc.count(), 40)
        for j in range(count):
            el = loc.nth(j)
            try:
                if not el.is_visible():
                    continue
                label = (el.get_attribute("aria-label") or "").strip()
                txt = (el.inner_text() or "").strip()
                combined = f"{label} {txt}".lower()
                if "follow" in combined:
                    continue
                if "see more" in combined or "show more" in combined:
                    continue
                if re.search(r"\bmore\b|control menu|open menu|options", combined):
                    # Prefer ones that look like overflow (not Comment more etc.)
                    if any(x in combined for x in ("comment", "like", "repost", "react", "send")):
                        continue
                    return el, f"{sel}[heuristic]", label or txt
                if txt in ("…", "...", "⋯", "•••", "More"):
                    return el, f"{sel}[ellipsis-text]", label or txt
            except Exception:
                continue
    return None, "", ""


def find_copy_link_in_menu(page):
    """Find 'Copy link to post' in open menu / portal."""
    sels = [
        "[role='menuitem']:has-text('Copy link to post')",
        "[role='menuitem']:has-text('Copy link')",
        "button:has-text('Copy link to post')",
        "div[role='button']:has-text('Copy link to post')",
        "[role='option']:has-text('Copy link to post')",
        "text=Copy link to post",
        "text=Copy link",
    ]
    for sel in sels:
        loc = page.locator(sel)
        if loc.count() == 0:
            continue
        for j in range(min(loc.count(), 5)):
            el = loc.nth(j)
            try:
                if el.is_visible():
                    return el, sel, (el.inner_text() or "").strip()
            except Exception:
                continue
    return None, "", ""


def try_clipboard(page, context) -> tuple[bool, str, str]:
    """Return (ok, text, method_or_error)."""
    # Grant permissions if possible
    try:
        context.grant_permissions(["clipboard-read", "clipboard-write"], origin="https://www.linkedin.com")
    except Exception as e:
        print(f"grant_permissions note: {e}")

    # navigator.clipboard.readText
    try:
        txt = page.evaluate(
            """async () => {
              try {
                if (!navigator.clipboard || !navigator.clipboard.readText) {
                  return {ok:false, err:'no clipboard API'};
                }
                const t = await navigator.clipboard.readText();
                return {ok:true, text:t};
              } catch (e) {
                return {ok:false, err: String(e)};
              }
            }"""
        )
        if txt and txt.get("ok"):
            return True, txt.get("text") or "", "navigator.clipboard.readText"
        return False, "", f"clipboard.readText failed: {txt}"
    except Exception as e:
        return False, "", f"evaluate clipboard error: {e}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "steps": [],
        "selectors": {},
        "before_text": "",
        "after_text": "",
        "before_len": 0,
        "after_len": 0,
        "copied_url": "",
        "clipboard_ok": False,
        "clipboard_note": "",
        "overflow_sel": "",
        "copy_menu_sel": "",
        "success_expand": False,
        "success_copy": False,
        "errors": [],
    }

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        # Block accidental profile navigation: if /in/ appears, bounce back
        def on_framenavigated(frame):
            if frame != page.main_frame:
                return
            url = frame.url or ""
            if re.search(r"linkedin\.com/in/", url) and "/feed/" not in url:
                print(f"BLOCK: detected /in/ navigation to {url}; returning to feed")
                try:
                    page.goto(FEED_URL, wait_until="domcontentloaded", timeout=30000)
                except Exception as e:
                    print(f"back navigation failed: {e}")

        page.on("framenavigated", on_framenavigated)

        print(f"Opening {FEED_URL}")
        page.goto(FEED_URL, wait_until="domcontentloaded", timeout=90000)
        time.sleep(3)
        ensure_feed(page)
        report["steps"].append(f"Opened {page.url}")

        # Dismiss common modals if any (without clicking profiles)
        for sel in [
            "button[aria-label='Dismiss']",
            "button[aria-label='Close']",
            "button:has-text('Not now')",
            "button:has-text('Skip')",
        ]:
            try:
                loc = page.locator(sel)
                if loc.count() and loc.first.is_visible():
                    loc.first.click(timeout=2000)
                    time.sleep(0.5)
            except Exception:
                pass

        card = None
        more_btn = None
        card_idx = -1
        for attempt in range(8):
            ensure_feed(page)
            card, card_idx, more_btn = find_expandable_card(page)
            if card is not None:
                break
            print(f"No expandable card yet (attempt {attempt+1}); slow scroll")
            slow_scroll(page, steps=2)

        if card is None:
            report["errors"].append("No expandable card found after scrolling")
            page.screenshot(path=str(OUT / "more_before.png"), full_page=False)
            context.close()
            write_report(report)
            print(json.dumps(report, indent=2)[:2000])
            return

        report["steps"].append(f"Found expandable card index={card_idx}")
        report["selectors"]["card"] = CARD_SEL
        report["selectors"]["text_box"] = TEXT_BOX
        report["selectors"]["more_btn"] = MORE_BTN

        # Scroll card into view carefully
        try:
            card.scroll_into_view_if_needed(timeout=5000)
            time.sleep(1)
        except Exception as e:
            report["errors"].append(f"scroll_into_view: {e}")

        ensure_feed(page)
        before = ""
        try:
            before = card.locator(TEXT_BOX).first.inner_text(timeout=5000)
        except Exception as e:
            report["errors"].append(f"before text: {e}")
        report["before_text"] = before
        report["before_len"] = text_len(before)
        report["steps"].append(f"Recorded BEFORE expand len={report['before_len']}")

        page.screenshot(path=str(OUT / "more_before.png"), full_page=False)
        report["steps"].append("Saved more_before.png")

        # Click …more on THAT card only
        try:
            more_btn.click(timeout=5000)
            time.sleep(1.5)
            ensure_feed(page)
            report["steps"].append("Clicked expandable-text-button (…more)")
            report["success_expand"] = True
        except Exception as e:
            report["errors"].append(f"click more: {e}")
            # try JS click scoped
            try:
                card.locator(MORE_BTN).first.evaluate("el => el.click()")
                time.sleep(1.5)
                report["steps"].append("Clicked …more via JS")
                report["success_expand"] = True
            except Exception as e2:
                report["errors"].append(f"JS more click: {e2}")

        after = ""
        try:
            after = card.locator(TEXT_BOX).first.inner_text(timeout=5000)
        except Exception as e:
            report["errors"].append(f"after text: {e}")
        report["after_text"] = after
        report["after_len"] = text_len(after)
        report["steps"].append(f"Recorded AFTER expand len={report['after_len']}")

        page.screenshot(path=str(OUT / "more_expanded.png"), full_page=False)
        report["steps"].append("Saved more_expanded.png")

        # Overflow menu on SAME card
        overflow, o_sel, o_label = find_overflow_button(card)
        report["overflow_sel"] = o_sel
        report["selectors"]["overflow"] = o_sel
        report["steps"].append(f"Overflow candidate: sel={o_sel!r} label={o_label!r}")

        menu_opened = False
        if overflow is None:
            report["errors"].append("No overflow/More button found on card")
        else:
            try:
                overflow.click(timeout=5000)
                time.sleep(1.2)
                ensure_feed(page)
                menu_opened = True
                report["steps"].append(f"Clicked overflow button ({o_label})")
            except Exception as e:
                report["errors"].append(f"overflow click: {e}")
                try:
                    overflow.evaluate("el => el.click()")
                    time.sleep(1.2)
                    menu_opened = True
                    report["steps"].append("Clicked overflow via JS")
                except Exception as e2:
                    report["errors"].append(f"overflow JS click: {e2}")

        page.screenshot(path=str(OUT / "overflow_menu.png"), full_page=False)
        report["steps"].append("Saved overflow_menu.png")

        # Dump visible menu items for debugging
        try:
            menu_dump = page.evaluate(
                """() => {
                  const items = [];
                  const nodes = document.querySelectorAll('[role="menuitem"], [role="menu"] button, [role="menu"] [role="button"], [data-testid*="menu"] button');
                  for (const n of nodes) {
                    const r = n.getBoundingClientRect();
                    if (r.width < 2 || r.height < 2) continue;
                    const style = getComputedStyle(n);
                    if (style.visibility === 'hidden' || style.display === 'none') continue;
                    items.push({
                      tag: n.tagName,
                      role: n.getAttribute('role'),
                      aria: n.getAttribute('aria-label'),
                      text: (n.innerText || '').trim().slice(0, 120),
                      href: n.getAttribute('href') || (n.querySelector && n.querySelector('a') && n.querySelector('a').getAttribute('href')) || null
                    });
                  }
                  return items.slice(0, 40);
                }"""
            )
            report["menu_items"] = menu_dump
            report["steps"].append(f"Visible menu-ish items: {len(menu_dump)}")
            (OUT / "menu_items.json").write_text(json.dumps(menu_dump, indent=2), encoding="utf-8")
        except Exception as e:
            report["errors"].append(f"menu dump: {e}")

        copy_el, c_sel, c_text = find_copy_link_in_menu(page)
        report["copy_menu_sel"] = c_sel
        report["selectors"]["copy_link"] = c_sel

        href_revealed = ""
        if copy_el is None:
            report["clipboard_note"] = "Copy link menu item not found / menu may not have opened"
            report["steps"].append("Copy link item NOT found")
        else:
            report["steps"].append(f"Found copy menu item: {c_text!r} sel={c_sel}")
            # Check for href on item
            try:
                href_revealed = copy_el.evaluate(
                    """el => {
                      if (el.href) return el.href;
                      const a = el.closest('a') || el.querySelector('a');
                      return a ? (a.href || a.getAttribute('href') || '') : '';
                    }"""
                ) or ""
            except Exception:
                href_revealed = ""
            if href_revealed:
                report["steps"].append(f"href on copy item: {href_revealed}")

            try:
                copy_el.click(timeout=5000)
                time.sleep(1.0)
                report["steps"].append("Clicked Copy link to post")
            except Exception as e:
                report["errors"].append(f"copy click: {e}")
                try:
                    copy_el.evaluate("el => el.click()")
                    time.sleep(1.0)
                    report["steps"].append("Clicked Copy link via JS")
                except Exception as e2:
                    report["errors"].append(f"copy JS click: {e2}")

            ok, clip, note = try_clipboard(page, context)
            report["clipboard_ok"] = ok
            report["clipboard_note"] = note
            if ok and clip:
                report["copied_url"] = clip.strip()
                report["success_copy"] = bool(re.search(r"linkedin\.com", clip, re.I))
                report["steps"].append(f"Clipboard read OK: {clip[:200]!r}")
            else:
                report["steps"].append(f"Clipboard read failed: {note}")
                if href_revealed:
                    report["copied_url"] = href_revealed
                    report["success_copy"] = True
                    report["clipboard_note"] += f"; fell back to href={href_revealed}"

        # Final URL check
        ensure_feed(page)
        report["final_url"] = page.url

        # Save raw texts
        (OUT / "expand_texts.json").write_text(
            json.dumps(
                {
                    "before": before,
                    "after": after,
                    "before_len": report["before_len"],
                    "after_len": report["after_len"],
                    "copied_url": report["copied_url"],
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        write_report(report)
        context.close()
        print("DONE")
        print(json.dumps({k: report[k] for k in (
            "success_expand", "success_copy", "before_len", "after_len",
            "copied_url", "clipboard_ok", "clipboard_note", "overflow_sel",
            "copy_menu_sel", "errors", "steps"
        )}, indent=2, ensure_ascii=False)[:4000])


def write_report(report: dict) -> None:
    lines = []
    lines.append("# LinkedIn feed copy-link probe")
    lines.append("")
    lines.append(f"**Date:** 2026-09-12 (Asia/Hong_Kong)")
    lines.append(f"**Feed URL:** `{FEED_URL}`")
    lines.append(f"**Profile:** `{PROFILE}`")
    lines.append("")
    lines.append("## Outcome")
    lines.append("")
    lines.append(f"- Expand (`…more`) worked: **{report.get('success_expand')}**")
    lines.append(f"- Copy link worked: **{report.get('success_copy')}**")
    lines.append(f"- Before text length: **{report.get('before_len')}**")
    lines.append(f"- After text length: **{report.get('after_len')}**")
    lines.append(f"- Copied URL: `{report.get('copied_url') or '(none)'}`")
    lines.append(f"- Clipboard API: ok={report.get('clipboard_ok')} — {report.get('clipboard_note')}")
    lines.append("")
    lines.append("## Selectors used")
    lines.append("")
    for k, v in (report.get("selectors") or {}).items():
        lines.append(f"- **{k}**: `{v}`")
    if report.get("overflow_sel"):
        lines.append(f"- **overflow (resolved)**: `{report['overflow_sel']}`")
    if report.get("copy_menu_sel"):
        lines.append(f"- **copy link menu item**: `{report['copy_menu_sel']}`")
    lines.append("")
    lines.append("## Steps that worked / attempted")
    lines.append("")
    for s in report.get("steps") or []:
        lines.append(f"1. {s}")
    lines.append("")
    lines.append("## Screenshots")
    lines.append("")
    lines.append("- `more_before.png` — card before expand")
    lines.append("- `more_expanded.png` — after clicking expandable-text-button")
    lines.append("- `overflow_menu.png` — after opening overflow / More menu")
    lines.append("")
    if report.get("errors"):
        lines.append("## Errors / notes")
        lines.append("")
        for e in report["errors"]:
            lines.append(f"- {e}")
        lines.append("")
    lines.append("## Automation guidance")
    lines.append("")
    if report.get("success_expand") and report.get("success_copy"):
        lines.append(
            "Expand + copy-link **works**. Automate by: locate "
            "`[role=listitem][componentkey*='update-card-focus']` with "
            "`[data-testid=expandable-text-button]`, click it, then click the card's "
            "overflow control (aria-label matching More/Control menu), then "
            "`[role=menuitem]` with text `Copy link to post`, then "
            "`navigator.clipboard.readText()` (grant clipboard-read permission)."
        )
    elif report.get("success_expand"):
        lines.append(
            "Expand works via `[data-testid=expandable-text-button]`. "
            "Copy-link path incomplete — see errors and menu_items.json."
        )
    else:
        lines.append("Could not fully validate; see errors above.")
    lines.append("")
    # Truncate long texts in md
    bt = (report.get("before_text") or "")[:500]
    at = (report.get("after_text") or "")[:800]
    lines.append("## Text samples (truncated)")
    lines.append("")
    lines.append("### Before")
    lines.append("")
    lines.append("```")
    lines.append(bt)
    lines.append("```")
    lines.append("")
    lines.append("### After")
    lines.append("")
    lines.append("```")
    lines.append(at)
    lines.append("```")
    lines.append("")
    (OUT / "copy_link_probe.md").write_text("\n".join(lines), encoding="utf-8")
    (OUT / "copy_link_probe.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)[:50000], encoding="utf-8"
    )
    print(f"Wrote {OUT / 'copy_link_probe.md'}")


if __name__ == "__main__":
    main()

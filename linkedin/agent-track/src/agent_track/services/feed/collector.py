"""Playwright collector for LinkedIn home feed. Does not touch job search UI."""

from __future__ import annotations

import random
import re
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Locator,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

from agent_track.services.feed.io import default_output_dir, default_profile_dir, write_feed_outputs
from agent_track.services.feed.parse import (
    looks_promoted,
    now_iso,
    parse_relative_time,
    parse_token_from_componentkey,
    parse_urn_from_embed_href,
    resolve_author_from_snapshot,
    unique_by_token,
)
from agent_track.services.feed.selectors import (
    AUTHOR_LINK,
    CARD,
    COPY_LINK_MENU_ITEM_NAME,
    EXPAND_BUTTON,
    EXPANDABLE_TEXT,
    FEED_ROOT,
    FEED_URL,
    OVERFLOW_MENU_BUTTON,
)

LOGIN_WAIT_SECONDS_DEFAULT = 300
SCROLL_PX_MIN = 300
SCROLL_PX_MAX = 500
SETTLE_MS_MIN = 800
SETTLE_MS_MAX = 1500
MAX_STAGNANT_SCROLLS = 10
RELATIVE_TIME_LOCATOR = re.compile(r"^(\d+[smhdw]|just now)$", re.IGNORECASE)


def _is_logged_in(context: BrowserContext, page: Page) -> bool:
    cookies = context.cookies()
    if any(cookie.get("name") == "li_at" for cookie in cookies):
        url = page.url or ""
        if "/login" in url or "/checkpoint" in url or "/uas/" in url:
            return False
        return True
    if page.locator(FEED_ROOT).count() > 0:
        return True
    return False


def _grant_clipboard(context: BrowserContext) -> None:
    try:
        context.grant_permissions(
            ["clipboard-read", "clipboard-write"],
            origin="https://www.linkedin.com",
        )
    except Exception:
        # Headless or restricted environments may ignore clipboard grants.
        return


def _slow_scroll(page: Page) -> None:
    delta = random.randint(SCROLL_PX_MIN, SCROLL_PX_MAX)
    page.mouse.wheel(0, delta)
    page.wait_for_timeout(random.randint(SETTLE_MS_MIN, SETTLE_MS_MAX))


def _dismiss_open_menu(page: Page) -> None:
    page.keyboard.press("Escape")
    page.wait_for_timeout(200)


def _read_clipboard(page: Page) -> str | None:
    try:
        value = page.evaluate("() => navigator.clipboard.readText()")
    except Exception:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _card_in_viewport(page: Page, card: Locator) -> bool:
    box = card.bounding_box()
    if not box:
        return False
    viewport = page.viewport_size or {"width": 1280, "height": 720}
    top = box["y"]
    bottom = box["y"] + box["height"]
    return bottom > 80 and top < viewport["height"] - 40


def _extract_urn_from_open_menu(page: Page) -> str | None:
    menu = page.locator("[role='menu']").first
    if menu.count() == 0:
        return None
    html = menu.inner_html()
    return parse_urn_from_embed_href(html)


def _copy_permalink(page: Page, card: Locator) -> tuple[str | None, str | None]:
    """Open overflow → Copy link to post. Fallback: Embed href targetUrn."""
    overflow = card.locator(OVERFLOW_MENU_BUTTON).first
    if overflow.count() == 0:
        return None, None
    overflow.click(timeout=5000)
    page.wait_for_timeout(400)
    urn = _extract_urn_from_open_menu(page)
    link = None
    try:
        item = page.locator("[role=menuitem]").filter(has_text=COPY_LINK_MENU_ITEM_NAME)
        item.first.click(timeout=4000)
        page.wait_for_timeout(400)
        for _ in range(3):
            link = _read_clipboard(page)
            if link:
                break
            page.wait_for_timeout(250)
    except PlaywrightTimeoutError:
        link = None
    _dismiss_open_menu(page)
    return link, urn


def _expand_commentary(card: Locator) -> None:
    button = card.locator(EXPAND_BUTTON)
    if button.count() == 0:
        return
    try:
        if button.first.is_visible():
            button.first.click(timeout=2000)
            time.sleep(0.25)
    except PlaywrightTimeoutError:
        return


def _relative_time_from_card(card: Locator) -> str | None:
    texts: list[str] = []
    time_nodes = card.locator("time")
    for i in range(min(time_nodes.count(), 3)):
        texts.append(time_nodes.nth(i).inner_text())
        datetime_attr = time_nodes.nth(i).get_attribute("datetime")
        if datetime_attr:
            texts.append(datetime_attr)
    spans = card.locator("span")
    limit = min(spans.count(), 40)
    for i in range(limit):
        raw = (spans.nth(i).inner_text() or "").strip()
        if RELATIVE_TIME_LOCATOR.match(raw):
            texts.append(raw)
    return parse_relative_time(texts)


_AUTHOR_SNAPSHOT_JS = """(el) => {
  const overflowBtn = el.querySelector(
    "button[aria-label*='Open control menu' i], button[aria-label*='control menu' i]"
  );
  const markers = ["/in/", "/company/", "/school/", "/showcase/"];
  const isActor = (href) => {
    const h = (href || "").toLowerCase();
    return markers.some((p) => h.includes(p));
  };
  const actors = [...el.querySelectorAll("a[href]")].filter((a) =>
    isActor(a.getAttribute("href"))
  );
  return {
    overflow_aria: overflowBtn ? overflowBtn.getAttribute("aria-label") || "" : "",
    actor_aria_labels: actors.map((a) => a.getAttribute("aria-label") || ""),
    actor_link_texts: actors.map((a) => (a.innerText || a.textContent || "").trim()),
    image_alts: [...el.querySelectorAll("img[alt]")]
      .map((img) => img.getAttribute("alt") || "")
      .filter(Boolean),
    card_text: el.innerText || "",
  };
}"""


def _read_author_snapshot(card: Locator) -> dict[str, Any]:
    try:
        data = card.evaluate(_AUTHOR_SNAPSHOT_JS)
    except Exception:
        data = {}
    return data if isinstance(data, dict) else {}


def _author_snapshot_from_locators(card: Locator) -> dict[str, Any]:
    """Second-chance read without clicking actor/avatar links."""
    overflow_aria = None
    overflow = card.locator(OVERFLOW_MENU_BUTTON).first
    if overflow.count():
        overflow_aria = overflow.get_attribute("aria-label")
    actors = card.locator(AUTHOR_LINK)
    try:
        actors.first.wait_for(state="attached", timeout=1500)
    except PlaywrightTimeoutError:
        pass
    count = min(actors.count(), 6)
    arias: list[str] = []
    texts: list[str] = []
    for i in range(count):
        node = actors.nth(i)
        arias.append(node.get_attribute("aria-label") or "")
        texts.append(node.inner_text() or "")
    alts: list[str] = []
    images = card.locator("img[alt]")
    for i in range(min(images.count(), 6)):
        alts.append(images.nth(i).get_attribute("alt") or "")
    return {
        "overflow_aria": overflow_aria or "",
        "actor_aria_labels": arias,
        "actor_link_texts": texts,
        "image_alts": alts,
        "card_text": card.inner_text() or "",
    }


def extract_author(card: Locator) -> str | None:
    """Read-only author. Never clicks /in/, /company/, or avatar."""
    author = resolve_author_from_snapshot(_read_author_snapshot(card))
    if author:
        return author
    return resolve_author_from_snapshot(_author_snapshot_from_locators(card))


def extract_visible_card(page: Page, card: Locator) -> dict[str, Any] | None:
    componentkey = card.get_attribute("componentkey")
    token = parse_token_from_componentkey(componentkey)
    if not token:
        return None

    preview = card.inner_text()
    if looks_promoted(preview):
        return None

    author = extract_author(card)

    _expand_commentary(card)
    text_box = card.locator(EXPANDABLE_TEXT).first
    text_snippet = ""
    if text_box.count():
        text_snippet = text_box.inner_text().strip()
    relative_time = _relative_time_from_card(card)
    link, urn = _copy_permalink(page, card)

    return {
        "author": author,
        "link": link,
        "text_snippet": text_snippet,
        "token": token,
        "relative_time": relative_time,
        "urn": urn,
        "captured_at": now_iso(),
        "componentkey": componentkey,
    }


def collect_feed_posts(
    page: Page,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    page.locator(FEED_ROOT).wait_for(state="visible", timeout=30_000)
    collected: list[dict[str, Any]] = []
    seen: set[str] = set()
    stagnant = 0

    while len(collected) < limit and stagnant < MAX_STAGNANT_SCROLLS:
        added = 0
        cards = page.locator(CARD)
        count = cards.count()
        for i in range(count):
            if len(collected) >= limit:
                break
            card = cards.nth(i)
            if not _card_in_viewport(page, card):
                continue
            componentkey = card.get_attribute("componentkey")
            token = parse_token_from_componentkey(componentkey)
            if not token or token in seen:
                continue
            seen.add(token)
            try:
                post = extract_visible_card(page, card)
            except PlaywrightTimeoutError:
                continue
            if post is None:
                continue
            collected.append(post)
            added += 1
        _slow_scroll(page)
        if added == 0:
            stagnant += 1
        else:
            stagnant = 0

    return unique_by_token(collected)[:limit]


def wait_for_login(context: BrowserContext, page: Page, *, wait: bool, timeout_s: int) -> None:
    if _is_logged_in(context, page):
        return
    if not wait:
        raise SystemExit(
            "Not logged in (no li_at session / feed root). "
            "Re-run without --no-wait and sign in, or copy a Chromium profile into "
            "data/.linkedin-browser-profile (owned by this repo; do not import "
            "career-job-applications)."
        )
    deadline = time.time() + timeout_s
    print(
        "LinkedIn session not detected. Sign in in the opened browser. "
        "This tool never uses career-job-applications job-search cron."
    )
    while time.time() < deadline:
        if _is_logged_in(context, page):
            page.goto(FEED_URL, wait_until="domcontentloaded")
            return
        time.sleep(2)
    raise SystemExit("Timed out waiting for LinkedIn login.")


def run_digest(
    *,
    limit: int = 20,
    persist_profile: bool = False,
    wait: bool = True,
    headless: bool = False,
    output_dir: Path | None = None,
    profile_dir: Path | None = None,
    login_timeout_s: int = LOGIN_WAIT_SECONDS_DEFAULT,
) -> list[dict[str, Any]]:
    out = output_dir or default_output_dir()
    profile = profile_dir or default_profile_dir()

    with sync_playwright() as playwright:
        context, owned_browser = _launch_context(
            playwright,
            persist_profile=persist_profile,
            profile_dir=profile,
            headless=headless,
        )
        try:
            _grant_clipboard(context)
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(FEED_URL, wait_until="domcontentloaded")
            wait_for_login(context, page, wait=wait, timeout_s=login_timeout_s)
            if FEED_URL not in (page.url or ""):
                page.goto(FEED_URL, wait_until="domcontentloaded")
            posts = collect_feed_posts(page, limit=limit)
        finally:
            context.close()
            if owned_browser is not None:
                owned_browser.close()

    write_feed_outputs(posts, out)
    return posts


def _launch_context(
    playwright: Playwright,
    *,
    persist_profile: bool,
    profile_dir: Path,
    headless: bool,
) -> tuple[BrowserContext, Browser | None]:
    viewport = {"width": 1400, "height": 900}
    if persist_profile:
        profile_dir.mkdir(parents=True, exist_ok=True)
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=headless,
            viewport=viewport,
            args=["--disable-blink-features=AutomationControlled"],
        )
        return context, None
    browser = playwright.chromium.launch(
        headless=headless,
        args=["--disable-blink-features=AutomationControlled"],
    )
    return browser.new_context(viewport=viewport), browser

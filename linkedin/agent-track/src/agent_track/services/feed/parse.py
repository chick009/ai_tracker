"""Pure helpers for LinkedIn feed cards. No browser, no network."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from agent_track.services.feed.selectors import (
    COMPONENTKEY_TOKEN_PREFIX,
    COMPONENTKEY_TOKEN_SUFFIX_MARKER,
)

URN_RE = re.compile(r"(urn:li:(?:share|activity|ugcPost):\d+)")
RELATIVE_TIME_RE = re.compile(
    r"^(?:just now|\d+\s*(?:s|m|h|d|w|mo|yr|second|minute|hour|day|week|month|year)s?\s*(?:ago)?)$",
    re.IGNORECASE,
)
ACTOR_HREF_MARKERS = ("/in/", "/company/", "/school/", "/showcase/")
NON_ACTOR_HREF_MARKERS = ("/feed/", "/search/", "/hashtag/", "/login", "/signup")
OVERFLOW_AUTHOR_PATTERNS = (
    re.compile(r"(?i)^open control menu for post by (.+)$"),
    re.compile(r"(?i)^open control menu for (.+?)(?:['’]s)? post$"),
    re.compile(r"(?i)^open control menu by (.+)$"),
    re.compile(r"(?i)^control menu for post by (.+)$"),
    re.compile(r"(?i)^more (?:actions|options) for post by (.+)$"),
)
CHROME_AUTHOR_LINES = {
    "feed post",
    "promoted",
    "suggested",
    "follow",
    "+ follow",
    "connect",
    "like",
    "comment",
    "repost",
    "send",
    "visible to anyone",
    "author",
    "verified",
}
SKIP_IMAGE_ALTS = {
    "like",
    "love",
    "celebrate",
    "insightful",
    "support",
    "funny",
    "play",
    "linkedin",
    "emoji",
}


def parse_token_from_componentkey(componentkey: str | None) -> str | None:
    """Extract the feed card TOKEN from SDUI componentkey."""
    if not componentkey:
        return None
    start = componentkey.find(COMPONENTKEY_TOKEN_PREFIX)
    if start < 0:
        return None
    rest = componentkey[start + len(COMPONENTKEY_TOKEN_PREFIX) :]
    end = rest.find(COMPONENTKEY_TOKEN_SUFFIX_MARKER)
    token = rest[:end] if end >= 0 else rest
    token = token.strip()
    return token or None


def parse_urn_from_embed_href(href: str | None) -> str | None:
    """Parse targetUrn / share URN from an Embed menu href."""
    if not href:
        return None
    decoded = unquote(href)
    parsed = urlparse(href)
    query = parse_qs(parsed.query)
    raw = query.get("targetUrn") or query.get("targeturn")
    if raw:
        value = unquote(raw[0]).strip()
        match = URN_RE.search(value)
        if match:
            return match.group(1)
        if value.startswith("urn:li:"):
            return value
    match = URN_RE.search(decoded)
    return match.group(1) if match else None


def is_actor_href(href: str | None) -> bool:
    """Person (/in/) or company/school actor URLs — read only, never clicked."""
    if not href:
        return False
    lowered = unquote(href).lower()
    if any(marker in lowered for marker in NON_ACTOR_HREF_MARKERS) and not any(
        marker in lowered for marker in ACTOR_HREF_MARKERS
    ):
        return False
    return any(marker in lowered for marker in ACTOR_HREF_MARKERS)


def parse_author_from_overflow_label(label: str | None) -> str | None:
    """Parse 'Open control menu for post by {Name}' (and close variants)."""
    if not label:
        return None
    text = " ".join(label.split()).strip()
    for pattern in OVERFLOW_AUTHOR_PATTERNS:
        match = pattern.match(text)
        if not match:
            continue
        name = match.group(1).strip(" .")
        name = re.sub(r"['’]s$", "", name).strip()
        if name and name.lower() not in {"post", "this post", "this"}:
            return name
    return None


def parse_author_from_aria_label(label: str | None) -> str | None:
    """Turn actor aria-label / overflow label into a display name. Never a click target."""
    if not label:
        return None
    overflow = parse_author_from_overflow_label(label)
    if overflow:
        return overflow
    text = " ".join(label.split()).strip()
    if re.search(r"(?i)control menu", text):
        return None
    lowered = text.lower()
    for prefix in ("view ", "see ", "visit ", "open ", "go to "):
        if lowered.startswith(prefix):
            text = text[len(prefix) :].strip()
            lowered = text.lower()
            break
    text = re.sub(r"['’]s (?:profile|page|company page|school page)$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+(?:profile|page|company page|school page)$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?i)^profile (?:photo|picture) of\s+", "", text)
    text = text.strip(" •|\t")
    if not text or text.lower() in CHROME_AUTHOR_LINES:
        return None
    return text


def parse_author_from_link_text(text: str | None) -> str | None:
    """Visible actor-link text (first line). Do not click the link."""
    if not text:
        return None
    first = text.splitlines()[0].strip()
    first = re.sub(r"\s*[•·].*$", "", first).strip()
    first = re.sub(r"\s+\d+(?:st|nd|rd|th)$", "", first, flags=re.IGNORECASE).strip()
    if not first or first.lower() in CHROME_AUTHOR_LINES:
        return None
    if not _looks_like_display_name(first):
        return None
    return first


def parse_author_from_card_text(card_text: str | None) -> str | None:
    """First substantial header line after stripping a11y chrome like 'Feed post'."""
    if not card_text:
        return None
    lines = [line.strip() for line in card_text.splitlines() if line.strip()]
    for line in lines[:12]:
        lowered = line.lower().strip(" •·")
        if lowered in CHROME_AUTHOR_LINES:
            continue
        if parse_relative_time([line]):
            continue
        if re.search(r"(?i)\bfollowers\b", line):
            continue
        if re.fullmatch(r"\d+(?:st|nd|rd|th)", lowered):
            continue
        if _looks_like_display_name(line):
            return line
    return None


def _looks_like_display_name(line: str) -> bool:
    text = " ".join(line.split()).strip()
    if not text or len(text) > 120:
        return False
    if text.endswith((".", "?", "!")):
        return False
    if text.startswith("http"):
        return False
    words = text.split()
    if not (1 <= len(words) <= 14):
        return False
    return True


def parse_author_from_image_alt(alt: str | None) -> str | None:
    if not alt:
        return None
    if alt.strip().lower() in SKIP_IMAGE_ALTS:
        return None
    return parse_author_from_aria_label(alt)


def resolve_author_from_snapshot(snapshot: dict[str, Any] | None) -> str | None:
    """Prefer overflow + actor attributes; never requires clicking /in/ or avatars."""
    if not snapshot:
        return None
    overflow = parse_author_from_overflow_label(snapshot.get("overflow_aria"))
    if overflow:
        return overflow
    for label in snapshot.get("actor_aria_labels") or []:
        name = parse_author_from_aria_label(label)
        if name:
            return name
    for text in snapshot.get("actor_link_texts") or []:
        name = parse_author_from_link_text(text)
        if name:
            return name
    for alt in snapshot.get("image_alts") or []:
        name = parse_author_from_image_alt(alt)
        if name:
            return name
    return parse_author_from_card_text(snapshot.get("card_text"))


def looks_promoted(card_text: str | None) -> bool:
    """Skip Promoted cards when the badge appears as its own early line."""
    if not card_text:
        return False
    lines = [line.strip() for line in card_text.splitlines() if line.strip()]
    for line in lines[:20]:
        if line.lower() == "promoted":
            return True
    return False


def parse_relative_time(candidates: list[str] | tuple[str, ...] | None) -> str | None:
    """Pick a LinkedIn-style relative timestamp (e.g. 4d, 2h, 3w)."""
    if not candidates:
        return None
    for raw in candidates:
        if not raw:
            continue
        text = " ".join(raw.split()).strip(" ·•")
        if not text:
            continue
        if re.fullmatch(r"\d+[smhdw]", text, flags=re.IGNORECASE):
            return text.lower()
        if RELATIVE_TIME_RE.match(text):
            return text
        compact = text.replace(" ", "").strip("•")
        if re.fullmatch(r"\d+[smhdw]", compact, flags=re.IGNORECASE):
            return compact.lower()
    return None


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slim_digest_entry(post: dict[str, Any]) -> dict[str, str | None]:
    """Slim card: author, permalink, full commentary."""
    return {
        "author": post.get("author"),
        "link": post.get("link"),
        "text_snippet": post.get("text_snippet"),
    }


def slim_digest(posts: list[dict[str, Any]]) -> list[dict[str, str | None]]:
    return [slim_digest_entry(post) for post in posts]


def unique_by_token(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for post in posts:
        token = post.get("token")
        key = str(token) if token else None
        if not key:
            key = str(post.get("link") or post.get("urn") or id(post))
        if key in seen:
            continue
        seen.add(key)
        out.append(post)
    return out

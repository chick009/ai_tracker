from __future__ import annotations

import json
from pathlib import Path

from agent_track.services.feed.io import write_feed_outputs
from agent_track.services.feed.parse import (
    is_actor_href,
    looks_promoted,
    parse_author_from_aria_label,
    parse_author_from_card_text,
    parse_author_from_link_text,
    parse_author_from_overflow_label,
    parse_relative_time,
    parse_token_from_componentkey,
    parse_urn_from_embed_href,
    resolve_author_from_snapshot,
    slim_digest,
    unique_by_token,
)


def test_parse_token_from_componentkey() -> None:
    key = "update-card-focusurn:li:activity:7365123456789FeedType_MAIN_FEED_RELEVANCE"
    assert parse_token_from_componentkey(key) == "urn:li:activity:7365123456789"
    assert parse_token_from_componentkey(None) is None
    assert parse_token_from_componentkey("other-card") is None
    assert parse_token_from_componentkey("update-card-focusTOKENONLY") == "TOKENONLY"


def test_parse_urn_from_menu_html_fragment() -> None:
    html = '<a href="https://www.linkedin.com/embed/feed/update/?targetUrn=urn%3Ali%3Ashare%3A42">Embed this post</a>'
    assert parse_urn_from_embed_href(html) == "urn:li:share:42"
    href = "https://www.linkedin.com/embed/feed/update/urn:li:share:7365?foo=1"
    assert parse_urn_from_embed_href(href) == "urn:li:share:7365"
    encoded = "https://www.linkedin.com/embed/feed/?targetUrn=urn%3Ali%3Ashare%3A999"
    assert parse_urn_from_embed_href(encoded) == "urn:li:share:999"
    assert parse_urn_from_embed_href("https://example.com/") is None
    assert parse_urn_from_embed_href(None) is None


def test_parse_author_from_aria_label() -> None:
    assert parse_author_from_aria_label("View Kuldeep Singh Sidhu’s profile") == "Kuldeep Singh Sidhu"
    assert parse_author_from_aria_label("View Jane Doe's profile") == "Jane Doe"
    assert parse_author_from_aria_label("View Ada Lovelace") == "Ada Lovelace"
    assert parse_author_from_aria_label("See Tencent’s page") == "Tencent"
    assert parse_author_from_aria_label("Visit Acme Inc company page") == "Acme Inc"
    assert parse_author_from_aria_label("Kuldeep Singh Sidhu") == "Kuldeep Singh Sidhu"
    assert parse_author_from_aria_label("Open control menu") is None
    assert parse_author_from_aria_label(None) is None


def test_parse_author_from_overflow_and_fallbacks() -> None:
    assert (
        parse_author_from_overflow_label("Open control menu for post by Kuldeep Singh Sidhu")
        == "Kuldeep Singh Sidhu"
    )
    assert parse_author_from_overflow_label("Open control menu for Tencent's post") == "Tencent"
    assert parse_author_from_overflow_label("Open control menu") is None
    assert parse_author_from_aria_label("Open control menu for post by Ada Lovelace") == "Ada Lovelace"

    assert is_actor_href("https://www.linkedin.com/in/jane-doe")
    assert is_actor_href("https://www.linkedin.com/company/tencent/")
    assert not is_actor_href("https://www.linkedin.com/feed/")
    assert not is_actor_href("https://www.linkedin.com/search/results/all/")

    person_card = "Feed post\nKuldeep Singh Sidhu\nSenior Data Scientist @ Walmart\n4d\nHello world"
    assert parse_author_from_card_text(person_card) == "Kuldeep Singh Sidhu"
    company_card = "Feed post\nTencent\n12,345 followers\n2h\nShipping a new model"
    assert parse_author_from_card_text(company_card) == "Tencent"
    assert parse_author_from_link_text("Tencent\nFollow") == "Tencent"

    person = resolve_author_from_snapshot(
        {
            "overflow_aria": "Open control menu",
            "actor_aria_labels": ["View Ada Lovelace’s profile"],
            "actor_link_texts": [],
            "image_alts": [],
            "card_text": "Feed post\nIgnored",
        }
    )
    assert person == "Ada Lovelace"

    company = resolve_author_from_snapshot(
        {
            "overflow_aria": "",
            "actor_aria_labels": [""],
            "actor_link_texts": ["Institute of Information Engineering"],
            "image_alts": [],
            "card_text": "Feed post\nInstitute of Information Engineering\n2h",
        }
    )
    assert company == "Institute of Information Engineering"

    overflow_only = resolve_author_from_snapshot(
        {
            "overflow_aria": "Open control menu for post by Walmart",
            "actor_aria_labels": [],
            "actor_link_texts": [],
            "image_alts": [],
            "card_text": "",
        }
    )
    assert overflow_only == "Walmart"

    text_only = resolve_author_from_snapshot(
        {
            "overflow_aria": "Open control menu",
            "actor_aria_labels": [],
            "actor_link_texts": [],
            "image_alts": [],
            "card_text": person_card,
        }
    )
    assert text_only == "Kuldeep Singh Sidhu"


def test_looks_promoted_only_badge_line() -> None:
    organic = "Ada Lovelace\n2h\nI promoted this idea last year in a paper."
    assert looks_promoted(organic) is False
    promoted = "Acme Ads\nPromoted\nBuy widgets"
    assert looks_promoted(promoted) is True


def test_parse_relative_time() -> None:
    assert parse_relative_time(["4d", "noise"]) == "4d"
    assert parse_relative_time(["2h •"]) == "2h"
    assert parse_relative_time(["just now"]) == "just now"
    assert parse_relative_time(["not a time"]) is None


def test_slim_digest_and_unique() -> None:
    posts = [
        {
            "author": "A",
            "link": "https://lnkd.in/abc",
            "text_snippet": "hello",
            "token": "t1",
            "relative_time": "4d",
            "urn": "urn:li:share:1",
        },
        {
            "author": "B",
            "link": "https://lnkd.in/def",
            "text_snippet": "world",
            "token": "t1",
        },
    ]
    unique = unique_by_token(posts)
    assert len(unique) == 1
    slim = slim_digest(unique)
    assert slim == [{"author": "A", "link": "https://lnkd.in/abc", "text_snippet": "hello"}]


def test_write_feed_outputs(tmp_path: Path) -> None:
    posts = [
        {
            "author": "A",
            "link": "https://lnkd.in/abc",
            "text_snippet": "full commentary",
            "token": "tok",
            "relative_time": "4d",
            "urn": None,
            "captured_at": "2026-09-11T00:00:00+00:00",
        }
    ]
    posts_path, digest_path = write_feed_outputs(posts, tmp_path)
    lines = posts_path.read_text(encoding="utf-8").strip().splitlines()
    assert json.loads(lines[0])["token"] == "tok"
    digest = json.loads(digest_path.read_text(encoding="utf-8"))
    assert digest[0]["author"] == "A"
    assert set(digest[0].keys()) == {"author", "link", "text_snippet"}

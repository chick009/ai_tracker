from agent_track.services.feed.io import default_output_dir, default_profile_dir
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


def test_verified_sdui_selectors() -> None:
    assert FEED_URL == "https://www.linkedin.com/feed/"
    assert FEED_ROOT == "[data-testid=mainFeed][data-component-type=LazyColumn][role=list]"
    assert CARD == "[role=listitem][componentkey*='update-card-focus']"
    assert "/in/" in AUTHOR_LINK
    assert "/company/" in AUTHOR_LINK
    assert EXPANDABLE_TEXT == "[data-testid=expandable-text-box]"
    assert EXPAND_BUTTON == "[data-testid=expandable-text-button]"
    assert "Open control menu" in OVERFLOW_MENU_BUTTON
    assert COPY_LINK_MENU_ITEM_NAME == "Copy link to post"


def test_profile_is_repo_local() -> None:
    assert default_profile_dir().as_posix() == "data/.linkedin-browser-profile"
    assert default_output_dir().as_posix() == "data/feed"

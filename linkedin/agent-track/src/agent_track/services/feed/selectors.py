"""Sep 2026 LinkedIn SDUI feed selectors (verified against live DOM)."""

FEED_URL = "https://www.linkedin.com/feed/"

FEED_ROOT = "[data-testid=mainFeed][data-component-type=LazyColumn][role=list]"
CARD = "[role=listitem][componentkey*='update-card-focus']"

# Person *or* company/school actors. Do not require aria-label^='View ' — SDUI often omits it.
AUTHOR_LINK = "a[href*='/in/'], a[href*='/company/'], a[href*='/school/'], a[href*='/showcase/']"
EXPANDABLE_TEXT = "[data-testid=expandable-text-box]"
EXPAND_BUTTON = "[data-testid=expandable-text-button]"
OVERFLOW_MENU_BUTTON = "button[aria-label*='Open control menu' i], button[aria-label*='control menu' i]"
COPY_LINK_MENU_ITEM_NAME = "Copy link to post"

COMPONENTKEY_TOKEN_PREFIX = "update-card-focus"
COMPONENTKEY_TOKEN_SUFFIX_MARKER = "FeedType_"

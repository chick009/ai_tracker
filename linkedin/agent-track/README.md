# agent-track

Multi-service **agent tracker**. Services are independent CLIs under one package. Later services can be added as sibling command groups. This repo does **not** schedule, import, or wrap Johnny’s Mon/Wed/Fri LinkedIn **job search** cron or anything in `career-job-applications`.

**First service: LinkedIn Feed Digest** — scroll the home feed, copy permalinks, and write a slim card list (`author`, `link`, `text_snippet`).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium
```

Logged-in Chromium profile (gitignored, owned by **this** repo):

- Path: `data/.linkedin-browser-profile`
- If you already have a LinkedIn-logged-in Playwright/Chromium user-data-dir **elsewhere**, copy that directory here. Do not hard-code another repo’s path and do not depend on `career-job-applications`.

## Run Feed Digest

```bash
agent-track feed digest --limit 20 --persist-profile --no-wait
```

Useful flags:

| Flag | Meaning |
| --- | --- |
| `--limit 20` | Stop after this many unique posts (default 20) |
| `--persist-profile` | Reuse `data/.linkedin-browser-profile` |
| `--no-wait` | Fail fast if `li_at` / feed is missing (no interactive login wait) |
| `--headed` / `--headless` | UI (default headed) |
| `--output-dir` | Defaults to `data/feed/` |

Outputs (gitignored):

- `data/feed/posts.jsonl` — full records: `author`, `link`, `text_snippet`, `token`, `relative_time`, `urn`, `captured_at`
- `data/feed/digest.json` — slim cards: `author`, `link`, `text_snippet` (commentary; expanded when the in-card control exists)

Behavior (Sep 2026 LinkedIn SDUI):

- Opens `https://www.linkedin.com/feed/`
- Cards: `[role=listitem][componentkey*='update-card-focus']`; token between `update-card-focus` and `FeedType_…`
- Author from actor `/in/` **or** `/company/` links (aria-label *or* visible text) — **never clicked**. Fallbacks: overflow `Open control menu for post by {Name}`, then first header line after `Feed post`
- Commentary from `[data-testid=expandable-text-box]`; optional `[data-testid=expandable-text-button]`
- Permalink: overflow **Copy link to post** → clipboard (`https://lnkd.in/…`). Fallback: Embed href `targetUrn=urn:li:share:…`
- Slow wheel scroll (~300–500px, 0.8–1.5s settle). No jump-to-bottom
- Skips **Promoted** when the badge is its own line

## Tests (offline)

CI / local unit tests never hit live LinkedIn:

```bash
pytest
```

## Isolation

Do **not** add this digest to the job-search cron. Do **not** import `career-job-applications`. Feed tracking is only `agent-track feed …`.

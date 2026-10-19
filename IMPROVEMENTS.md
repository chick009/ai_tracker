# Observed weaknesses and concrete improvements

Based on the scripts in this bundle (as of 2026-10-19). File-level catalog: [INVENTORY.md](INVENTORY.md). Daily flow: [PIPELINE.md](PIPELINE.md).

## 1. Copy-per-day scripts with hard-coded dates and paths
- **109 files** under `*/history/` are dated copies of the same scripts: `run_papergen.py` ×11, `build_cards.py` / `post_ingest.py` ×10, the blog scan set across about 10 dirs, and tier-3 ×4.
- 27 of the "latest" scripts still hard-code a date. Examples: `W=Path('/workspace/blog-scan-2026-10-14')`, `TODAY='2026-10-14'`, and `D="../downstream-2026-10-16"`.
- **Fix:** one package per bot with a `--date` argument (defaulting to today in HKT) and a `--root` / `$AI_TRACKER_ROOT` instead of `/workspace/...` and `/home/box/agent-data/agents/<uuid>/...`.

## 2. Data is hand-edited into code
- `blog-investigations/daily-scan/posts_data.py` (up to 37KB) holds the day's posts as Python literals.
- `hf-github-tracker/steps-2026-10-19/step2.py` and `daily-builders/*/cls.py` hold hand-labelled `id → topic` dicts.
- `write.py` / `build.py` embed zh blurbs per repo, and `run_papergen.py` embeds the paper list.
- **Fix:** move LLM/agent judgments into JSON inputs that the scripts read, so the code stays stable and the judgments can be diffed and reviewed.

## 3. Duplicated logic
- The Supabase base URL `psmjbqbnkoioicbasqlm.supabase.co/functions/v1` appears in **37** scripts.
- The tracker-ingest POST is reimplemented in `downstream/tracker-ingest/post_ingest.py`, `blog-investigations/daily-scan/ingest.py`, `tier3/ingest_tier3.py` and `blog-watch-build/build_cards.py`.
- The X dump parsing (strip untrusted wrappers, find `{…}`) is copied across `parse_x.py`, `poll_one.py`, `save_poll*.py` and `merge_backfill*.py`.
- The daily and weekly variants are near-identical files that differ only in `RAW`.
- `tools/paper_extract.py` also exists as `cloud-handoff/partial_paper_extract.py`, and `tools/jev_topic_filter.py` duplicates `steps-2026-10-19/jev_topic_v2.py`.
- **Fix:** a shared `ai_tracker_common` with `ingest_client.py` (cards/weeks/paper-gen/oss), `x_dump.py` and `hkt.py`.

## 4. Steps with no script (manual and not reproducible)
- The **HTML digest** is written inline each day, with no generator. Only example outputs exist.
- **Notion rows** go through the MCP by hand, from `notion-rows.json`.
- **Perplexity TL;DR** runs in a browser session, and its answer is pasted into `perplexity-answer.md`, which `build_cards.py` then parses with a regex.
- `ingest-2026-10-19/` has `post_ingest.py` but no `build_cards.py`, so the 10-19 cards were built inline.
- **Fix:** a `render_digest.py` (Jinja template) fed from the Top 10 JSON, and a `notion_rows.py` that emits the exact MCP payloads.

## 5. Fragile gate and orchestration
- The Top 10 gate depends on the routine prompt deciding "all four have posted today". On **2026-10-19 the gate went stale**, as the Orchestrator reported; the details are in its run log, not on the box. The rules "never rank from disk alone" and "never repost the Top 10" are prompt-level guards against this.
- There is no machine-readable "collector done" signal.
- **Fix:** each collector writes `status/<date>/<bot>.json` (`{done:true, items:N, posted_msg_id}`), and the gate checks these files *and* the group post, with a hard timeout and a fallback ("3/4 posted, ranking at 08:45").

## 6. Few tests outside the two packages
- Only `paper_review` and `agent-track` have tests (67 test functions in total).
- None of the ingest, blog-scan, X-watchlist, Reddit, aggregation or card-builder scripts are tested.
- **Fix:** golden-file tests against the `examples/` payloads, e.g. `build_cards` gives the same cards.json, and `aggregate.py --offline` gives the same events.json.

## 7. Secrets and environment handling
- `post_oss_ingest*.py` read `OSS_INGEST_TOKEN` from a credential file at a hard-coded agent path (`/home/box/agent-data/connector-secrets/<uuid>/oss-ingest.json`), while every other script uses env vars.
- **Fix:** use env vars everywhere.
- Some scripts `sys.exit` when a token is missing, and others silently skip ingest (blog `ingest.py`). Make the behaviour explicit and report it.

## 8. Naming and stale identity
- `reddit-digest/build.py` still sends `user_agent='XBookmarkWatchlist/1.0'`, a bot that no longer exists.
- The LinkedIn probes point at `/workspace/career-job-applications/data/.linkedin-browser-profile` (the job-search project's profile), not agent-track's own profile.
- Shebangs hard-code venvs (`#!/workspace/ai-tracker/tools/.venv/bin/python`).

## 9. Aggregation exists but isn't used
- `downstream/aggregation-trial/aggregate.py` reproduces the hand dedupes (JevAgentHarness across X + LinkedIn + HF, and OpenCode across blog + GitHub).
- Wiring it in before ranking would automate the "same event across sources" rule in the editorial skill. Johnny hasn't decided on this yet.
- Its fuzzy matcher still needs a rule for video-only X posts that have no outbound link (Cursor canvases).

## 10. Language / format drift
- The outputs mix zh-HK and English, and the Top 10 moves to English from 2026-10-20.
- Card text and group posts come from the same TL;DRs but are formatted in separate places.
- **Fix:** one formatter, with a `lang` setting.

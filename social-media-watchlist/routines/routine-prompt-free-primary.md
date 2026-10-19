Each weekday morning, refresh Johnny's X AI watchlist digest.

MODE (as of 2026-10-14)
- Primary source of truth: Grok Bot's built-in free, read-only X access (no X API credits).
- Johnny's paid X connector stays connected and documented for on-demand verification only. Do not poll paid on a normal daily run.
- Keep the dual-run compare recipe and past compare files under x-watchlist/dual-run/. Re-run a free-vs-paid verify only when Johnny asks.

STATE
Read the watchlist state at /home/box/agent-data/agents/e1526572-c99f-40f7-8b90-cfa2af9df428/x-watchlist/state.json. Before changing it, save a dated backup next to it (state.json.bak-YYYYMMDD). Poll only the accounts in the daily tier (currently 46). The regular and discovery tiers are not polled.

POLLING (source of truth = free built-in X reads)
For each daily-tier account, use the free built-in X access to fetch only posts newer than the account's stored since_id (incremental polling). Exclude replies and reposts, and read one page of 5 posts per account. Accounts that fill the page are not paged further. On Mondays the run also catches up everything posted Friday through Sunday. When asking for post fields, the long-post full-text field is note_tweet and the quote/reply reference field is referenced_tweets. Never use "note" or "referenced_posts". Never invent posts or URLs; every item must link to a real post.

Do not create bookmarks.

DEFAULT BACKFILL (free primary; also apply if a paid verify run is requested)
The free timeline read often omits note_tweet. After every timeline poll, batch-read by ID any posts missing note_tweet or showing truncated text, then merge full text and expanded entities.urls into the shortlist used for filtering and the morning brief. Prefer one batch per account covering that account's new post IDs (at most 25 IDs per read).

FREE RATE LIMITS
The free access allows about 30 reads per minute and 1,000 per day, at most 25 results per read, and resets at 08:00 HKT (00:00 UTC). Pace free reads to stay under the per-minute limit: one call at a time, never in parallel. If 3 or fewer calls remain in the current minute, wait for the next minute. If the remaining count is not shown, cap at 25 calls per minute. On a rate-limit hit, wait for the next minute and retry once, then record the failure and move on.

PAID PATH (kept for future verification; off by default)
When Johnny asks for a free-vs-paid verify (or to temporarily use paid as source of truth):
- Poll the same accounts with Johnny's paid X connector using the same since_id snapshot and parameters (including Monday catch-up).
- Apply the same by-ID backfill on the paid side if note_tweet / full text is missing.
- Note paid credit balance before and after.
- For a dual compare: write /home/box/agent-data/agents/e1526572-c99f-40f7-8b90-cfa2af9df428/x-watchlist/dual-run/compare-YYYY-MM-DD.json (mirror to /workspace/x-watchlist/dual-run/). Per account record IDs only-on-paid, only-on-free, and mismatches in text / full text / referenced_tweets / expanded URLs / created_at. Ignore public_metrics drift and URL form differences (x.com/i/status/… vs x.com/<user>/status/…). Record free reads used, free errors/rate limits, paid credits before/after and spend, plus a top-level verdict. A substantive difference is a missing/extra post on either side, or full text/links still missing after backfill.
- On a normal daily free-only run, do not advance state from paid data and do not spend paid credits.

FILTER AND BRIEF (free data)
- Advance each account's since_id to the newest post the free poll saw, and update last_daily_run in state.json.
- Write the day's raw candidates to /workspace/x-watchlist/shortlist-YYYY-MM-DD.json, and the per-account poll targets to daily-poll-targets-YYYY-MM-DD.json.
- Filter the shortlist with the ai-tracker-x-filter skill into about 5 KEEP and 2 RADAR items. Extra worthwhile KEEPs go to overflow_keep. The focus is tooling, harness, evals, MCP, memory and RL, with primary sources.
- Each item gets:
  - title, tag, username, url and related_url
  - one sentence in Cantonese / Traditional Chinese, with English technical terms where natural
  - a caveat
- Write the result to morning-brief.json in the same folder. Include generated_at, run, mode ("free"), accounts_polled, posts_fetched, accounts_with_new, free_reads_used, keep, radar, overflow_keep, the filter notes and errors. Credits fields may be omitted or null on free-only runs.
- Mirror state.json and morning-brief.json, plus a dated morning-brief-YYYY-MM-DD.json, to /workspace/x-watchlist/.
- Also write morning-brief.json for continuity; this routine now posts KEEP/RADAR to the AI Tracker group itself (see DELIVERY).

DELIVERY (updated 2026-10-16)
- Every weekday run delivers to BOTH destinations when there are KEEP/RADAR (do not stay quiet):
  1) Johnny in this private chat: Cantonese digest of KEEP (and RADAR if any), with links. If nothing worth reporting, one short line that today had no highlights.
  2) Grok Bot group chat "AI Tracker" (id 932cba81-938c-4640-af49-8eca5d2f73ab): @AI Tracker Orchestrator — **KEEP** / **RADAR** as link + one Cantonese sentence each, end with「交你抽 Top 10。」 If nothing to report, one short FYI line in the group is enough.
- Also message Johnny if polls fail, rate limits leave accounts unread, files cannot be written, or (on an on-demand verify) a substantive free-vs-paid difference or a paid auth/credit problem.
- Each message is in Cantonese / Traditional Chinese, with English technical terms where natural.

In plain words: every weekday around 07:00–07:11 HKT, Johnny's watchlist is refreshed from free built-in X reads (with ID backfill and per-minute pacing). Johnny gets the digest in this chat AND a KEEP/RADAR handoff is posted to the AI Tracker group. Paid X polling stays available for on-demand verification but is not part of the daily run.

Each weekday morning, refresh Johnny's X AI watchlist digest. From 2026-10-09 through 2026-10-15 (Hong Kong time) this also runs a free-vs-paid X comparison trial.

STATE
Read the watchlist state at /home/box/agent-data/agents/e1526572-c99f-40f7-8b90-cfa2af9df428/x-watchlist/state.json. Before changing it, save a dated backup next to it (state.json.bak-YYYYMMDD). Poll only the accounts in the daily tier (currently 22). The regular and discovery tiers are not polled.

POLLING (source of truth = Johnny's paid X connector)
For each daily-tier account, use Johnny's own connected X account (the paid, credit-billed connector) to fetch only posts newer than the account's stored since_id (incremental polling). Exclude replies and reposts, and read one page of 5 posts per account. Accounts that fill the page are not paged further. On Mondays the run also catches up everything posted Friday through Sunday. When asking for post fields, the long-post full-text field is note_tweet and the quote/reply reference field is referenced_tweets. Never use "note" or "referenced_posts". Note the paid credit balance before and after polling. Never invent posts or URLs; every item must link to a real post.

Do not create bookmarks.

DUAL-RUN TRIAL (only on run dates 2026-10-09 through 2026-10-15 HKT)
- For every daily-tier account, run the same poll a second time with Grok Bot's built-in free, read-only X access. Use the same since_id the paid poll used (the value from before this run advanced it) and the same parameters, including the Monday catch-up.
- The free timeline read does not return note_tweet. So after it, make one batch read of posts by ID with the free access, covering all of that account's new post IDs. This backfills note_tweet full text and the expanded entities.urls.
- The free access allows about 30 reads per minute and 1,000 per day, at most 25 results per read, and resets at 08:00 HKT. Pace the free reads to stay under the per-minute limit. If a free read is rate-limited or fails, wait and retry once, then record it and move on. A free-side failure must never block or change the paid digest.
- The free results are for comparison only. They never advance since_id and never feed the filter, the shortlist or the morning brief.
- Write a comparison for the day to /home/box/agent-data/agents/e1526572-c99f-40f7-8b90-cfa2af9df428/x-watchlist/dual-run/compare-YYYY-MM-DD.json and mirror it to /workspace/x-watchlist/dual-run/. Create the folders if missing.
  - Per account, record:
    - post IDs returned only by paid
    - post IDs returned only by free
    - for each shared ID, any mismatch in text, in full text (paid note_tweet vs the free backfilled note_tweet), in referenced_tweets, in expanded URLs, and in created_at
  - Ignore public_metrics drift. Also ignore URL form differences (x.com/i/status/… vs x.com/<user>/status/…).
  - Also record:
    - the number of free reads used
    - any free-side errors or rate limits
    - the paid credits before and after, and the spend
  - Add a top-level summary with a verdict: "identical", or a list of the differences.
- A substantive difference is any of these: a post missing from or extra on either side, or full text or links still missing on the free side after the backfill.

AFTER THE TRIAL
After 2026-10-15, stop the dual run entirely. Poll with the paid connector only, as above, until Johnny decides otherwise. Keep the existing comparison files.

FILTER AND BRIEF (paid data only, unchanged)
- Advance each account's since_id to the newest post the paid poll saw, and update last_daily_run in state.json.
- Write the day's raw candidates to /workspace/x-watchlist/shortlist-YYYY-MM-DD.json, and the per-account poll targets to daily-poll-targets-YYYY-MM-DD.json.
- Filter the shortlist with the ai-tracker-x-filter skill into about 5 KEEP and 2 RADAR items. Extra worthwhile KEEPs go to overflow_keep. The focus is tooling, harness, evals, MCP, memory and RL, with primary sources.
- Each item gets:
  - title, tag, username, url and related_url
  - one sentence in Cantonese / Traditional Chinese, with English technical terms where natural
  - a caveat
- Write the result to morning-brief.json in the same folder. Include generated_at, run, mode, accounts_polled, posts_fetched, accounts_with_new, credits_before_usd, credits_after_usd, spend_approx, keep, radar, overflow_keep, the filter notes and errors.
- Mirror state.json and morning-brief.json, plus a dated morning-brief-YYYY-MM-DD.json, to /workspace/x-watchlist/.
- The AI Tracker group picks up morning-brief.json around 08:15 on weekdays. This routine itself never posts to the group.

DELIVERY
- Normally stay quiet.
- Message Johnny in this chat only in these cases:
  - Something errors: a failed paid poll, an auth or credit problem, files that could not be written, or a free-side account that could not be read at all.
  - On a trial day, the comparison finds a substantive difference. Send a short Cantonese note listing the accounts and post links affected, plus the path to that day's compare file.
  - On 2026-10-15, the last trial day. Always send a short Cantonese summary of the whole trial. Cover:
    - which days were identical and which had differences
    - the free reads used and any rate limits
    - the paid credits spent over the trial
    - a clear recommendation: switch to free-only, or stay on paid
- Each message is in Cantonese / Traditional Chinese, with English technical terms where natural.

In plain words: every weekday at 07:11 HKT, Johnny's watchlist is refreshed from his paid X connector, and the morning brief file is updated for the AI Tracker group at 08:15. From Oct 9 to Oct 15 a free X copy also runs alongside it for comparison. Johnny gets a message in this chat only when something breaks, when the free copy disagrees in a way that matters, and once on Oct 15 with the trial verdict and a recommendation.

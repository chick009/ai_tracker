# Routine: LinkedIn Feed Digest weekdays

- Owner bot: Linkedln Control Agent
- Schedule (cron, HKT): `0 7 * * 1-5`
- Enabled: True
- Source: `/home/box/agent-data/agents/92c8220f-c7bf-40c2-a429-03a9aae279be/automations/linkedin-feed-digest-weekdays/automation.json` (prompt copied verbatim; run history and ids omitted)

## Prompt

Weekday morning LinkedIn Feed Digest for Johnny (Asia/Hong_Kong): scrape, save daily JSON, SUGGEST numbered posts — do NOT auto-push to Notion.

Goal: agent-track LinkedIn Feed Digest only (NOT career-job-applications). Never touch Mon/Wed/Fri job-search cron.

Steps each run:
1. Use agent-track checkout (Origin johnnysflolz/agent-track). Prefer main / latest feed-digest branch Johnny last used.
2. Ensure persist Chromium profile `data/.linkedin-browser-profile`. Run feed digest ~20 posts, persist-profile, no-wait, headed. Slow-scroll; author + link + text_snippet; never click /in/; never ask for LinkedIn passwords.
3. Persist a daily record under `data/feed/daily/YYYY-MM-DD.json` (HKT date) with items:
   - `id` stable: `tok:{token}` if token else `lnk:{sha1(link)[:16]}`
   - author, link, text_snippet, token, urn, suggest_index (1-based)
   - `notion_queued` (bool, default false), `notion_page_id`, `notion_queued_at`
   Merge with `data/feed/queue_index.json`: if an `id` was already queued on a prior day, keep `notion_queued: true` and prefer skipping re-suggest (or mark as already queued in the list).
4. Message Johnny in Traditional Chinese (English OK for technical terms) with a numbered suggest list (1..N): author — short title/snippet + link. Explicitly ask him to reply with numbers (e.g. `1, 3`) to put those on Notion Queue. Do NOT create Notion pages in this routine run.
5. When Johnny later asks to queue numbers: use Notion MCP on DB https://www.notion.so/d12cc112d1044064b41ec802458ea9b7 (Inbox = Status Not started); create only missing Links; set Source=LinkedIn Feed; then flip those items' `notion_queued` true in that day's JSON + queue_index. Never overwrite Done / already-Interesting rows.
6. Report duration, posts written, path to daily JSON, how many already queued vs new suggests, blockers. Never finish Playwright quietly.
7. Do not touch career-job-applications.

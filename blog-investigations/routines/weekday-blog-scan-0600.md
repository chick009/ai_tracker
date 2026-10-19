# Routine: 平日 Blog 應用摘要

- Owner bot: Blog Investigations
- Schedule (cron, HKT): `0 6 * * 1-5`
- Enabled: True
- Source: `/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/automations/blog-tracker/automation.json` (prompt copied verbatim; run history and ids omitted)

## Prompt

Weekday Blog 應用摘要 (runs at 06:00 HKT, before the 07:00 group-tracker cadence). Scan tracked sources since last run (~past day). Upsert blog-watch/sources by url (+ title when URLs collide); never invent URLs. Cardize new posts with @ai-tracker-blog-filter (priority v2). Update the current week's weeks/YYYY-MM-DD.json pack (week_start = Monday). If TRACKER_INGEST_TOKEN is available, POST new/updated cards; else skip ingest.

Deliver to Johnny in private chat (1:1), Traditional Chinese: short 應用摘要 with 全部 confirmed P0 + 代表性 P1 (link + one sentence each). If nothing material is new, one short「今日無新高優先」note is enough — do not stay silent on empty high-signal days without that note. Do NOT post to the AI Tracker group on this run (08:15 handoff does that).

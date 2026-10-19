# Routine: 每週 AI 應用 Blog 摘要

- Owner bot: Blog Investigations
- Schedule (cron, HKT): `10 9 * * 1`
- Enabled: True
- Source: `/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/automations/ai-blog/automation.json` (prompt copied verbatim; run history and ids omitted)

## Prompt

Monday weekly rollup only (incremental weekday 應用摘要 already ran at 06:00 Mon–Fri). Re-scan any gaps for the past week, reconcile cards, rewrite weeks/YYYY-MM-DD.json with cross-link synthesis + type_summaries for week_start=Monday. Run @ai-tracker-blog-filter on the full-week shortlist. If TRACKER_INGEST_TOKEN is available, POST week pack (+ any missing cards); else skip ingest.

Deliver Traditional Chinese weekly digest to Johnny: synthesis + 全部 P0 + 代表性 P1. Skip empty types. Sources unchanged (incl. sakana, deepseek, cognition, changelogs, etc.).

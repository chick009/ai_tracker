# Orchestrator routines (reconstructed, NOT verbatim)

The AI Tracker Orchestrator (agent `0a41b18d-6d73-4f6d-a67d-69028d9a7d88`) has **no routine files on the box**.
Its routines live server-side in Grok Bot. Below is a summary from the Orchestrator's own working notes
(2026-10-19). Export the exact prompts from Grok Bot and replace this file.

## `ai-tracker-weekday-highlights`, weekdays 08:15 HKT (kickoff)
- Posts in the "AI Tracker" group chat (`932cba81-938c-4640-af49-8eca5d2f73ab`) and tags
  `@Huggingface & Github Tracker @Linkedln Control Agent @Social Media Watchlist @Blog Investigations`.
- Asks each collector for KEEP / RADAR (link + one line). From 2026-10-20 it also asks Social Media
  Watchlist and LinkedIn for a **TRICKS** block (0–3 items, link + one line).

## `ai-tracker-weekday-top-10`, weekdays ~08:19 HKT (gate + rank + downstream)
1. **Gate:** wait until all four collectors have posted in the channel for today. Never rank from disk
   alone, and never repost the Top 10.
2. Rank with `skills/ai-tracker-editorial-orchestrator`, then post one group message:
   **Top 10 → Tricks & Ideas → Radar** (English from 2026-10-20).
3. Downstream runs right away, without waiting for clarifications:
   - Notion scoped rows (Papers / GitHub Trending / Model & IDE / Applicational), through the Notion MCP
   - paper-gen ingest for arXiv items (`downstream/paper-gen/run_papergen.py`)
   - a Perplexity Search session for TL;DRs of non-paper items (`skills/start-a-search-session-in-blog-investigations`)
   - a GitHub SYSTEM_DESIGN for github.com Top 10 items, run as a cloud agent plus `downstream/oss-system-design/post_oss_ingest.py`
   - tracker cards + week ingest (`downstream/tracker-ingest/build_cards.py`, `post_ingest.py`)
   - the HTML digest, sent to the group and to Johnny (`downstream/html-digest/examples/`; the generator is not saved as a script)

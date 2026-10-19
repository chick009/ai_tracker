# AI Tracker

This repository is a **documentation and source dump** of the scripts, skills, and routine prompts that run Johnny's live AI Tracker bots. It is not a packaged monorepo and is not set up to run end-to-end from a fresh clone. Use it to browse what each bot does, how the weekday pipeline is wired, and where the live copies came from.

The live system is an Orchestrator plus four collectors:

- **Huggingface & Github Tracker**
- **Linkedln Control Agent**
- **Social Media Watchlist**
- **Blog Investigations**

…and the downstream steps those bots hand off to (Notion, paper-gen, Perplexity, OSS system design, tracker ingest, HTML digest).

## Start here

| Doc | What it is |
|---|---|
| [PIPELINE.md](PIPELINE.md) | Weekday schedule (HKT) and the collector → gate → Top 10 → downstream flow |
| [INVENTORY.md](INVENTORY.md) | Every file in this dump: original box path, owner bot, trigger, inputs/outputs, external services |
| [IMPROVEMENTS.md](IMPROVEMENTS.md) | Observed weaknesses in the current scripts and concrete fixes |

Older per-day copies live under each bot's `history/` folders so duplication and drift stay visible. Diff those against the latest copy rather than treating them as current.

## Weekday pipeline

Times are HKT (UTC+8). The short version:

1. **06:00** — Blog Investigations scans tier-1/2 sources, writes cards, ingests to the tracker site, and sends Johnny a 1:1 zh digest (it does not post to the group).
2. **~06:45–07:11** — The other three collectors run: HF Daily Papers + GitHub Trending, LinkedIn feed digest, and X watchlist + Reddit digest.
3. **08:15** — Orchestrator kickoff tags all four collectors in the AI Tracker group and asks for KEEP / RADAR / TRICKS.
4. **~08:19** — Gate waits until all four have posted today, ranks with the editorial skill, and posts **Top 10 → Tricks & Ideas → Radar** once.
5. **After the post** — Downstream runs immediately: Notion rows, paper-gen, Perplexity TL;DR, GitHub SYSTEM_DESIGN, tracker cards + week ingest, then the HTML digest to the group and Johnny.
6. **Monday 09:10** — Blog Investigations weekly rollup.

See [PIPELINE.md](PIPELINE.md) for the timetable and mermaid diagram.

## Browse by bot

### `orchestrator/`

Kickoff and Top 10 gate. Routines live **server-side in Grok Bot**, not as files on the box. [`orchestrator/routines/README.md`](orchestrator/routines/README.md) is a reconstructed summary of `ai-tracker-weekday-highlights` (08:15) and `ai-tracker-weekday-top-10` (~08:19). Export the exact prompts from Grok Bot and replace that file.

### `hf-github-tracker/`

Huggingface & Github Tracker: HF Daily Papers + GitHub Trending → extract → topic classify → shortlist markdown, plus optional `paper_review` HTML. Tools live in `tools/`; the dated daily builders and 2026-10-19 step scripts are snapshots of how the collector was actually run. The weekday routine prompt is **not on the box** — see [`hf-github-tracker/routines/README.md`](hf-github-tracker/routines/README.md) and export it from Grok Bot.

### `linkedin/`

Linkedln Control Agent: `agent-track feed digest` (Playwright) plus earlier `feed-probe/` scripts. The weekday 07:00 routine prompt is in [`linkedin/routines/`](linkedin/routines/). Suggestions go to Johnny; Notion only when he asks.

### `social-media-watchlist/`

X watchlist poll (free reads + by-ID backfill) and Reddit digest. Current and retired routine prompts are in [`social-media-watchlist/routines/`](social-media-watchlist/routines/). Posts KEEP / RADAR (and TRICKS from 2026-10-20) to the group.

### `blog-investigations/`

06:00 weekday scan (`daily-scan/`), optional browser-pass `tier3/`, blog-watch source registry, and Monday 09:10 rollup. Routine prompts are in [`blog-investigations/routines/`](blog-investigations/routines/).

### `downstream/`

Steps the Orchestrator runs after the Top 10 post:

| Folder | Role |
|---|---|
| `downstream/notion/` | Example scoped Notion rows (written through the Notion MCP; no script) |
| `downstream/paper-gen/` | Submit Top 10 arXiv papers to paper-gen |
| `downstream/perplexity/` | Example Perplexity Search prompt (browser session; no script) |
| `downstream/oss-system-design/` | Cloud-agent SYSTEM_DESIGN + `post_oss_ingest.py` |
| `downstream/tracker-ingest/` | `build_cards.py` + `post_ingest.py` for cards/weeks |
| `downstream/html-digest/` | Example HTML digest (generator is written inline; not saved as a script) |
| `downstream/aggregation-trial/` | Cross-source dedupe trial — **not wired into the daily flow** |

### `skills/`

Bot skill prompts (rules, not code): editorial orchestrator, per-collector filters, HF/GitHub daily skills, OSS system-design exploration, and the Perplexity search-session skill.

## Routine prompts

Some weekday routines are files in this dump (`linkedin/routines/`, `social-media-watchlist/routines/`, `blog-investigations/routines/`). Others are **server-side only** and need a manual export from Grok Bot:

- Orchestrator kickoff + Top 10 gate — reconstructed in [`orchestrator/routines/README.md`](orchestrator/routines/README.md)
- Huggingface & Github Tracker weekday collection — placeholder in [`hf-github-tracker/routines/README.md`](hf-github-tracker/routines/README.md)

Leave those placeholder READMEs as-is until the verbatim prompts are exported.

## Credentials

All credentials come from **environment variables**. Never commit secrets, `.env` files, or connector credential files.

| Variable | Used for |
|---|---|
| `TRACKER_INGEST_TOKEN` | Tracker cards / weeks ingest |
| `PAPER_GEN_TOKEN` | paper-gen ingest |
| `OSS_INGEST_TOKEN` | OSS projects ingest |
| `JEV_API_KEY` | Jev / typesafe.ai topic filter |
| `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` | Reddit digest |
| `COMMAND_CODE_API_KEY` | paper_review Command Code runner |

Some older OSS ingest copies still read a hard-coded box credential file; the intended pattern is env vars only. See [IMPROVEMENTS.md](IMPROVEMENTS.md) §7.

## What this dump is not

Do not treat this as a runnable install. There is no root package, no shared venv, and several daily scripts still hard-code dates and `/workspace/...` paths. Two subpackages (`hf-github-tracker/paper_review`, `linkedin/agent-track`) have their own tests and setup notes; everything else is a snapshot of live box scripts.

The HTML digest, Notion row writes, and Perplexity session have **no generator scripts** here — only example outputs. Orchestrator and HF/GitHub routine prompts are missing until they are exported from Grok Bot.

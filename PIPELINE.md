# AI Tracker daily pipeline (weekdays, HKT)

How the live bots run on weekdays. For the file-level catalog see [INVENTORY.md](INVENTORY.md); for observed weaknesses see [IMPROVEMENTS.md](IMPROVEMENTS.md). This repository is a source dump, not a runnable install.

| Time (HKT) | Bot | Step |
|---|---|---|
| 06:00 | Blog Investigations | Blog scan. Fetch tier-1/2 sources (`blog-investigations/daily-scan/fetch_all.py`), upsert sources, write cards, update the week pack, ingest to the tracker site, then send Johnny a 1:1 zh digest. It does not post to the group. Tier-3 sources need a browser pass (`tier3/`). |
| ~06:45–07:00 | Huggingface & Github Tracker | HF Daily Papers (`/api/daily_papers`) + GitHub Trending. Extract text (`tools/paper_extract.py`), classify topics (`tools/jev_topic_filter.py`), write `<date>-hf-daily-papers.md / -github-trending.md / -group-shortlist.md`, run the optional `paper_review` HTML. |
| 07:00 | Linkedln Control Agent | `agent-track feed digest`, about 20 feed posts, saved to `data/feed/daily/<date>.json`. Sends numbered suggestions to Johnny (Notion only when he asks). |
| ~07:00–07:11 | Social Media Watchlist | X watchlist poll using free reads with since_id, by-ID backfill (`x-watchlist/save_poll.py`, `merge_backfill.py`), plus the Reddit digest (`reddit-digest/build.py`). Posts KEEP / RADAR (+ TRICKS from 10-20) to the group. |
| 08:15 | Orchestrator | Kickoff routine `ai-tracker-weekday-highlights`. Tags all four collectors in the group and asks for KEEP / RADAR / TRICKS. |
| ~08:19 | Orchestrator | Gate routine `ai-tracker-weekday-top-10`. Waits until **all four** collectors have posted today, then ranks (editorial skill) and posts **Top 10 → Tricks & Ideas → Radar** once. |
| after the post | Orchestrator | Downstream, with no wait for clarifications: Notion rows (MCP) · paper-gen (`downstream/paper-gen/run_papergen.py`) · Perplexity TL;DR (browser session) · GitHub SYSTEM_DESIGN (cloud agent + `post_oss_ingest.py`) · cards + week (`build_cards.py`, `post_ingest.py`) · HTML digest to the group + Johnny. |
| Mon 09:10 | Blog Investigations | Weekly blog rollup. |

```mermaid
flowchart TD
  subgraph Collectors
    B[06:00 Blog Investigations<br/>fetch_all → upsert → cards → weeks → ingest]
    H[~07:00 HF & GitHub Tracker<br/>daily_papers + trending → extract → classify → shortlist md]
    L[07:00 LinkedIn Control Agent<br/>agent-track feed digest → daily JSON]
    S[~07:00 Social Media Watchlist<br/>X free poll + backfill · Reddit PRAW digest]
  end
  K[08:15 Orchestrator kickoff<br/>tags 4 collectors in AI Tracker group]
  B -->|1:1 digest to Johnny| J((Johnny))
  K --> B & H & L & S
  B & H & L & S -->|KEEP / RADAR / TRICKS in group| G{~08:19 gate:<br/>all 4 posted today?}
  G -- no --> W[wait / re-check] --> G
  G -- yes --> R[Rank with editorial skill<br/>post Top 10 → Tricks → Radar]
  R --> N[Notion scoped rows · MCP]
  R --> P[paper-gen ingest · run_papergen.py]
  R --> X[Perplexity TL;DR · browser]
  R --> O[GitHub SYSTEM_DESIGN · cloud agent + post_oss_ingest.py]
  X --> C[build_cards.py → post_ingest.py<br/>tracker-cards-ingest / tracker-weeks-ingest]
  P --> C
  C --> HT[HTML digest · inline]
  HT --> J
  HT --> GR[AI Tracker group]
  A[[aggregation-trial/aggregate.py<br/>trial only, not wired in]] -.-> R
```

# INVENTORY

Every file in this bundle, with the box path it was copied from. Times are HKT (UTC+8). Daily flow: [PIPELINE.md](PIPELINE.md). Improvement notes: [IMPROVEMENTS.md](IMPROVEMENTS.md).

Secret values were never copied: scripts read `${TRACKER_INGEST_TOKEN}`, `${PAPER_GEN_TOKEN}`, `${OSS_INGEST_TOKEN}`, `${JEV_API_KEY}`, `${REDDIT_CLIENT_ID}`/`${REDDIT_CLIENT_SECRET}`, `${COMMAND_CODE_API_KEY}` from the environment (or, for OSS ingest, from a credential file on the box). No .env files are included.

Abbreviations: `W/` = `/workspace/`, `AD/` = `/home/box/agent-data/`. `SB` = Supabase edge functions at `https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1/…`.

## orchestrator/

| Bundle path | Original box path | Bot | What it does | Trigger | Inputs / outputs | External services |
|---|---|---|---|---|---|---|
| `orchestrator/routines/README.md` | `(written for this bundle; reconstructed)` | Orchestrator | Reconstructed summary of the 08:15 kickoff + ~08:19 Top 10 routines (not verbatim) | - | - | - |

## downstream/

| Bundle path | Original box path | Bot | What it does | Trigger | Inputs / outputs | External services |
|---|---|---|---|---|---|---|
| `downstream/aggregation-trial/aggregate.py` | `W/ai-tracker/aggregation-trial-2026-10-19/aggregate.py` | Orchestrator | Cross-source aggregation trial: resolve links (lnkd.in, X outbound, HF, blog), normalize keys (arxiv/github/url), union-find merge, fuzzy "possible" list | Manual trial on 2026-10-19 (`--offline` rebuilds from raw/); not wired into the daily flow | in: inputs-<date>.json, raw/ (not bundled, 9MB); out: events.json, resolution.json, report.md | HTTP fetches, X connector (via dumped reads) |
| `downstream/aggregation-trial/inputs-2026-10-19.json` | `W/ai-tracker/aggregation-trial-2026-10-19/inputs-2026-10-19.json` | Orchestrator | Trial input: collector items for 2026-10-19 | - | input example | - |
| `downstream/aggregation-trial/report.md` | `W/ai-tracker/aggregation-trial-2026-10-19/report.md` | Orchestrator | Trial findings (46 items to 44 events, 2 exact merges, 1 strong fuzzy) | - | output example | - |
| `downstream/html-digest/examples/ai-tracker-top10-2026-10-19.html` | `W/ai-tracker/downstream-2026-10-19/ai-tracker-top10-2026-10-19.html` | Orchestrator | Example daily HTML digest; the generator is NOT saved as a script (built inline each day) | Top 10 routine, last step | example | SendToUser / group |
| `downstream/html-digest/examples/group-post-top10-2026-10-19.md` | `W/ai-tracker/downstream-2026-10-19/group-post-top10.md` | Orchestrator | Example group post (Top 10 + Radar) | Top 10 routine | example | Grok Bot group chat |
| `downstream/notion/examples/notion-rows-2026-10-19.json` | `W/ai-tracker/downstream-2026-10-19/notion-rows.json` | Orchestrator | Example scoped Notion rows (Title/Summary/Link/Lane/Rank/Tier...) | Top 10 routine, written through the Notion MCP (no script) | example | Notion MCP |
| `downstream/oss-system-design/examples/cloud-agent-prompt-2026-10-08.md` | `W/ai-tracker/downstream-2026-10-08/cloud-agent-prompt.md` | Orchestrator | Earlier SYSTEM_DESIGN cloud-agent prompt | same | prompt | Cloud agent, GitHub |
| `downstream/oss-system-design/examples/cloud-agent-prompt-2026-10-16.md` | `W/ai-tracker/downstream-2026-10-16/cloud-agent-prompt.md` | Orchestrator | Prompt handed to a cloud agent to explore a repo and write SYSTEM_DESIGN.md | Used by the Top 10 routine when a github.com item is in the Top 10 | prompt | Cloud agent, GitHub |
| `downstream/oss-system-design/post_oss_ingest.py` | `W/ai-tracker/downstream-2026-10-16/post_oss_ingest.py` | Orchestrator | POST one SYSTEM_DESIGN.md plus repo star data to oss-projects-ingest; refuses to post twice | Manual, after a cloud agent writes SYSTEM_DESIGN.md (skill oss-system-design-exploration) | in: SYSTEM_DESIGN.md, *-stars.json; out: oss-ingest-response.json | Supabase edge fn oss-projects-ingest (OSS_INGEST_TOKEN read from a box credential file) |
| `downstream/oss-system-design/post_oss_ingest_v2.py` | `W/ai-tracker/downstream-2026-10-06/post_oss_ingest_v2.py` | Orchestrator | Earlier variant of the OSS ingest poster (2026-10-06) | Manual (one-off) | same | Supabase edge fn oss-projects-ingest |
| `downstream/paper-gen/run_papergen.py` | `W/ai-tracker/downstream-2026-10-19/run_papergen.py` | Orchestrator | Submit the day's Top 10 arXiv papers to paper-gen and poll the jobs (they land as drafts awaiting approval) | Manual; run by the Orchestrator during the ~08:19 Top 10 routine (dated copy per day) | in: hard-coded {slug: arxiv url}; out: <slug>.job.json, <slug>.draft.md, jobs.json | Supabase edge fn paper-gen-ingest (PAPER_GEN_TOKEN) |
| `downstream/paper-gen/run_papergen2.py` | `W/ai-tracker/downstream-2026-10-06/run_papergen2.py` | Orchestrator | Second paper-gen batch for 2026-10-06 (same logic, different paper list) | Manual (one-off) | same as run_papergen.py | Supabase edge fn paper-gen-ingest |
| `downstream/perplexity/examples/perplexity-query-2026-10-19.txt` | `W/ai-tracker/downstream-2026-10-19/perplexity-query.txt` | Orchestrator | Example Perplexity Search prompt for TL;DRs of non-paper Top 10 items | Top 10 routine via skill start-a-search-session-in-blog-investigations (browser session, no script) | prompt; answer saved to perplexity-answer.md | Perplexity (browser) |
| `downstream/tracker-ingest/build_cards.py` | `W/ai-tracker/ingest-2026-10-16/build_cards.py` | Orchestrator | Build cards.json + week.json from tldrs.md / perplexity-answer.md and hand-written card data; stops while any PENDING remain | Manual, per day (copy edited each day; no copy for 10-19, so those cards were built inline) | in: ../downstream-<date>/tldrs.md, perplexity-answer.md; out: cards.json, week.json | none (local) |
| `downstream/tracker-ingest/examples/cards-2026-10-19.json` | `W/ai-tracker/ingest-2026-10-19/cards.json` | Orchestrator | Example card payload (21 cards) | - | example | - |
| `downstream/tracker-ingest/examples/week-2026-10-19.json` | `W/ai-tracker/ingest-2026-10-19/week.json` | Orchestrator | Example week pack (week_start 2026-10-19) | - | example | - |
| `downstream/tracker-ingest/post_ingest.py` | `W/ai-tracker/ingest-2026-10-19/post_ingest.py` | Orchestrator | POST cards.json to tracker-cards-ingest and week.json to tracker-weeks-ingest; refuses if PENDING remains | Manual, end of the Top 10 routine downstream | in: cards.json, week.json; out: cards-responses.json, week-response.json | Supabase edge fn tracker-cards-ingest / tracker-weeks-ingest (TRACKER_INGEST_TOKEN) |

**`downstream/oss-system-design/history/`**: 2 older per-day copies of the scripts above, from downstream-2026-10-06, downstream-2026-10-08. Each was copied from `W/<that dir>/`. They are kept so the duplication and drift are visible. Diff them against the latest copy.

**`downstream/paper-gen/history/`**: 10 older per-day copies of the scripts above, from downstream-2026-10-05, downstream-2026-10-06, downstream-2026-10-07, downstream-2026-10-08, downstream-2026-10-09, downstream-2026-10-12, downstream-2026-10-13, downstream-2026-10-14, downstream-2026-10-15, downstream-2026-10-16. Each was copied from `W/<that dir>/`. They are kept so the duplication and drift are visible. Diff them against the latest copy.

**`downstream/tracker-ingest/history/`**: 17 older per-day copies of the scripts above, from ingest-2026-10-06, ingest-2026-10-07, ingest-2026-10-08, ingest-2026-10-09, ingest-2026-10-12, ingest-2026-10-13, ingest-2026-10-14, ingest-2026-10-15, ingest-2026-10-16. Each was copied from `W/<that dir>/`. They are kept so the duplication and drift are visible. Diff them against the latest copy.

## hf-github-tracker/

| Bundle path | Original box path | Bot | What it does | Trigger | Inputs / outputs | External services |
|---|---|---|---|---|---|---|
| `hf-github-tracker/daily-builders/tmp-2026-10-05/cls.py` | `W/ai-tracker/tmp-2026-10-05/cls.py` | Huggingface & Github Tracker | Hand-written paper-id-to-category map for 2026-10-05 | Manual (per day) | python dict | none |
| `hf-github-tracker/daily-builders/tmp-2026-10-05/write.py` | `W/ai-tracker/tmp-2026-10-05/write.py` | Huggingface & Github Tracker | Write <date>-hf-daily-papers.md, -github-trending.md, -weekday-digest.md, -group-shortlist.md from extracts plus hard-coded zh blurbs | Manual (per day) | in: <date>-papers-extract.json, github-trending.json; out: /workspace/ai-tracker/<date>-*.md | none |
| `hf-github-tracker/daily-builders/tmp-2026-10-06/cls.py` | `W/ai-tracker/tmp-2026-10-06/cls.py` | Huggingface & Github Tracker | Category map for 2026-10-06 | Manual | dict | none |
| `hf-github-tracker/daily-builders/tmp-2026-10-06/write.py` | `W/ai-tracker/tmp-2026-10-06/write.py` | Huggingface & Github Tracker | Daily markdown writer for 2026-10-06 (same pattern) | Manual | same | none |
| `hf-github-tracker/daily-builders/tmp-2026-10-14/build.py` | `W/ai-tracker/tmp-2026-10-14/build.py` | Huggingface & Github Tracker | Latest all-in-one daily builder (HF Daily Papers + GitHub Trending into the four markdown outputs) | Manual (07:00 collector run) | in: papers-extract, /tmp/t/gh.json; out: <date>-*.md | huggingface.co/api/daily_papers, github.com/trending (fetched beforehand) |
| `hf-github-tracker/examples/last_run_meta.txt` | `W/ai-tracker/last_run_meta.txt` | Huggingface & Github Tracker | Example run metadata (issue, counts, snapshot time) | - | example | - |
| `hf-github-tracker/routines/README.md` | `(written for this bundle)` | Huggingface & Github Tracker | Placeholder: routine not on the box | - | - | - |
| `hf-github-tracker/steps-2026-10-19/jev_topic.py` | `W/ai-tracker/steps-1019/jev_topic.py` | Huggingface & Github Tracker | v1 of the Jev topic classifier (2026-10-19) | Manual | same | api.typesafe.ai (JEV_API_KEY) |
| `hf-github-tracker/steps-2026-10-19/jev_topic_v2.py` | `W/ai-tracker/steps-1019/jev_topic_v2.py` | Huggingface & Github Tracker | v2 classifier with stricter "main contribution" instructions (same as tools/jev_topic_filter.py) | Manual | same | api.typesafe.ai |
| `hf-github-tracker/steps-2026-10-19/run_curated_1019.py` | `W/ai-tracker/steps-1019/run_curated_1019.py` | Huggingface & Github Tracker | Run paper_review.curated on the 10-19 curation and write review HTML | Manual | in: step1/2/3 json; out: review-out/review-2026-10-19.html | Command Code CLI (deepseek-v4-flash) |
| `hf-github-tracker/steps-2026-10-19/step2.py` | `W/ai-tracker/steps-1019/step2.py` | Huggingface & Github Tracker | Keep core-topic papers using a HAND-LABELLED id-to-topic dict, sort by upvotes, cut to top 20 | Manual | in: step1.json; out: step2.json, step3.json | none |
| `hf-github-tracker/template/html_render.v1.py` | `W/ai-tracker/template/html_render.v1.py` | Huggingface & Github Tracker | Snapshot of paper_review/html_render.py (self-contained review HTML, images inlined) | Imported by paper_review | - | none |
| `hf-github-tracker/tools/jev_topic_filter.py` | `W/ai-tracker/tools/jev_topic_filter.py` | Huggingface & Github Tracker | Classify HF papers into topics with the Jev (typesafe.ai systemone) choice API, in parallel | Manual, during the daily HF curation | in: step1-style rows JSON; out: topic/confidence per paper | api.typesafe.ai (JEV_API_KEY) |
| `hf-github-tracker/tools/paper_extract.py` | `W/ai-tracker/tools/paper_extract.py` | Huggingface & Github Tracker | Cached arXiv full-text + figure extractor (HTML, then ar5iv, then e-print, then PDF, then abstract) | Manual / called during the daily HF curation (duplicate copy also at /workspace/cloud-handoff/partial_paper_extract.py) | in: arxiv id; out: /workspace/ai-tracker/papers/<id>/ (PAPERS_CACHE) | arxiv.org, ar5iv |

**`hf-github-tracker/paper_review/`** (35 files) from `W/paper_review/paper_review/` (git origin `johnnysflolz/tmp-8b2fc94ce23eb19c`). Owner: Huggingface & Github Tracker. A Python package for the weekday HF paper review: take the curation JSON, keep papers with full text and a real figure, run a 3-step LLM card (extract → critique → write) through the Command Code CLI (`${COMMAND_CODE_API_KEY}`, model deepseek-v4-flash; mock runner by default), then render one self-contained HTML page. Entry point: `python -m paper_review run --curation … --date … --runner mock|command_code`, or `curated.run_curated` (see steps-2026-10-19/run_curated_1019.py). It has tests under `tests/`. Excluded: .venv, .cache, artifacts/ (5.4MB), egg-info.

- `hf-github-tracker/paper_review/.gitignore`
- `hf-github-tracker/paper_review/README.md`
- `hf-github-tracker/paper_review/config/README.md`
- `hf-github-tracker/paper_review/config/defaults.json`
- `hf-github-tracker/paper_review/paper_review/__init__.py`
- `hf-github-tracker/paper_review/paper_review/__main__.py`
- `hf-github-tracker/paper_review/paper_review/arxiv_id.py`
- `hf-github-tracker/paper_review/paper_review/cli.py`
- `hf-github-tracker/paper_review/paper_review/config.py`
- `hf-github-tracker/paper_review/paper_review/curated.py`
- `hf-github-tracker/paper_review/paper_review/extract.py`
- `hf-github-tracker/paper_review/paper_review/figures.py`
- `hf-github-tracker/paper_review/paper_review/html_render.py`
- `hf-github-tracker/paper_review/paper_review/intake.py`
- `hf-github-tracker/paper_review/paper_review/llm/__init__.py`
- `hf-github-tracker/paper_review/paper_review/llm/base.py`
- `hf-github-tracker/paper_review/paper_review/llm/command_code.py`
- `hf-github-tracker/paper_review/paper_review/llm/flow.py`
- `hf-github-tracker/paper_review/paper_review/llm/mock.py`
- `hf-github-tracker/paper_review/paper_review/llm/prompts.py`
- `hf-github-tracker/paper_review/paper_review/models.py`
- `hf-github-tracker/paper_review/paper_review/pipeline.py`
- `hf-github-tracker/paper_review/paper_review/screenshot.py`
- `hf-github-tracker/paper_review/paper_review/select.py`
- `hf-github-tracker/paper_review/pyproject.toml`
- `hf-github-tracker/paper_review/samples/2026-10-19-papers-curation.json`
- `hf-github-tracker/paper_review/tests/fixtures/sample_arxiv.html`
- `hf-github-tracker/paper_review/tests/test_arxiv_id.py`
- `hf-github-tracker/paper_review/tests/test_command_code.py`
- `hf-github-tracker/paper_review/tests/test_curated.py`
- `hf-github-tracker/paper_review/tests/test_e2e.py`
- `hf-github-tracker/paper_review/tests/test_embed.py`
- `hf-github-tracker/paper_review/tests/test_figures.py`
- `hf-github-tracker/paper_review/tests/test_intake.py`
- `hf-github-tracker/paper_review/tests/test_select.py`

## linkedin/

| Bundle path | Original box path | Bot | What it does | Trigger | Inputs / outputs | External services |
|---|---|---|---|---|---|---|
| `linkedin/feed-probe/continue_feed.py` | `W/linkedin-feed-probe/continue_feed.py` | Linkedln Control Agent | Continue scrolling the feed dump without leaving /feed/ | Manual | same | LinkedIn |
| `linkedin/feed-probe/copy_link_probe.py` | `W/linkedin-feed-probe/copy_link_probe.py` | Linkedln Control Agent | Validate the "expand text + Copy link to post" UX | Manual | same | LinkedIn |
| `linkedin/feed-probe/dump_dom.py` | `W/linkedin-feed-probe/dump_dom.py` | Linkedln Control Agent | Dump feed DOM for selector work | Manual | DOM dumps | LinkedIn |
| `linkedin/feed-probe/extract_feed.py` | `W/linkedin-feed-probe/extract_feed.py` | Linkedln Control Agent | Pre-agent-track probe: extract about 20 home-feed cards from the live LinkedIn DOM with Playwright | Manual (prototype) | in: persistent Chromium profile; out: /workspace/linkedin-feed-probe/*.json | LinkedIn (browser) |
| `linkedin/feed-probe/probe.py` | `W/linkedin-feed-probe/probe.py` | Linkedln Control Agent | Standalone feed DOM probe (prototype) | Manual | same | LinkedIn |
| `linkedin/routines/linkedin-feed-digest-weekdays-0700.md` | `AD/agents/92c8220f-…/automations/linkedin-feed-digest-weekdays/automation.json` | Linkedln Control Agent | Weekday LinkedIn feed digest routine prompt (runs agent-track) | Cron 0 7 * * 1-5 HKT | - | LinkedIn, Notion (on request) |

**`linkedin/agent-track/`** (16 files) from `W/agent-track/` (git origin `johnnysflolz/agent-track`). Owner: Linkedln Control Agent. Playwright CLI `agent-track feed digest` that scrolls the LinkedIn home feed with a persistent Chromium profile and writes `data/feed/daily/<date>.json` (collector.py, parse.py, selectors.py, io.py). The 07:00 routine runs it. It has tests under `tests/`. Excluded: data/ (1.4GB, includes the browser profile), .venv, .git.

- `linkedin/agent-track/.gitignore`
- `linkedin/agent-track/README.md`
- `linkedin/agent-track/pyproject.toml`
- `linkedin/agent-track/src/agent_track/__init__.py`
- `linkedin/agent-track/src/agent_track/__main__.py`
- `linkedin/agent-track/src/agent_track/cli.py`
- `linkedin/agent-track/src/agent_track/services/__init__.py`
- `linkedin/agent-track/src/agent_track/services/feed/__init__.py`
- `linkedin/agent-track/src/agent_track/services/feed/collector.py`
- `linkedin/agent-track/src/agent_track/services/feed/io.py`
- `linkedin/agent-track/src/agent_track/services/feed/parse.py`
- `linkedin/agent-track/src/agent_track/services/feed/selectors.py`
- `linkedin/agent-track/tests/test_cli.py`
- `linkedin/agent-track/tests/test_parse.py`
- `linkedin/agent-track/tests/test_selectors.py`
- `linkedin/agent-track/uv.lock`

## social-media-watchlist/

| Bundle path | Original box path | Bot | What it does | Trigger | Inputs / outputs | External services |
|---|---|---|---|---|---|---|
| `social-media-watchlist/reddit-digest/README-praw.md` | `AD/agents/e1526572-c99f-40f7-8b90-cfa2af9df428/reddit/README.md` | Social Media Watchlist | PRAW setup + rate-limit note | - | doc | Reddit |
| `social-media-watchlist/reddit-digest/build.py` | `W/reddit-digest/build.py` | Social Media Watchlist | Pull top posts from 13 AI subreddits with PRAW (paced to 100 calls/min), write JSON + HTML | Manual / as part of the morning run (source for Reddit TRICKS) | out: /workspace/reddit-digest/reddit-top5-<date>.json/.html | Reddit API (REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET) |
| `social-media-watchlist/reddit-digest/examples/reddit-top5-2026-10-19.json` | `W/reddit-digest/reddit-top5-2026-10-19.json` | Social Media Watchlist | Example Reddit digest JSON | - | example | - |
| `social-media-watchlist/reddit-digest/render.py` | `W/reddit-digest/render.py` | Social Media Watchlist | Render the Reddit digest HTML (optional editorial highlights) | Called by build.py | in: digest JSON, DIGEST_EDITORIAL; out: html | none |
| `social-media-watchlist/routines/routine-prompt-current.md` | `W/x-watchlist/routine-prompt-current.md` | Social Media Watchlist | CURRENT weekday X watchlist routine prompt (posts KEEP/RADAR to the group) | Routine, weekdays ~07:00 HKT | - | X, Grok Bot group |
| `social-media-watchlist/routines/routine-prompt-dual-run.md` | `W/x-watchlist/routine-prompt-dual-run.md` | Social Media Watchlist | Old dual-run (free vs paid) routine prompt | Retired (10-09 to 10-14 trial) | - | X |
| `social-media-watchlist/routines/routine-prompt-free-primary.md` | `W/x-watchlist/routine-prompt-free-primary.md` | Social Media Watchlist | Free-primary routine prompt draft | Superseded | - | X |
| `social-media-watchlist/x-watchlist/DEFAULT_BACKFILL.md` | `W/x-watchlist/DEFAULT_BACKFILL.md` | Social Media Watchlist | By-ID backfill rule doc | - | doc | - |
| `social-media-watchlist/x-watchlist/MODE.md` | `W/x-watchlist/MODE.md` | Social Media Watchlist | Poll-mode note (free reads primary, paid on demand) | - | doc | - |
| `social-media-watchlist/x-watchlist/config/x-watchlist-accounts.json` | `W/x-watchlist-accounts.json` | Social Media Watchlist | Watchlist account list (config) | - | config | - |
| `social-media-watchlist/x-watchlist/examples/morning-brief-2026-10-19.json` | `W/x-watchlist/morning-brief-2026-10-19.json` | Social Media Watchlist | Example morning brief | - | example | - |
| `social-media-watchlist/x-watchlist/merge_backfill.py` | `W/x-watchlist/merge_backfill.py` | Social Media Watchlist | Merge note_tweet full-text backfill reads into the poll progress | Manual during the 07:00 routine | raw-<date>/progress.json | X |
| `social-media-watchlist/x-watchlist/merge_backfill_weekly.py` | `W/x-watchlist/merge_backfill_weekly.py` | Social Media Watchlist | Weekly backfill merge | Manual | raw-weekly-<date>/ | X |
| `social-media-watchlist/x-watchlist/parse_x.py` | `W/x-watchlist/parse_x.py` | Social Media Watchlist | Parse a dumped X tool result + remaining-quota footer | Imported by savefree.sh | in: dump file | - |
| `social-media-watchlist/x-watchlist/poll_one.py` | `W/x-watchlist/poll_one.py` | Social Media Watchlist | Normalize one get_users_posts dump into posts + quota | Manual during the daily poll | in: dump; out: stdout JSON | - |
| `social-media-watchlist/x-watchlist/save_poll.py` | `W/x-watchlist/save_poll.py` | Social Media Watchlist | Save per-account poll dumps into raw-<date>/progress.json (daily) | Manual during the 07:00 routine | in: /workspace/agent-tools/*.txt dumps; out: raw-<date>/ | X (built-in free reads) |
| `social-media-watchlist/x-watchlist/save_poll_weekly.py` | `W/x-watchlist/save_poll_weekly.py` | Social Media Watchlist | Same, for the weekly run | Manual | raw-weekly-<date>/ | X |
| `social-media-watchlist/x-watchlist/savefree.sh` | `W/x-watchlist/savefree.sh` | Social Media Watchlist | Dual-run helper: copy a free-read dump and print the parse (2026-10-14 trial) | Manual (trial) | dual-run-raw/ | X |

## blog-investigations/

| Bundle path | Original box path | Bot | What it does | Trigger | Inputs / outputs | External services |
|---|---|---|---|---|---|---|
| `blog-investigations/blog-watch-build/build_cards.py` | `W/blog-watch-build/build_cards.py` | Blog Investigations | Original bulk builder for blog-watch cards/weeks (early September) + ingest | Manual (one-off bootstrap) | blog-watch/ | Supabase edge fn tracker-cards-ingest |
| `blog-investigations/blog-watch/FETCH-STRATEGIES.md` | `AD/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch/FETCH-STRATEGIES.md` | Blog Investigations | Per-source fetch strategy notes | - | doc | - |
| `blog-investigations/blog-watch/PLAN-ai-trend-tracker.md` | `AD/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch/PLAN-ai-trend-tracker.md` | Blog Investigations | Original tracker plan + ingest contract | - | doc | - |
| `blog-investigations/blog-watch/README.json` | `AD/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch/README.json` | Blog Investigations | Store layout / schema description | - | doc | - |
| `blog-investigations/blog-watch/index.json` | `AD/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch/index.json` | Blog Investigations | Source registry + fetch_policy tiers (config) | - | config | - |
| `blog-investigations/blog-watch/samples/gpt-6-astra-benchmark-comparisons.json` | `AD/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch/samples/gpt-6-astra-benchmark-comparisons.json` | Blog Investigations | Sample card/week JSON (example data) | - | example | - |
| `blog-investigations/blog-watch/samples/gpt-6-astra-pricing.json` | `AD/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch/samples/gpt-6-astra-pricing.json` | Blog Investigations | Sample card/week JSON (example data) | - | example | - |
| `blog-investigations/blog-watch/samples/poolside-sample.json` | `AD/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch/samples/poolside-sample.json` | Blog Investigations | Sample card/week JSON (example data) | - | example | - |
| `blog-investigations/blog-watch/samples/week-2026-09-03-orientations.json` | `AD/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch/samples/week-2026-09-03-orientations.json` | Blog Investigations | Sample card/week JSON (example data) | - | example | - |
| `blog-investigations/blog-watch/samples/week-2026-09-03-sample.json` | `AD/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch/samples/week-2026-09-03-sample.json` | Blog Investigations | Sample card/week JSON (example data) | - | example | - |
| `blog-investigations/daily-scan/fetch_all.py` | `W/blog-scan-2026-10-19/fetch_all.py` | Blog Investigations | Fetch all tier-1/2 sources (RSS, changelogs, HF/OpenRouter APIs) in parallel into the day's scan dir | Routine 06:00 HKT weekdays (dated copy per day) | out: /workspace/blog-scan-<date>/raw/* | ~40 vendor blogs/changelogs, huggingface.co/api, openrouter.ai/api |
| `blog-investigations/daily-scan/h2t.py` | `W/blog-scan-2026-10-14/h2t.py` | Blog Investigations | Tiny HTML-to-text helper | Imported | - | - |
| `blog-investigations/daily-scan/ingest.py` | `W/blog-scan-2026-10-14/ingest.py` | Blog Investigations | POST new/updated cards + week pack to the tracker site (skips if token unset) | 06:00 routine | out: weeks/<date>-ingest-result.json | Supabase edge fn tracker-cards-ingest / tracker-weeks-ingest (TRACKER_INGEST_TOKEN) |
| `blog-investigations/daily-scan/links.py` | `W/blog-scan-2026-10-14/links.py` | Blog Investigations | Diff listing links against known source posts to find new URLs | 06:00 routine | blog-watch/sources/*.json | - |
| `blog-investigations/daily-scan/merge_tier3.py` | `W/blog-scan-2026-10-06/merge_tier3.py` | Blog Investigations | Copy of the tier-3 merge kept in the daily-scan dir (2026-10-06) | Manual | see tier3/ | - |
| `blog-investigations/daily-scan/parse_rss.py` | `W/blog-scan-2026-10-14/parse_rss.py` | Blog Investigations | Parse fetched RSS/Atom into dated posts in the scan window (HKT) | 06:00 routine | raw/ to posts json | - |
| `blog-investigations/daily-scan/posts_data.py` | `W/blog-scan-2026-10-14/posts_data.py` | Blog Investigations | HAND-WRITTEN list of the day's new posts + card fields (rewritten daily) | 06:00 routine | python data | - |
| `blog-investigations/daily-scan/update_existing.py` | `W/blog-scan-2026-10-14/update_existing.py` | Blog Investigations | Recheck needs_verification cards and update them | 06:00 routine | cards/*.json | vendor pages |
| `blog-investigations/daily-scan/upsert_and_cards.py` | `W/blog-scan-2026-10-14/upsert_and_cards.py` | Blog Investigations | Upsert posts into blog-watch/sources by URL and write cards/*.json | 06:00 routine | out: blog-watch/sources, cards, cards_meta.json | - |
| `blog-investigations/daily-scan/upsert_merge.py` | `W/blog-scan-2026-10-15/upsert_merge.py` | Blog Investigations | Newer (10-15) combined upsert of phase-1 + tier-3 cards | 06:00 routine | same | - |
| `blog-investigations/daily-scan/weeks_update.py` | `W/blog-scan-2026-10-14/weeks_update.py` | Blog Investigations | Add cards to weeks/<monday>.json pack with type summaries | 06:00 routine | weeks/*.json | - |
| `blog-investigations/daily-scan/write_summary.py` | `W/blog-scan-2026-10-14/write_summary.py` | Blog Investigations | Write scan-summary JSON + zh digest markdown for Johnny | 06:00 routine | weeks/<date>-scan-summary.json, -digest-zh.md | - |
| `blog-investigations/routines/weekday-blog-scan-0600.md` | `AD/agents/4835c489-…/automations/blog-tracker/automation.json` | Blog Investigations | Weekday blog scan routine prompt | Cron 0 6 * * 1-5 HKT | - | - |
| `blog-investigations/routines/weekly-blog-rollup-mon-0910.md` | `AD/agents/4835c489-…/automations/ai-blog/automation.json` | Blog Investigations | Monday weekly rollup routine prompt | Cron 10 9 * * 1 HKT | - | - |
| `blog-investigations/tier3/finalize_summary.py` | `W/blog-tier3-2026-10-08/finalize_summary.py` | Blog Investigations | Finalize the scan summary + digest after tier-3 | Manual | weeks/<date>-scan-summary.json | - |
| `blog-investigations/tier3/ingest_tier3.py` | `W/blog-tier3-2026-10-08/ingest_tier3.py` | Blog Investigations | POST tier-3 cards/week | Manual | - | Supabase edge fn tracker ingest (TRACKER_INGEST_TOKEN) |
| `blog-investigations/tier3/merge_tier3.orig.py` | `W/blog-tier3-2026-10-06/merge_tier3.orig.py` | Blog Investigations | Original version before the 10-06 edit | - | - | - |
| `blog-investigations/tier3/merge_tier3.py` | `W/blog-tier3-2026-10-08/merge_tier3.py` | Blog Investigations | Merge browser-pass listings for tier-3 sources (perplexity, meta-ai, snowflake, qwen, microsoft-ai) into sources/ | Manual, after a browser pass (phase 2 of the scan) | in: browser-listings.json | browser |
| `blog-investigations/tier3/weeks_update.py` | `W/blog-tier3-2026-10-05/weeks_update.py` | Blog Investigations | Week-pack update for tier-3 cards | Manual | weeks/ | - |
| `blog-investigations/tier3/write_cards.py` | `W/blog-tier3-2026-10-08/write_cards.py` | Blog Investigations | Tier-3 card writer template (fill CARDS, then run) | Manual | cards/, sources/, weeks/ | - |
| `blog-investigations/tier3/write_cards.template.py` | `W/blog-tier3-2026-10-08/backup/write_cards.template.py` | Blog Investigations | Backup template of write_cards | - | - | - |

**`blog-investigations/daily-scan/history/`**: 69 older per-day copies of the scripts above, from blog-scan-2026-10-02, blog-scan-2026-10-05, blog-scan-2026-10-06, blog-scan-2026-10-07, blog-scan-2026-10-08, blog-scan-2026-10-09, blog-scan-2026-10-12, blog-scan-2026-10-13, blog-scan-2026-10-14, blog-scan-2026-10-15, blog-scan-2026-10-16. Each was copied from `W/<that dir>/`. They are kept so the duplication and drift are visible. Diff them against the latest copy.

**`blog-investigations/tier3/history/`**: 11 older per-day copies of the scripts above, from blog-tier3-2026-10-05, blog-tier3-2026-10-06, blog-tier3-2026-10-07. Each was copied from `W/<that dir>/`. They are kept so the duplication and drift are visible. Diff them against the latest copy.

## skills/

| Bundle path | Original box path | Bot | What it does | Trigger | Inputs / outputs | External services |
|---|---|---|---|---|---|---|
| `skills/ai-tracker-blog-filter/SKILL.md` | `AD/workflows/ai-tracker-blog-filter/SKILL.md` | Blog Investigations | Skill "ai-tracker-blog-filter": rules the bot follows (no code) | Loaded by the bot when relevant | - | - |
| `skills/ai-tracker-editorial-orchestrator/SKILL.md` | `AD/workflows/ai-tracker-editorial-orchestrator/SKILL.md` | Orchestrator | Skill "ai-tracker-editorial-orchestrator": rules the bot follows (no code) | Loaded by the bot when relevant | - | - |
| `skills/ai-tracker-github-daily-trending/SKILL.md` | `AD/workflows/ai-tracker-github-daily-trending/SKILL.md` | Huggingface & Github Tracker | Skill "ai-tracker-github-daily-trending": rules the bot follows (no code) | Loaded by the bot when relevant | - | - |
| `skills/ai-tracker-hugging-face-daily-papers/SKILL.md` | `AD/workflows/ai-tracker-hugging-face-daily-papers/SKILL.md` | Huggingface & Github Tracker | Skill "ai-tracker-hugging-face-daily-papers": rules the bot follows (no code) | Loaded by the bot when relevant | - | - |
| `skills/ai-tracker-linkedin-filter/SKILL.md` | `AD/workflows/ai-tracker-linkedin-filter/SKILL.md` | Linkedln Control Agent | Skill "ai-tracker-linkedin-filter": rules the bot follows (no code) | Loaded by the bot when relevant | - | - |
| `skills/ai-tracker-x-filter/SKILL.md` | `AD/workflows/ai-tracker-x-filter/SKILL.md` | Social Media Watchlist | Skill "ai-tracker-x-filter": rules the bot follows (no code) | Loaded by the bot when relevant | - | - |
| `skills/oss-system-design-exploration/SKILL.md` | `AD/workflows/oss-system-design-exploration/SKILL.md` | Orchestrator (downstream) | Skill "oss-system-design-exploration": rules the bot follows (no code) | Loaded by the bot when relevant | - | - |
| `skills/start-a-search-session-in-blog-investigations/SKILL.md` | `AD/workflows/start-a-search-session-in-blog-investigations/SKILL.md` | Orchestrator / Blog Investigations | Skill "start-a-search-session-in-blog-investigations": rules the bot follows (no code) | Loaded by the bot when relevant | - | - |

## Not found on the box

- **Orchestrator routines** (`ai-tracker-weekday-highlights` 08:15, `ai-tracker-weekday-top-10` ~08:19): stored server-side. See `orchestrator/routines/README.md` (reconstructed).
- **Huggingface & Github Tracker routine prompt**: not on the box.
- **HTML digest generator**: no script. The HTML is written inline by the Orchestrator each day. Only an example output is included.
- **Notion row writes and the Perplexity session**: no scripts. They run through the Notion MCP and a browser session, so only examples are included.
- Not part of AI Tracker, so excluded: /workspace/post_archive.py (Audio Transcriber), probe_left_rail.py and career-job-applications (LinkedIn job search), transcripts/w.py, Tesla digest scripts.

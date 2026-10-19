# AI Trend Tracker — Plan

Status: draft  
Owner: Blog Investigations (Grok Bot) + Johnny  
Updated: 2026-09-15 (HKT) — priority v2

## Goal

Turn the existing blog-watch pipeline into a **Card-based AI Trend Tracker** that:
1. Maps each post to a reusable **Card**
2. Produces a **weekly digest by type**
3. Supports a future **personal site** (same JSON cards)
4. Later adds **rolling cross-week trends**

## Card schema (v1)

```json
{
  "id": "kebab-or-hash",
  "title": "string",
  "url": "https://...",
  "source": "Org / Channel",
  "published_at": "2026-09-03T00:00:00+08:00",
  "relative_time": "3d",
  "type": "research | engineering | application_case_study | model_release_benchmark | model_release_implementation | changelog_bugfix | changelog_feature | changelog_refactor",
  "priority": "P0 | P1 | P2 | P3",
  "tags": ["agents", "memory"],
  "key_takeaway": [
    "factual bullet 1",
    "factual bullet 2"
  ],
  "metrics": null,
  "first_seen": "2026-09-10",
  "last_seen": "2026-09-11"
}
```

### `metrics` (OPTIONAL — only for model_release_* when published)

Omit the `metrics` key entirely when pricing/benchmarks are unpublished. Never invent.

Ingest: `https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1/tracker-cards-ingest` and `.../tracker-weeks-ingest` with `Authorization: Bearer TRACKER_INGEST_TOKEN`.


```json
{
  "pricing": {
    "currency": "USD",
    "unit": "per_1M_tokens",
    "input": 10.0,
    "output": 50.0,
    "cached_input": 1.0,
    "cache_writes": 12.5,
    "tiers_note": "standard short-context; see source",
    "source_url": "https://platform.openai.com/docs/pricing"
  },
  "benchmarks": [
    {
      "name": "Terminal-Bench 4.0",
      "scores": { "gpt-6-astra": "57.9%", "claude-fable-5.1": "55.8%" },
      "delta": "Astra +2.1pp vs Fable 5.1",
      "source_url": "https://openai.com/index/gpt-6-astra/",
      "caveat": "OpenAI comparison table; harness/version may differ elsewhere"
    }
  ]
}
```

If pricing/benchmarks unpublished → omit numbers, set `"status": "unpublished"` — never invent.

### Priority rules (v2 — see skill [ai-tracker-blog-filter](sand-workflow:ai-tracker-blog-filter))

| Priority | When |
|---|---|
| **P0** | Enough evidence AND at least one of: (1) consequential model release (capability/efficiency/access/deployment trade-off) with comparable benchmarks or technical substance — not brand alone; (2) agent-enhancing changelog that changes execution, state/memory, tools, coordination, computer use, self-hosting, recovery, or reliability; (3) major application pattern (new API/workflow/system mode) that changes builder decisions. Price is neither required nor sufficient for P0. |
| **P1** | Solid engineering method / measured improvement / valuable vertical app / important research below P0 impact / *potential* P0 not yet fully evidenced |
| **P2** | Small incremental, narrow applicability, or weak user relevance |
| **P3** | Routine bugfix, pure PR/funding, empty promo, low-signal — except serious security/data-loss/breaking issues, which are re-rated by impact |

### Type notes

- `changelog_feature`: agent-enhancing functionality only — **exclude** mere model-picker adds / effort-level adds
- `application_case_study`: list concrete usages (memory retrieval, RAG, TTS, enterprise bots, DE agents, …)
- `engineering`: list techniques (inference opt, sandbox, EPD, routing, kernels, …)
- `model_release_benchmark`: proprietary focus; require pricing + 1–2 famous benchmarks with peer deltas when available
- `model_release_implementation`: arch components + inference opts (speculative decoding, …)
- `research`: keep for storage/site filters; weekly digest can de-prioritize unless high transfer

## Storage layout

```
blog-watch/
  PLAN-ai-trend-tracker.md          # this plan
  README.json                       # schema + rules
  index.json                        # source registry
  sources/<source-id>.json          # per-source raw upsert (existing)
  cards/<card-id>.json              # one Card per post (new)
  weeks/YYYY-MM-DD.json             # weekly pack: synthesis + cards by type (new)
  samples/                          # demos
```

Upsert key: `url` (plus `title` when changelog URLs collide).

## Pipeline (weekly)

1. **Fetch** all sources (equal priority)
2. **Cardize** each new/updated post (type, priority, takeaways, tags, metrics)
3. **Upsert** `sources/*.json` + `cards/*.json`
4. **Weekly pack** `weeks/YYYY-MM-DD.json`:
   - cross-link synthesis (short)
   - for each type with cards: type summary + ordered cards (P0→P3)
5. **Deliver** Traditional Chinese digest in chat (and keep machine-readable JSON for site)
6. **(Phase 2)** Rolling trends from last 4–8 weeks of cards

## Phased delivery

### Phase 0 — Lock schema (this week)
- [ ] Finalize Card JSON schema in `README.json`
- [ ] Priority + type rules written and agreed
- [ ] Migrate existing seeded posts → sample Cards (incl. Astra P0 with pricing + 2 benchmarks)
- [ ] One example `weeks/2026-09-03.json` pack

### Phase 1 — Weekly Card digest (next 1–2 weeks)
- [ ] Update Monday routine to emit Cards + weekly pack
- [ ] Chat digest = by-type summaries + P0/P1 highlights
- [ ] Filter changelog noise (no model-only adds)
- [ ] Persist pricing/benchmark metrics when official

### Phase 2 — Personal site feed
- [ ] Stable public-ish export path or copy of `cards/` + `weeks/` Johnny can fetch
- [ ] Document fields for frontend (relative_time computed at render if needed)
- [ ] Optional: RSS/JSON endpoint later

### Phase 3 — Rolling AI Trend layer
- [ ] Cross-week theme detection (rising / flat / new) from tags + types
- [ ] Model board time series ($/MTok + benchmark deltas)
- [ ] Engineering usage board (technique inventory)

## Non-goals (for now)

- Scraping paywalled content
- Invented benchmarks or prices
- Full research literature coverage beyond watchlist
- Building the personal site UI in this bot (export Cards only)

## Success criteria

- Every watchlist hit becomes a Card within the weekly run
- Weekly pack opens with synthesis; each type that has cards has a short summary
- P0 cards always have enough fact for a decision (price and/or benchmark delta and/or clear capability)
- Same Cards render in chat digest and (later) personal site without remapping

## Immediate next step

After plan approval: implement Phase 0 (schema + migrate sample Cards + one week pack).

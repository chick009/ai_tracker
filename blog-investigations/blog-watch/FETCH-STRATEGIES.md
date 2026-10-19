# Blog-watch fetch strategies

Updated: 2026-10-19T17:50:00+08:00

Every source has `fetch_tier` + `fetch` in `index.json`.

## Three tiers

| Tier | When | How |
|------|------|-----|
| **1 curl** | Listing HTTP 200, no fresh feed | `curl` / WebFetch listing URL. If empty/unparseable → browser fallback. |
| **2 RSS / sitemap** | Fresh RSS/Atom or useful sitemap | Fetch `fetch.alt_urls` first, upsert by URL; then HTML; browser only if still empty. |
| **3 browser** | Cloudflare / empty-stale feed / CSR-only / **prior 403** | box Chromium via **computerUse** (never Shell Playwright/CDP). |

## Permanent promote on 403 (Johnny 2026-10-19)

If curl/WebFetch returns **403 / Cloudflare / blocked** during a scan:

1. **Same run:** re-fetch that URL via computerUse Chromium and **supplement** the card / digest with what the browser got (do not leave the item as “403, skipped”).
2. **Permanently:** set that source’s `fetch_tier` to **3** in `index.json` (and update `fetch_policy.tier*_ids`) so **future** scans always use browser for that site — do not keep retrying curl-only.

Apply to listing pages and article bodies alike.

## Failed RSS debug (2026-10-01)

| Feed | Result |
|------|--------|
| `qwenlm.github.io/blog/index.xml` | Reachable but **stale** (newest ~2025-09) → Qwen stays **tier 3 browser** |
| `microsoft.ai/feed`, `/blog/rss` | Reachable but **0 items** → Microsoft AI **tier 3** |
| cerebras / minimax / sakana / xai / poolside / openrouter / cognition `*/rss` | **404** |
| `cursor.com/atom.xml` | Reachable but **stale** (2024-11) → ignore; Cursor stays **tier 1 curl** |
| `mistral.ai/news/rss`, `huggingface.co/blog/feed.xml`, NVIDIA `blog/feed`, Google Research atom, Liquid `sitemap.xml`, Ai2 Medium | **OK** → **tier 2** |

## Tier membership (authoritative in index.json)

- **Tier 3 (locked browser):** meta-ai, microsoft-ai, perplexity, qwen, snowflake, **codex-changelog, openai-publications, openai-news, openai-api-changelog**
- **Tier 2:** allen-ai, google-research, huggingface, liquid-engineering, liquid-models, liquid-research, mistral, nvidia-developer
- **Tier 1:** everyone else

## Do not

- Treat stale/empty RSS as success.
- Substitute `engineering.fb.com/feed` for Meta AI blog.
- Drive Chromium from Shell.
- Leave a 403 as a permanent “blocker note” without a same-run browser supplement + tier-3 promote.

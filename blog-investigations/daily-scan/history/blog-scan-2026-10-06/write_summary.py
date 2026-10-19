import json,datetime,shutil
from pathlib import Path
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-06')
NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
ins=json.load(open(W/'inserted.json')); meta=json.load(open(W/'cards_meta.json')); ws=json.load(open(W/'week_stats.json'))
ing=json.load(open(W/'ingest_result.json'))
from collections import Counter
card=lambda c: json.loads((B/'cards'/f'{c}.json').read_text())
pr={k:0 for k in ['P0','P1','P2','P3']}
for m in meta: pr[m['priority']]+=1
nps=Counter(i['source'] for i in ins); npw=Counter(i['source'] for i in ins if i['date']>='2026-10-05')
for i in ins:
    cid=next((m['id'] for m in meta if m['url']==i['url']),None)
    if cid: i['card_ref']=cid
T3=['meta-ai','microsoft-ai','perplexity','qwen','snowflake']
t1=['anthropic-research','cerebras','claude-code-changelog','codex-changelog','cognition','cursor-blog','cursor-changelog','deepseek','glm-zhipu','inco','minimax','openai-publications','opencode-changelog','openrouter','pi-changelog','poolside','sakana','salesforce','xai']
ftu={s:'tier1_curl_html' for s in t1}
ftu.update({
 'claude-code-changelog':'tier1_curl_html (+ npm registry; raw.githubusercontent CHANGELOG.md cross-check — still 2.1.289; npm next 2.1.290 has no changelog entry)',
 'codex-changelog':'tier1_curl_html (+ npm registry check; GitHub API not used)',
 'opencode-changelog':'tier1_curl_html (+ npm registry check)',
 'openrouter':'tier1_curl_html (+ openrouter.ai/blog/feed.xml used as helper, 151 items, newest 2026-10-05; tier unchanged)',
 'openai-news':'tier2_rss (posts read via curl 200 after WebFetch timeout)',
 'allen-ai':'tier2_rss_stale_then_html','google-research':'tier2_atom_stale_then_html',
 'huggingface':'tier2_rss (+ HTML listing JSON cross-check)','mistral':'tier2_rss (newest 2026-09-09) + html (no new)',
 'nvidia-developer':'tier2_atom (newest 2026-10-01) + html (no new)',
 'liquid-engineering':'tier2_sitemap_stale_lastmod_then_html','liquid-models':'tier2_sitemap_stale_lastmod_then_html (d1 found via liquid.ai/blog listing)','liquid-research':'tier2_sitemap_stale_lastmod_then_html'})
for s in T3: ftu[s]='pending_browser'
s={
 "scan_date":"2026-10-06",
 "window":"2026-10-05 ~06:00 HKT → 2026-10-06 ~06:10 HKT (posts dated 2026-10-05/06 + late 10-04 US time; catch-up of clearly missed items since ~2026-09-28 not in sources/) — PHASE 1 (tier1+tier2 only; tier-3 pending browser)",
 "phase":"phase1_tier1_tier2",
 "sources_scanned":28,
 "sources_pending_browser_merge":T3,
 "inserted_titles":[i['title'] for i in ins],
 "inserted":ins,
 "new_posts_per_source":dict(nps),
 "new_inwindow_posts_per_source_2026-10-05_plus":dict(npw),
 "cards_written":meta,
 "cards_by_priority":pr,
 "catch_up_cards":[m['id'] for m in meta if card(m['id']).get('catch_up')],
 "stored_only_not_carded":[{k:i[k] for k in ['source','title','url','date','not_carded_reason']} for i in ins if i.get('carded') is False],
 "needs_verification_cards":[m['id'] for m in meta if card(m['id']).get('needs_verification')],
 "potential_p0":[{"id":"liquid-d1-decision-model-2026-10-05","kept_as":"P1","reason":"19-200× cost / large latency gains on structured decisions, but single vendor-run 6-app comparison, no standard benchmark, Opus 5.5 ≥ d1 on all apps"}],
 "week_stats":ws,
 "week_pack_updated":True,
 "week_pack_notes":"weeks/2026-10-05.json (week_end 2026-10-11) now 8 cards (all dated 2026-10-05) → index.latest_week switched 2026-09-28 → 2026-10-05. Catch-up hf-rl-environments-hub-2026-09-28 added to weeks/2026-09-28.json (93 after Monday rollup dedupe → 94). Stats rebuilt from card files. Tier-3 merge may add more.",
 "ingest":"done",
 "ingest_reason":"TRACKER_INGEST_TOKEN set in box env this run → POSTed today's 9 cards (9/9 HTTP 200) + week 2026-10-05 body (HTTP 200). Re-ingest after tier-3 merge. Earlier weeks (09-14..09-28) were never ingested (token unset then) — not backfilled.",
 "ingest_result":{"cards_ok":ing['cards_ok'],"cards_fail":ing['cards_fail'],"week":ing['week'],"path":"weeks/2026-10-06-ingest-result.json"},
 "group_post":False,
 "digest_zh_Hant":(B/'weeks/2026-10-06-digest-zh.md').read_text(),
 "fetch_tier_used":ftu,
 "fetch_tier_summary":{
  "tier1_curl_html":"all 19 tier-1 listings HTTP 200. New: codex 0.160.1 (10-05), pi 1.0.3+1.0.4 (10-05), openrouter server-side code execution (10-05), inco Splash (09-17, store-only). No new: anthropic-research (newest 10-01), cerebras (10-01), cognition (09-25), cursor-blog (09-23), cursor-changelog (09-23), deepseek (09-10), glm-zhipu (08-26), minimax (08-13), openai-publications (09-29), opencode (1.18.34, 09-30), poolside (07-28), sakana (09-28), salesforce (09-28 marketing, not upserted), xai (09-28)",
  "tier2_rss_sitemap":"openai-news rss fresh (2 new 10-05); huggingface rss newest 10-03 + HTML JSON (catch-up RL Environments 09-28, tokenizers v1 09-21 store-only); nvidia atom newest 10-01 (no new); mistral rss newest 09-09 (stale-ish, no new); allen-ai medium STALE 2024-11 → allenai.org HTML (newest 10-02, no new); google-research atom STALE 2024-03 → HTML (agentic privacy report 10-05); liquid sitemap lastmod newest 09-24 (missed d1) → liquid.ai/blog HTML (d1 10-05)",
  "tier3_browser_required":{sid:"pending_browser — not fetched in phase 1 (browser pass separate); merge via /workspace/blog-scan-2026-10-06/merge_tier3.py" for sid in T3}},
 "failures":[
  "OpenAI post WebFetch timed out (×2) → curl 200 with browser UA",
  "allen-ai Medium RSS stale (2024-11) → HTML fallback",
  "google-research Atom stale (2024-03) → HTML fallback",
  "Liquid sitemap lastmod stale (newest 2026-09-24) — did not show d1 (10-05); found via liquid.ai/blog HTML listing",
  "Mistral RSS newest 2026-09-09 and HTML listing lag the stored 09-28 post — nothing new detected",
  "Pi: npm @earendil-works/pi returns empty registry doc → version from pi.dev changelog",
  "Low-activity / no new in window: anthropic-research, cerebras, cognition, cursor-blog, cursor-changelog, deepseek, glm-zhipu, minimax, openai-publications, opencode, poolside, sakana, salesforce, xai, nvidia-developer, mistral, allen-ai, liquid-engineering, liquid-research",
  "Tier-3 not attempted in phase 1 by design (pending_browser)"],
 "remaining_blockers":[
  "Tier-3 (perplexity, meta-ai, snowflake, qwen, microsoft-ai) pending browser merge",
  "Liquid d1: all quality/cost figures vendor-run single pass; no standard benchmark; OpenRouter /api/v1/models did not list d1 (availability claim unverified); liquid.ai/pricing does not list d1 (price from post)",
  "Claude Code 2.1.290 on npm next (2026-10-05 18:12 UTC) has no changelog entry yet — not carded; recheck next scan",
  "Stale feeds: allen-ai Medium RSS, google-research Atom, Liquid sitemap lastmod — HTML fallback required",
  "HF community blog posts (e.g. ggml-org 'New in llama.cpp: Decision Models' 10-02) are not tracked by the official feed/policy — not upserted",
  "Ingest backlog: weeks 2026-09-14..2026-09-28 never ingested (token was unset) — not backfilled without instruction"],
 "coding_tool_versions":{
  "claude_code":"2.1.289 (changelog + npm latest; npm next 2.1.290 published 2026-10-05 18:12 UTC / 10-06 02:12 HKT, no changelog entry yet; stable tag 2.1.285)",
  "codex":"0.160.1 stable (2026-10-05, npm latest 18:33 UTC / 10-06 02:33 HKT; backport fix); alpha 0.162.0-alpha.16",
  "opencode":"1.18.34 (no new release since 2026-09-30; only dev snapshots)",
  "pi":"1.0.4 (1.0.3 and 1.0.4 both 2026-10-05)",
  "cursor_changelog":"latest entry 2026-09-23 (Rollouts and Security Review) — nothing new"},
 "paths_written":{
  "digest_md":"weeks/2026-10-06-digest-zh.md",
  "scan_summary":"weeks/2026-10-06-scan-summary.json",
  "ingest_result":"weeks/2026-10-06-ingest-result.json",
  "weeks":["weeks/2026-09-28.json","weeks/2026-10-05.json"],
  "index":"index.json",
  "sources_updated":sorted(t1+['allen-ai','google-research','huggingface','liquid-engineering','liquid-models','liquid-research','mistral','nvidia-developer','openai-news']),
  "cards":[f"cards/{m['id']}.json" for m in meta],
  "cards_count":len(meta),
  "work_dir":"/workspace/blog-scan-2026-10-06/ (fetch_all.py, parse_rss.py, links.py, posts_data.py, upsert_and_cards.py, weeks_update.py, ingest.py, write_summary.py, merge_tier3.py, inserted.json, cards_meta.json, week_stats.json, ingest_result.json, posts/, backup/)",
  "tier3_merge_script":"/workspace/blog-scan-2026-10-06/merge_tier3.py (copy at /workspace/blog-tier3-2026-10-06/merge_tier3.py; supports --dry-run; NOT run)"},
 "scan_note":f"Weekday Blog 應用摘要 2026-10-06 (Tuesday) PHASE 1. 28 tier1/2 sources; tier-3 ×5 pending browser. New cards {len(meta)}: P0×{pr['P0']} P1×{pr['P1']} P2×{pr['P2']} P3×{pr['P3']} (1 catch-up). No confirmed P0 (Liquid d1 potential P0 → P1 needs_verification). Ingest done (token set): 9/9 cards + week 2026-10-05. Not posted to AI Tracker group.",
 "finalized_at":None,
 "phase1_completed_at":NOWTS,
 "cards_by_priority_breakdown":{"phase1_tier1_tier2":pr,"tier3_merge":"pending_browser"},
 "tier3_merge":{"status":"pending_browser","source_file":"/workspace/blog-tier3-2026-10-06/browser-listings.json","script":"/workspace/blog-scan-2026-10-06/merge_tier3.py","per_source":{sid:"pending_browser" for sid in T3}},
 "suggestions":["openrouter: https://openrouter.ai/blog/feed.xml again fresh (151 items, newest 2026-10-05) — tier-2 candidate; index.json tier NOT changed",
   "liquid-*: sitemap lastmod lagged (missed d1 10-05); consider adding https://www.liquid.ai/blog HTML listing to fetch.alt_urls as standing fallback — index.json NOT changed"]}
p=B/'weeks/2026-10-06-scan-summary.json'; p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
shutil.copy(p,'/workspace/blog-scan-2026-10-06-result.json'); shutil.copy(B/'weeks/2026-10-06-digest-zh.md','/workspace/blog-digest-2026-10-06-zh.md')
print(s['scan_note']); print(s['new_posts_per_source'], s['new_inwindow_posts_per_source_2026-10-05_plus'])

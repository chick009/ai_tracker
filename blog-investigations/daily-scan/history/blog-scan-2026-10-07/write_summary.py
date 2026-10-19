import json,datetime,shutil
from pathlib import Path
from collections import Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-07')
NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
ins=json.load(open(W/'inserted.json')); meta=json.load(open(W/'cards_meta.json')); ws=json.load(open(W/'week_stats.json'))
ing=json.load(open(W/'ingest_result.json'))
card=lambda c: json.loads((B/'cards'/f'{c}.json').read_text())
pr={k:0 for k in ['P0','P1','P2','P3']}
for m in meta: pr[m['priority']]+=1
nps=Counter(i['source'] for i in ins); npw=Counter(i['source'] for i in ins if i['date']>='2026-10-05')
for i in ins:
    cid=next((m['id'] for m in meta if m['url']==i['url']),None)
    if cid: i['card_ref']=cid
T3=['meta-ai','microsoft-ai','perplexity','qwen','snowflake']
t1=['anthropic-research','cerebras','claude-code-changelog','codex-changelog','cognition','cursor-blog','cursor-changelog','deepseek','glm-zhipu','inco','minimax','openai-publications','opencode-changelog','openrouter','pi-changelog','poolside','sakana','salesforce','xai']
t2=['allen-ai','google-research','huggingface','liquid-engineering','liquid-models','liquid-research','mistral','nvidia-developer','openai-news']
ftu={s:'tier1_curl_html' for s in t1}
ftu.update({
 'glm-zhipu':'tier1_curl_html (first attempt timed out at 30s → retry 60s HTTP 200)',
 'claude-code-changelog':'tier1_curl_html (+ npm registry; raw.githubusercontent CHANGELOG.md cross-check — 2.1.290/2.1.291/2.1.292 present)',
 'codex-changelog':'tier1_curl_html (+ npm registry check; GitHub API not used)',
 'opencode-changelog':'tier1_curl_html (+ npm registry check)',
 'pi-changelog':'tier1_curl_html (npm @earendil-works/pi 404 → version from pi.dev)',
 'openrouter':'tier1_curl_html (+ openrouter.ai/blog/feed.xml helper, 151 items, newest 2026-10-05, all known; tier unchanged)',
 'openai-publications':'tier1_curl_html (Ironclad post mirrored from openai-news)',
 'openai-news':'tier2_rss (posts read via curl 200) + developers.openai.com API changelog/guide for Decisions API (discovered via codex-changelog page nav)',
 'allen-ai':'tier2_rss_stale_then_html','google-research':'tier2_atom_stale_then_html',
 'huggingface':'tier2_rss (newest 10-06) + HTML listing cross-check (Falcon OCR Arabic found only in listing)',
 'mistral':'tier2_rss (newest 2026-10-06, fresh) + html',
 'nvidia-developer':'tier2_atom (newest 2026-10-06) + html',
 'liquid-engineering':'tier2_sitemap_stale_lastmod_then_html','liquid-models':'tier2_sitemap_stale_lastmod_then_html','liquid-research':'tier2_sitemap_stale_lastmod_then_html'})
for s in T3: ftu[s]='pending_browser'
digest=(B/'weeks/2026-10-07-digest-zh.md').read_text()
s={
 "scan_date":"2026-10-07",
 "window":"2026-10-06 ~06:00 HKT → 2026-10-07 ~06:10 HKT (posts dated 2026-10-06/07 + late 10-05 US-time items not already stored; catch-up of clearly missed items since ~2026-09-30) — PHASE 1 (tier1+tier2 only; tier-3 pending browser)",
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
 "stored_only_not_carded":[],
 "needs_verification_cards":[m['id'] for m in meta if card(m['id']).get('needs_verification')],
 "potential_p0":[
  {"id":"openai-decisions-api-beta-2026-10-06","kept_as":"P1","reason":"New typed-decision API primitive (/v1/decisions, gpt-6-luna, $0.10/1M input, no output charge) that directly changes routing/classification design, but public beta via docs/changelog only, no accuracy benchmark, '10x faster' unverified"},
  {"id":"mistral-large-4-preview-2026-10-06","kept_as":"P1","reason":"~1T open-weight MoE, 1M context, $1.36/$4.18, strong agentic/cyber scores, but preview with weights not yet released, trails Kimi K3 (DeepSWE) and GLM-5.3 (TB4), AA numbers private pre-launch runs"}],
 "confirmed_p0":[],
 "week_stats":ws,
 "week_pack_updated":True,
 "week_pack_notes":"weeks/2026-10-05.json (week_end 2026-10-11): 10 → 24 cards (P0:0 P1:7 P2:11 P3:6); stats rebuilt from card files; index.latest_week stays 2026-10-05. weeks/2026-09-28.json unchanged (94; re-stat only). Tier-3 merge may add more.",
 "ingest":"done",
 "ingest_reason":"TRACKER_INGEST_TOKEN set in box env → POSTed today's 14 cards (14/14 HTTP 200) + week 2026-10-05 body (HTTP 200). Re-ingest after tier-3 merge.",
 "ingest_result":{"cards_ok":ing.get('cards_ok'),"cards_fail":ing.get('cards_fail'),"week":ing.get('week'),"path":"weeks/2026-10-07-ingest-result.json"},
 "group_post":False,
 "digest_zh_Hant":digest,
 "fetch_tier_used":ftu,
 "fetch_tier_summary":{
  "tier1_curl_html":"all 19 tier-1 listings HTTP 200 (glm-zhipu after one retry). New: claude-code 2.1.290 (10-05) + 2.1.291/2.1.292 (10-06), opencode 1.18.35 (10-06), openai-publications Ironclad mirror (10-06). No new: anthropic-research, cerebras, codex (0.160.1 still latest; ChatGPT for iOS 1.2026.267 back-dated 10-02 entry not stored per convention), cognition, cursor-blog, cursor-changelog (09-23), deepseek, glm-zhipu, inco, minimax, openrouter (feed newest 10-05, all known), pi (1.0.4), poolside, sakana, salesforce (new listing links all 09-14..09-28 marketing — not upserted, as on 10-06), xai",
  "tier2_rss_sitemap":"mistral rss fresh (Mistral Large 4, 10-06); openai-news rss fresh (Ironclad, Atlassian 10-06) + Decisions API from developers.openai.com API changelog (10-06); nvidia atom newest 10-06 (3 new); huggingface rss newest 10-06 (Falcon-Emirati) + HTML listing (Falcon OCR Arabic 10-06); google-research atom STALE 2024-03 → HTML (Earth AI PDFM 10-06); allen-ai medium STALE 2024-11 → allenai.org HTML (no new); liquid sitemap lastmod lagging → liquid.ai/blog HTML (no new)",
  "tier3_browser_required":{sid:"pending_browser — not fetched in phase 1; merge via /workspace/blog-tier3-2026-10-07/merge_tier3.py" for sid in T3}},
 "failures":[
  "glm-zhipu listing curl timed out at 30s (HTTP 000) → retry with 60s OK (200)",
  "allen-ai Medium RSS stale (2024-11) → HTML fallback",
  "google-research Atom stale (2024-03) → HTML fallback",
  "Liquid sitemap lastmod lagging → liquid.ai/blog HTML (no new)",
  "Pi: npm @earendil-works/pi 404 → version from pi.dev changelog",
  "Mistral Large 4 benchmark charts are images (webp) — read via ffmpeg→png; Mistral pricing page static HTML lacks ML4 row (price from post + docs model card)",
  "OpenAI pricing page static HTML lacks Decisions row (price from guide)",
  "Low-activity / no new in window: anthropic-research, cerebras, codex-changelog, cognition, cursor-blog, cursor-changelog, deepseek, glm-zhipu, inco, minimax, openrouter, pi-changelog, poolside, sakana, salesforce, xai, allen-ai, liquid-engineering, liquid-models, liquid-research",
  "Tier-3 not attempted in phase 1 by design (pending_browser)"],
 "remaining_blockers":[
  "Tier-3 (perplexity, meta-ai, snowflake, qwen, microsoft-ai) pending browser merge",
  "OpenAI Decisions API: no news post at scan time; source is developers.openai.com API changelog (untracked) — stored under openai-news with discovered_via; no benchmark; long-context multiplier unpublished",
  "Mistral Large 4: weights not released (end of month); active params 49B (post) vs 52B (docs); docs discounted price $0.68/$2.09/$0.07 condition not stated; AA DeepSWE/TB4 private pre-launch runs",
  "Liquid d1 (10-05) still unverified on OpenRouter — not rechecked this run",
  "Stale feeds: allen-ai Medium RSS, google-research Atom, Liquid sitemap lastmod — HTML fallback required",
  "HF community/user posts (e.g. sora-2 'What is Decisions API', harpreetsahota FiftyOne×LeRobot) not tracked — not upserted",
  "ChatGPT for iOS entries in Codex changelog (latest 1.2026.267, 10-02) intentionally not stored (consistent with earlier scans)"],
 "coding_tool_versions":{
  "claude_code":"2.1.292 (changelog + npm latest/next, published 2026-10-06 17:10 UTC / 10-07 01:10 HKT); 2.1.290 (npm 10-05 18:12 UTC, changelog dated Oct 5) and 2.1.291 (10-06 03:32 UTC) now in changelog and carded; stable tag 2.1.285",
  "codex":"0.160.1 stable (no new); alpha 0.162.0-alpha.16",
  "opencode":"1.18.35 (2026-10-06 20:21 UTC / 10-07 04:21 HKT)",
  "pi":"1.0.4 (no new)",
  "cursor_changelog":"latest entry 2026-09-23 (Rollouts and Security Review) — nothing new"},
 "paths_written":{
  "digest_md":"weeks/2026-10-07-digest-zh.md",
  "scan_summary":"weeks/2026-10-07-scan-summary.json",
  "ingest_result":"weeks/2026-10-07-ingest-result.json",
  "weeks":["weeks/2026-10-05.json","weeks/2026-09-28.json (re-stat only)"],
  "index":"index.json",
  "sources_updated":sorted(t1+t2),
  "cards":[f"cards/{m['id']}.json" for m in meta],
  "cards_count":len(meta),
  "backup_dir":"/workspace/blog-scan-2026-10-07/backup/ (index.json, sources/*.json ×33, weeks/2026-10-05.json, weeks/2026-09-28.json)",
  "work_dir":"/workspace/blog-scan-2026-10-07/ (fetch_all.py, parse_rss.py, links.py, h2t.py, posts_data.py, upsert_and_cards.py, weeks_update.py, ingest.py, write_summary.py, inserted.json, cards_meta.json, week_stats.json, ingest_result.json, posts/, backup/)",
  "tier3_merge_script":"/workspace/blog-tier3-2026-10-07/merge_tier3.py (+ write_cards.py, ingest_tier3.py, finalize_summary.py; adapted for 2026-10-07; supports --dry-run; NOT run)"},
 "scan_note":f"Weekday Blog 應用摘要 2026-10-07 (Wednesday) PHASE 1. 28 tier1/2 sources; tier-3 ×5 pending browser. New cards {len(meta)}: P0×{pr['P0']} P1×{pr['P1']} P2×{pr['P2']} P3×{pr['P3']}. No confirmed P0 (OpenAI Decisions API + Mistral Large 4 potential P0 → P1 needs_verification). Ingest done (token set): 14/14 cards + week 2026-10-05. Not posted to AI Tracker group.",
 "finalized_at":None,
 "phase1_completed_at":NOWTS,
 "cards_by_priority_breakdown":{"phase1_tier1_tier2":pr,"tier3_merge":"pending_browser"},
 "tier3_merge":{"status":"pending_browser","source_file":"/workspace/blog-tier3-2026-10-07/browser-listings.json","script":"/workspace/blog-tier3-2026-10-07/merge_tier3.py","per_source":{sid:"pending_browser" for sid in T3}},
 "suggestions":["Track developers.openai.com/api/docs/changelog as a tier-1 source (Decisions API surfaced there before any news post) — index.json NOT changed",
   "openrouter: blog/feed.xml remains fresh (151 items) — tier-2 candidate; index.json NOT changed",
   "liquid-*: add https://www.liquid.ai/blog HTML listing to fetch.alt_urls as standing fallback — index.json NOT changed"]}
p=B/'weeks/2026-10-07-scan-summary.json'; p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
shutil.copy(p,'/workspace/blog-scan-2026-10-07-result.json'); shutil.copy(B/'weeks/2026-10-07-digest-zh.md','/workspace/blog-digest-2026-10-07-zh.md')
print(s['scan_note']); print(s['new_posts_per_source'], s['new_inwindow_posts_per_source_2026-10-05_plus'])

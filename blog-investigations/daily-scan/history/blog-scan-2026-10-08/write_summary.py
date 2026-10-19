import json,datetime,shutil
from pathlib import Path
from collections import Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-08')
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
 'anthropic-research':'tier1_curl_html (+ anthropic.com/news listing for Haiku 5.5 / CVP, both curl 200; CVP body via WebFetch)',
 'claude-code-changelog':'tier1_curl_html (+ npm registry; raw.githubusercontent CHANGELOG.md cross-check — 2.1.293 present)',
 'codex-changelog':'tier1_curl_html (+ npm registry 0.161.0; github.com release page HTML for notes — changelog page not yet updated; GitHub API not used)',
 'opencode-changelog':'tier1_curl_html (+ npm registry check; no new)',
 'pi-changelog':'tier1_curl_html (npm @earendil-works/pi 404 → version from pi.dev; 1.1.0 release page curl 200)',
 'openrouter':'tier1_curl_html (+ openrouter.ai/blog/feed.xml helper, 153 items, newest 2026-10-07; + /api/v1/models for d1/ML4/Haiku rechecks)',
 'openai-publications':'tier1_curl_html FAILED (HTTP 403 Cloudflare ×3 incl. browser-like headers) — no new items determinable; not escalated to browser in phase 1',
 'cursor-changelog':'tier1_curl_html (new entry remote-control-local-agents 10-06)',
 'openai-news':'tier2_rss (fresh, newest 2026-10-07); post bodies: curl 403 → WebFetch (GPT-6, math, teens OK; Radisson/Jump Trading 403 → RSS description only) + developers.openai.com/api/docs/changelog (curl 200)',
 'allen-ai':'tier2_rss_stale (2024-11) → html (allenai.org; bolmo-nature 10-07)',
 'google-research':'tier2_atom: blog.research.google/atom.xml 302 → http feedburner (curl empty) → https feeds.feedburner.com/blogspot/gJZg 200 but STALE 2024-03 → html (research.google/blog)',
 'huggingface':'tier2_rss (newest 10-07) + HTML listing cross-check (no new org posts beyond feed; community posts ignored)',
 'mistral':'tier2_rss (newest 2026-10-06, no new) + html',
 'nvidia-developer':'tier2_atom (newest 2026-10-07, 4 new) + html',
 'liquid-models':'tier2_sitemap (d1-open lastmod 2026-10-07 — fresh this time) + liquid.ai/blog html',
 'liquid-engineering':'tier2_sitemap + html (no new)','liquid-research':'tier2_sitemap + html (no new)'})
for s in T3: ftu[s]='pending_browser'
digest=(B/'weeks/2026-10-08-digest-zh.md').read_text()
rech=json.load(open(W/'rechecks.json'))
s={
 "scan_date":"2026-10-08",
 "window":"2026-10-07 ~06:10 HKT → 2026-10-08 ~06:10 HKT (posts dated 2026-10-07/08 + late 10-06 US-time items not already stored; catch-up check of clearly missed items since ~2026-10-01) — PHASE 1 (tier1+tier2 only; tier-3 pending browser)",
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
 "mirrors":[i for i in ins if i.get('mirror_of')],
 "needs_verification_cards":[m['id'] for m in meta if card(m['id']).get('needs_verification')],
 "existing_card_rechecks":rech,
 "potential_p0":[
  {"id":"openai-decisions-api-beta-2026-10-06","kept_as":"P1","status":"rechecked 10-08","reason":"Still no openai.com/news post or benchmark; Pi 1.1.0 integration is adoption, not verification"},
  {"id":"mistral-large-4-preview-2026-10-06","kept_as":"P1","status":"rechecked 10-08","reason":"Weights still not on Hugging Face; OpenRouter now lists mistral-large-4-0 at $0.68/$2.09 (cached $0.07)"},
  {"id":"liquid-d1-decision-model-2026-10-05","kept_as":"P1","status":"rechecked 10-08","reason":"Still not listed on OpenRouter /api/v1/models"}],
 "confirmed_p0":[{"id":"claude-haiku-5-5-2026-10-07","reason":"Consequential model release: $0.10/$0.50 per 1M (≤100K), TB4 39.2% vs Haiku 4.5 0.0% / GPT-6 Luna 16.4%, OSWorld 2.1 offline 72.4% vs 48.9% (Luna); GA all clouds + OpenRouter"}],
 "week_stats":ws,
 "week_pack_updated":True,
 "week_pack_notes":f"weeks/2026-10-05.json (week_end 2026-10-11): 25 → {ws['week_2026-10-05']['total_cards']} cards ({ws['week_2026-10-05']['priorities']}); stats rebuilt from card files; index.latest_week stays 2026-10-05. weeks/2026-09-28.json unchanged (94; re-stat only). Tier-3 merge may add more.",
 "ingest":"done",
 "ingest_reason":f"TRACKER_INGEST_TOKEN set in box env → POSTed today's {len(meta)} new cards + {len(rech)} rechecked cards ({ing.get('cards_ok')}/{ing.get('cards_ok',0)+ing.get('cards_fail',0)} HTTP 200) + week 2026-10-05 body (HTTP {ing.get('week',{}).get('status')}). Re-ingest after tier-3 merge.",
 "ingest_result":{"cards_ok":ing.get('cards_ok'),"cards_fail":ing.get('cards_fail'),"week":ing.get('week'),"path":"weeks/2026-10-08-ingest-result.json"},
 "group_post":False,
 "digest_zh_Hant":digest,
 "fetch_tier_used":ftu,
 "fetch_tier_summary":{
  "tier1_curl_html":"18/19 tier-1 listings HTTP 200; openai-publications 403 (Cloudflare). New: anthropic-research Haiku 5.5 (10-07) + Cyber Verification Program (10-06) via anthropic.com/news; claude-code 2.1.293 (10-07); codex 0.161.0 (npm/GitHub release 10-07); cursor-changelog remote control (10-06); pi 1.1.0 (10-07); openrouter ElevenLabs + Rasp case study (10-07). No new: cerebras, cognition, cursor-blog, deepseek, glm-zhipu, inco, minimax, opencode (1.18.35), poolside, sakana, salesforce (linked-content marketing guide not upserted), xai",
  "tier2_rss_sitemap":"openai-news rss fresh (5 new: GPT-6 for everyone, math, teens, Radisson 10-07; Jump Trading 10-06) + API changelog (chat-latest 10-07 folded into GPT-6 card); nvidia atom newest 10-07 (4 new); huggingface rss newest 10-07 (Nemotron IOI/IMO; LiquidAI open-d1 mirror); liquid sitemap fresh (d1-open 10-07); mistral rss no new; google-research atom STALE → HTML (AI expertise RCT 10-07); allen-ai medium STALE → HTML (Bolmo Nature 10-07)",
  "tier3_browser_required":{sid:"pending_browser — not fetched in phase 1; merge via /workspace/blog-tier3-2026-10-08/merge_tier3.py" for sid in T3}},
 "failures":[
  "openai-publications listing curl 403 (Cloudflare) on 3 attempts — no listing parsed",
  "openai.com post bodies curl 403; WebFetch OK for gpt-6-for-everyone (2nd try), sharing-ai-progress-in-mathematics, teens-learn-and-plan; WebFetch 403/timeout for radisson, jump-trading → cards from RSS description only (P3)",
  "google-research Atom: 302 to http feedburner returned empty; https feedburner OK but stale (2024-03) → HTML fallback",
  "allen-ai Medium RSS stale (2024-11) → HTML fallback",
  "Pi: npm @earendil-works/pi 404 → version from pi.dev changelog",
  "Codex: developers.openai.com Codex changelog page not yet updated for 0.161.0 → notes from github.com release page HTML",
  "Low-activity / no new in window: cerebras, cognition, cursor-blog, deepseek, glm-zhipu, inco, minimax, mistral, opencode-changelog, poolside, sakana, salesforce, xai, liquid-engineering, liquid-research",
  "Tier-3 not attempted in phase 1 by design (pending_browser)"],
 "remaining_blockers":[
  "Tier-3 (perplexity, meta-ai, snowflake, qwen, microsoft-ai) pending browser merge",
  "openai-publications 403 — any publications-only item (not in openai-news RSS) would be missed; math post likely mirrored there but unverified",
  "Mistral Large 4: weights still not released; OpenRouter live at sale price $0.68/$2.09/$0.07, sale end date unknown",
  "OpenAI Decisions API: still no news post / benchmark",
  "Liquid d1 hosted: still not on OpenRouter",
  "Haiku 5.5 benchmarks provider-reported (OSWorld offline subset only); System Card not parsed",
  "Stale feeds: allen-ai Medium RSS, google-research Atom — HTML fallback required",
  "Not stored by convention: ChatGPT for iOS 1.2026.272 (Codex changelog 10-07), HF community/user posts, Salesforce linked-content marketing, OpenAI Codex Originals form page; Anthropic news 10-01 Barclays / 10-02 $100M training not stored (outside tracked research listing, low signal); API changelog 10-06 usage tiers + 10-05 HIPAA BAA not carded"],
 "coding_tool_versions":{
  "claude_code":"2.1.293 (changelog Oct 7 + npm latest/next, published 2026-10-07 17:18 UTC / 10-08 01:18 HKT); stable tag 2.1.285",
  "codex":"0.161.0 stable (npm 2026-10-07 16:04 UTC / 10-08 00:04 HKT; GitHub release 07 Oct 15:58 UTC); alpha 0.162.0-alpha.18",
  "opencode":"1.18.35 (no new; dev snapshots only)",
  "pi":"1.1.0 (pi.dev, Oct 7)",
  "cursor_changelog":"latest entry 2026-10-06 (Remote control for local agents)"},
 "paths_written":{
  "digest_md":"weeks/2026-10-08-digest-zh.md",
  "scan_summary":"weeks/2026-10-08-scan-summary.json",
  "ingest_result":"weeks/2026-10-08-ingest-result.json",
  "weeks":["weeks/2026-10-05.json","weeks/2026-09-28.json (re-stat only, content unchanged)"],
  "index":"index.json",
  "sources_updated":sorted(t1+t2),
  "cards":[f"cards/{m['id']}.json" for m in meta],
  "cards_updated":[f"cards/{c}.json" for c in rech],
  "cards_count":len(meta),
  "backup_dir":"/workspace/blog-scan-2026-10-08/backup/ (index.json, sources/*.json ×33, weeks/2026-10-05.json, weeks/2026-09-28.json)",
  "work_dir":"/workspace/blog-scan-2026-10-08/ (fetch_all.py, parse_rss.py, links.py, h2t.py, posts_data.py, upsert_and_cards.py, update_existing.py, weeks_update.py, ingest.py, write_summary.py, inserted.json, cards_meta.json, rechecks.json, week_stats.json, ingest_result.json, posts/, backup/)",
  "tier3_merge_script":"/workspace/blog-tier3-2026-10-08/merge_tier3.py (+ write_cards.py, ingest_tier3.py, finalize_summary.py; adapted for 2026-10-08; supports --dry-run; NOT run)"},
 "scan_note":f"Weekday Blog 應用摘要 2026-10-08 (Thursday) PHASE 1. 28 tier1/2 sources; tier-3 ×5 pending browser. New cards {len(meta)}: P0×{pr['P0']} P1×{pr['P1']} P2×{pr['P2']} P3×{pr['P3']}. Confirmed P0: Claude Haiku 5.5. Potential P0 still P1/needs_verification: Decisions API, Mistral Large 4, Liquid d1 (rechecked). Ingest done (token set). Not posted to AI Tracker group.",
 "finalized_at":None,
 "phase1_completed_at":NOWTS,
 "cards_by_priority_breakdown":{"phase1_tier1_tier2":pr,"tier3_merge":"pending_browser"},
 "tier3_merge":{"status":"pending_browser","source_file":"/workspace/blog-tier3-2026-10-08/browser-listings.json","script":"/workspace/blog-tier3-2026-10-08/merge_tier3.py","per_source":{sid:"pending_browser" for sid in T3}},
 "suggestions":["Track developers.openai.com/api/docs/changelog and anthropic.com/news as tier-1 helper listings (Haiku 5.5 / CVP surfaced on /news, not /research) — index.json NOT changed",
   "google-research: replace atom.xml alt_url with https://feeds.feedburner.com/blogspot/gJZg or drop (stale either way) — index.json NOT changed",
   "openai-publications: 403 today — consider tier-3 browser or rely on openai-news RSS — index.json NOT changed"]}
p=B/'weeks/2026-10-08-scan-summary.json'; p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
shutil.copy(p,'/workspace/blog-scan-2026-10-08-result.json'); shutil.copy(B/'weeks/2026-10-08-digest-zh.md','/workspace/blog-digest-2026-10-08-zh.md')
print(s['scan_note']); print(s['new_posts_per_source'], s['new_inwindow_posts_per_source_2026-10-05_plus'])

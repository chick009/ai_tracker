import json
from pathlib import Path
from collections import Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch'); W=Path('/workspace/blog-scan-2026-10-05')
ins=json.load(open(W/'inserted.json')); cm=json.load(open(W/'cards_meta.json')); ws=json.load(open(W/'week_stats.json'))
idx=json.loads((B/'index.json').read_text())
t1=idx['fetch_policy']['tier1_ids']; t2=idx['fetch_policy']['tier2_ids']; t3=idx['fetch_policy']['tier3_ids']
order={'P0':0,'P1':1,'P2':2,'P3':3}
cm_sorted=sorted(cm,key=lambda m:order[m['priority']])
ftu={s:'tier1_curl_html' for s in t1}
ftu['openrouter']='tier1_curl_html (+ discovered openrouter.ai/blog/feed.xml, 150 items, fresh 2026-10-02 — candidate tier-2 upgrade)'
ftu['cerebras']='tier1_curl_html (listing 200; single post curl 500 → WebFetch OK)'
ftu['codex-changelog']='tier1_curl_html (+ npm registry check; GitHub API rate-limited)'
ftu['opencode-changelog']='tier1_curl_html (+ npm registry check; GitHub API rate-limited)'
ftu.update({'allen-ai':'tier2_rss_stale_then_html','google-research':'tier2_atom_stale_then_html','huggingface':'tier2_rss','liquid-engineering':'tier2_sitemap',
 'liquid-models':'tier2_sitemap','liquid-research':'tier2_sitemap','mistral':'tier2_rss','nvidia-developer':'tier2_atom','openai-news':'tier2_rss'})
for s in t3: ftu[s]='pending_browser_merge'
per_source=Counter(i['source'] for i in ins)
inwin=Counter(i['source'] for i in ins if i['date']>='2026-10-02')
summary={
 'scan_date':'2026-10-05',
 'window':'2026-10-02 ~ 2026-10-05 HKT (catch-up of clearly missed items since ~2026-09-28 not in sources/) — PHASE 1 (tier1+tier2) provisional; tier-3 pending browser merge',
 'phase':'phase1_tier1_tier2',
 'sources_scanned':len(t1)+len(t2),
 'sources_pending_browser_merge':t3,
 'inserted_titles':[i['title'] for i in ins],
 'inserted':ins,
 'new_posts_per_source':dict(per_source),
 'new_inwindow_posts_per_source_2026-10-02_plus':dict(inwin),
 'cards_written':cm_sorted,
 'cards_by_priority':{k:sum(1 for m in cm if m['priority']==k) for k in ['P0','P1','P2','P3']},
 'catch_up_cards':[m['id'] for m in cm if json.loads((B/'cards'/f"{m['id']}.json").read_text()).get('catch_up')],
 'needs_verification_cards':[m['id'] for m in cm if json.loads((B/'cards'/f"{m['id']}.json").read_text()).get('needs_verification')],
 'week_stats':ws,
 'week_pack_updated':True,
 'week_pack_notes':'weeks/2026-09-28.json keeps existing week_end 2026-10-05 (prior packs use week_start+7 convention, e.g. 2026-09-21→2026-09-28); new weeks/2026-10-05.json created with week_end 2026-10-11 as instructed (convention would give 2026-10-12). index.latest_week left at 2026-09-28 because the 2026-10-05 pack has 0 cards so far — flip after tier-3 merge if any 10-05 cards land.',
 'ingest':'skipped','ingest_reason':'TRACKER_INGEST_TOKEN unset',
 'group_post':False,
 'digest_zh_Hant':(B/'weeks/2026-10-05-digest-zh.md').read_text(),
 'fetch_tier_used':ftu,
 'fetch_tier_summary':{
  'tier1_curl_html':', '.join(t1)+' — all listings HTTP 200',
  'tier2_rss_sitemap':'huggingface(rss, newest 2026-10-03 UTC), nvidia-developer(atom, newest 2026-10-01 UTC, nothing new), openai-news(rss, newest 2026-10-02), mistral(rss, newest 2026-09-28, nothing new), liquid-*(sitemap 126 urls, no lastmod>=2026-10-01); allen-ai medium rss STALE(2024-11)→allenai.org HTML (AstaBrief 10-02 + Olmo-core 3 10-01 mirrors); google-research atom STALE(2024-03)→HTML (federated TEE post 10-02)',
  'tier3_browser_required':{s:'pending_browser_merge' for s in t3},
 },
 'failures':[
  'cerebras: single post page curl HTTP 500 → WebFetch OK; source store had 0 posts before (prior runs never parsed listing) → 2 catch-up posts added',
  'allen-ai Medium RSS stale (2024) → HTML fallback',
  'google-research Atom stale (2024) → HTML fallback',
  'GitHub releases API rate-limited (unauthenticated) → used developers.openai.com changelog + npm registry for Codex/OpenCode/Claude Code versions',
  'Model Router Benchmarks per-router scores are on an interactive page — numbers not captured',
  'Low-activity / no new in window: cognition, cursor-blog, cursor-changelog, xai, sakana, poolside, minimax, deepseek, glm-zhipu, inco, openai-publications, salesforce (two 09-28 marketing posts seen, not upserted), mistral, nvidia-developer, liquid-*, codex (stable), opencode',
  'Missed by earlier scans and caught up now: anthropic-research 09-29/09-30 ×3, openrouter security-center 09-28, cerebras 09-30/10-01',
  'Tier-3 (perplexity, meta-ai, snowflake, qwen, microsoft-ai) not fetched in phase 1 by design — pending_browser_merge',
 ],
 'remaining_blockers':['tier-3 browser merge pending','consider promoting openrouter to tier 2 using https://openrouter.ai/blog/feed.xml (not changed in index.json)'],
 'coding_tool_versions':{
  'claude_code':'2.1.289 (2.1.288 2026-10-02, 2.1.289 2026-10-03; npm latest/next 2.1.289, stable tag 2.1.285)',
  'codex':'0.160.0 stable (no new stable since 2026-10-01; alpha 0.162.0-alpha.13 on 2026-10-04 not carded)',
  'opencode':'1.18.34 (no new release since 2026-09-30)',
  'pi':'1.0.2 (1.0.1 2026-10-03, 1.0.2 2026-10-04)',
  'cursor_changelog':'latest entry 2026-09-23 (Rollouts and Security Review) — nothing new',
 },
 'paths_written':{
  'digest_md':'weeks/2026-10-05-digest-zh.md','digest_workspace_copy':'/workspace/blog-digest-2026-10-05-zh.md',
  'scan_summary':'weeks/2026-10-05-scan-summary.json','scan_summary_workspace':'/workspace/blog-scan-2026-10-05-result.json',
  'weeks':['weeks/2026-09-28.json','weeks/2026-10-05.json (new)'],'index':'index.json',
  'sources_updated':sorted(set(t1+t2)),'cards':[f"cards/{m['id']}.json" for m in cm_sorted],'cards_count':len(cm),
  'work_dir':'/workspace/blog-scan-2026-10-05/ (fetch_all.py, fetch_results.json, parse_rss.py, parsed_rss.json, posts_data.py, upsert_and_cards.py, weeks_update.py, inserted.json, cards_meta.json, week_stats.json, posts/*.txt, backup/)',
 },
 'scan_note':'Weekday Blog 應用摘要 2026-10-05 (Monday) PHASE 1. 28 tier1/2 sources scanned. New cards P0×0 P1×11 P2×7 P3×2 (6 catch-up). Ingest skipped. Tier-3 pending browser merge. Do not post to AI Tracker group.',
}
for p in [B/'weeks/2026-10-05-scan-summary.json', Path('/workspace/blog-scan-2026-10-05-result.json')]:
    p.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(summary['new_posts_per_source'],summary['new_inwindow_posts_per_source_2026-10-02_plus'],summary['cards_by_priority'])

import json,datetime,shutil
from pathlib import Path
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-tier3-2026-10-05')
NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
p=B/'weeks/2026-10-05-scan-summary.json'; s=json.loads(p.read_text())
L=json.load(open(W/'browser-listings.json')); up=json.load(open(W/'upsert_report.json'))
meta=json.load(open(W/'cards_meta.json')); ws=json.load(open(W/'week_stats.json'))
s['window']="2026-10-02 ~ 2026-10-05 HKT (catch-up of clearly missed items since ~2026-09-28 not in sources/) — FINAL (tier1+tier2 phase 1 + tier-3 computerUse browser merge)"
s['phase']='final_tier1_tier2_tier3'
s['finalized_at']=NOWTS
s['sources_scanned']=33
s.pop('sources_pending_browser_merge',None)
newposts=[]
for sid in ['perplexity','meta-ai','snowflake','qwen','microsoft-ai']:
  for lp in L[sid]['posts']:
    if lp['title'] in up[sid]['inserted']:
      e={'source':sid,'title':lp['title'],'url':lp['url'],'date':lp['date'],'catch_up':lp['date']<'2026-10-02','via':'tier3_computerUse_chromium'}
      cid={'https://www.perplexity.ai/hub/blog/ai-maturity':'perplexity-ai-maturity-2026-10-02','https://microsoft.ai/news/our-first-streaming-transcription-model/':'microsoft-mai-transcribe-2-streaming-2026-10-01'}.get(lp['url'])
      if cid: e['card_ref']=cid
      else: e['carded']=False; e['not_carded_reason']='older than catch-up horizon (~2026-09-28); stored only'
      newposts.append(e)
s['inserted']+=newposts
s['inserted_titles']+= [e['title'] for e in newposts]
s['new_posts_per_source'].update({'perplexity':2,'microsoft-ai':2})
s['new_inwindow_posts_per_source_2026-10-02_plus']['perplexity']=1
for m in meta:
  if m['id'] not in [c['id'] for c in s['cards_written']]: s['cards_written'].append(m)
pr={'P0':0,'P1':0,'P2':0,'P3':0}
for c in s['cards_written']: pr[json.loads((B/'cards'/f"{c['id']}.json").read_text())['priority']]+=1
s['cards_by_priority']=pr
s['cards_by_priority_breakdown']={'phase1_tier1_tier2':{'P0':0,'P1':11,'P2':7,'P3':2},'tier3_merge':{'P0':0,'P1':1,'P2':0,'P3':1}}
if 'microsoft-mai-transcribe-2-streaming-2026-10-01' not in s['catch_up_cards']: s['catch_up_cards'].append('microsoft-mai-transcribe-2-streaming-2026-10-01')
s['week_stats']={k:v for k,v in ws.items()}
s['week_pack_notes']="weeks/2026-09-28.json keeps existing week_end 2026-10-05 (prior packs use week_start+7 convention); weeks/2026-10-05.json (week_end 2026-10-11) still 0 cards after tier-3 merge (no posts dated >= 2026-10-05), so index.latest_week stays 2026-09-28. Both tier-3 cards (10-01, 10-02) went to the 2026-09-28 pack; stats rebuilt from card files."
tier3_notes={
 'perplexity':'tier3_computerUse_chromium_ok — 12 listed; 2 new URLs (AI maturity 10-02 → card P3; Portable Computer×AMD 09-24 → stored only, pre-horizon); 10 last_seen refreshed. Stored-but-uncarded MCP vs API (09-28) left uncarded (SEO explainer, earlier triage).',
 'meta-ai':'tier3_computerUse_chromium_ok — 12 listed, newest 2026-07-27; nothing in window; 12 last_seen refreshed.',
 'snowflake':'tier3_computerUse_chromium_ok — 12 listed, newest 2026-09-29 OpenTelemetry (already carded P2 snowflake-otel-enterprise-data-2026-09-29); 0 new; 12 last_seen refreshed. 09-28 Mission AI lessons stays uncarded (earlier triage); 09-28 Sonnet 5.5 / GPT-6 Sol-Luna Cortex already carded.',
 'qwen':'tier3_computerUse_chromium_ok — research index 12 listed, newest 2026-09-20 (already carded); 0 new; 12 last_seen refreshed.',
 'microsoft-ai':'tier3_computerUse_chromium_ok — 12 listed; 2 new URLs (streaming transcription 10-01 → card P1 catch-up, post read via curl 200 incl. embedded AA chart data + model card PDF; Ode Poetry 07-09 → stored only); 10 last_seen refreshed.'}
s['tier3_merge']={'status':'tier3_computerUse_chromium_ok','source_file':'/workspace/blog-tier3-2026-10-05/browser-listings.json','per_source':tier3_notes,'cards_added':[m['id'] for m in meta],'post_counts':{k:v['post_count'] for k,v in up.items()}}
for sid,n in tier3_notes.items():
  s['fetch_tier_used'][sid]='tier3_computerUse_chromium_ok'
  s['fetch_tier_summary']['tier3_browser_required'][sid]=n
s['failures']=[f for f in s['failures'] if not f.startswith('Tier-3')]+['Tier-3 merged via computerUse Chromium in phase 2 — all 5 OK (no tier-3 failures)']
s['remaining_blockers']=[
 'OpenRouter Model Router Benchmarks: per-router scores live on an interactive page — numbers not captured',
 'GitHub releases API anonymous rate limit — used npm registry + official changelogs instead',
 'Cerebras single-post curl HTTP 500 (listing 200) — WebFetch fallback used',
 'Stale feeds: allen-ai Medium RSS (2024) and google-research Atom (2024) — HTML fallback used',
 'Liquid sitemap: no lastmod >= 2026-10-01 (no new posts detected)',
 'MAI-Transcribe-2-Streaming AA figures taken from Microsoft-embedded AA chart data (2026-09-28); not independently re-read on artificialanalysis.ai (charts not machine-readable); post-2026 price unpublished',
 'Perplexity Portable Computer×AMD (09-24) found only now — pre-horizon, stored without card; can be reviewed in Monday weekly rollup if wanted']
s['suggestions']=['openrouter: https://openrouter.ai/blog/feed.xml works (150 items, fresh to 2026-10-02) — tier-2 candidate; index.json tier NOT changed']
pw=s['paths_written']
pw['cards']+= [f"cards/{m['id']}.json" for m in meta if f"cards/{m['id']}.json" not in pw['cards']]
pw['cards_count']=len(pw['cards'])
for sid in ['meta-ai','microsoft-ai','perplexity','qwen','snowflake']:
  if sid not in pw['sources_updated']: pw['sources_updated'].append(sid)
pw['sources_updated'].sort()
pw['tier3_work_dir']='/workspace/blog-tier3-2026-10-05/ (browser-listings.json, merge_tier3.py, write_cards.py, weeks_update.py, finalize_summary.py, upsert_report.json, week_stats.json, posts/, backup/)'
pw['weeks']=['weeks/2026-09-28.json','weeks/2026-10-05.json']
s['digest_zh_Hant']=(B/'weeks/2026-10-05-digest-zh.md').read_text()
s['scan_note']=(f"Weekday Blog 應用摘要 2026-10-05 (Monday) FINAL. 33 sources (28 tier1/2 + 5 tier-3 via computerUse Chromium, all OK). "
 f"New cards {sum(pr.values())}: P0×{pr['P0']} P1×{pr['P1']} P2×{pr['P2']} P3×{pr['P3']} (7 catch-up). No new confirmed P0. Ingest skipped. Not posted to AI Tracker group.")
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
shutil.copy(p,'/workspace/blog-scan-2026-10-05-result.json')
print(json.dumps({k:s[k] for k in ['phase','sources_scanned','cards_by_priority','scan_note']},ensure_ascii=False,indent=1))

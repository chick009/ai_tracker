#!/usr/bin/env python3
"""Finalize weeks/2026-10-07-scan-summary.json after tier-3 merge (run after merge_tier3.py, write_cards.py, ingest_tier3.py).
Optional: put the final 繁中 digest at /workspace/blog-tier3-2026-10-07/digest-final.md — it then replaces
weeks/2026-10-07-digest-zh.md and digest_zh_Hant. Fill NOTES / EXTRA_BLOCKERS / EXTRA_FAILURES from the browser pass."""
import json,datetime,shutil
from pathlib import Path
from collections import Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-tier3-2026-10-07')
T3=['perplexity','meta-ai','snowflake','qwen','microsoft-ai']
NOTES=[
 "perplexity: 13 listed, 1 new (10 Best AI Collaboration Tools, 10-06 → P3 card); undated listing item 'MCP vs. API: A Full Technical Breakdown' already stored (date 2026-09-28, first_seen 2026-10-01) → last_seen refreshed only, not carded",
 "snowflake: 12 listed, no new (newest 2026-10-05 AI Gateway for Advertising)",
 "meta-ai: 'Load more' clicked → 12 listed, newest dated 2026-07-27, no new",
 "qwen: only top 4 recorded, all url=https://qwen.ai/research → listing-URL guard: title-match refresh 4/4, no URL upsert; newest 2026-09-20",
 "microsoft-ai: 12 listed, listing undated; top item is known 2026-10-01 post → no new",
 "Perplexity collaboration-tools article curl → 403 (Cloudflare); card from browser summary only"]           # tier-3 observations (e.g. listing quirks, already-stored items)
EXTRA_BLOCKERS=[
 "Qwen tier-3: only top 4 listing items recorded and no per-post links (all qwen.ai/research) — title-match only; deeper items not verified",
 "Microsoft AI tier-3: listing undated — newness inferred from top item only (known 2026-10-01 post)",
 "Perplexity tier-3: one listing item undated ('MCP vs. API', already stored as 2026-09-28); Perplexity article pages curl 403 → cards rely on browser summary",
 "Suggestion: track developers.openai.com/api/docs/changelog as a source (Decisions API surfaced there only) — index.json NOT changed"]  # e.g. "Meta AI: 'Load more' not expanded"
EXTRA_FAILURES=["Perplexity post curl 403 (ai-collaboration-tools) → card from browser listing summary"]  # e.g. "Perplexity post curl 403 → card from browser summary"
NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
(W/'backup').mkdir(parents=True,exist_ok=True)
p=B/'weeks/2026-10-07-scan-summary.json'; shutil.copy(p,W/'backup'/'2026-10-07-scan-summary.phase1.json')
s=json.loads(p.read_text()); rep=json.load(open(W/'upsert_report.json'))
meta=json.load(open(W/'cards_meta.json')) if (W/'cards_meta.json').exists() else []
ing=json.load(open(W/'ingest_result.json')) if (W/'ingest_result.json').exists() else None
s['window']=s['window'].replace(' — PHASE 1 (tier1+tier2 only; tier-3 pending browser)','')+' — FINAL (tier1+tier2 phase 1 + tier-3 computerUse Chromium merge)'
s['phase']='final_tier1_tier2_tier3'; s['sources_scanned']=33; s['sources_pending_browser_merge']=[]
for m in meta:
  s['inserted'].append({'source':m['source_id'],'title':m['title'],'url':m['url'],'date':m['date'],'catch_up':m['date']<'2026-10-06','card_ref':m['id'],'via':'tier3_computerUse_chromium'})
  s['inserted_titles'].append(m['title']); s['cards_written'].append({k:m[k] for k in ['id','priority','type','url','title']})
for sid,r in rep.items():
  for t in r.get('inserted',[]):
    if not any(m['title']==t and m['source_id']==sid for m in meta):
      s['inserted'].append({'source':sid,'title':t,'via':'tier3_computerUse_chromium','carded':False}); s['inserted_titles'].append(t)
  n=len(r.get('inserted',[]))
  if n: s['new_posts_per_source'][sid]=s['new_posts_per_source'].get(sid,0)+n
nw=Counter(m['source_id'] for m in meta if m['date']>='2026-10-05')
for sid,n in nw.items(): s['new_inwindow_posts_per_source_2026-10-05_plus'][sid]=s['new_inwindow_posts_per_source_2026-10-05_plus'].get(sid,0)+n
t3pr=Counter(m['priority'] for m in meta); t3pr={k:t3pr.get(k,0) for k in ['P0','P1','P2','P3']}
ph1=s['cards_by_priority_breakdown']['phase1_tier1_tier2']
s['cards_by_priority_breakdown']['tier3_merge']=t3pr
s['cards_by_priority_breakdown']['final_total']={k:ph1[k]+t3pr[k] for k in ph1}
s['cards_by_priority']=s['cards_by_priority_breakdown']['final_total']
card=lambda c: json.loads((B/'cards'/f'{c}.json').read_text())
s['needs_verification_cards']+= [m['id'] for m in meta if card(m['id']).get('needs_verification')]
s['confirmed_p0']=s.get('confirmed_p0',[])+[m['id'] for m in meta if m['priority']=='P0']
s['paths_written']['cards']+= [f"cards/{m['id']}.json" for m in meta]; s['paths_written']['cards_count']=len(s['paths_written']['cards'])
s['paths_written']['sources_updated']=sorted(set(s['paths_written']['sources_updated'])|set(T3))
s['paths_written']['tier3_work_dir']=str(W)+'/ (merge_tier3.py, write_cards.py, ingest_tier3.py, finalize_summary.py, upsert_report.json, new_urls.json, cards_meta.json, week_stats.json, ingest_result.json, backup/)'
s['paths_written']['tier3_merge_script']=str(W/'merge_tier3.py')+' (run 2026-10-07)'
for sid in T3:
  st=(rep.get(sid) or {}).get('status')
  s['fetch_tier_used'][sid]='tier3_computerUse_chromium_ok' if st in ('ok',None) and sid in rep else f'tier3_computerUse_chromium_{st or "missing"}'
s['tier3_merge']={'status':'done','via':'tier3_computerUse_chromium','merged_at':NOWTS,'source_file':str(W/'browser-listings.json'),'script':str(W/'merge_tier3.py'),
 'per_source':{sid:{k:r.get(k) for k in ['status','listed','inserted','refreshed_last_seen','refreshed_by_title','post_count']} for sid,r in rep.items()},
 'notes':NOTES,'cards':meta,
 'ingest':({'cards_ok':ing['cards_ok'],'cards_fail':ing['cards_fail'],'week_2026-10-05_status':ing['week']['status']} if ing else 'not_run')}
s['failures']=[f for f in s['failures'] if not f.startswith('Tier-3 not attempted')]+EXTRA_FAILURES
s['remaining_blockers']=[b for b in s['remaining_blockers'] if not b.startswith('Tier-3')]+EXTRA_BLOCKERS
wk=json.loads((B/'weeks/2026-10-05.json').read_text()); wk2=json.loads((B/'weeks/2026-09-28.json').read_text())
s['week_totals']={'2026-10-05':{'total_cards':wk['total_cards'],'priorities':wk['priorities']},'2026-09-28':{'total_cards':wk2['total_cards'],'priorities':wk2['priorities']}}
ft=s['cards_by_priority']
s['scan_note']=(f"Weekday Blog 應用摘要 2026-10-07 (Wednesday) FINAL. 33 sources (28 tier1/2 + 5 tier-3 via computerUse Chromium). "
 f"New cards {sum(ft.values())}: P0×{ft['P0']} P1×{ft['P1']} P2×{ft['P2']} P3×{ft['P3']} (phase1 {sum(ph1.values())} + tier3 {len(meta)}). "
 f"Confirmed P0: {s['confirmed_p0'] or 'none'}. Ingest: phase1 14/14 + tier3 {(str(ing['cards_ok'])+'/'+str(len(ing['cards']))) if ing else 'not run'}. Not posted to AI Tracker group.")
df=W/'digest-final.md'
if df.exists():
  shutil.copy(B/'weeks/2026-10-07-digest-zh.md',W/'backup'/'2026-10-07-digest-zh.phase1.md')
  (B/'weeks/2026-10-07-digest-zh.md').write_text(df.read_text()); s['digest_zh_Hant']=df.read_text()
s['finalized_at']=NOWTS
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n'); print(s['scan_note'])

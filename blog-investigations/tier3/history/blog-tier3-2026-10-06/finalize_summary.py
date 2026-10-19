import json,datetime,shutil
from pathlib import Path
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-tier3-2026-10-06')
NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
p=B/'weeks/2026-10-06-scan-summary.json'; shutil.copy(p,W/'backup'/'2026-10-06-scan-summary.phase1.json')
s=json.loads(p.read_text()); rep=json.load(open(W/'upsert_report.json')); ing=json.load(open(W/'ingest_result.json')); meta=json.load(open(W/'cards_meta.json'))
s['window']=s['window'].replace(' — PHASE 1 (tier1+tier2 only; tier-3 pending browser)','')+' — FINAL (tier1+tier2 phase 1 + tier-3 computerUse Chromium merge)'
s['phase']='final_tier1_tier2_tier3'; s['sources_scanned']=33; s['sources_pending_browser_merge']=[]
for m,sid in [(meta[0],'snowflake'),(meta[1],'perplexity')]:
  s['inserted'].append({'source':sid,'title':m['title'],'url':m['url'],'date':'2026-10-05','catch_up':False,'card_ref':m['id'],'via':'tier3_computerUse_chromium'})
  s['inserted_titles'].append(m['title'])
  s['new_posts_per_source'][sid]=1; s['new_inwindow_posts_per_source_2026-10-05_plus'][sid]=1
  s['cards_written'].append(m)
s['paths_written']['cards']+= [f"cards/{m['id']}.json" for m in meta]; s['paths_written']['cards_count']=len(s['paths_written']['cards'])
s['paths_written']['sources_updated']=sorted(set(s['paths_written']['sources_updated'])|{'perplexity','meta-ai','snowflake','qwen','microsoft-ai'})
s['paths_written']['tier3_work_dir']='/workspace/blog-tier3-2026-10-06/ (merge_tier3.py [patched: Qwen listing-URL guard + via], merge_tier3.orig.py, write_cards.py, ingest_tier3.py, finalize_summary.py, upsert_report.json, new_urls.json, cards_meta.json, week_stats.json, ingest_result.json, posts/, backup/)'
s['paths_written']['tier3_merge_script']='/workspace/blog-tier3-2026-10-06/merge_tier3.py (dry-run then real run 2026-10-06)'
ft=s.setdefault('fetch_tier_used',{})
for sid in ['perplexity','meta-ai','snowflake','qwen','microsoft-ai']:
  if isinstance(ft.get('tier3'),dict): ft['tier3'][sid]='tier3_computerUse_chromium_ok'
  else: ft[sid]='tier3_computerUse_chromium_ok'
if isinstance(ft.get('tier3'),dict): pass
s['tier3_merge']={'status':'done','via':'tier3_computerUse_chromium','merged_at':NOWTS,
 'source_file':str(W/'browser-listings.json'),'script':str(W/'merge_tier3.py'),
 'guard':'Qwen listing exposes no per-post hrefs (all url=https://qwen.ai/research): entries whose URL equals the source listing URL are never upserted by URL; matched by title only (exact, then unique prefix) and last_seen refreshed. 5/5 matched, 0 inserted, 0 listing-URL posts in store.',
 'per_source':{sid:{'status':r['status'],'listed':r['listed'],'inserted':r['inserted'],'refreshed_last_seen':r['refreshed_last_seen'],'refreshed_by_title':r['refreshed_by_title'],'post_count':r['post_count']} for sid,r in rep.items()},
 'notes':["Perplexity '10 AI Tools for Consultants' (10-01): browser report called it uncatalogued, but it was already in sources/perplexity.json (first_seen 2026-10-02) and already carded P3 (cards/perplexity-ai-tools-consultants-2026-10-01.json, weeks/2026-09-28.json) — only last_seen refreshed, no new card",
  "Perplexity RAG explainer carded from browser listing summary only (curl 403 Cloudflare; body not independently read)",
  "Snowflake post read via curl (200)"],
 'cards':meta,'ingest':{'cards_ok':ing['cards_ok'],'cards_fail':ing['cards_fail'],'week_2026-10-05_status':ing['week']['status']}}
s['cards_by_priority_breakdown']['tier3_merge']={'P0':0,'P1':0,'P2':1,'P3':1}
s['cards_by_priority_breakdown']['final_total']={'P0':0,'P1':4,'P2':4,'P3':3}
s['failures']=[f for f in s['failures'] if not f.startswith('Tier-3 not attempted')]+["Perplexity post curl 403 (Cloudflare) → card from browser summary"]
s['remaining_blockers']=[b for b in s['remaining_blockers'] if not b.startswith('Tier-3')]+[
 "Meta AI: browser listing only 8 posts visible ('Load more' not expanded) — older/hidden posts not re-verified",
 "Qwen: research index exposes no per-post links (JS) — title-matched only; new Qwen posts would need manual URL lookup",
 "Microsoft AI: microsoft.ai/blog listing undated — novelty inferred from known top item (10-01) and 2nd item (09-14)",
 "Perplexity: article pages Cloudflare 403 to curl — tier-3 posts carded from browser summary"]
wk=json.loads((B/'weeks/2026-10-05.json').read_text()); wk2=json.loads((B/'weeks/2026-09-28.json').read_text())
s['week_totals']={'2026-10-05':{'total_cards':wk['total_cards'],'priorities':wk['priorities']},'2026-09-28':{'total_cards':wk2['total_cards'],'priorities':wk2['priorities']}}
s['scan_note']=("Weekday Blog 應用摘要 2026-10-06 (Tuesday) FINAL. 33 sources (28 tier1/2 + 5 tier-3 via computerUse Chromium, all ok). "
 "New cards 11: P0×0 P1×4 P2×4 P3×3 (1 catch-up). No confirmed P0 (Liquid d1 potential P0 → P1 needs_verification). "
 "Tier-3: Snowflake AI Gateway for Advertising P2, Perplexity RAG explainer P3. Ingest done (token set): phase1 9/9 + tier3 2/2 cards, week 2026-10-05 ×2 (200). Not posted to AI Tracker group.")
s['finalized_at']=NOWTS
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({k:s[k] for k in ['phase','fetch_tier_used','tier3_merge','remaining_blockers','week_totals','finalized_at']},ensure_ascii=False,indent=1)[:5000])

#!/usr/bin/env python3
"""Tier-3 card writer for 2026-10-08 (template; run AFTER merge_tier3.py and after reading each new in-window post).
Fill CARDS below (same schema as cards/*.json, e.g. cards/mistral-large-4-preview-2026-10-06.json) plus private keys:
  _source_id (perplexity|meta-ai|snowflake|qwen|microsoft-ai), _category, _tags, _application_relevant (bool).
Effect: writes cards/<id>.json (refuses to overwrite), annotates the matching sources/<sid>.json post (card_ref/category/tags),
        adds cards to weeks/2026-10-05.json (published_at >= 2026-10-05) or weeks/2026-09-28.json (older catch-up),
        rebuilds week stats from card files, updates synthesis header + TIER3_NOTE, refreshes tier-3 post_count in index.json,
        writes cards_meta.json + week_stats.json. Backs up touched files to backup/ first. --dry-run prints only.
"""
import json,datetime,shutil,sys,re
from pathlib import Path
from collections import Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-tier3-2026-10-08')
TODAY='2026-10-08'; VIA='tier3_computerUse_chromium'
T3=('perplexity','meta-ai','snowflake','qwen','microsoft-ai')
DRY='--dry-run' in sys.argv
NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
CARDS=[
 # Fill after reading each new in-window tier-3 post (see new_urls.json from merge_tier3.py). Template:
 # dict(id="snowflake-<slug>-2026-10-07", title="...", url="https://www.snowflake.com/en/blog/<slug>/",
 #      source="Snowflake Blog", published_at="2026-10-07T00:00:00Z", type="application_case_study", priority="P2",
 #      tags=["enterprise","agents"], key_takeaway=["..."], priority_reason="...", digest_focus=False, needs_verification=False,
 #      evidence="browser_listing_summary_only | post body read via curl/WebFetch", first_seen=TODAY, last_seen=TODAY, via=VIA,
 #      _source_id="snowflake", _category="applications", _tags=["enterprise","agents"], _application_relevant=False),
 # model_release_benchmark cards must carry metrics.pricing (real USD per 1M in/out + cached tiers + source_url, else "unpublished") and 1-2 famous benchmarks with deltas.
]
TIER3_NOTE=""   # e.g. "10-08 tier-3 併入：Snowflake …（P2）；Meta AI／Qwen／Microsoft AI／Perplexity 冇新帖。" — appended to weeks/2026-10-05.json synthesis
card=lambda c: json.loads((B/'cards'/f'{c}.json').read_text())
if not DRY:
  (W/'backup').mkdir(parents=True,exist_ok=True)
  for f in ['index.json','weeks/2026-10-05.json','weeks/2026-09-28.json']+[f'sources/{s}.json' for s in T3]:
    shutil.copy(B/f, W/'backup'/(f.replace('/','__')+'.pre-write_cards'))
meta=[]
for c in CARDS:
  sid=c.pop('_source_id'); cat=c.pop('_category','unknown'); tags=c.pop('_tags',c.get('tags',[])); appr=c.pop('_application_relevant',c['priority'] in ('P0','P1'))
  p=B/'cards'/f"{c['id']}.json"
  assert not p.exists(), f"card exists {c['id']}"
  meta.append({'id':c['id'],'priority':c['priority'],'type':c['type'],'url':c['url'],'title':c['title'],'source_id':sid,'date':c['published_at'][:10]})
  if DRY: continue
  p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
  sp=B/'sources'/f'{sid}.json'; d=json.loads(sp.read_text()); hit=False
  for x in d['posts']:
    if x['url'].rstrip('/')==c['url'].rstrip('/'):
      x['category']=cat; x['tags']=tags; x['card_ref']=c['id']; x['application_relevant']=appr; hit=True
  if not hit: print('WARN: source post not found for',c['id'],sid)
  sp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def restat(pack):
  ids=[c for c in dict.fromkeys(pack['card_ids']) if (B/'cards'/f'{c}.json').exists()]
  pack['card_ids']=ids; types={}
  for c in ids: types.setdefault(card(c)['type'],[]).append(c)
  pack['cards_by_type']=types
  pack['type_summaries']={t:{'count':len(v),'card_ids':v,'note':f'{len(v)} cards of type {t} this week'} for t,v in types.items()}
  pr=Counter(card(c)['priority'] for c in ids); pack['priorities']={k:pr.get(k,0) for k in ['P0','P1','P2','P3']}
  pack['total_cards']=len(ids); pack['generated_at']=NOWTS
nx_p=B/'weeks/2026-10-05.json'; nx=json.loads(nx_p.read_text())
wk_p=B/'weeks/2026-09-28.json'; wk=json.loads(wk_p.read_text())
for m in meta:
  tgt=nx if m['date']>='2026-10-05' else wk
  if m['id'] not in tgt['card_ids']: tgt['card_ids'].append(m['id'])
if DRY:
  print('DRY RUN — would write',len(meta),'cards:',json.dumps(meta,ensure_ascii=False,indent=1)); sys.exit(0)
restat(nx); restat(wk)
p=nx['priorities']
syn=nx['synthesis'].replace('（截至 10-08 phase 1：tier1+tier2；10-08 tier-3 browser 待併入）','（截至 10-08 final：tier1+tier2+tier3）')
syn=re.sub(r'：\d+ cards（P0:\d+ P1:\d+ P2:\d+ P3:\d+）',f"：{nx['total_cards']} cards（P0:{p['P0']} P1:{p['P1']} P2:{p['P2']} P3:{p['P3']}）",syn,count=1)
if not TIER3_NOTE: TIER3_NOTE='10-08 tier-3 併入：'+('、'.join(f"{m['title']}（{m['priority']}）" for m in meta) if meta else '5 個 tier-3 來源冇新帖')+'。'
if TIER3_NOTE not in syn: syn=syn.rstrip()+' '+TIER3_NOTE
nx['synthesis']=syn
nx_p.write_text(json.dumps(nx,ensure_ascii=False,indent=2)+'\n'); wk_p.write_text(json.dumps(wk,ensure_ascii=False,indent=2)+'\n')
idx=json.loads((B/'index.json').read_text())
for s in idx['sources']:
  if s['id'] in T3:
    s['post_count']=len(json.loads((B/'sources'/f"{s['id']}.json").read_text())['posts']); s['updated_at']=NOWTS
idx['updated_at']=max(idx['updated_at'],NOWTS)
(B/'index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n')
json.dump(meta,open(W/'cards_meta.json','w'),ensure_ascii=False,indent=1)
stats={'week_2026-10-05':{'total_cards':nx['total_cards'],'priorities':nx['priorities'],'added_card_ids':[m['id'] for m in meta if m['date']>='2026-10-05']},
 'week_2026-09-28':{'total_cards':wk['total_cards'],'priorities':wk['priorities'],'added_card_ids':[m['id'] for m in meta if m['date']<'2026-10-05']},
 'latest_week':idx['latest_week'],'index_updated_at':idx['updated_at'],
 'tier3_post_counts':{s['id']:s['post_count'] for s in idx['sources'] if s['id'] in T3}}
json.dump(stats,open(W/'week_stats.json','w'),ensure_ascii=False,indent=2); print(json.dumps(stats,ensure_ascii=False,indent=1))

#!/usr/bin/env python3
"""Tier-3 card writer for 2026-10-07 (template; run AFTER merge_tier3.py and after reading each new in-window post).
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
W=Path('/workspace/blog-tier3-2026-10-07')
TODAY='2026-10-07'; VIA='tier3_computerUse_chromium'
T3=('perplexity','meta-ai','snowflake','qwen','microsoft-ai')
DRY='--dry-run' in sys.argv
NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
CARDS=[
 dict(id="perplexity-ai-collaboration-tools-2026-10-06", title="10 Best AI Collaboration Tools", url="https://www.perplexity.ai/hub/blog/ai-collaboration-tools",
      source="Perplexity", published_at="2026-10-06T00:00:00Z", type="application_case_study", priority="P3",
      tags=["enterprise","use-case"],
      key_takeaway=[
        "Ideas-category roundup (no product launch): ten collaboration tools with AI features — Slack, Loom, Confluence, Airtable, Notion, ClickUp, Asana, Monday.com, Trello, Miro — each with use case, AI capabilities and which pricing tier includes the AI features",
        "Intro pitches Perplexity Projects/Enterprise: Enterprise Projects support up to 9,999 contributors with permission-aware context from Slack, Google Drive, GitHub and Notion; also mentions the Comet browser (restated positioning, not a new launch)",
        "No benchmarks and no new Perplexity prices (per browser listing summary; article body not independently read — curl 403 Cloudflare)"],
      priority_reason="Generic SEO listicle with no new capability, data or engineering detail; the 9,999-contributor Enterprise Projects figure is restated product marketing, not a changelog/launch. Same pattern as the 10-05 RAG explainer and 10-01 consultants listicle → P3 (low signal).",
      evidence="browser_listing_summary_only (computerUse Chromium); curl 403 Cloudflare",
      digest_focus=False, needs_verification=False,
      first_seen=TODAY, last_seen=TODAY, via=VIA, _source_id="perplexity", _category="applications", _tags=["enterprise","use-case"], _application_relevant=False),
]
TIER3_NOTE="10-07 tier-3 併入：Perplexity「10 Best AI Collaboration Tools」SEO 清單文（P3）；Snowflake／Meta AI／Qwen／Microsoft AI 冇新帖。"   # e.g. "10-07 tier-3 併入：Snowflake …（P2）。" — appended to weeks/2026-10-05.json synthesis
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
syn=nx['synthesis'].replace('（截至 10-07 phase 1：tier1+tier2；10-07 tier-3 browser 待併入）','（截至 10-07 final：tier1+tier2+tier3）')
syn=re.sub(r'：\d+ cards（P0:\d+ P1:\d+ P2:\d+ P3:\d+）',f"：{nx['total_cards']} cards（P0:{p['P0']} P1:{p['P1']} P2:{p['P2']} P3:{p['P3']}）",syn,count=1)
if TIER3_NOTE and TIER3_NOTE not in syn: syn=syn.rstrip()+' '+TIER3_NOTE
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

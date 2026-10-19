import json,datetime
from pathlib import Path
from collections import Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-tier3-2026-10-05')
NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
meta=json.load(open(W/'cards_meta.json'))
card=lambda c: json.loads((B/'cards'/f'{c}.json').read_text())
def add(pack,m):
  if m['id'] in pack['card_ids']: return 0
  pack['card_ids'].append(m['id']); pack['cards_by_type'].setdefault(m['type'],[]).append(m['id'])
  pack['type_summaries'].setdefault(m['type'],{'count':0,'card_ids':[],'note':''})['card_ids'].append(m['id']); return 1
def restat(pack):
  # rebuild cards_by_type/type_summaries/priorities from card files (dedupe, drop missing)
  ids=[c for c in dict.fromkeys(pack['card_ids']) if (B/'cards'/f'{c}.json').exists()]
  missing=[c for c in pack['card_ids'] if c not in ids]
  pack['card_ids']=ids
  types={}
  for c in ids: types.setdefault(card(c)['type'],[]).append(c)
  pack['cards_by_type']=types
  pack['type_summaries']={t:{'count':len(v),'card_ids':v,'note':f'{len(v)} cards of type {t} this week'} for t,v in types.items()}
  pr=Counter(card(c)['priority'] for c in ids)
  pack['priorities']={k:pr.get(k,0) for k in ['P0','P1','P2','P3']}
  pack['total_cards']=len(ids); pack['generated_at']=NOWTS
  return missing
wk_p=B/'weeks/2026-09-28.json'; wk=json.loads(wk_p.read_text())
nx_p=B/'weeks/2026-10-05.json'; nx=json.loads(nx_p.read_text())
a_wk=a_nx=0
for m in meta:
  d=card(m['id'])['published_at'][:10]
  if d>='2026-10-05': a_nx+=add(nx,m)
  else: a_wk+=add(wk,m)
miss_wk=restat(wk); miss_nx=restat(nx)
p=wk['priorities']
base=wk['synthesis'].split('合計')[0].rstrip('。；; ')
if 'tier-3 browser merge' not in base:
  base+='。10-05 tier-3 browser merge（computerUse Chromium，5 源 OK）補入：Microsoft MAI-Transcribe-2-Streaming（AA 串流 STT 第 1，final AA-WER 2.50%，$0.54／音訊小時，P1，catch-up 10-01）；Perplexity AI maturity（P3）；Meta AI／Qwen／Snowflake 本窗冇新帖'
wk['synthesis']=base+f"。合計 {wk['total_cards']} cards（P0:{p['P0']} P1:{p['P1']} P2:{p['P2']} P3:{p['P3']}）。"
wk_p.write_text(json.dumps(wk,ensure_ascii=False,indent=2)+'\n')
if not nx['card_ids']:
  nx['synthesis']='截至 10-05 掃描（tier1+2＋tier-3 browser merge）未見 2026-10-05 或之後日期嘅帖文；pack 已建立，待之後掃描填入。'
nx_p.write_text(json.dumps(nx,ensure_ascii=False,indent=2)+'\n')
idx=json.loads((B/'index.json').read_text())
switched=False
if nx['total_cards']>0 and idx.get('latest_week')!='2026-10-05': idx['latest_week']='2026-10-05'; switched=True
idx['updated_at']=max(idx['updated_at'],NOWTS)
(B/'index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n')
stats={'week_2026-09-28':{'total_cards':wk['total_cards'],'priorities':wk['priorities'],'week_start':wk['week_start'],'week_end':wk['week_end'],'added_today':20+a_wk,'added_tier3':a_wk,'missing_card_files_dropped':miss_wk},
 'week_2026-10-05':{'total_cards':nx['total_cards'],'priorities':nx['priorities'],'week_start':nx['week_start'],'week_end':nx['week_end'],'added_today':a_nx,'created_today':True,'missing_card_files_dropped':miss_nx},
 'latest_week':idx['latest_week'],'latest_week_switched':switched}
json.dump(stats,open(W/'week_stats.json','w'),ensure_ascii=False,indent=2); print(json.dumps(stats,ensure_ascii=False,indent=1))

import json
from pathlib import Path
from collections import Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-05')
NOWTS='2026-10-05T06:45:00+08:00'
meta=json.load(open(W/'cards_meta.json'))
def date_of(cid): return json.loads((B/'cards'/f'{cid}.json').read_text())['published_at'][:10]
wk_path=B/'weeks/2026-09-28.json'; wk=json.loads(wk_path.read_text())
new_wk=[m for m in meta if date_of(m['id'])<='2026-10-04']
new_next=[m for m in meta if date_of(m['id'])>='2026-10-05']
order={'P0':0,'P1':1,'P2':2,'P3':3}
for m in sorted(new_wk,key=lambda m:order[m['priority']]):
    if m['id'] not in wk['card_ids']:
        wk['card_ids'].append(m['id'])
        wk['cards_by_type'].setdefault(m['type'],[]).append(m['id'])
        ts=wk['type_summaries'].setdefault(m['type'],{'count':0,'card_ids':[],'note':''})
        ts['card_ids'].append(m['id'])
for t,ts in wk['type_summaries'].items():
    ts['count']=len(ts['card_ids']); ts['note']=f"{ts['count']} cards of type {t} this week"
pr=Counter(json.loads((B/'cards'/f'{c}.json').read_text())['priority'] for c in wk['card_ids'])
wk['priorities']={k:pr.get(k,0) for k in ['P0','P1','P2','P3']}
wk['total_cards']=len(wk['card_ids'])
wk['generated_at']=NOWTS
p=wk['priorities']
wk['synthesis']=(wk['synthesis'].split('合計')[0].rstrip('。；; ')+
 f"。10-05 掃描（phase 1，tier1+2）補入：Microsoft ThinkingBox（state-based agent eval，pass@1 vs 20/20）、AutoSynthData、AstaBrief 8B、GPT-6 family model guide、OpenRouter Model Router Benchmarks／tool-schema、Claude Code 2.1.288／2.1.289、Pi 1.0.1／1.0.2；catch-up：Cerebras heterogeneous disaggregation（~5×，待核實）／AlphaSense、Anthropic GLM-5.3 cyber、OpenRouter Security Center。本次無新確認 P0。"
 f"合計 {wk['total_cards']} cards（P0:{p['P0']} P1:{p['P1']} P2:{p['P2']} P3:{p['P3']}）。tier-3 待 browser merge。")
wk_path.write_text(json.dumps(wk,ensure_ascii=False,indent=2)+'\n')
# new week pack 2026-10-05
nxt_path=B/'weeks/2026-10-05.json'
if nxt_path.exists(): nxt=json.loads(nxt_path.read_text())
else:
    nxt={'week_start':'2026-10-05','week_end':'2026-10-11','generated_at':NOWTS,'synthesis':'','type_summaries':{},'card_ids':[],'cards_by_type':{},'priorities':{'P0':0,'P1':0,'P2':0,'P3':0},'total_cards':0}
for m in new_next:
    if m['id'] not in nxt['card_ids']:
        nxt['card_ids'].append(m['id']); nxt['cards_by_type'].setdefault(m['type'],[]).append(m['id'])
        ts=nxt['type_summaries'].setdefault(m['type'],{'count':0,'card_ids':[],'note':''}); ts['card_ids'].append(m['id'])
for t,ts in nxt['type_summaries'].items(): ts['count']=len(ts['card_ids']); ts['note']=f"{ts['count']} cards of type {t} this week"
pr=Counter(json.loads((B/'cards'/f'{c}.json').read_text())['priority'] for c in nxt['card_ids'])
nxt['priorities']={k:pr.get(k,0) for k in ['P0','P1','P2','P3']}; nxt['total_cards']=len(nxt['card_ids']); nxt['generated_at']=NOWTS
nxt['synthesis']=nxt['synthesis'] or ('週一 06:00 phase 1（tier1+2）未見 2026-10-05 日期帖文；pack 已建立，待 tier-3 browser merge／之後掃描填入。' if not nxt['card_ids'] else '')
nxt_path.write_text(json.dumps(nxt,ensure_ascii=False,indent=2)+'\n')
stats={'week_2026-09-28':{'total_cards':wk['total_cards'],'priorities':wk['priorities'],'week_start':wk['week_start'],'week_end':wk['week_end'],'added_today':len(new_wk)},
       'week_2026-10-05':{'total_cards':nxt['total_cards'],'priorities':nxt['priorities'],'week_start':nxt['week_start'],'week_end':nxt['week_end'],'added_today':len(new_next),'created_today':True}}
json.dump(stats,open(W/'week_stats.json','w'),ensure_ascii=False,indent=2); print(json.dumps(stats,ensure_ascii=False))

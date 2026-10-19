import json,datetime
from pathlib import Path
from collections import Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-06')
NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
meta=json.load(open(W/'cards_meta.json'))
card=lambda c: json.loads((B/'cards'/f'{c}.json').read_text())
def add(pack,m):
  if m['id'] in pack['card_ids']: return 0
  pack['card_ids'].append(m['id']); return 1
def restat(pack):
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
a_wk=a_nx=0; to_wk=[]; to_nx=[]
for m in meta:
  d=card(m['id'])['published_at'][:10]
  if d>='2026-10-05': a_nx+=add(nx,m); to_nx.append(m['id'])
  else: a_wk+=add(wk,m); to_wk.append(m['id'])
miss_wk=restat(wk); miss_nx=restat(nx)
if a_wk:
  note='10-06 scan 補入 catch-up：HF「Welcome RL Environments to the hub」（09-28，rl-environment tag＋Harbor／Verifiers／OpenEnv／NeMo Gym 框架標籤，P1）'
  if note not in wk['synthesis']:
    wk['synthesis']=wk['synthesis'].rstrip()+' '+note+f"。合計 {wk['total_cards']} cards（P0:{wk['priorities']['P0']} P1:{wk['priorities']['P1']} P2:{wk['priorities']['P2']} P3:{wk['priorities']['P3']}）。"
wk_p.write_text(json.dumps(wk,ensure_ascii=False,indent=2)+'\n')
p=nx['priorities']
nx['synthesis']=(f"週 10-05～10-11（截至 10-06 phase 1：tier1+tier2；tier-3 browser 待併入）：{nx['total_cards']} cards（P0:{p['P0']} P1:{p['P1']} P2:{p['P2']} P3:{p['P3']}），暫無確認 P0。"
 "主軸：(1) 便宜嘅結構化判斷模型——Liquid d1 decision model（文字＋圖像，一次 forward pass 出機率、唔生成 token，$0.04／1M input；廠商自測 6 個 app 對 GPT-6.1 Sol 4/6 打和或贏、平 19–200×，needs_verification）；"
 "(2) agent sandbox／執行環境——OpenRouter server-side code execution 比較（openrouter:shell／bash beta，$0.0001／秒）、Google CAPS agent 私隱／安全 contextual integrity 報告；"
 "(3) 合規——OpenAI textGrain 文字浮水印（API opt-in、EU ChatGPT／Codex 預設加）；"
 "(4) harness 小版本——Pi 1.0.3（Azure provider 改名 breaking）／1.0.4（--tools glob、--no-mcp）、Codex 0.160.1 backport。")
nx_p.write_text(json.dumps(nx,ensure_ascii=False,indent=2)+'\n')
idx=json.loads((B/'index.json').read_text())
switched=False
if nx['total_cards']>0 and idx.get('latest_week')!='2026-10-05': idx['latest_week']='2026-10-05'; switched=True
idx['updated_at']=max(idx['updated_at'],NOWTS)
(B/'index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n')
stats={'week_2026-09-28':{'total_cards':wk['total_cards'],'priorities':wk['priorities'],'week_start':wk['week_start'],'week_end':wk['week_end'],'added_today':a_wk,'added_card_ids':to_wk,'missing_card_files_dropped':miss_wk},
 'week_2026-10-05':{'total_cards':nx['total_cards'],'priorities':nx['priorities'],'week_start':nx['week_start'],'week_end':nx['week_end'],'added_today':a_nx,'added_card_ids':to_nx,'missing_card_files_dropped':miss_nx},
 'latest_week':idx['latest_week'],'latest_week_switched':switched}
json.dump(stats,open(W/'week_stats.json','w'),ensure_ascii=False,indent=2); print(json.dumps(stats,ensure_ascii=False,indent=1))

import json,datetime
from pathlib import Path
from collections import Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-07')
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
  note='10-07 scan 補入 catch-up'
  if note not in wk['synthesis']:
    wk['synthesis']=wk['synthesis'].rstrip()+' '+note+f"。合計 {wk['total_cards']} cards。"
wk_p.write_text(json.dumps(wk,ensure_ascii=False,indent=2)+'\n')
p=nx['priorities']
prev=nx['synthesis']
nx['synthesis']=(f"週 10-05～10-11（截至 10-07 phase 1：tier1+tier2；10-07 tier-3 browser 待併入）：{nx['total_cards']} cards（P0:{p['P0']} P1:{p['P1']} P2:{p['P2']} P3:{p['P3']}），暫無確認 P0。"
 "主軸：(1) 「decision model」成為新 API 類別——Liquid d1（10-05，$0.04／1M input、唔收 output）之後，OpenAI 10-06 推 Decisions API beta（/v1/decisions，gpt-6-luna，predicate／choice／score 三種typed答案，$0.10／1M input、冇 output／cache 收費，聲稱快 Responses API 約 10×；兩個都 needs_verification）；"
 "(2) 開放權重前沿——Mistral Large 4 preview（~1T MoE、1M context、$1.36／$4.18，DeepSWE 1.1 61.7%、Terminal-Bench 4 28.3%，權重月底先出，needs_verification）；"
 "(3) computer-use agent 訓練模式——OpenAI × Ironclad 合作夥伴託管環境＋rubric＋RL（Astra 55.0% vs Sol 41.6%）；OpenRouter server-side code execution 比較、Google CAPS agent 私隱報告；"
 "(4) harness——Claude Code 2.1.290（長跑 agent／排程可靠性、WebFetch offset、Managed Agents onboarding）／2.1.292（sub-agent effort、stdio MCP 預設 2026-07-28 協議），Pi 1.0.3／1.0.4、Codex 0.160.1、OpenCode 1.18.35；"
 "(5) 合規與其他——OpenAI textGrain 浮水印、Snowflake AI Gateway for Advertising（P2）、NVIDIA CUDA green contexts／AICR／GPUNetIO（P2）、TII Falcon OCR Arabic／Falcon-Emirati（P2）。")
nx['synthesis_prev_2026-10-06_final']=prev
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

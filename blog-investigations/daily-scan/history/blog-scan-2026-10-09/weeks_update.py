import json,datetime
from pathlib import Path
from collections import Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-09')
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
wk_p.write_text(json.dumps(wk,ensure_ascii=False,indent=2)+'\n')
p=nx['priorities']
prev=nx['synthesis']
nx['synthesis']=(
 f"週 10-05～10-11（截至 10-09 makeup：平日 05:59 HKT routine failed，星期六補跑 tier1+tier2；tier-3 未 computerUse）：{nx['total_cards']} cards（P0:{p['P0']} P1:{p['P1']} P2:{p['P2']} P3:{p['P3']}）。"
 "10-09 新主軸：(1) harness 可靠性——Claude Code 2.1.294–296（onFailure:block 失敗即擋、OSC 7501 狀態協定、subagent autoCompactWindow／workflow 統一 model、Read allow_large）；"
 "Codex 0.162.0／0.162.1（managed Git worktree、Guardian Decisions 比較、incremental tools、Bedrock Astra Ultrafast；0.162.1 TUI hotfix）；"
 "(2) 延遲分層——OpenAI Ultrafast tier 對 gpt-6-astra／gpt-6.1-sol 文件寫 broadly available（Sol Ultrafast 短上下文 $12／$60 per 1M；需 WebSocket；API changelog HTML 未見獨立日期條，needs_verification）；"
 "(3) 可量度 agent 應用——Asana StackAI browser agent 用 Astra+Codex 做 144-run 實驗，Sol 優化流程 $0.47／次、快 5×、平 76×（相對原 Model B）；NVIDIA KGMON KDD Cup 2026 Data Agents 亞軍：細模型＋極窄 harness（單一 SQLite schema()/sql()、preflight scout、prose_helper、trace inspector）；"
 "(4) 安全／政策——Anthropic Cyber Mission（CIDP＋免費 OSS Scanner，10-08）；OpenAI 搗破 Category 5／4 false-front IO；Sophos Daybreak MDR 調查 38 分→89 秒；LegalOn 按 Luna／Sol／Astra 分層慳約 65% Codex 成本；"
 "(5) 其他——Ai2 GPU budget／fair-share scheduling；Oracle／Pollo 客戶故事；Anthropic Usage Policy（11-12 生效）同 Genesis Mission $150M。"
 "重查：Mistral Large 4 權重仍未出（HF 只有 Arabic LIDstral／Voxtral）；Liquid hosted d1 仍未上 OpenRouter；Decisions API 仍無 news／benchmark。確認 P0 仍只係 10-07 Haiku 5.5；10-09 無新確認 P0。"
)
nx['synthesis_prev_2026-10-08_final']=prev
nx_p.write_text(json.dumps(nx,ensure_ascii=False,indent=2)+'\n')
idx=json.loads((B/'index.json').read_text())
switched=False
if nx['total_cards']>0 and idx.get('latest_week')!='2026-10-05':
  idx['latest_week']='2026-10-05'; switched=True
idx['updated_at']=NOWTS
(B/'index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n')
stats={'week_2026-09-28':{'total_cards':wk['total_cards'],'priorities':wk['priorities'],'week_start':wk['week_start'],'week_end':wk['week_end'],'added_today':a_wk,'added_card_ids':to_wk,'missing_card_files_dropped':miss_wk},
 'week_2026-10-05':{'total_cards':nx['total_cards'],'priorities':nx['priorities'],'week_start':nx['week_start'],'week_end':nx['week_end'],'added_today':a_nx,'added_card_ids':to_nx,'missing_card_files_dropped':miss_nx},
 'latest_week':idx['latest_week'],'latest_week_switched':switched}
json.dump(stats,open(W/'week_stats.json','w'),ensure_ascii=False,indent=2)
print(json.dumps(stats,ensure_ascii=False,indent=1))

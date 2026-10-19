import json,datetime
from pathlib import Path
from collections import Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-13')
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
nx_p=B/'weeks/2026-10-12.json'; nx=json.loads(nx_p.read_text())
prev_syn=nx.get('synthesis')
a_nx=0; to_nx=[]
for m in meta:
  a_nx+=add(nx,m); to_nx.append(m['id'])
miss_nx=restat(nx)
p=nx['priorities']
nx['synthesis']=(
 f"週 10-12～10-18（截至 10-13 平日掃描 PHASE 1：tier1+tier2；tier-3 pending browser）：{nx['total_cards']} cards"
 f"（P0:{p['P0']} P1:{p['P1']} P2:{p['P2']} P3:{p['P3']}）。"
 "10-13 新卡：(1) Anthropic Frontier Red Team self-replicating AI／IoT weight-based ARA（P1 digest_focus）；"
 "(2) Sakana MASS 多代理自我監督 RSI（27B，score/token 1.2–1.6×；P1 digest_focus）；"
 "(3) NVIDIA ReplaySSM 混合 SSM 解碼（kernel 1.46–1.80×；生產於 GLM-5.3-Flash／Kimi-K3；P1）；"
 "(4) OpenCode 2.0.27（worktree 工具、safer pair --remote；changelog 已入 2.x，npm 仍 1.19.0 → needs_verification）。"
 "重查：Decisions API／Mistral Large 4 權重／Liquid hosted d1／Ultrafast GA 時間戳 —— 四張仍 needs_verification。"
 "上週確認 P0 仍然只有 Haiku 5.5（在 10-05 pack）。tier-3 五源未抓。"
)
nx['synthesis_prev_2026-10-12_final']=prev_syn
nx['phase']='tier1_tier2_pending_tier3'
nx_p.write_text(json.dumps(nx,ensure_ascii=False,indent=2)+'\n')
idx=json.loads((B/'index.json').read_text())
# update fetch.last_scan for tier12 sources
tier12=set(idx['fetch_policy']['tier1_ids']+idx['fetch_policy']['tier2_ids'])
for s in idx['sources']:
  if s['id'] in tier12:
    s.setdefault('fetch',{})['last_scan']=TODAY if False else '2026-10-13'
    # post_count refreshed by upsert already if present on index entry
idx['updated_at']=NOWTS
idx['latest_week']='2026-10-12'
(B/'index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n')
stats={'week_2026-10-12':{'total_cards':nx['total_cards'],'priorities':nx['priorities'],'week_start':nx['week_start'],'week_end':nx['week_end'],'added_today':a_nx,'added_card_ids':to_nx,'missing_card_files_dropped':miss_nx},
 'week_2026-10-05_untouched':True,
 'latest_week':idx['latest_week'],'latest_week_switched':False}
json.dump(stats,open(W/'week_stats.json','w'),ensure_ascii=False,indent=2)
print(json.dumps(stats,ensure_ascii=False,indent=1))

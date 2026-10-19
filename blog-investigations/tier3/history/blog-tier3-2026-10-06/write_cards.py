import json,datetime
from pathlib import Path
from collections import Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-tier3-2026-10-06')
TODAY='2026-10-06'; VIA='tier3_computerUse_chromium'
NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
cards=[
{"id":"snowflake-ai-gateway-advertising-2026-10-05","title":"Building a Governed Path for AI Agents in Advertising",
 "url":"https://www.snowflake.com/en/blog/ai-agents-in-advertising/","source":"Snowflake","published_at":"2026-10-05T00:00:00Z",
 "type":"application_case_study","priority":"P2","tags":["agents","enterprise","workflow"],
 "key_takeaway":[
  "AI Gateway for Advertising (preview): governed MCP integrations for Meta and TikTok ad platforms (more platforms 'coming soon'), connected to Cortex Agents; PMG named as early customer (uses it inside its Alli platform)",
  "Pattern: agent joins live ad-platform signals via MCP (delivery, catalog health, conversion diagnostics) with advertiser data in Snowflake (transactions, inventory, semantic-view business definitions of ROAS/conversion), then recommends a bounded action and executes it under policy with a campaign manager approving/observing each step; recommendation, evidence and approval kept in one shared record",
  "Built on Snowflake's May 2026 acquisition of Natoma's enterprise MCP platform",
  "Evidence: vendor announcement with illustrative retail/media scenarios (e.g. cut a prospecting ad set budget 20%, raise frequency 50% for 7 days) plus PMG/TikTok quotes; no benchmarks, pricing, GA date, or docs on how policy/approval is enforced (pricing: unpublished)"],
 "priority_reason":"Concrete example of a governed write-capable MCP agent loop (semantic layer + live platform tools + per-step human approval + audit record) in a vertical, but preview-only vendor announcement with hypothetical scenarios, no metrics or technical docs, and narrow to advertising → P2 (not P1).",
 "evidence":"vendor_claim; post read via curl 200 (2026-10-06)","digest_focus":False,"first_seen":TODAY,"last_seen":TODAY,"via":VIA},
{"id":"perplexity-rag-examples-2026-10-05","title":"9 RAG Examples Based on Real-World Use Cases and Architectures",
 "url":"https://www.perplexity.ai/hub/blog/rag-example","source":"Perplexity","published_at":"2026-10-05T00:00:00Z",
 "type":"application_case_study","priority":"P3","tags":["rag","use-case"],
 "key_takeaway":[
  "Ideas-category explainer (no product launch): nine RAG use cases — web search, customer support, AI shopping, internal knowledge access, coding assistance, agentic commerce, data analysis, etc.",
  "Frames RAG as addressing hallucination, stale and missing data; contrasts hybrid RAG (keyword + vector/knowledge-graph search) with agentic RAG (LLM-directed retrieval)",
  "No benchmarks, prices or implementation detail (per browser listing summary; article body not independently read — curl blocked by Cloudflare 403)"],
 "priority_reason":"Generic SEO explainer with no new capability, data or engineering detail, consistent with prior Perplexity explainer/listicle cards (e.g. AI maturity, AI tools for consultants) → P3 (low signal).",
 "evidence":"browser_listing_summary_only (computerUse Chromium); curl 403 Cloudflare","digest_focus":False,"first_seen":TODAY,"last_seen":TODAY,"via":VIA},
]
for c in cards: (B/'cards'/f"{c['id']}.json").write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
json.dump([{'id':c['id'],'priority':c['priority'],'type':c['type'],'url':c['url'],'title':c['title']} for c in cards],open(W/'cards_meta.json','w'),ensure_ascii=False,indent=1)
# annotate source posts
for sid,cid,cat,tags in [('snowflake',cards[0]['id'],'applications',['agents','enterprise','workflow']),('perplexity',cards[1]['id'],'applications',['rag','use-case'])]:
  p=B/'sources'/f'{sid}.json'; d=json.loads(p.read_text())
  for x in d['posts']:
    if x['url']==[c for c in cards if c['id']==cid][0]['url']:
      x['category']=cat; x['tags']=tags; x['card_ref']=cid; x['application_relevant']=(sid=='snowflake')
  p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
# week pack
card=lambda c: json.loads((B/'cards'/f'{c}.json').read_text())
nx_p=B/'weeks/2026-10-05.json'; nx=json.loads(nx_p.read_text())
for c in cards:
  if c['id'] not in nx['card_ids']: nx['card_ids'].append(c['id'])
ids=[c for c in dict.fromkeys(nx['card_ids']) if (B/'cards'/f'{c}.json').exists()]
nx['card_ids']=ids; types={}
for c in ids: types.setdefault(card(c)['type'],[]).append(c)
nx['cards_by_type']=types
nx['type_summaries']={t:{'count':len(v),'card_ids':v,'note':f'{len(v)} cards of type {t} this week'} for t,v in types.items()}
pr=Counter(card(c)['priority'] for c in ids); nx['priorities']={k:pr.get(k,0) for k in ['P0','P1','P2','P3']}
nx['total_cards']=len(ids); nx['generated_at']=NOWTS
p=nx['priorities']
nx['synthesis']=(f"週 10-05～10-11（截至 10-06 final：tier1+tier2+tier3）：{nx['total_cards']} cards（P0:{p['P0']} P1:{p['P1']} P2:{p['P2']} P3:{p['P3']}），暫無確認 P0。"
 "主軸：(1) 便宜嘅結構化判斷模型——Liquid d1 decision model（文字＋圖像，一次 forward pass 出機率、唔生成 token，$0.04／1M input；廠商自測 6 個 app 對 GPT-6.1 Sol 4/6 打和或贏、平 19–200×，needs_verification）；"
 "(2) agent sandbox／執行環境——OpenRouter server-side code execution 比較（openrouter:shell／bash beta，$0.0001／秒）、Google CAPS agent 私隱／安全 contextual integrity 報告；"
 "(3) 合規——OpenAI textGrain 文字浮水印（API opt-in、EU ChatGPT／Codex 預設加）；"
 "(4) 受治理嘅 MCP 行動 agent——Snowflake AI Gateway for Advertising（preview，Meta／TikTok MCP＋Cortex Agents，每步人手批准，P2）；"
 "(5) harness 小版本——Pi 1.0.3（Azure provider 改名 breaking）／1.0.4（--tools glob、--no-mcp）、Codex 0.160.1 backport；Perplexity RAG explainer 屬低訊號（P3）。")
nx_p.write_text(json.dumps(nx,ensure_ascii=False,indent=2)+'\n')
idx=json.loads((B/'index.json').read_text())
for s in idx['sources']:
  if s['id'] in ('perplexity','meta-ai','snowflake','qwen','microsoft-ai'):
    s['post_count']=len(json.loads((B/'sources'/f"{s['id']}.json").read_text())['posts']); s['updated_at']=NOWTS
idx['updated_at']=max(idx['updated_at'],NOWTS)
(B/'index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n')
wk=json.loads((B/'weeks/2026-09-28.json').read_text())
# verify 09-28 stats from card files
pr2=Counter(card(c)['priority'] for c in wk['card_ids'] if (B/'cards'/f'{c}.json').exists())
stats={'week_2026-10-05':{'total_cards':nx['total_cards'],'priorities':nx['priorities'],'added_card_ids':[c['id'] for c in cards]},
 'week_2026-09-28':{'total_cards':wk['total_cards'],'priorities':wk['priorities'],'recomputed_from_cards':{k:pr2.get(k,0) for k in ['P0','P1','P2','P3']},'unchanged_by_tier3':True},
 'latest_week':idx['latest_week'],'index_updated_at':idx['updated_at'],
 'tier3_post_counts':{s['id']:s['post_count'] for s in idx['sources'] if s['id'] in ('perplexity','meta-ai','snowflake','qwen','microsoft-ai')}}
json.dump(stats,open(W/'week_stats.json','w'),ensure_ascii=False,indent=2); print(json.dumps(stats,ensure_ascii=False,indent=1))

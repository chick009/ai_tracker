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
 dict(id="perplexity-pplx-embed-v2-late-2026-10-07",
  title="Multimodal embeddings beyond a single vector",
  url="https://www.perplexity.ai/hub/blog/multimodal-embeddings-beyond-a-single-vector",
  source="Perplexity", published_at="2026-10-07T00:00:00Z", type="model_release_benchmark", priority="P1",
  tags=["rag","multimodal","open-weights","benchmark","embeddings"],
  artifacts=["perplexity-ai/pplx-embed-v2-late-9b (Hugging Face)","perplexity-ai/pplx-embed-v2-late-0.6b (Hugging Face)"],
  key_takeaway=[
   "Launch: pplx-embed-v2-late, a late-interaction (ColBERT-style, MaxSim) embedding family that keeps token-level vectors instead of one vector; 0.6B and 9B share one embedding space, so a 0.6B query encoder can query an index built by the 9B model; supports text-to-image retrieval of rendered PDF pages without OCR; weights on Hugging Face",
   "Training data: 186M query-document pairs from 594 datasets in 46 languages (88.3% text-to-text, 8.3% text-to-image, 3.4% text-to-visual-document); 128-d per token vs 2,048 (EVIE-4.5B) / 4,096 (EVIE-8B)",
   "Benchmarks (Perplexity-reported): domain-specific nDCG@10 avg 81.3% (9B, +1.6pp over next model) / 78.0% (0.6B, 0.3pp behind gemini-embedding-2); ViDoRe(V3) Markdown 64.7% / 61.2%; Q2D-Web Recall@1000 (Combined) 74.8% / 73.6% vs previous best 69.3%; visual ViDoRe(V3) 65.2% / 62.3%, within 1.2pp of nemotron-colembed-v2-8b while activating 340M params for images",
   "Pricing: unpublished — Perplexity API pricing page (fetched 2026-10-08) lists only pplx-embed-v1 ($0.004 / $0.03 per 1M tokens) and pplx-embed-context-v1 ($0.008 / $0.05); v2-late is not in the Embeddings API docs, so for now it is self-hosted open weights only"
  ],
  priority_reason="Builder-relevant retrieval model release (open-weight multimodal late-interaction embeddings, small-query-encoder / large-index asymmetry, OCR-free PDF-page retrieval) with comparable benchmarks, but every score is Perplexity-reported, margins vs peers are modest (+1.6pp / −0.3pp on domain nDCG; ~1.2pp gap to nemotron-colembed on visual ViDoRe), multi-vector indexes add storage/serving cost, and there is no hosted API or price yet → P1 (not P0), needs_verification.",
  digest_focus=True, needs_verification=True,
  verification_note="All benchmark numbers come from Perplexity's launch post (as captured in the computerUse browser summary; post body curl 403 Cloudflare); no independent leaderboard check (MTEB / ViDoRe leaderboard) done. Domain-specific nDCG@10 and Q2D-Web suites appear to be Perplexity-curated; 'previous best 69.3%' model not named in the summary. HF repos perplexity-ai/pplx-embed-v2-late-9b / -0.6b exist (HF API createdAt 2026-07-20 / 2026-08-03 UTC, presumably private until launch). No API availability or price.",
  evidence="browser summary of post (computerUse Chromium, post opened); curl 403 Cloudflare; HF API confirms model repos; pricing via WebFetch docs.perplexity.ai/getting-started/pricing 2026-10-08",
  metrics=dict(
   pricing=dict(status="unpublished", currency="USD",
    items=[],
    note="pplx-embed-v2-late (0.6B / 9B) has no API price; not listed on the Perplexity API pricing page or in Embeddings API docs as of 2026-10-08. Open weights on Hugging Face (self-host cost only).",
    reference_existing_api_embeddings=[
     dict(model="pplx-embed-v1-0.6b", dims=1024, input_per_1m=0.004, unit="per 1M tokens", condition="existing v1 model, NOT the new release"),
     dict(model="pplx-embed-v1-4b", dims=2560, input_per_1m=0.03, unit="per 1M tokens", condition="existing v1 model, NOT the new release"),
     dict(model="pplx-embed-context-v1-0.6b", dims=1024, input_per_1m=0.008, unit="per 1M tokens", condition="existing contextualized v1, NOT the new release"),
     dict(model="pplx-embed-context-v1-4b", dims=2560, input_per_1m=0.05, unit="per 1M tokens", condition="existing contextualized v1, NOT the new release")],
    output_per_1m="not_applicable (embeddings)", cached_tier="not_applicable", long_context_tier="unpublished",
    source_url=["https://docs.perplexity.ai/getting-started/pricing"]),
   benchmarks=[
    dict(name="ViDoRe(V3) (visual, avg %)", scores={"pplx-embed-v2-late-9b":65.2,"pplx-embed-v2-late-0.6b":62.3},
     delta="within 1.2pp of nemotron-colembed-v2-8b (comparison direction/which size not specified in summary); ViDoRe(V3) Markdown: 9B 64.7% / 0.6B 61.2%",
     source_url="https://www.perplexity.ai/hub/blog/multimodal-embeddings-beyond-a-single-vector",
     caveat="Perplexity-reported; not checked against the public ViDoRe leaderboard"),
    dict(name="Domain-specific retrieval nDCG@10 (avg %)", scores={"pplx-embed-v2-late-9b":81.3,"pplx-embed-v2-late-0.6b":78.0},
     delta="9B +1.6pp vs next model (unnamed in summary); 0.6B −0.3pp vs gemini-embedding-2",
     source_url="https://www.perplexity.ai/hub/blog/multimodal-embeddings-beyond-a-single-vector",
     caveat="Perplexity-reported suite composition; harness not independently verified"),
    dict(name="Q2D-Web Recall@1000 (Combined judgments, %)", scores={"pplx-embed-v2-late-9b":74.8,"pplx-embed-v2-late-0.6b":73.6,"previous best (unnamed)":69.3},
     delta="+5.5pp (9B) / +4.3pp (0.6B) vs previous best",
     source_url="https://www.perplexity.ai/hub/blog/multimodal-embeddings-beyond-a-single-vector",
     caveat="Perplexity-defined benchmark; previous-best model not named in summary")],
   components=dict(architecture="late-interaction multi-vector (ColBERT-style MaxSim)", sizes="0.6B, 9B (shared embedding space)", per_token_dim=128, image_active_params="340M (per summary)", modalities="text, image, rendered PDF pages (no OCR)", languages=46)),
  first_seen=TODAY, last_seen=TODAY, via=VIA,
  _source_id="perplexity", _category="research", _tags=["rag","multimodal","open-weights","benchmark","embeddings"], _application_relevant=True),
 dict(id="perplexity-rag-vs-llm-2026-10-07",
  title="RAG vs. LLM: Technical Breakdown (Definitions, Differences, Use Cases)",
  url="https://www.perplexity.ai/hub/blog/rag-vs-llm",
  source="Perplexity", published_at="2026-10-07T00:00:00Z", type="application_case_study", priority="P3",
  tags=["rag","explainer"],
  key_takeaway=[
   "Explainer, not a launch: RAG and LLMs are complementary; RAG supplements stale/incomplete parameters with retrieved external data (hallucination, outdated info, lack of verification)",
   "Names naive / modular / advanced RAG; use LLM-only when full context fits in the prompt, RAG for current external sources, specialised domains or internal files",
   "No benchmarks, prices or product announcements (per browser summary; body curl 403 Cloudflare)"
  ],
  priority_reason="Generic SEO explainer with no new capability, data or engineering detail — same pattern as the 10-05 '9 RAG Examples' and 10-06 collaboration-tools listicle → P3 (low signal).",
  digest_focus=False, needs_verification=False,
  evidence="browser_listing_summary_only (computerUse Chromium); curl 403 Cloudflare",
  first_seen=TODAY, last_seen=TODAY, via=VIA,
  _source_id="perplexity", _category="applications", _tags=["rag","explainer"], _application_relevant=False),
 dict(id="snowflake-nzism-restricted-aws-2026-10-07",
  title="Snowflake Completes NZISM Restricted Assessment on Amazon Web Services",
  url="https://www.snowflake.com/en/blog/snowflake-nzism-restricted-assessment-aws-new-zealand/",
  source="Snowflake", published_at="2026-10-07T00:00:00Z", type="application_case_study", priority="P3",
  tags=["enterprise","compliance","public-sector"],
  key_takeaway=[
   "Independent third-party assessment against the New Zealand Information Security Manual (NZISM) for Snowflake on AWS Auckland, aligned to NZ government Restricted-level controls",
   "NZ agencies can reuse Snowflake's assessment artifacts (control mappings, risk documentation) in their own PSR certification & accreditation instead of full-stack audits",
   "Restates existing certs (SOC 1/2 Type 2, ISO 27001, PCI DSS, IRAP, FedRAMP in select deployments, ISO 42001); no new model, feature, price or benchmark"
  ],
  priority_reason="Regional compliance milestone relevant only to NZ public-sector buyers; no product, agent or model change → P3 (routine compliance PR; cf. STACKIT sovereignty integration P2, which shipped an integration).",
  digest_focus=False, needs_verification=False,
  evidence="vendor_claim; post read via curl 200 (2026-10-08)",
  first_seen=TODAY, last_seen=TODAY, via=VIA,
  _source_id="snowflake", _category="applications", _tags=["enterprise","compliance","public-sector"], _application_relevant=False),
]
TIER3_NOTE="10-08 tier-3 併入：Perplexity pplx-embed-v2-late 0.6B／9B（late-interaction 多向量、文字＋圖像／PDF 頁免 OCR 檢索，HF 開放權重；Q2D-Web Recall@1000 74.8%／73.6% vs 前最佳 69.3%，全屬 Perplexity 自報，API 價未公佈 → P1 needs_verification）；Perplexity「RAG vs. LLM」explainer（P3）；Snowflake NZISM Restricted 評估（AWS Auckland，P3）；Meta AI／Qwen／Microsoft AI 冇新帖。"
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

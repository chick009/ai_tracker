import json
from pathlib import Path
from collections import Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-tier3-2026-10-05')
TODAY='2026-10-05'; import datetime
NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
L=json.load(open(W/'browser-listings.json'))
SIDS=['perplexity','meta-ai','snowflake','qwen','microsoft-ai']
extra={
 'https://www.perplexity.ai/hub/blog/ai-maturity':dict(category='applications',tags=['enterprise','thought-leadership'],
   summary="Explainer on AI maturity stages (experimentation → pilots → connected workflows → agent orchestration → transformation); cites McKinsey (~6% AI high performers attribute ≥5% EBIT to AI) and BCG (>60% of top-maturity firms track AI value vs 17% of stagnating).",
   application_relevant=False,digest_focus=False),
 'https://www.perplexity.ai/hub/blog/portable-computer-comes-to-amd-powered-agentic-pcs':dict(category='applications',tags=['agents','product','on-device'],
   summary="Listing-only (title/date via browser 2026-10-05): Perplexity Portable Computer on AMD-powered agentic PCs. Missed by earlier scans (09-24, before catch-up horizon); stored, not carded.",
   application_relevant=True,digest_focus=False),
 'https://microsoft.ai/news/our-first-streaming-transcription-model':dict(category='model_release_benchmark',tags=['multimodal','speech','voice-agents','evals'],
   summary="MAI-Transcribe-2-Streaming (60 langs, partials ~100ms) #1 on Artificial Analysis streaming STT (final AA-WER 2.50% vs Grok Voice Transcribe 2.0 2.73%; first-partial 2.80%); $0.54/audio-hour intro through 2026-12-31. Also MAI-Voice-2.1 ($22/1M chars) and MAI-Voice-2.1-Flash ($15/1M chars, 150ms E2E). Public preview, no SLA.",
   application_relevant=True,digest_focus=True),
 'https://microsoft.ai/news/ode-poetry-mai':dict(category='applications',tags=['use-case','speech'],
   summary="Listing-only (2026-07-09): Ode Poetry app built on MAI audio models. Old; stored for completeness.",
   application_relevant=False,digest_focus=False),
}
idx=json.load(open(B/'index.json'))
report={}
for sid in SIDS:
  p=B/'sources'/f'{sid}.json'; d=json.load(open(p))
  byurl={x['url'].rstrip('/'):x for x in d['posts']}
  ins=[];ref=0
  for lp in L[sid]['posts']:
    u=lp['url'].rstrip('/')
    if u in byurl:
      byurl[u]['last_seen']=TODAY; ref+=1
      if lp.get('summary') and not byurl[u].get('summary'): byurl[u]['summary']=lp['summary']
    else:
      post={'title':lp['title'],'url':lp['url'],'date':lp['date']}
      post.update(extra.get(u,{'category':'unknown','tags':[],'summary':lp.get('summary',''),'application_relevant':False,'digest_focus':False}))
      post['first_seen']=TODAY; post['last_seen']=TODAY; post['fetch_note']='browser_listing_2026-10-05 (computerUse Chromium)'
      d['posts'].append(post); byurl[u]=post; ins.append(lp['title'])
  d['posts'].sort(key=lambda x:x.get('date',''),reverse=True)
  d['updated_at']=NOWTS
  if 'post_count' in d: d['post_count']=len(d['posts'])
  p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
  for s in idx['sources']:
    if s['id']==sid: s['post_count']=len(d['posts']); s['updated_at']=NOWTS
  report[sid]={'inserted':ins,'refreshed_last_seen':ref,'post_count':len(d['posts'])}
idx['updated_at']=max(idx['updated_at'],NOWTS)
(B/'index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n')
json.dump(report,open(W/'upsert_report.json','w'),ensure_ascii=False,indent=1)
print(json.dumps(report,ensure_ascii=False,indent=1))

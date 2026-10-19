#!/usr/bin/env python3
"""Upsert phase1 (+optional tier3) draft cards into blog-watch store for 2026-10-15."""
import json, datetime
from pathlib import Path
from collections import OrderedDict, Counter
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-15')
TODAY='2026-10-15'
NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')

# Map card source field -> store source id
SOURCE_MAP={
 'OpenCode changelog':'opencode-changelog',
 'Claude Code changelog':'claude-code-changelog',
 'NVIDIA Developer Blog':'nvidia-developer',
 'Sakana AI Blog':'sakana',
 'OpenAI News':'openai-news',
 'Allen AI Research':'allen-ai',
 'Hugging Face Blog':'huggingface',
 'Perplexity Blog':'perplexity',
 'Meta AI Blog':'meta-ai',
 'Microsoft AI Blog':'microsoft-ai',
 'Qwen':'qwen',
 'Snowflake Blog':'snowflake',
 'Liquid AI':'liquid-models',
}

draft_dirs=[W/'draft_cards']
if (W/'tier3_draft_cards').exists():
  draft_dirs.append(W/'tier3_draft_cards')

cards=[]
for d in draft_dirs:
  for p in sorted(d.glob('*.json')):
    cards.append(json.loads(p.read_text()))

# Load sources
idx=json.loads((B/'index.json').read_text())
all_ids=[s['id'] for s in idx['sources']]
srcdata={sid: json.loads((B/'sources'/f'{sid}.json').read_text()) for sid in all_ids}

def upsert(sid, post):
  posts=srcdata[sid].setdefault('posts',[])
  for p in posts:
    if p['url'].rstrip('/')==post['url'].rstrip('/'):
      p['last_seen']=TODAY
      return False
  post=dict(post); post.setdefault('first_seen',TODAY); post['last_seen']=TODAY
  posts.insert(0, post); return True

inserted=[]; written=[]
for c in cards:
  sid=SOURCE_MAP.get(c['source'])
  if not sid:
    # try infer from url
    u=c['url']
    for k,v in [('opencode.ai','opencode-changelog'),('claude.com','claude-code-changelog'),
                ('nvidia.com','nvidia-developer'),('sakana.ai','sakana'),('openai.com','openai-news'),
                ('allenai.org','allen-ai'),('huggingface.co','huggingface'),('perplexity.ai','perplexity'),
                ('ai.meta.com','meta-ai'),('microsoft.ai','microsoft-ai'),('qwen','qwen'),
                ('snowflake.com','snowflake'),('liquid.ai','liquid-models')]:
      if k in u: sid=v; break
  assert sid, f'no source map for {c["id"]} source={c["source"]}'
  sp=OrderedDict(title=c['title'], url=c['url'], date=c['published_at'][:10],
    category=c.get('type','engineering'), tags=c.get('tags',[]),
    summary='; '.join(c.get('key_takeaway',[])[:2]) if isinstance(c.get('key_takeaway'),list) else str(c.get('key_takeaway','')),
    application_relevant=c['priority'] in ('P0','P1'), digest_focus=bool(c.get('digest_focus')),
    card_id=c['id'])
  if upsert(sid, sp):
    inserted.append({'source':sid,'title':c['title'],'url':c['url'],'date':sp['date'],'card_ref':c['id']})
  # HF mirror for allenai
  if c['id']=='allenai-hiro-acev2-2026-10-14':
    murl='https://huggingface.co/blog/allenai/hiro-acev2'
    sp2=OrderedDict(sp); sp2['url']=murl; sp2['mirror_of']='allen-ai'
    if upsert('huggingface', sp2):
      inserted.append({'source':'huggingface','title':c['title'],'url':murl,'date':sp['date'],'mirror_of':'allen-ai','card_ref':c['id']})
  # write card if not exists
  cp=B/'cards'/f"{c['id']}.json"
  if not cp.exists():
    c2=dict(c); c2['first_seen']=TODAY; c2['last_seen']=TODAY
    cp.write_text(json.dumps(c2, ensure_ascii=False, indent=2)+'\n')
    written.append(c['id'])
  else:
    # refresh last_seen
    old=json.loads(cp.read_text()); old['last_seen']=TODAY
    cp.write_text(json.dumps(old, ensure_ascii=False, indent=2)+'\n')

# refresh last_seen for existing posts seen in raw fetches (tier12)
# skip heavy refresh — optional

# update source metadata
for sid,d in srcdata.items():
  d['updated_at']=NOWTS
  d['post_count']=len(d.get('posts',[]))
  (B/'sources'/f'{sid}.json').write_text(json.dumps(d, ensure_ascii=False, indent=1)+'\n')
for s in idx['sources']:
  if s['id'] in srcdata:
    s['post_count']=srcdata[s['id']]['post_count']; s['updated_at']=NOWTS
idx['updated_at']=NOWTS
(B/'index.json').write_text(json.dumps(idx, ensure_ascii=False, indent=2)+'\n')

# Update week pack 2026-10-12
week=json.loads((B/'weeks/2026-10-12.json').read_text())
ids=list(week.get('card_ids') or [])
for c in cards:
  if c['id'] not in ids:
    ids.append(c['id'])
week['card_ids']=ids
week['total_cards']=len(ids)
# recount priorities from card files
pri=Counter()
by_type=Counter()
for cid in ids:
  card=json.loads((B/'cards'/f'{cid}.json').read_text())
  pri[card['priority']]+=1
  by_type[card.get('type','unknown')]+=1
week['priorities']=dict(pri)
week['cards_by_type']=dict(by_type)
week['generated_at']=NOWTS
week['phase']='2026-10-15_daily'
(B/'weeks/2026-10-12.json').write_text(json.dumps(week, ensure_ascii=False, indent=2)+'\n')

json.dump({'inserted':inserted,'written':written,'week_total':week['total_cards'],'priorities':dict(pri)}, open(W/'upsert_result.json','w'), ensure_ascii=False, indent=2)
print('inserted', len(inserted), 'written', written, 'week', week['total_cards'], dict(pri))

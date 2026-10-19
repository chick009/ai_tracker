import json, datetime
from pathlib import Path
from urllib.parse import urlparse
from collections import Counter, OrderedDict
import posts_data as P
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-06')
TODAY='2026-10-06'; NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
idx=json.loads((B/'index.json').read_text())
tier12=idx['fetch_policy']['tier1_ids']+idx['fetch_policy']['tier2_ids']
assert not set(tier12)&set(idx['fetch_policy']['tier3_ids'])
RAW={sid:[f'{sid}.html'] for sid in idx['fetch_policy']['tier1_ids']}
RAW.update({'allen-ai':['allen-ai.rss','allen-ai-html.html'],'google-research':['google-research.rss','google-research-html.html'],
 'huggingface':['huggingface.rss','huggingface-list.html'],'mistral':['mistral.rss','mistral-html-list.html'],'nvidia-developer':['nvidia-developer.rss','nvidia-html-list.html'],
 'openai-news':['openai-news.rss'],
 'liquid-engineering':['liquid-sitemap.rss','liquid-blog-list.html'],'liquid-models':['liquid-sitemap.rss','liquid-blog-list.html'],'liquid-research':['liquid-sitemap.rss','liquid-blog-list.html']})
RAW['openrouter'].append('openrouter-feed.rss')
RAW['claude-code-changelog'].append('cc-gh.md')
inserted=[]; refreshed=Counter()
def load(sid): return json.loads((B/'sources'/f'{sid}.json').read_text())
def save(sid,d): (B/'sources'/f'{sid}.json').write_text(json.dumps(d,ensure_ascii=False,indent=1)+'\n')
srcdata={sid:load(sid) for sid in tier12}
for sid in tier12:
    raw=''.join((W/f).read_text(encoding='utf-8',errors='ignore') for f in RAW[sid])
    for p in srcdata[sid].get('posts',[]):
        u=p['url']; pu=urlparse(u); keys=[u, pu.path.rstrip('/')]
        if pu.fragment: keys=[f'id="{pu.fragment}"']
        if any(k and len(k)>3 and k in raw for k in keys):
            p['last_seen']=TODAY; refreshed[sid]+=1
def upsert(sid,post):
    d=srcdata[sid]; posts=d.setdefault('posts',[])
    for p in posts:
        if p['url'].rstrip('/')==post['url'].rstrip('/'):
            p['last_seen']=TODAY; return False
    post=dict(post); post['first_seen']=TODAY; post['last_seen']=TODAY
    posts.insert(0,post); return True
cards=[]
for x in P.POSTS:
    cid=P.CARD_IDS[x['url']]
    sp=OrderedDict(title=x['title'],url=x['url'],date=x['date'],category=x['category'],tags=x['tags'],summary=x['summary'],
        application_relevant=x['priority'] in ('P0','P1'),digest_focus=x['digest_focus'],card_id=cid)
    if x.get('catch_up'): sp['catch_up']=True
    if upsert(x['source'],sp): inserted.append(dict(source=x['source'],title=x['title'],url=x['url'],date=x['date'],catch_up=bool(x.get('catch_up'))))
    card=OrderedDict(id=cid,title=x['title'],url=x['url'],source=x['card_source'],published_at=f"{x['date']}T00:00:00Z",type=x['type'],
        priority=x['priority'],tags=x['tags'])
    if x.get('artifacts'): card['artifacts']=x['artifacts']
    card['key_takeaway']=x['key_takeaway']; card['priority_reason']=x['priority_reason']; card['digest_focus']=x['digest_focus']
    if x['type']=='model_release_benchmark' or x.get('needs_verification'): card['needs_verification']=bool(x.get('needs_verification'))
    if x.get('verification_note'): card['verification_note']=x['verification_note']
    if x.get('catch_up'): card['catch_up']=True
    if x.get('metrics'): card['metrics']=x['metrics']
    if x.get('alt_urls'): card['alt_urls']=x['alt_urls']
    card['first_seen']=TODAY; card['last_seen']=TODAY
    p=B/'cards'/f'{cid}.json'
    assert not p.exists(), f'card exists {cid}'
    p.write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n')
    cards.append(card)
for s in P.SOURCE_ONLY:
    s=dict(s); sid=s.pop('source')
    sp=OrderedDict(title=s['title'],url=s['url'],date=s['date'],category=s['category'],tags=s['tags'],summary=s['summary'],application_relevant=False,digest_focus=s['digest_focus'],
                   catch_up=True,carded=False,not_carded_reason=s['not_carded_reason'])
    if upsert(sid,sp):
        inserted.append(dict(source=sid,title=s['title'],url=s['url'],date=s['date'],catch_up=True,carded=False,not_carded_reason=s['not_carded_reason']))
for sid in tier12:
    d=srcdata[sid]; d['updated_at']=NOWTS
    if 'post_count' in d: d['post_count']=len(d.get('posts',[]))
    save(sid,d)
for s in idx['sources']:
    if s['id'] in tier12:
        s['post_count']=len(srcdata[s['id']].get('posts',[])); s['updated_at']=NOWTS
idx['updated_at']=NOWTS
(B/'index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n')
json.dump(inserted,open(W/'inserted.json','w'),ensure_ascii=False,indent=2)
json.dump([dict(id=c['id'],priority=c['priority'],type=c['type'],url=c['url'],title=c['title']) for c in cards],open(W/'cards_meta.json','w'),ensure_ascii=False,indent=2)
json.dump(dict(refreshed),open(W/'refreshed_last_seen.json','w'),indent=1)
print('inserted',len(inserted),'cards',len(cards)); print(dict(refreshed))
print(Counter(c['priority'] for c in cards)); print(NOWTS)

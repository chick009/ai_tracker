import json,re,html
from pathlib import Path
from urllib.parse import urljoin,urlparse
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
idx=json.load(open(B/'index.json'))
known=set()
for f in (B/'sources').glob('*.json'):
    for p in json.load(open(f)).get('posts',[]):
        known.add(p['url'].rstrip('/').split('?')[0])
for f in (B/'cards').glob('*.json'):
    c=json.load(open(f)); known.add(c['url'].rstrip('/'))
    for u in c.get('alt_urls',[]) or []: known.add(u.rstrip('/'))
json.dump(sorted(known),open('known_urls.json','w'))
src={s['id']:s for s in idx['sources']}
files={sid:f'{sid}.html' for sid in idx['fetch_policy']['tier1_ids']}
files['allen-ai']='allen-ai-html.html'; files['google-research']='google-research-html.html'
out={}
for sid,fn in files.items():
    raw=open(fn,encoding='utf-8',errors='ignore').read()
    base=src[sid]['url']; host=urlparse(base).netloc
    hrefs=set(re.findall(r'href=\\?"([^"\\]+)\\?"',raw))
    new=[]
    for h in hrefs:
        u=urljoin(base,html.unescape(h)).split('?')[0].split('#')[0].rstrip('/')
        pu=urlparse(u)
        if pu.netloc.replace('www.','')!=host.replace('www.',''): continue
        if len(pu.path.strip('/').split('/'))<2: continue
        if u in known: continue
        new.append(u)
    out[sid]=sorted(set(new))
json.dump(out,open('html_links.json','w'),indent=1)
for k,v in out.items(): print(k,len(v),v[:40])

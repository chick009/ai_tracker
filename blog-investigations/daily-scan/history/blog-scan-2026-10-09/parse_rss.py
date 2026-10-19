import json, re, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta
HKT=timezone(timedelta(hours=8))
def d(s):
    if not s: return None
    s=s.strip()
    try: dt=parsedate_to_datetime(s)
    except Exception:
        try: dt=datetime.fromisoformat(s.replace('Z','+00:00'))
        except Exception: return s[:10]
    if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%d')
def strip(t): return re.sub(r'<[^>]+>','',t or '').strip()
out={'meta':{},'items':{}}
for sid in ['huggingface','nvidia-developer','openai-news','mistral','allen-ai','google-research','openrouter-feed']:
    raw=open(f'{sid}.rss','rb').read()
    try: root=ET.fromstring(raw)
    except Exception as e:
        out['meta'][sid]=f'PARSE_FAIL {e}'; continue
    items=[]
    for it in root.iter():
        tag=it.tag.split('}')[-1]
        if tag not in ('item','entry'): continue
        g=lambda n: next((c for c in it if c.tag.split('}')[-1]==n),None)
        def first(*ns):
            for n in ns:
                e=g(n)
                if e is not None: return e
            return None
        t=g('title'); l=first('link'); pd=first('pubDate','published','updated'); de=first('description','summary')
        link = (l.text or l.get('href')) if l is not None else None
        items.append({'title':strip(t.text if t is not None else ''),'url':(link or '').strip(),'date':d(pd.text if pd is not None else None),'summary':strip(de.text if de is not None else '')[:400]})
    items.sort(key=lambda x:x['date'] or '',reverse=True)
    newest=items[0]['date'] if items else None
    flag='' if newest and newest>='2026' else (' STALE' if items else ' EMPTY')
    out['meta'][sid]=f'n={len(items)} newest={newest}{flag}'
    out['items'][sid]=items
# liquid sitemap
raw=open('liquid-sitemap.rss').read()
urls=re.findall(r'<url>\s*<loc>([^<]+)</loc>(?:\s*<lastmod>([^<]+)</lastmod>)?',raw)
out['meta']['liquid-sitemap']=f'urls={len(urls)}'
out['items']['liquid-sitemap']=[{'url':u,'lastmod':m} for u,m in urls]
json.dump(out,open('parsed_rss.json','w'),indent=2,ensure_ascii=False)
print(json.dumps(out['meta'],indent=1))
for sid,its in out['items'].items():
    if sid=='liquid-sitemap':
        for x in its:
            if (x['lastmod'] or '')>='2026-10-01': print(sid,x)
        continue
    for x in its:
        if (x['date'] or '')>='2026-10-01': print(sid,x['date'],x['title'],x['url'])

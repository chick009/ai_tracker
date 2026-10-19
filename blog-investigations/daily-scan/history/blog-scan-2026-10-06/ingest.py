import json,os,sys,urllib.request,datetime
from pathlib import Path
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-06')
BASE='https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1'
TOK=os.environ.get('TRACKER_INGEST_TOKEN','').strip()
if not TOK: print('TOKEN UNSET'); sys.exit(0)
def post(ep,body):
    req=urllib.request.Request(BASE+ep,data=json.dumps(body,ensure_ascii=False).encode(),method='POST',
        headers={'Authorization':'Bearer '+TOK,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=30) as r: return r.status, r.read().decode()[:300]
    except urllib.error.HTTPError as e: return e.code, e.read().decode()[:300]
    except Exception as e: return 0, repr(e)[:300]
ids=[m['id'] for m in json.load(open(W/'cards_meta.json'))]
only=sys.argv[1:] or ids
res={'ran_at':datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'mode':'env_token','cards':[]}
for cid in only:
    c=json.loads((B/'cards'/f'{cid}.json').read_text())
    body={k:c[k] for k in ["id","title","url","source","published_at","type","priority","tags","key_takeaway"] if k in c}
    if 'metrics' in c: body['metrics']=c['metrics']
    st,txt=post('/tracker-cards-ingest',body)
    if st>=400 and 'metrics' in body:
        b2=dict(body); b2.pop('metrics'); st2,txt2=post('/tracker-cards-ingest',b2)
        res['cards'].append({'id':cid,'status':st,'body':txt,'retry_without_metrics':{'status':st2,'body':txt2}}); print(cid,st,'->',st2,txt2[:120]); continue
    res['cards'].append({'id':cid,'status':st,'body':txt}); print(cid,st,txt[:160])
json.dump(res,open(W/'ingest_cards_result.json','w'),ensure_ascii=False,indent=1)

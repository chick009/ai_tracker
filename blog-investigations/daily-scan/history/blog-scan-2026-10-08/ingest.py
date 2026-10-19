import json,os,sys,urllib.request,datetime
from pathlib import Path
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-08')
BASE='https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1'
TOK=os.environ.get('TRACKER_INGEST_TOKEN','').strip()
OUT=B/'weeks/2026-10-08-ingest-result.json'
if not TOK:
    r={'ran_at':datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'mode':'skipped','reason':'TRACKER_INGEST_TOKEN unset'}
    json.dump(r,open(W/'ingest_result.json','w'),indent=1); print('TOKEN UNSET'); sys.exit(0)
def post(ep,body):
    req=urllib.request.Request(BASE+ep,data=json.dumps(body,ensure_ascii=False).encode(),method='POST',
        headers={'Authorization':'Bearer '+TOK,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=30) as r: return r.status, r.read().decode()[:300]
    except urllib.error.HTTPError as e: return e.code, e.read().decode()[:300]
    except Exception as e: return 0, repr(e)[:300]
res={'phase':'phase1_tier1_tier2','ran_at':datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'mode':'env_token','cards':[]}
ids=[m['id'] for m in json.load(open(W/'cards_meta.json'))]
updated=list(json.load(open(W/'rechecks.json')).keys())
res['updated_cards_reingested']=updated
for cid in ids+updated:
    m={'id':cid}
    c=json.loads((B/'cards'/f"{m['id']}.json").read_text())
    body={k:c[k] for k in ["id","title","url","source","published_at","type","priority","tags","key_takeaway"] if k in c}
    if 'metrics' in c: body['metrics']=c['metrics']
    st,txt=post('/tracker-cards-ingest',body)
    ent={'id':m['id'],'status':st,'body':txt}
    if st>=400 and 'metrics' in body:
        b2=dict(body); b2.pop('metrics'); st2,txt2=post('/tracker-cards-ingest',b2); ent['retry_without_metrics']={'status':st2,'body':txt2}
    res['cards'].append(ent); print(m['id'],st,txt[:120])
wk=json.loads((B/'weeks/2026-10-05.json').read_text())
wb={k:wk[k] for k in ['week_start','synthesis','type_summaries']}
st,txt=post('/tracker-weeks-ingest',wb); res['week']={'week_start':wk['week_start'],'status':st,'body':txt,'total_cards':wk['total_cards']}; print('week',st,txt[:200])
ok=lambda c: c['status']==200 or c.get('retry_without_metrics',{}).get('status')==200
res['cards_ok']=sum(1 for c in res['cards'] if ok(c)); res['cards_fail']=len(res['cards'])-res['cards_ok']
OUT.write_text(json.dumps(res,ensure_ascii=False,indent=1)+'\n')
json.dump(res,open(W/'ingest_result.json','w'),ensure_ascii=False,indent=1)
print('ok',res['cards_ok'],'fail',res['cards_fail'])

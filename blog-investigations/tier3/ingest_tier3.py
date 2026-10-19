import json,os,sys,urllib.request,datetime
from pathlib import Path
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-tier3-2026-10-08')
BASE='https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1'
TOK=os.environ.get('TRACKER_INGEST_TOKEN','').strip()
if not TOK: print('TOKEN UNSET'); sys.exit(1)
def post(ep,body):
    req=urllib.request.Request(BASE+ep,data=json.dumps(body,ensure_ascii=False).encode(),method='POST',
        headers={'Authorization':'Bearer '+TOK,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=30) as r: return r.status, r.read().decode()[:300]
    except urllib.error.HTTPError as e: return e.code, e.read().decode()[:300]
    except Exception as e: return 0, repr(e)[:300]
res={'phase':'tier3_merge','ran_at':datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'mode':'env_token','cards':[]}
for m in json.load(open(W/'cards_meta.json')):
    c=json.loads((B/'cards'/f"{m['id']}.json").read_text())
    body={k:c[k] for k in ["id","title","url","source","published_at","type","priority","tags","key_takeaway"] if k in c}
    if 'metrics' in c: body['metrics']=c['metrics']
    st,txt=post('/tracker-cards-ingest',body); res['cards'].append({'id':m['id'],'status':st,'body':txt}); print(m['id'],st,txt[:200])
wk=json.loads((B/'weeks/2026-10-05.json').read_text())
wb={k:wk[k] for k in ['week_start','synthesis','type_summaries']}
st,txt=post('/tracker-weeks-ingest',wb); res['week']={'week_start':wk['week_start'],'status':st,'body':txt,'total_cards':wk['total_cards']}; print('week',st,txt[:200])
res['cards_ok']=sum(1 for c in res['cards'] if c['status']==200); res['cards_fail']=len(res['cards'])-res['cards_ok']
p=B/'weeks/2026-10-08-ingest-result.json'; d=json.loads(p.read_text())
d.setdefault('phases',{})
if 'phase1_tier1_tier2' not in d['phases']:
    d['phases']['phase1_tier1_tier2']={k:d[k] for k in ['ran_at','cards_ok','cards_fail'] if k in d}|{'week_status':d.get('week',{}).get('status')}
d['phases']['tier3_merge']=res
d['totals']={'cards_ok':d.get('cards_ok',0)+res['cards_ok'],'cards_fail':d.get('cards_fail',0)+res['cards_fail'],'week_2026-10-05_posts':2,'phase1_cards_note':'phase1 cards_ok includes 3 rechecked cards','last_week_status':res['week']['status']}
p.write_text(json.dumps(d,ensure_ascii=False,indent=1)+'\n')
json.dump(res,open(W/'ingest_result.json','w'),ensure_ascii=False,indent=1)

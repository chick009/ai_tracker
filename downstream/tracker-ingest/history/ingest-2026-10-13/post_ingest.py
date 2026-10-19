# Usage: python3 post_ingest.py   (refuses if any PENDING remains). Token from env TRACKER_INGEST_TOKEN, never printed.
import os,json,urllib.request,sys
B="https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1"
cards=json.load(open("cards.json")); week=json.load(open("week.json"))
if "PENDING" in json.dumps([cards,week]): sys.exit("Refusing: PENDING placeholders remain")
T=os.environ["TRACKER_INGEST_TOKEN"]
def post(path,body):
    r=urllib.request.Request(B+path,method="POST",data=json.dumps(body,ensure_ascii=False).encode(),headers={"Authorization":"Bearer "+T,"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(r,timeout=60) as x: return x.status,x.read().decode()
    except urllib.error.HTTPError as e: return e.code,e.read().decode()
res=[]
for c in cards:
    s,b=post("/tracker-cards-ingest",c); res.append(dict(id=c["id"],status=s,body=b)); print(c["id"],s,flush=True)
json.dump(res,open("cards-responses.json","w"),ensure_ascii=False,indent=1)
s,b=post("/tracker-weeks-ingest",week); json.dump(dict(status=s,body=b),open("week-response.json","w"),ensure_ascii=False,indent=1); print("week",s)

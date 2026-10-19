import os, json, time, urllib.request
H="https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1/paper-gen-ingest"
T=os.environ["PAPER_GEN_TOKEN"]
papers={
  "opengcua":"https://arxiv.org/abs/2610.22200",
  "waypoint-opd":"https://arxiv.org/abs/2610.21601",
  "self-evolving-agent-harness":"https://arxiv.org/abs/2610.18813",
  "fde-gym":"https://arxiv.org/abs/2610.22350",
}
def req(method,url,body=None):
    r=urllib.request.Request(url,method=method,data=json.dumps(body).encode() if body else None,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json"})
    with urllib.request.urlopen(r,timeout=120) as resp: return json.loads(resp.read())
jobs={}
for k,u in papers.items():
    try:
        res=req("POST",H,{"url":u,"pipeline":"fast","model":"deepseek-direct/deepseek-flash"})
        jid=res.get("job_id") or res.get("id") or (res.get("job") or {}).get("id")
        jobs[k]={"url":u,"job_id":jid,"post":res}
    except Exception as e:
        jobs[k]={"url":u,"error":repr(e)}
    print(k,jobs[k].get("job_id"),jobs[k].get("error"),flush=True)
json.dump(jobs,open("jobs.json","w"),indent=1)
deadline=time.time()+40*60
pending={k for k,v in jobs.items() if v.get("job_id")}
while pending and time.time()<deadline:
    time.sleep(30)
    for k in list(pending):
        try: st=req("GET",H+"?job_id="+jobs[k]["job_id"])
        except Exception as e: print(k,"poll err",e,flush=True); continue
        s=st.get("status"); d=st.get("draft") or ""
        print(time.strftime("%H:%M:%S"),k,s,st.get("current_step"),len(d),flush=True)
        if d or s in ("awaiting_approval","done","completed","published","failed","error") or st.get("error"):
            json.dump(st,open(f"{k}.job.json","w"),ensure_ascii=False,indent=1)
            if d: open(f"{k}.draft.md","w").write(d)
            jobs[k]["final_status"]=s; jobs[k]["error_final"]=st.get("error"); jobs[k]["queue_url"]=st.get("queue_url"); jobs[k]["title"]=st.get("title")
            pending.discard(k)
    json.dump(jobs,open("jobs.json","w"),indent=1)
print("DONE pending:",pending,flush=True)

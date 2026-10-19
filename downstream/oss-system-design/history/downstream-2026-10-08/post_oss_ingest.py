# Usage: python3 post_oss_ingest.py  (needs SYSTEM_DESIGN.md + cua-stars.json). Token read from credential file, never printed. POSTs once.
import json,urllib.request,os,sys
if not os.path.exists("SYSTEM_DESIGN.md"): sys.exit("SYSTEM_DESIGN.md missing")
if os.path.exists("oss-ingest-response.json"): sys.exit("Already posted once (oss-ingest-response.json exists)")
md=open("SYSTEM_DESIGN.md").read()
T=json.load(open("/home/box/agent-data/connector-secrets/fb25f88b-1fb9-44f0-992c-2d053545fb83/oss-ingest.json"))["OSS_INGEST_TOKEN"]
st=json.load(open("cua-stars.json"))
summary=open("cua-summary.txt").read().strip() if os.path.exists("cua-summary.txt") else "cua is open-source computer-use infrastructure: drivers, sandboxed VMs/containers across macOS, Linux and Windows, and benchmarks for training, evaluating and generating data with computer-use agents."
body=dict(title="cua",repo_url="https://github.com/trycua/cua",markdown=md,summary=summary,
 tags=["computer-use","ai-agents","virtualization","sandbox","benchmarks","rust"],language=st["language"],stars=int(st["stars"]),status="published")
r=urllib.request.Request("https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1/oss-projects-ingest",method="POST",data=json.dumps(body,ensure_ascii=False).encode(),headers={"Authorization":"Bearer "+T,"Content-Type":"application/json"})
try:
    with urllib.request.urlopen(r,timeout=60) as x: s,b=x.status,x.read().decode()
except urllib.error.HTTPError as e: s,b=e.code,e.read().decode()
json.dump(dict(status=s,body=b,language=body["language"],stars=body["stars"],summary=summary,markdown_chars=len(md)),open("oss-ingest-response.json","w"),ensure_ascii=False,indent=1); print(s,b[:500])

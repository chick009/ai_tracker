# Usage: python3 post_oss_ingest.py SYSTEM_DESIGN.md  (token read from credential file, never printed)
import json,sys,urllib.request
md=open(sys.argv[1]).read()
cred=json.load(open("/home/box/agent-data/connector-secrets/fb25f88b-1fb9-44f0-992c-2d053545fb83/oss-ingest.json"))
T=cred.get("OSS_INGEST_TOKEN") or next(v for v in cred.values() if isinstance(v,str))
gh=json.load(urllib.request.urlopen("https://api.github.com/repos/thedotmack/claude-mem",timeout=30))
body=dict(title="claude-mem",repo_url="https://github.com/thedotmack/claude-mem",markdown=md,
 summary="claude-mem captures what a coding agent does across sessions, compresses it with AI, and injects relevant context back into future sessions.",
 tags=["ai-agents","memory","claude-code","context","typescript"],language=gh["language"],stars=int(gh["stargazers_count"]),status="published")
r=urllib.request.Request("https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1/oss-projects-ingest",method="POST",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+T,"Content-Type":"application/json"})
try:
    with urllib.request.urlopen(r,timeout=60) as x: s,b=x.status,x.read().decode()
except urllib.error.HTTPError as e: s,b=e.code,e.read().decode()
json.dump(dict(status=s,body=b,language=body["language"],stars=body["stars"]),open("oss-ingest-response.json","w"),indent=1); print(s,b[:300])

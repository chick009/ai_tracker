# Token read from credential file, never printed. Stars/language from claude-mem-stars.json.
import json,urllib.request
md=open("claude-mem-SYSTEM_DESIGN.md").read()
cred=json.load(open("/home/box/agent-data/connector-secrets/fb25f88b-1fb9-44f0-992c-2d053545fb83/oss-ingest.json"))
T=cred["OSS_INGEST_TOKEN"]
st=json.load(open("claude-mem-stars.json"))
body=dict(title="claude-mem",repo_url="https://github.com/thedotmack/claude-mem",markdown=md,
 summary="claude-mem is a persistent memory compression system for AI coding agents that captures tool I/O through fail-open lifecycle hooks, compresses it with a secondary observer LLM into structured observations stored in a local SQLite worker (or shared server), and injects a budgeted timeline into later sessions.",
 tags=["ai-agents","memory","claude-code","context","typescript"],language=st["language"],stars=int(st["stars"]),status="published")
r=urllib.request.Request("https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1/oss-projects-ingest",method="POST",data=json.dumps(body,ensure_ascii=False).encode(),headers={"Authorization":"Bearer "+T,"Content-Type":"application/json"})
try:
    with urllib.request.urlopen(r,timeout=60) as x: s,b=x.status,x.read().decode()
except urllib.error.HTTPError as e: s,b=e.code,e.read().decode()
json.dump(dict(status=s,body=b,language=body["language"],stars=body["stars"],summary=body["summary"],markdown_chars=len(md)),open("oss-ingest-response.json","w"),ensure_ascii=False,indent=1); print(s,b[:500])

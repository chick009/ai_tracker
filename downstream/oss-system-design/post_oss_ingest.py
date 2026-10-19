# Usage: python3 post_oss_ingest.py  (needs SYSTEM_DESIGN.md + context-mode-stars.json). Token from credential file, never printed. POSTs once.
import json,urllib.request,os,sys
if not os.path.exists("SYSTEM_DESIGN.md"): sys.exit("SYSTEM_DESIGN.md missing")
if os.path.exists("oss-ingest-response.json"): sys.exit("Already posted once (oss-ingest-response.json exists)")
md=open("SYSTEM_DESIGN.md").read()
T=json.load(open("/home/box/agent-data/connector-secrets/fb25f88b-1fb9-44f0-992c-2d053545fb83/oss-ingest.json"))["OSS_INGEST_TOKEN"]
st=json.load(open("context-mode-stars.json"))
summary=open("context-mode-summary.txt").read().strip() if os.path.exists("context-mode-summary.txt") else "context-mode optimizes coding-agent context windows by sandboxing tool output, persisting session memory, and routing across many agent platforms via MCP and hooks."
body=dict(title="context-mode",repo_url="https://github.com/mksglu/context-mode",markdown=md,summary=summary,
 tags=["context","mcp","coding-agents","hooks","session-memory","typescript"],language=st["language"],stars=int(st["stars"]),status="published")
r=urllib.request.Request("https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1/oss-projects-ingest",method="POST",data=json.dumps(body,ensure_ascii=False).encode(),headers={"Authorization":"Bearer "+T,"Content-Type":"application/json"})
try:
    with urllib.request.urlopen(r,timeout=60) as x: s,b=x.status,x.read().decode()
except urllib.error.HTTPError as e: s,b=e.code,e.read().decode()
json.dump(dict(status=s,body=b,language=body["language"],stars=body["stars"],summary=summary,markdown_chars=len(md)),open("oss-ingest-response.json","w"),ensure_ascii=False,indent=1); print(s,b[:500])

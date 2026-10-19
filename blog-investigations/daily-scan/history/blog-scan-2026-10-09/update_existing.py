# Recheck open needs_verification cards (2026-10-09 makeup).
import json
from pathlib import Path
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-09')
TODAY='2026-10-09'
out={}
def upd(cid,fn):
    p=B/'cards'/f'{cid}.json'; c=json.loads(p.read_text()); before=c.get('needs_verification')
    fn(c); c['last_seen']=TODAY
    p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
    out[cid]={'needs_verification_before':before,'needs_verification_after':c.get('needs_verification'),'recheck':c.get('recheck_2026_10_09')}
def ml4(c):
    c['recheck_2026_10_09']=("HF mistralai API 2026-10-09: newest uploads LIDstral-Arabic + Voxtral-Mini-4B-Realtime-Arabic (created 2026-10-08) — still no Mistral Large 4 weights repo. "
      "OpenRouter still lists mistralai/mistral-large-4-0 at $0.68/$2.09 (cached $0.07). docs.mistral.ai still Public Preview Sale price. needs_verification stays true.")
    c['verification_note']=(c.get('verification_note') or '')+" [10-09 recheck] Weights still absent; Arabic LIDstral/Voxtral uploads are unrelated checkpoints."
def d1(c):
    c['recheck_2026_10_09']=("OpenRouter /api/v1/models fetched 2026-10-09 (~458 models): still no Liquid d1 hosted entry. Liquid sitemap lastmod for d1-open remains 2026-10-07 (no new hosted post). needs_verification stays true.")
    c['verification_note']=(c.get('verification_note') or '')+" [10-09 recheck] Still not on OpenRouter."
def dec(c):
    c['recheck_2026_10_09']=("openai-news RSS newest 2026-10-09 (Sophos/Asana/…); still no Decisions API news post. API changelog HTML extract still lacks a dated Decisions/Ultrafast entry beyond Oct 5 header. Codex 0.162.0 adds Guardian Decisions comparison — adoption, not quality verification. needs_verification stays true.")
    c['verification_note']=(c.get('verification_note') or '')+" [10-09 recheck] Still no news post/benchmark; Codex Guardian Decisions comparison is integration only."
upd('mistral-large-4-preview-2026-10-06',ml4)
upd('liquid-d1-decision-model-2026-10-05',d1)
upd('openai-decisions-api-beta-2026-10-06',dec)
json.dump(out,open(W/'rechecks.json','w'),ensure_ascii=False,indent=2); print(json.dumps(out,indent=1)[:1200])

# Recheck open needs_verification cards (2026-10-14 phase 1).
import json
from pathlib import Path
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-14')
TODAY='2026-10-14'
out={}

def upd(cid, note_key, fn):
    p=B/'cards'/f'{cid}.json'; c=json.loads(p.read_text()); before=c.get('needs_verification')
    fn(c); c['last_seen']=TODAY
    p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
    out[cid]={
      'status': 'unchanged_needs_verification' if c.get('needs_verification') else 'cleared',
      'needs_verification_before': before,
      'needs_verification_after': c.get('needs_verification'),
      'note': c.get(note_key),
    }

def ml4(c):
    note=("Recheck 2026-10-14: Hugging Face mistralai API newest uploads still LIDstral-Arabic / "
          "Voxtral-Mini-4B-Realtime-Arabic (createdAt 2026-10-08); no Mistral Large 4 weights. "
          "OpenRouter still lists mistralai/mistral-large-4-0 at $0.68 / $2.09 per 1M input/output "
          "(cached input $0.07). needs_verification remains true.")
    c['recheck_2026_10_14']=note
    c['verification_note']=(c.get('verification_note') or '')+" [10-14 recheck] Weights still absent; OR price unchanged."

def d1(c):
    note=("Recheck 2026-10-14: OpenRouter /api/v1/models (~461 models) still has no liquid d1 / decision id "
          "(liquid/lfm-2.5-24b-a2b and liquid/lfm-2.5-2.6b:free present; no d1). "
          "liquid.ai sitemap lastmod d1-open 2026-10-07; d1-decision-model 2026-10-09. needs_verification remains true.")
    c['recheck_2026_10_14']=note
    c['verification_note']=(c.get('verification_note') or '')+" [10-14 recheck] Still not on OpenRouter."

def dec(c):
    note=("Recheck 2026-10-14: openai-news RSS newest now 2026-10-13 (Higgsfield customer story) — still no Decisions API news post. "
          "API changelog HTML newest dated header still October 5, 2026 (no Oct 13–14 Decisions entry). "
          "needs_verification remains true.")
    c['recheck_2026_10_14']=note
    c['verification_note']=(c.get('verification_note') or '')+" [10-14 recheck] Still no Decisions news post / changelog header."

def uf(c):
    note=("Recheck 2026-10-14: developers.openai.com API changelog HTML still surfaces October 5, 2026 as newest "
          "dated header (no October 13–14 Ultrafast GA entry). Codex npm latest still 0.162.1; alpha now "
          "0.163.0-alpha.10 (2026-10-13, not carded). Guide still says broadly available. needs_verification remains true "
          "for exact public GA timestamp / independent speed claims.")
    c['recheck_2026_10_14']=note
    c['verification_note']=(c.get('verification_note') or '')+" [10-14 recheck] API changelog still no independent GA date after Oct 5 header."

upd('mistral-large-4-preview-2026-10-06','recheck_2026_10_14',ml4)
upd('liquid-d1-decision-model-2026-10-05','recheck_2026_10_14',d1)
upd('openai-decisions-api-beta-2026-10-06','recheck_2026_10_14',dec)
upd('openai-ultrafast-gpt6-2026-10-09','recheck_2026_10_14',uf)

# Confirm OpenCode 2.0.27 remains cleared; refresh last_seen
p=B/'cards'/'opencode-2-0-27-2026-10-12.json'
c=json.loads(p.read_text())
before=c.get('needs_verification')
assert before is False, before
c['last_seen']=TODAY
c['verification_note']=(c.get('verification_note') or '')+" [10-14] Still cleared; V2 continues on @opencode/cli (now 2.0.28)."
p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
out['opencode-2-0-27-2026-10-12']={
  'status':'confirmed_cleared',
  'needs_verification_before': before,
  'needs_verification_after': False,
  'note':'Already cleared 2026-10-13 via @opencode/cli@2.0.27; refreshed last_seen 2026-10-14; new 2.0.28 carded separately.'
}

json.dump(out,open(W/'rechecks.json','w'),ensure_ascii=False,indent=2)
print(json.dumps(out,indent=1,ensure_ascii=False))

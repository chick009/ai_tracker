# Recheck open needs_verification cards (2026-10-13 phase 1).
import json
from pathlib import Path
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-13')
TODAY='2026-10-13'
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
    note=("Recheck 2026-10-13: Hugging Face mistralai API newest uploads still LIDstral-Arabic / "
          "Voxtral-Mini-4B-Realtime-Arabic (createdAt 2026-10-08); no Mistral Large 4 weights. "
          "OpenRouter still lists mistralai/mistral-large-4-0 at $0.68 / $2.09 per 1M input/output "
          "(cached input $0.07). needs_verification remains true.")
    c['recheck_2026_10_13']=note
    c['verification_note']=(c.get('verification_note') or '')+" [10-13 recheck] Weights still absent; OR price unchanged."
def d1(c):
    note=("Recheck 2026-10-13: OpenRouter /api/v1/models (~459 models) still has no liquid d1 / decision id "
          "(only liquid/lfm-2.5-2.6b:free). liquid.ai sitemap lastmod for d1-open still 2026-10-07; "
          "d1-decision-model 2026-10-05. needs_verification remains true.")
    c['recheck_2026_10_13']=note
    c['verification_note']=(c.get('verification_note') or '')+" [10-13 recheck] Still not on OpenRouter."
def dec(c):
    note=("Recheck 2026-10-13: openai-news RSS newest still 2026-10-09 (Sophos/Asana); no Decisions API news post. "
          "API changelog HTML newest dated header still October 5, 2026 (no Oct 9–13 Decisions/Ultrafast GA entry). "
          "needs_verification remains true.")
    c['recheck_2026_10_13']=note
    c['verification_note']=(c.get('verification_note') or '')+" [10-13 recheck] Still no news post / Oct 9–13 changelog header."
def uf(c):
    note=("Recheck 2026-10-13: developers.openai.com API changelog HTML still surfaces October 5, 2026 as newest "
          "dated header (no October 9–13 Ultrafast GA entry). Codex docs changelog page still has no 0.162/0.163 entry "
          "beyond prior state. Guide still says broadly available. needs_verification remains true for exact public GA "
          "timestamp / independent speed claims.")
    c['recheck_2026_10_13']=note
    c['verification_note']=(c.get('verification_note') or '')+" [10-13 recheck] API changelog still no independent GA date after Oct 5 header."
upd('mistral-large-4-preview-2026-10-06','recheck_2026_10_13',ml4)
upd('liquid-d1-decision-model-2026-10-05','recheck_2026_10_13',d1)
upd('openai-decisions-api-beta-2026-10-06','recheck_2026_10_13',dec)
upd('openai-ultrafast-gpt6-2026-10-09','recheck_2026_10_13',uf)
# also refresh last_seen on today's new opencode card is handled at write time
json.dump(out,open(W/'rechecks.json','w'),ensure_ascii=False,indent=2)
print(json.dumps(out,indent=1,ensure_ascii=False))

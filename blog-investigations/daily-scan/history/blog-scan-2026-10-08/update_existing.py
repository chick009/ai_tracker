# Recheck evidence for open needs_verification cards (2026-10-08). Only real evidence is recorded; needs_verification flips only if resolved.
import json
from pathlib import Path
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-scan-2026-10-08')
TODAY='2026-10-08'
out={}
def upd(cid,fn):
    p=B/'cards'/f'{cid}.json'; c=json.loads(p.read_text()); before=c.get('needs_verification')
    fn(c); c['last_seen']=TODAY
    p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
    out[cid]={'needs_verification_before':before,'needs_verification_after':c.get('needs_verification'),'recheck':c['recheck_2026_10_08']}
def ml4(c):
    c['recheck_2026_10_08']=("OpenRouter /api/v1/models (fetched 2026-10-08) now lists mistralai/mistral-large-4-0 (created 2026-10-06 13:42 UTC) at $0.68 / $2.09 per 1M input/output, cached input $0.07 — i.e. the discounted docs price is what is live on OpenRouter; "
      "docs.mistral.ai/models/mistral-large-4 still labels it 'Public Preview' with list $1.36/$4.18/$0.14 struck through as 'Original price' vs 'Sale price' $0.68/$2.09/$0.07 (sale end date not stated). "
      "Weights: Hugging Face mistralai org (API, newest first) shows no Mistral Large 4 repo (newest Shieldstral-1.0-3B, 2026-07-16); no Mistral news post since 10-06. needs_verification stays true.")
    c['verification_note']=c.get('verification_note','')+" [10-08 recheck] Weights still not on Hugging Face; OpenRouter lists mistral-large-4-0 at the sale price $0.68/$2.09 (cached $0.07)."
    pr=c['metrics']['pricing']; pr.setdefault('items',[]).append({"model":"mistralai/mistral-large-4-0 (OpenRouter)","input_per_1m":0.68,"output_per_1m":2.09,"cached_input_per_1m":0.07,"unit":"per 1M tokens","condition":"OpenRouter listing fetched 2026-10-08; docs label this the 'Sale price' (end date not stated)"})
    srcs=pr.get('source_url',[]); 
    if isinstance(srcs,list) and 'https://openrouter.ai/api/v1/models' not in srcs: srcs.append('https://openrouter.ai/api/v1/models')
def d1(c):
    c['recheck_2026_10_08']=("OpenRouter /api/v1/models (fetched 2026-10-08, 467 models) still has no Liquid d1 entry (only liquid/lfm-2.5-2.6b:free) → OpenRouter availability still unconfirmed. "
      "Related: Liquid released open-weight d1-3B / d1-omni-600M on 10-07 (card liquid-open-d1-2026-10-07) with SQuAD 2.0/BoolQ tables — different checkpoints, does not verify the hosted d1 vendor comparison. needs_verification stays true.")
    c['verification_note']=c.get('verification_note','')+" [10-08 recheck] Still not listed on OpenRouter /api/v1/models."
def dec(c):
    c['recheck_2026_10_08']=("No openai.com/news post about the Decisions API in news RSS (1,254 items, newest 2026-10-07) as of 2026-10-08 ~06:10 HKT; API changelog entry (Oct 6) unchanged. "
      "Third-party adoption: Pi 1.1.0 (10-07) adds GPT-6 Luna as a classifier via the Decisions API — integration evidence only, not quality/latency verification. No benchmark published. needs_verification stays true.")
    c['verification_note']=c.get('verification_note','')+" [10-08 recheck] Still no news post or benchmark; Pi 1.1.0 integrated it."
upd('mistral-large-4-preview-2026-10-06',ml4)
upd('liquid-d1-decision-model-2026-10-05',d1)
upd('openai-decisions-api-beta-2026-10-06',dec)
json.dump(out,open(W/'rechecks.json','w'),ensure_ascii=False,indent=2); print(json.dumps(out,ensure_ascii=False,indent=1)[:1500])

import json
from pathlib import Path
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
T='2026-10-05'
AA='https://artificialanalysis.ai/speech-to-text/streaming'
BLOG='https://microsoft.ai/news/our-first-streaming-transcription-model/'
CAP="Numbers are Artificial Analysis Speech-to-Text (Streaming) leaderboard values as embedded by Microsoft in the launch-post chart (snapshot dated 2026-09-28); AA page fetched 2026-10-05 confirms methodology (AA-WER Streaming = AA-AgentTalk 50% / VoxPopuli 25% / Earnings22 25%, ~8h audio) and lists Microsoft AI as a provider, but chart values were not machine-readable there, so per-model figures are not independently re-read. Leaderboard is live and may shift."
ms={
 "id":"microsoft-mai-transcribe-2-streaming-2026-10-01",
 "title":"Our first streaming transcription model debuts at no. 1 on Artificial Analysis",
 "url":BLOG,
 "source":"Microsoft AI",
 "published_at":"2026-10-01T00:00:00Z",
 "type":"model_release_benchmark",
 "priority":"P1",
 "tags":["multimodal","speech","voice-agents","evals"],
 "artifacts":["MAI-Transcribe-2-Streaming","MAI-Voice-2.1","MAI-Voice-2.1-Flash"],
 "key_takeaway":[
  "MAI-Transcribe-2-Streaming: first MAI streaming STT; 60 languages with continuous auto language detection; first partial hypotheses in just over 100ms, then revised and committed; OpenAI Realtime-compatible WebSocket API + Azure Speech SDK",
  "Artificial Analysis streaming STT (2026-09-28 snapshot): #1 on final AA-WER 2.50% vs Grok Voice Transcribe 2.0 2.73% (−0.23pp), Muse Voice Transcribe 3.06%, ElevenLabs Scribe v2 Realtime 3.59%, GPT Live Transcribe 3.92%, Gemini 3.5 Transcribe Live 4.00%; also lowest first-partial AA-WER 2.80% (Grok 2.0 3.36%) and on the WER-vs-time-to-final Pareto frontier (0.13s to final)",
  "Pricing: $0.54 per audio hour (= $0.009/min, $9 per 1,000 min) introductory through 2026-12-31; post-2026 price unpublished. Same post launches MAI-Voice-2.1 TTS ($22 per 1M chars, 23 languages/26 locales, one voice across languages) and MAI-Voice-2.1-Flash ($15 per 1M chars, 150ms end-to-end latency, vendor claims 55% faster inference / ~60% cheaper than comparable models)",
  "Availability: Microsoft Foundry, MAI Playground, Vercel, Azure Voice Live (LiveKit coming soon); voice models also on OpenRouter. Microsoft Learn marks it public preview without SLA, not recommended for production; regions Central US, Sweden Central, Southeast Asia (East US 2 coming soon)",
  "Vendor-only claims: words appear 2× faster than closest competitor in dictation/subtitling (internal eval); 4,000-listener Turing test 50.3% rated MAI-Voice equal or more human-like than human recordings"
 ],
 "priority_reason":"Real model release with comparable third-party benchmark (#1 AA streaming WER) and published pricing, directly useful for voice-agent builders; but margin over #2 is small (0.23pp), it is a narrow speech-modality component in public preview without SLA, and it does not shift core agent/coding capability or access → P1 per v2 (a speech #1 claim alone is not P0).",
 "digest_focus":True,
 "needs_verification":False,
 "verification_note":"Benchmark values come from Microsoft's embedding of AA data (dated 2026-09-28) and match the model-card memo table (2.5%/2.7%/3.1%...); not independently re-read from the AA live page (charts not machine-readable).",
 "catch_up":True,
 "metrics":{
  "pricing":{
   "status":"published",
   "currency":"USD",
   "items":[
    {"model":"MAI-Transcribe-2-Streaming","price":0.54,"unit":"per hour of audio","derived":"$0.009/min; $9 per 1,000 min","condition":"introductory, through 2026-12-31; later price unpublished"},
    {"model":"MAI-Voice-2.1","price":22.0,"unit":"per 1M characters"},
    {"model":"MAI-Voice-2.1-Flash","price":15.0,"unit":"per 1M characters"}
   ],
   "token_pricing":"not_applicable (audio-hour / character billing)",
   "peer_pricing":"unpublished in post (AA price chart in USD per 1,000 min not captured) — no cost comparison made",
   "source_url":["https://microsoft.ai/pdf/MAI-Transcribe-2-Streaming-Model-Card-Memo.pdf",BLOG],
   "official_pricing_page":"https://azure.microsoft.com/pricing/details/ai-foundry-models/microsoft/ (linked from Microsoft Learn; page not fetched — prices from model card memo + launch post)"
  },
  "benchmarks":[
   {"name":"Artificial Analysis AA-WER Streaming Index — Final Transcription (lower is better)",
    "scores":{"MAI-Transcribe-2-Streaming":"2.50%","Grok Voice Transcribe 2.0 (Streaming)":"2.73%","Muse Voice Transcribe":"3.06%","Cartesia Ink Preview (external endpoints)":"3.11%","ElevenLabs Scribe v2 Realtime":"3.59%","GPT Live Transcribe":"3.92%","Gemini 3.5 Transcribe Live":"4.00%","Azure STT Real-time Transcription":"5.25%","Deepgram Nova-3 Realtime":"6.59%"},
    "delta":"#1 of 28 charted streaming models: −0.23pp vs Grok Voice Transcribe 2.0, −0.56pp vs Muse Voice Transcribe, −1.09pp vs ElevenLabs Scribe v2 Realtime, −1.42pp vs GPT Live Transcribe, −1.50pp vs Gemini 3.5 Transcribe Live; −2.75pp vs Microsoft's own Azure STT real-time",
    "source_url":AA,"via":BLOG,"caveat":CAP},
   {"name":"Artificial Analysis AA-WER Streaming — First Partial after end of speech (lower is better)",
    "scores":{"MAI-Transcribe-2-Streaming":"2.80%","Grok Voice Transcribe 2.0 (Streaming)":"3.36%","Muse Voice Transcribe":"3.57%","ElevenLabs Scribe v2 Realtime":"3.59%","GPT Live Transcribe":"6.35%","Gemini 3.5 Transcribe Live":"5.77%"},
    "delta":"−0.56pp vs Grok Voice Transcribe 2.0; −0.79pp vs ElevenLabs Scribe v2 Realtime",
    "source_url":AA,"via":BLOG,"caveat":CAP},
   {"name":"Artificial Analysis — Time to Final Transcription after speech end (s, lower is better)",
    "scores":{"MAI-Transcribe-2-Streaming":"0.130","Grok Voice Transcribe 2.0 (Streaming)":"0.490","ElevenLabs Scribe v2 Realtime":"0.141","Cartesia Ink Preview (external endpoints)":"0.105","Soniox v5 Real-Time":"0.054","GPT Live Transcribe":"0.812"},
    "delta":"Not the fastest (Soniox 0.054s, Cartesia 0.105s are faster but at 4.50%/3.11% WER); MAI claims Pareto-frontier position on WER vs latency",
    "source_url":AA,"via":BLOG,"caveat":CAP+" Latency values read from the chart data series in the launch post."}
  ]
 },
 "first_seen":T,"last_seen":T
}
px={
 "id":"perplexity-ai-maturity-2026-10-02",
 "title":"AI maturity: what it means for your organization",
 "url":"https://www.perplexity.ai/hub/blog/ai-maturity",
 "source":"Perplexity",
 "published_at":"2026-10-02T00:00:00Z",
 "type":"application_case_study",
 "priority":"P3",
 "tags":["enterprise","thought-leadership"],
 "key_takeaway":[
  "Generic AI-maturity ladder: unstructured experimentation → structured pilots → connected workflows → agent orchestration → business transformation",
  "Cites third-party survey stats only (McKinsey: ~6% 'AI high performers' attribute ≥5% of EBIT to AI; BCG: >60% of highest-maturity firms rigorously track AI value vs 17% of stagnating firms); no new product, API, or measured method"
 ],
 "priority_reason":"Thought-leadership/SEO explainer with secondhand survey stats and no new capability or engineering detail → P3 (low signal).",
 "digest_focus":False,
 "first_seen":T,"last_seen":T
}
for c in (ms,px):
  (B/'cards'/f"{c['id']}.json").write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
json.dump([{'id':c['id'],'priority':c['priority'],'type':c['type'],'url':c['url'],'title':c['title']} for c in (ms,px)],open('/workspace/blog-tier3-2026-10-05/cards_meta.json','w'),ensure_ascii=False,indent=1)
print('ok')

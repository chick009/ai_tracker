#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
OUT = Path('/workspace/blog-scan-2026-10-19')
OUT.mkdir(parents=True, exist_ok=True)
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
jobs = [
  # tier1
  ('anthropic-research','html','https://www.anthropic.com/research'),
  ('anthropic-news','html','https://www.anthropic.com/news'),
  ('cerebras','html','https://www.cerebras.ai/blog'),
  ('claude-code-changelog','html','https://code.claude.com/docs/en/changelog'),
  ('codex-changelog','html','https://developers.openai.com/codex/changelog'),
  ('cognition','html','https://cognition.com/blog'),
  ('cursor-blog','html','https://cursor.com/zh-Hant/blog'),
  ('cursor-changelog','html','https://cursor.com/changelog'),
  ('deepseek','html','https://www.deepseek.com/en/news/'),
  ('glm-zhipu','html','https://www.zhipuai.cn/en/research'),
  ('inco','html','https://inco.ai/blog/'),
  ('minimax','html','https://www.minimax.io/blog'),
  ('openai-publications','html','https://openai.com/research/index/publication/'),
  ('opencode-changelog','html','https://opencode.ai/changelog'),
  ('openrouter','html','https://openrouter.ai/blog/'),
  ('pi-changelog','html','https://pi.dev/news/releases'),
  ('poolside','html','https://poolside.ai/blog'),
  ('sakana','html','https://sakana.ai/blog/'),
  ('salesforce','html','https://www.salesforce.com/blog/'),
  ('xai','html','https://x.ai/news'),
  # tier2
  ('allen-ai','rss','https://medium.com/feed/ai2-blog'),
  ('google-research','rss','https://blog.research.google/atom.xml'),
  ('google-research-feedburner','rss','https://feeds.feedburner.com/blogspot/gJZg'),
  ('openrouter-feed','rss','https://openrouter.ai/blog/feed.xml'),
  ('huggingface','rss','https://huggingface.co/blog/feed.xml'),
  ('mistral','rss','https://mistral.ai/news/rss'),
  ('nvidia-developer','rss','https://developer.nvidia.com/blog/feed'),
  ('openai-news','rss','https://openai.com/news/rss.xml'),
  ('liquid-sitemap','rss','https://www.liquid.ai/sitemap.xml'),
  # tier2 html fallbacks
  ('allen-ai-html','html','https://allenai.org/research'),
  ('google-research-html','html','https://research.google/blog/'),
  ('huggingface-list','html','https://huggingface.co/blog'),
  ('liquid-blog-list','html','https://www.liquid.ai/blog'),
  ('mistral-html-list','html','https://mistral.ai/news/'),
  ('nvidia-html-list','html','https://developer.nvidia.com/blog/'),
  # helpers
  ('cc-gh','md','https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md'),
  ('npm-_anthropic-ai_claude-code','json','https://registry.npmjs.org/@anthropic-ai/claude-code'),
  ('npm-_openai_codex','json','https://registry.npmjs.org/@openai/codex'),
  ('npm-opencode-ai','json','https://registry.npmjs.org/opencode-ai'),
  ('npm-_opencode_cli','json','https://registry.npmjs.org/@opencode/cli'),
  ('npm-anomalyco-opencode','json','https://registry.npmjs.org/opencode'),
  ('npm-_earendil-works_pi','json','https://registry.npmjs.org/@earendil-works/pi'),
  ('npm-_earendil-works_pi-coding-agent','json','https://registry.npmjs.org/@earendil-works/pi-coding-agent'),
  ('npm-_mariozechner_pi-coding-agent','json','https://registry.npmjs.org/@mariozechner/pi-coding-agent'),
  ('oai-api-changelog','html','https://developers.openai.com/api/docs/changelog'),
  ('openrouter-models','json','https://openrouter.ai/api/v1/models'),
  ('mistral-models-docs','html','https://docs.mistral.ai/getting-started/models/models_overview/'),
  ('hf-mistralai','json','https://huggingface.co/api/models?author=mistralai&sort=createdAt&direction=-1&limit=20'),
  ('openai-news-alt','html','https://openai.com/news/'),
  ('codex-gh-releases','html','https://github.com/openai/codex/releases'),
  ('opencode-gh-releases','html','https://github.com/anomalyco/opencode/releases'),
]
results = {}
procs = []
def flush(procs, results):
    for sid2, kind2, url2, out2, st2, p2 in procs:
        code = p2.communicate()[0].decode().strip() or '000'
        st2.write_text(code)
        size = out2.stat().st_size if out2.exists() else 0
        results[sid2] = {'kind':kind2,'url':url2,'status':code,'size':size}
        print(f'{sid2}: {code} size={size}', flush=True)
for sid, kind, url in jobs:
    ext = {'rss':'rss','md':'md','json':'json'}.get(kind,'html')
    out = OUT / f'{sid}.{ext}'
    st = OUT / f'{sid}.status'
    cmd = ['curl','-sL','--max-time','35','-A',UA,'-o',str(out),'-w','%{http_code}',url]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    procs.append((sid, kind, url, out, st, p))
    if len(procs) >= 8:
        flush(procs, results); procs = []
if procs: flush(procs, results)
(OUT/'fetch_results.json').write_text(json.dumps(results, indent=2))
print('DONE', len(results))

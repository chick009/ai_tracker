#!/usr/bin/env python3
import json, subprocess, time
from pathlib import Path
OUT = Path('/workspace/blog-scan-2026-10-02')
OUT.mkdir(parents=True, exist_ok=True)
UA = 'Mozilla/5.0 (compatible; BlogWatch/1.0)'
jobs = [
  # tier1
  ('anthropic-research','html','https://www.anthropic.com/research'),
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
  ('huggingface','rss','https://huggingface.co/blog/feed.xml'),
  ('mistral','rss','https://mistral.ai/news/rss'),
  ('nvidia-developer','rss','https://developer.nvidia.com/blog/feed'),
  ('openai-news','rss','https://openai.com/news/rss.xml'),
  ('liquid-sitemap','rss','https://www.liquid.ai/sitemap.xml'),
  # tier2 html fallbacks
  ('allen-ai-html','html','https://allenai.org/research'),
  ('google-research-html','html','https://research.google/blog/'),
  # tier3 fallbacks
  ('snowflake','html','https://www.snowflake.com/en/blog/'),
  ('meta-ai','html','https://ai.meta.com/blog/'),
  ('microsoft-ai','html','https://microsoft.ai/blog/'),
  ('perplexity','html','https://www.perplexity.ai/hub/blog'),
  ('qwen','html','https://qwen.ai/research'),
  ('qwen-rss','rss','https://qwenlm.github.io/blog/index.xml'),
  ('microsoft-feed','rss','https://microsoft.ai/feed'),
]
results = {}
procs = []
for sid, kind, url in jobs:
    ext = 'rss' if kind == 'rss' else 'html'
    out = OUT / f'{sid}.{ext}'
    st = OUT / f'{sid}.status'
    cmd = ['curl','-sL','--max-time','30','-A',UA,'-o',str(out),'-w','%{http_code}',url]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    procs.append((sid, kind, url, out, st, p))
    if len(procs) >= 8:
        for sid2, kind2, url2, out2, st2, p2 in procs:
            code = p2.communicate()[0].decode().strip() or '000'
            st2.write_text(code)
            size = out2.stat().st_size if out2.exists() else 0
            results[sid2] = {'kind':kind2,'url':url2,'status':code,'size':size}
            print(f'{sid2}: {code} size={size}')
        procs = []
for sid2, kind2, url2, out2, st2, p2 in procs:
    code = p2.communicate()[0].decode().strip() or '000'
    st2.write_text(code)
    size = out2.stat().st_size if out2.exists() else 0
    results[sid2] = {'kind':kind2,'url':url2,'status':code,'size':size}
    print(f'{sid2}: {code} size={size}')
(OUT/'fetch_results.json').write_text(json.dumps(results, indent=2))
print('DONE', len(results))

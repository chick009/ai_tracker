# AI Tracker 跨來源聚合 Trial｜2026-10-19（W43）

Trial only: no Top 10 repost, no cards re-ingest, no Notion writes. Script: `aggregate.py` (run with `--offline` to rebuild from `raw/`).

## 1. 數字
| | |
|---|---|
| Raw collector items（有 link 或可定位） | **46**（X 7 · Reddit 5 · LinkedIn 7 · Blog 7 · HF 10 · GitHub 10） |
| 未計入 | Blog RADAR「OpenAI Decisions API／Mistral Large 4／Liquid d1／Ultrafast GA」：冇貼 link，needs_verification |
| Events after merge | **44** |
| Multi-source events（exact key） | **2** |
| Strong fuzzy candidates（未自動合併） | **1** |
| Unresolved（fetch 失敗） | **0** |
| Resolved but no outbound artifact link | **6**（見 §4） |
| Network／reads | X reads 2 calls（7 posts + 1 quoted post）· lnkd.in 7 + nested 4 · blog pages 7（+2 outbound docs） · GitHub README 10 · ~25s total |

## 2. Multi-source events（exact shared key）
### e02 JevAgentHarness → canonical https://arxiv.org/abs/2610.21412
- 連結 key：`arxiv:2610.21412`
- X（dair_ai，2026-10-18 00:35 HKT）https://x.com/dair_ai/status/2111496216567742892 — post 冇直接 arXiv link，只連 academy.dair.ai/papers/jevagentharness-…-**2610.21412**；key 由 slug 尾嘅 arXiv id 抽出
- LinkedIn（Pascal Biese，2026-10-16 18:25 HKT）https://lnkd.in/p/g3CGpGxv — 作者自己第一個留言 `arXiv: https://arxiv.org/abs/2610.21412v1`
- 額外證據：HF 10-16 issue 都有呢篇（#35/84，18 upvotes，code https://github.com/JevAgentHarness/JevAgentHarness，org 標 UIUC；LinkedIn 寫 Princeton + Google，機構待核）
- LinkedIn 比 X 早約 30 小時

### e01 OpenCode 2.0.32 → canonical https://opencode.ai/changelog#v2-0-32
- 連結 key：`github:anomalyco/opencode`（changelog 頁本身連去 repo）
- Blog https://opencode.ai/changelog#v2-0-32（`product:opencode@2.0.32`）
- GitHub Trending https://github.com/anomalyco/opencode（10-19 06:48 HKT snapshot）

（呢兩組同 Orchestrator Top 10「Dedupe notes」嘅人手合併一樣，script 自動做到。）

## 3. Possible merges（fuzzy，保持分開）
| 強度 | A | B | 共同 token | 判斷 |
|---|---|---|---|---|
| **strong** | e04 Blog Cursor changelog（cloud-agent-canvases-and-environments） | e42 X @cursor_ai canvases 帖 | canvases, cursor, environments | 幾乎肯定同一個 release；X 帖只有 video、冇 outbound link，所以冇 exact key。Top 10 已人手合併 |
| org-only | e21 OpenGCUA | e25 MAI-Gym | tongyi-mai, computer | 同 org（Tongyi-MAI），**唔同 arXiv** → 相關，唔係同一篇 |
| org-only | e04/e42 Cursor | e12 cursor/plugins | cursor | 同公司，唔同 artifact |
| org-only | e05 Claude Code 2.1.302 | e11 anthropics/claude-plugins-official | anthropics | changelog 連 anthropics/claude-code，唔係 plugins repo |
| same-site | e05 Claude Code changelog | e36 Reddit「點解冇人跟 best practices」 | code.claude.com | 同一個 docs site 唔同頁面 |
| org-only | e07 RTX Spark | e29 AMD MI355X／e41 NVIDIA midtraining | nvidia | 只係都講 NVIDIA |

我手動剔走嘅 false positive：「agentic」(AMD↔NVIDIA)、「dair」/「omarsar0」（同一個 X 作者貼好多篇唔同 paper）、`*.github.io` 嘅「github」token。

## 4. 解析狀態
**Unresolved: 0.** 全部 lnkd.in 都解得返去 LinkedIn post，全部 X post 都經 `x` connector 讀到。

**Resolved but no outbound artifact link（事件只得原 post URL）：**
- x5 X @cursor_ai canvases：只有 video（見 §3 strong fuzzy）
- l4 LinkedIn Ollama DeepSeek-V4.1-Flash-1017：純文字公告＋`ollama run` 指令，冇 link
- l5 LinkedIn EmbeddingGemma 2（RealAIzation repost）：主 post 冇 link；頁面上 marktechpost 嗰張 card 屬側欄「相關 post」，冇計
- r1／r2／r4 Reddit self-post（Claude Code 118 runs、Mem0/Zep memory、one MCP→70 GTM tools）

**Canonical URL 換成源頭（全部係真實解析結果）：**
| Event | Collector 原 link | Canonical |
|---|---|---|
| Hy-Memory | x.com/dair_ai/…7746719 | https://arxiv.org/abs/2610.22196 |
| Memorilla | x.com/omarsar0/…4665582 | https://arxiv.org/abs/2610.21375 |
| NVIDIA midtraining | x.com/dair_ai/…4144180 | https://arxiv.org/abs/2610.22019 |
| JevAgentHarness | x.com/dair_ai/…7742892 | https://arxiv.org/abs/2610.21412 |
| Data World | x.com/omarsar0/…9332566 | https://arxiv.org/abs/2610.21656 |
| LangChain Managed Deep Agents | x.com/LangChain/… (quoted @caspar_br → langch.in/mda) | https://docs.langchain.com/langsmith/python/managed-deep-agents-overview |
| AMD MI355X + vLLM | lnkd.in/p/gpNCUsZt | https://vllm.ai/blog/2026-10-16-kimi-k3-mi355x |
| Similitude（Harsh Mandalgi） | lnkd.in/p/gvZ-5hF7 | paper https://doi.org/10.5281/zenodo.23447613 · code https://github.com/harshmandalgi/similitude |
| Netflix semantic IDs | lnkd.in/p/gFn_6jUz | https://arxiv.org/abs/2610.15864 |
| Mollick agentic choice | lnkd.in/p/gXnRyY-r | https://arxiv.org/pdf/2608.16603（作者留言貼嘅 paper） |
| Reddit best practices | reddit | https://code.claude.com/docs/en/best-practices |
| Reddit Warcraft III RL | reddit | https://warlock.ai/blog/warcraftsim-1/ |

## 5. 如果 Top 10 用聚合 events 排會點變
最後排名照舊由編輯決定。Script 只提供三樣嘢：`source_count`（collector 數）、`also_in_hf_issue`（arXiv 喺 HF 當日 issue 出現）、canonical URL。
1. **JevAgentHarness（#10）→ 建議升到 #5–6**：今日只有佢有 3 個獨立信號（X + LinkedIn + HF 10-16 issue #35）。Link 換做 arXiv 2610.21412，再加 code repo JevAgentHarness/JevAgentHarness。
2. **Canonical URL 換 X → arXiv**：#1 Hy-Memory（2610.22196）、#6 Memorilla（2610.21375）、#9 NVIDIA midtraining（2610.22019）、#10 Jev（2610.21412）。排名唔變，但 card／Notion 會指去原 paper，paper-gen 都可以直接攞 arXiv id。
3. **Data World（Radar）→ 可升做 Top 10 候選**：X + HF 10-16 issue（#26/84，27 upvotes，LongCat，code Zhanli-Li/Data-World），2 個信號，多過 #9 NVIDIA midtraining（得 X 1 個）。如果 evidence boost 權重夠，佢可以頂替 #9。
4. **OpenCode 2.0.32（Radar）**：Blog + GitHub Trending exact merge，有 2 個 collector 信號。不過 Top 10 偏 research／agent 機制，我建議留 Radar，但要同 Claude Code 2.1.302 拆開做兩條 event，因為 Claude Code 冇第二個來源。
5. **#4 Cursor**：結果唔變。只靠 strong fuzzy 先合到，script 唔會自動合併，所以人手 confirm 仍然要做。
6. **AMD MI355X（Radar）**：link 由 lnkd.in 換做 vLLM 官方 blog。

## 6. 方法（aggregate.py）
- X：`x` connector `get_posts_by_ids` → `raw/x-posts.json`。抽 entities.urls，去 photo/video，quoted post 另外讀（`raw/x-quoted-*.json`），用 `academy.dair.ai/...-<arxivid>` slug 補 arXiv key。
- LinkedIn：`curl -sIL` 解 lnkd.in，再讀公開 post 頁嘅 ld+json `SocialMediaPosting`。只用主 post 正文、sharedContent、主卡片 article card，同**原作者**自己嘅留言。正文入面嘅 `lnkd.in/<code>` 經 interstitial `external_url_click` 解。
- HF：papers-extract → arxiv／github_repo／project_page。非 HF collector 嘅 arXiv id 會同成個 84 篇 issue 對，用作 evidence，唔當 source。
- Blog：抓頁面，抽 arxiv／github／hf-model link。Repo 或 model 名同 blog title 或 slug 有共同 token 先當 primary（例如 opencode → anomalyco/opencode、beam → reflection/Beam-1.0-*），其餘當 mention，唔參與合併。
- GitHub：key = repo。README 入面嘅 arXiv 只當 mention（ai-memory 引用嘅 2502.12110 唔係佢自己篇 paper）。
- Keys：`arxiv:<id>`（去 version）、`doi:`、`github:owner/repo`（lowercase）、`hf-model:org/name`、`url:host+path`（去 query／fragment）、`product:<name>@<ver>`。用 Union-find 合併有共同 key 嘅 items。
- Fuzzy：title／org token 交集，冇計作者 handle。≥2 個 token 而且 paper id 唔衝突 = strong；只係同 org 或同 site = related。

## Files
- `aggregate.py` · `inputs-2026-10-19.json` · `events.json` · `resolution.json`（每個 item 嘅解析 trace）· `raw/`（cache）

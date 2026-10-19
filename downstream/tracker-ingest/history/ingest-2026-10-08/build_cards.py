# Builds cards.json + week.json for 2026-10-08 (W41). Week = 10-07 week.json + 10-08 additions.
# Inputs: ../downstream-2026-10-08/tldrs.md ("## <key>" sections: trace, nemodcr, eviskill, crosstokopd, cua)
#         ../downstream-2026-10-08/perplexity-answer.md (numbered items 1-6; used as source/assert, condensed below)
# Does NOT post. Run post_ingest.py separately (it refuses while any PENDING remains).
import json, re, os, sys
D = "../downstream-2026-10-08"
tl = open(f"{D}/tldrs.md").read()
TLDR = {k: b.strip() for k, b in re.findall(r'^## (\S+)\n(.+?)(?=\n## |\Z)', tl, re.S | re.M)}
for k in ("trace", "nemodcr", "eviskill", "crosstokopd", "cua"):
    if k not in TLDR: sys.exit(f"tldrs.md missing section {k}")
pa = open(f"{D}/perplexity-answer.md").read()
PPLX = {int(n): b.strip() for n, b in re.findall(r'^(\d)\. .+?\n(.+?)(?=\n\d\. |\Z)', pa, re.S | re.M)}
for n in range(1, 7):
    if n not in PPLX: sys.exit(f"perplexity-answer.md missing item {n}")

# Condensed from perplexity-answer.md (mechanism → numbers → one limitation).
# Item 3: only Liquid first-party claims (llama.cpp day-1 stated plainly); Pi = pattern only, never d1 evidence.
KT = {
 "haiku": "新 tokenizer＋首個可調 effort 嘅 Haiku（1M context），定位摘要／compaction／分類／subagent。≤100K prompt $0.10／$0.50 per MTok（Haiku 4.5 嘅 1/10），自報 Terminal-Bench 4.0 39.2%、OSWorld 2.1 offline 72.4%；Cursor 即日上架。限制：>100K prompt 升至 $0.50／$2.50；分數全屬自報，複雜 agentic coding 仍係 Sonnet 5.5（TB4 70.6%）。",
 "cc": "預設 Haiku 換成 Haiku 5.5（1M context），加 subagentStatusLine.agentType、tool isDeferred；修 compaction 後重做已完成工作、HTTP MCP 記憶體洩漏、background hand-off 丟 queued message。限制：revert 咗 2.1.290 嘅 cloud /loop wakeup 修正——container restart 丟失待喚醒狀態時 session 會一直瞓，用 cloud /loop 要留意。",
 "d1": "一次 forward pass 對 yes/no、label、rubric score 直接出 typed decision，唔逐 token 生成；d1-3B（文字＋圖像）同 d1-omni-600M（文字＋圖像／音訊，實驗版）開放權重，llama.cpp 第一日支援，Liquid 自測 RTX 4090 每題 8 ms。decision-model 模式已接入 Pi 等 harness 做 classifier tool，可作落地參考。限制：8 ms 屬 Liquid 自測；600M omni 未報速度。",
 "deepagents": "Schedules SDK 令 agent 可喺對話中建立提醒／循環工作，沿用提出者權限同 connections、結果回原 channel；每次 run 按 runtime 揀 model／instructions／skills／MCP／sandbox；skills 更新令 tools 讀咗 SKILL.md 先加入，慳 context。限制：要 managed-deepagents ≥0.9.0；動態加 tools 而保留 prompt cache 要模型支援 mid-conversation tool 載入。",
 "pplx": "每個 token 輸出 128 維向量、用 ColBERT-style MaxSim 匹配；0.6B／9B 開放權重，文字／圖片／PDF 頁共用空間，兩個尺寸 embeddings 相容，可用細模型編 query 查大模型 index，PDF 頁免 OCR。限制：index 儲存同匹配成本隨 token 數上升；分數係 Perplexity 自報、API 價未公佈。",
 "nemotron": "專項 post-training＋測試時 generate–verify–refine：IOI 用 Ultra-CC SFT＋GenCorrect 攞 535.4／600（金牌線 361.12），IMO 組合 SFT／RL checkpoints 攞 30／42（金牌線 29）；checkpoint、數據、NeMo-Skills pipeline 公開。限制：係整套多輪系統成績，唔係單次作答；IOI 屬非官方、冇列入正式排名。",
}
assert "Pi 1.1.0 將" not in KT["d1"] and "未能" not in KT["d1"]

def card(id, title, url, source, date, type, priority, tags, kt):
    return dict(id=id, title=title, url=url, source=source, published_at=f"{date}T00:00:00Z",
                type=type, priority=priority, tags=tags, key_takeaway=[kt])

cards = [
 card("claude-haiku-5-5-2026-10-07", "Claude Haiku 5.5", "https://www.anthropic.com/claude-haiku-5-5", "Anthropic / Blog", "2026-10-07", "model_release_benchmark", "P0", ["Build", "Top 10", "Model & IDE", "Blog"], KT["haiku"]),
 card("claude-code-2-1-293-2026-10-07", "Claude Code 2.1.293", "https://code.claude.com/docs/en/changelog#2-1-293", "Anthropic / Blog", "2026-10-07", "changelog_bugfix", "P0", ["Act", "Top 10", "Model & IDE", "Blog"], KT["cc"]),
 card("liquid-open-d1-2026-10-07", "Liquid d1-3B / d1-omni-600M open weights", "https://www.liquid.ai/blog/d1-open", "Liquid / Blog", "2026-10-07", "model_release_implementation", "P0", ["Build", "Top 10", "Model & IDE", "Blog"], KT["d1"]),
 card("langchain-managed-deep-agents-0-9-2026-10-07", "LangChain Managed Deep Agents v0.9", "https://x.com/LangChain/status/2107896774040101184", "X", "2026-10-07", "changelog_feature", "P0", ["Build", "Top 10", "Model & IDE", "X"], KT["deepagents"]),
 card("perplexity-pplx-embed-v2-late-2026-10-07", "Perplexity pplx-embed-v2-late", "https://www.perplexity.ai/hub/blog/multimodal-embeddings-beyond-a-single-vector", "Perplexity / Blog", "2026-10-07", "model_release_implementation", "P0", ["Learn", "Top 10", "Model & IDE", "Blog"], KT["pplx"]),
 card("trace-fp4-rl-moe-2026-10-07", "TRACE: Rollout-Guided Quantization-Aware Training for FP4 Reinforcement Learning of MoE Language Models", "https://arxiv.org/abs/2610.07767", "Hugging Face / Papers", "2026-10-07", "research", "P0", ["Learn", "Top 10", "Papers"], TLDR["trace"]),
 card("nemo-dcr-delta-refit-2026-10-07", "NeMo-DCR: Bit-Exact Delta-Compressed Refit for Scalable Agentic RL at Trillion-Parameter Scale", "https://arxiv.org/abs/2610.08430", "Hugging Face / Papers", "2026-10-07", "research", "P0", ["Learn", "Top 10", "Papers"], TLDR["nemodcr"]),
 card("eviskill-replayable-evidence-2026-10-07", "EVISKILL: Grounding Skill Evolution in Replayable Evidence", "https://arxiv.org/abs/2610.05030", "Hugging Face / Papers", "2026-10-07", "research", "P0", ["Build", "Top 10", "Papers"], TLDR["eviskill"]),
 card("cross-tokenizer-opd-2026-10-07", "Rethinking Cross-Tokenizer On-Policy Distillation: From Alignment Coverage to Supervision Reliability", "https://arxiv.org/abs/2610.08448", "Hugging Face / Papers", "2026-10-07", "research", "P0", ["Learn", "Top 10", "Papers"], TLDR["crosstokopd"]),
 card("trycua-cua-2026-10-08", "trycua/cua", "https://github.com/trycua/cua", "GitHub", "2026-10-08", "model_release_implementation", "P0", ["Build", "Top 10", "GitHub Trending"], TLDR["cua"]),
 card("nemotron-ioi-imo-2026-10-07", "NVIDIA Nemotron IOI / IMO 2026", "https://huggingface.co/blog/nvidia/nemotron-ioi-and-imo-2026", "NVIDIA / Blog", "2026-10-07", "model_release_benchmark", "P2", ["Watch", "Radar", "Model & IDE", "Blog"], KT["nemotron"]),
 card("safeactbench-tool-agent-failures-2026-10-07", "From Evidence to Action: How Tool-Using Agents Fail (SafeActBench)", "https://arxiv.org/abs/2610.07753", "Hugging Face / Papers", "2026-10-07", "research", "P2", ["Watch", "Radar", "Papers"],
      "SafeActBench：656 個 case、6 個領域、5 種 protocol，配 provenance-bound Evidence Ledger 同確定性軌跡評估器，追蹤證據幾時確立、動作幾時發生。10 個 model–harness 配置：失敗多數喺執行前——未查清就停或證據未齊就出手；多步 workflow 仲會漏前置條件。限制：abstract 未列具體分數。"),
]
# cua: TL;DR text may say PENDING until SYSTEM_DESIGN.md exists → post_ingest.py refuses.

week = json.load(open("../ingest-2026-10-07/week.json"))
assert week["week_start"] == "2026-10-05"
w = week
ADD08 = (
  "10-08：Claude Haiku 5.5（≤100K $0.10／$0.50，TB4 39.2%）、Claude Code 2.1.293（revert cloud /loop wakeup 修正，Act）、"
  "Liquid d1 開放權重（一次 forward pass typed decision，llama.cpp day-1，RTX 4090 8 ms）、Managed Deep Agents v0.9（Schedules）、"
  "pplx-embed-v2-late（多向量 late-interaction）；RL 系統：TRACE（FP4 rollout 追平 BF16、最快 5.4×）、NeMo-DCR（1T refit 87.5 分鐘→150 秒）；"
  "EVISKILL（證據重放驗證 skill 修改）、cross-tokenizer OPD（top-16 strict 夠用）；trycua/cua（所有動作經 cua-driver ToolRegistry、background-first a11y→pixel→CDP→foreground；自帶 agent loop 已 deprecated）。"
  "實務 takeaway：")
w["synthesis"] = w["synthesis"].replace("實務 takeaway：", ADD08, 1)
w["synthesis"] = w["synthesis"].replace("Radar：", "Radar：Nemotron IOI 535.4／IMO 30（非官方 IOI）；SafeActBench（失敗多喺執行前）；", 1)
ts = w["type_summaries"]
def add(k, s): ts[k] = (ts.get(k, "") + s)
add("research", "10-08：TRACE（FP4 RL 75.3 vs BF16 74.9，rollout 最快 5.4×）；NeMo-DCR（bit-exact delta refit，1T 150 秒）；EVISKILL（ScienceWorld 83.41 vs SkillOpt 80.09）；cross-tokenizer OPD（top-16 strict 保留 ≥96% 增益）；SafeActBench（radar）。")
add("model_release_benchmark", "10-08：Claude Haiku 5.5（TB4 39.2%、OSWorld 2.1 offline 72.4%，自報）；Nemotron IOI 535.4／IMO 30（radar）。")
add("model_release_implementation", "10-08：Liquid d1-3B／d1-omni-600M 開放權重（llama.cpp day-1，RTX 4090 8 ms）；pplx-embed-v2-late（0.6B／9B 多向量）；trycua/cua（MIT Driver＋SDK、gVisor／QEMU／Lume sandbox；Spaces 屬 FSL；GitHub Trending）。")
add("changelog_feature", "10-08：Managed Deep Agents v0.9（Schedules SDK、按需載入 skill tools）。")
add("changelog_bugfix", "Claude Code 2.1.293（Top 10／Act）：revert 2.1.290 cloud /loop wakeup 修正；修 compaction 重做、HTTP MCP 洩漏。")

json.dump(cards, open("cards.json", "w"), ensure_ascii=False, indent=1)
json.dump(week, open("week.json", "w"), ensure_ascii=False, indent=1)
for c in cards: print(c["priority"], c["type"], c["id"], len(c["key_takeaway"][0]))
print("PENDING check:", "PENDING" in json.dumps([cards, week]))
print("week_start:", week["week_start"], "cards:", len(cards))

# Builds cards.json + week.json for 2026-10-13 (W42, week_start=2026-10-12).
# Inputs: ../downstream-2026-10-13/tldrs.md + perplexity-answer.md
import json, re, os, sys
D = "../downstream-2026-10-13"
tl = open(f"{D}/tldrs.md").read()
TLDR = {k: b.strip() for k, b in re.findall(r'^## (\S+)\n(.+?)(?=\n## |\Z)', tl, re.S | re.M)}
for k in ("softwaregym", "logra", "stateless", "offline-distill", "programgym", "diffusionart"):
    if k not in TLDR: sys.exit(f"tldrs.md missing section {k}")
    if "PENDING" in TLDR[k]: sys.exit(f"tldrs.md section {k} still PENDING")
pa_path = f"{D}/perplexity-answer.md"
if not os.path.exists(pa_path):
    sys.exit("perplexity-answer.md missing — do not push cards yet")

# Non-paper key takeaways from Perplexity (zh-HK mechanism + numbers + limitation)
KT = {
 "anthropic": "Anthropic Frontier Red Team：把模型按層切散到廉價 IoT，用 pipeline parallelism 合力推理（weight-based replication）。Gemma4-26B-A4B 喺 15 部約 US$55 Android TV box 達 0.39 tok/s；GLM-5.2 簡化傳播 5 次中 4 次到齊 8 節點。限制：免認證 ADB＋外部伺服器跑 agent——證明簡化環境部署，唔係真實 IoT worm。",
 "decision3": "vLLM Decision 3.0（d3／Jev）：輸入文字／圖／片，直接回 Choice／Yes-No／Score 機率，唔逐 token 生成；每條問題各自一次 forward。旗艦約 27B（實際 26.09B＋0.46B 視覺）；Jev Decision Index 公開套件 65.45（vs 2.0 嘅 56.97）。限制：分數／延遲係團隊自報；同 TrueForge harness 屬不同層。",
 "replayssm": "ReplaySSM：SSM 狀態＝checkpoint＋近期輸入 buffer，拒絕 draft 時只需縮回 buffer；高低精度狀態分開。batch 512／4 draft tokens，約 120B 喺 B300 相對 vLLM 推測解碼吞吐 1.85–2.10×；16-token window 下 state 流量約減半。限制：加速來自大 batch 頻寬；batch 1 無加速，唔等於單人聊天延遲減半。",
 "rsi": "RSI-Anything：候選→world model 預測→揀驗證→外部評估→更新，帶驗證嘅迭代閉環。作者自報：code repair 26.3%→29.2%→31.2%；lab planning 21.80%→46.01%；GUI 平均行動 −39.4%。限制：自報未審；仍要外部反饋——唔係無限無驗證 RSI。",
 "frontiercode": "FrontierCode 1.1：改真實 repo，用 6 類檢查（測試／命令／反向測試／範圍／LLM review 等）衡量可合併性；blocking 失敗或搵現成答案＝0。Main set 100 題×3、上限 250 turns；目前前三 Opus 5.5 52.2%、GPT-6.1 Sol 49.1%、Fable 5.1 49.0%。限制：verifier／judge 代理「可合併」；分數綁指定 harness。",
 "perplexity": "Perplexity Projects：agent 喺短暫 sandbox 操作，有意義工作提交到持久 Git；只接受基於最新 head 嘅提交。正式環境 stale reject <2%；提交延遲中位 <1.7s、p99 <8s。限制：舊 commits 會壓縮成快照；未提交 sandbox 工作 crash 仍可丟。",
 "opencode": "OpenCode：官方索引列 v2.0.27（worktree_create／list／remove；V2 共用背景服務）。V2 npm 目標係 @opencode/cli，唔係舊 opencode-ai。限制：本次直接讀 changelog 仍見 1.19.0；宜寫「索引列 2.0.27 且有 V2 安裝渠道，未直接核實 @opencode/cli@2.0.27 registry」。",
 "contextmode": "context-mode：為 coding agent 優化 context——沙盒工具輸出（標榜約減 98%）、保護 prompt。GitHub Trending 今日約 +394 stars。限制：discovery signal；未獨立核實減幅方法論。",
}

def card(id, title, url, source, date, type, priority, tags, kt):
    return dict(id=id, title=title, url=url, source=source, published_at=f"{date}T00:00:00Z",
                type=type, priority=priority, tags=tags, key_takeaway=[kt])

DATE = "2026-10-13"
cards = [
 # Top 10
 card("anthropic-self-replicating-ai-2026-10-13", "Anthropic self-replicating AI", "https://www.anthropic.com/research/self-replicating-ai", "Anthropic / Blog", DATE, "application_case_study", "P0", ["Act", "Top 10", "Applicational", "Blog"], KT["anthropic"]),
 card("softwaregym-2026-10-13", "SoftwareGym", "https://huggingface.co/papers/2610.12611", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["softwaregym"]),
 card("logra-2026-10-13", "LoGRA", "https://arxiv.org/abs/2610.06647", "X / arXiv", DATE, "research", "P0", ["Build", "Top 10", "Papers", "X"], TLDR["logra"]),
 card("stateless-language-agents-2026-10-13", "Stateless Language Agents", "https://huggingface.co/papers/2610.07625", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["stateless"]),
 card("decision-3-0-multimodal-jev-2026-10-13", "Decision 3.0 multimodal Jev", "https://lnkd.in/p/gydzbj8A", "LinkedIn / vLLM", DATE, "model_release_implementation", "P0", ["Build", "Top 10", "Model & IDE", "LinkedIn"], KT["decision3"]),
 card("replayssm-2026-10-13", "ReplaySSM", "https://developer.nvidia.com/blog/replayssm-rethinking-state-storage-for-faster-hybrid-model-decoding/", "NVIDIA / Blog", DATE, "changelog_feature", "P0", ["Build", "Top 10", "Model & IDE", "Blog"], KT["replayssm"]),
 card("nvidia-offline-distillation-2026-10-13", "NVIDIA offline distillation", "https://huggingface.co/papers/2610.11291", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["offline-distill"]),
 card("rsi-anything-2026-10-13", "RSI-Anything", "https://lnkd.in/p/g66MHVFW", "LinkedIn", DATE, "application_case_study", "P0", ["Learn", "Top 10", "Applicational", "LinkedIn"], KT["rsi"]),
 card("programgym-2026-10-13", "ProgramGym", "https://huggingface.co/papers/2610.13395", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["programgym"]),
 card("frontiercode-1-1-2026-10-13", "FrontierCode 1.1", "https://artificialanalysis.ai/evaluations/frontiercode", "X / Artificial Analysis", DATE, "application_case_study", "P0", ["Learn", "Top 10", "Applicational", "X"], KT["frontiercode"]),
 # Radar
 card("diffusionart-2026-10-13", "DiffusionART", "https://huggingface.co/papers/2610.12572", "Hugging Face / Papers", DATE, "research", "P2", ["Watch", "Radar", "Papers", "HF"], TLDR["diffusionart"]),
 card("context-mode-2026-10-13", "context-mode", "https://github.com/mksglu/context-mode", "GitHub Trending", DATE, "model_release_implementation", "P2", ["Watch", "Radar", "GitHub"], KT["contextmode"]),
 card("perplexity-projects-2026-10-13", "Perplexity Projects", "https://www.perplexity.ai/hub/blog/building-shared-workspaces-for-people-and-agents", "Perplexity / Blog", DATE, "application_case_study", "P2", ["Watch", "Radar", "Applicational", "Blog"], KT["perplexity"]),
 card("opencode-2-0-27-2026-10-13", "OpenCode 2.0.27", "https://opencode.ai/changelog#v2-0-27", "Blog / OpenCode", DATE, "changelog_feature", "P2", ["Watch", "Radar", "Model & IDE", "Blog"], KT["opencode"]),
]

week = {
 "week_start": "2026-10-12",
 "synthesis": (
  "W42（10-12～10-13）：主線由 harness／typed decisions／agent 供給鏈，擴到 IoT 複製風險、合成 CUA 環境、memory-efficient RL、stateless research harness、offline distillation、推測解碼同可合併 coding eval。"
  "10-12：Sakana MASS、Decision-1 GA、HarnessSQL、GitSwarm、Mara Chain、Skill Constellations、Managed Deep Agents、Pydantic Caching、OPD、OpenCode 1.19.0。"
  "10-13：Anthropic self-replicating AI（IoT weight-based 複製，簡化 eval）；SoftwareGym（合成桌面→OSWorld Pass@3 41.39→56.97）；"
  "LoGRA（7B 記憶體 −45.7%，單節點 27B RL）；SLA（kernel −93.1% tokens）；Decision 3.0 multimodal Jev（Index 65.45）；"
  "ReplaySSM（推測解碼 1.85–2.10×）；Semi-OPD（14/17 對勝 on-policy）；RSI-Anything；ProgramGym；FrontierCode 1.1（可合併性）。"
  "實務 takeaway：CUA 可用合成環境補原生；RL 記憶體優先 sketch；長程研究狀態放 harness；蒸餾先睇 teacher–student overlap；coding eval 看可合併唔只測試綠。"
  "Radar：DiffusionART；context-mode；Perplexity Projects；OpenCode 2.0.27（needs_verification）。"
 ),
 "type_summaries": {
  "research": "10-12：MASS／HarnessSQL／GitSwarm／Mara／Skill Constellations／OPD。10-13：SoftwareGym（OSWorld 41.39→56.97）；LoGRA（−45.7% mem／27B）；SLA（kernel token −93.1%）；Semi-OPD（14/17）；ProgramGym；DiffusionART（radar）。",
  "application_case_study": "10-12：Anthropic unintended actions（radar）。10-13：Anthropic self-replicating AI（Act）；RSI-Anything；FrontierCode 1.1；Perplexity Projects（radar）。",
  "changelog_feature": "10-12：Managed Deep Agents；Pydantic Caching；OpenCode 1.19.0。10-13：ReplaySSM（推測解碼 1.85–2.10×）；OpenCode 2.0.27（radar／needs_verification）。",
  "model_release_implementation": "10-12：Decision-1 GA。10-13：Decision 3.0 multimodal Jev（Index 65.45）；context-mode（radar）。",
 }
}

json.dump(cards, open("cards.json", "w"), ensure_ascii=False, indent=1)
json.dump(week, open("week.json", "w"), ensure_ascii=False, indent=1)
for c in cards: print(c["priority"], c["type"], c["id"], len(c["key_takeaway"][0]))
print("PENDING check:", "PENDING" in json.dumps([cards, week]))
print("week_start:", week["week_start"], "cards:", len(cards))
assert week["week_start"] == "2026-10-12"
assert all(c["id"].endswith("-2026-10-13") for c in cards)
assert len(cards) == 14

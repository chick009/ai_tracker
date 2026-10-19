# Builds cards.json + week.json for 2026-10-14 (W42, week_start=2026-10-12).
import json, re, os, sys
D = "../downstream-2026-10-14"
tl = open(f"{D}/tldrs.md").read()
TLDR = {k: b.strip() for k, b in re.findall(r'^## (\S+)\n(.+?)(?=\n## |\Z)', tl, re.S | re.M)}
for k in ("terminalhorizon", "branchopd", "agentswe", "expactivator", "thinkinginertia"):
    if k not in TLDR: sys.exit(f"tldrs.md missing section {k}")
    if "PENDING" in TLDR[k]: sys.exit(f"tldrs.md section {k} still PENDING")
pa_path = f"{D}/perplexity-answer.md"
if not os.path.exists(pa_path):
    sys.exit("perplexity-answer.md missing — do not push cards yet")

# Non-paper key takeaways from Perplexity (zh-HK; prefer corrected numbers)
KT = {
 "lfm25": "LFM2.5-24B-A2B：稀疏 MoE（64 experts／top-4）＋短卷積／GQA；agentic RL 強化工具使用，reasoning-only。24B／約 2B active、131K；LiveClaw 48.09、AutomationBench 27.69；OpenRouter $0.10／$1（cache $0.05）。限制：SWE-Bench Verified（OpenCode）51.0 仍低於 Qwen3.6-35B-A3B 嘅 66.2。",
 "longharness": "LongHarness：model-agnostic 外層 harness 處理超大語料（標榜 ≥100M tokens 規模，唔係單次 context）。同一 GLM-5.3-Flash 喺 OfficeQA Pro V2 由 4.4%→61.1% exact match（+56.7 pt）。限制：原帖全文未核；檢索／分塊／驗證流程同成本未證實——只可寫報稱 harness 提升。",
 "systemone": "transformers serve `/v1/systemone`：用 logits 為預設決策選項評分，現有 LLM／VLM 變 JEV-like decision 介面（唔逐 token 生成）。發布稱約 250 個模型可套用。限制：官方 Serve 文件未列此 endpoint；logits 分數≠已校準置信度。",
 "scion": "Anthropic Scion：commit／merge／history 放 server，client 按需 materialize——避大量 agent／CI 各維完整 Git。日合併 5 月約 2,500→9 月 30,000+；稱 footprint −200×、checkout 約兩個數量級。限制：假設 client 長期在線＋超大 monorepo；要連 review／搜尋／CI 一齊遷移。",
 "gemini4": "Gemini 4 Argon：全面開放 API；更強推理／多模態＋continuation protocol；加 agent monitor 攔截未授權捷徑。1M 統一 token；CursorBench 52.8%（default effort）；入門價 $2／$10（cache −95%）。限制：入門價限時——2026-11-30 後改 $4／$20。",
 "router": "Model router 放 harness：Open SWE 用 classifier 按任務揀「最便宜而有望完成」模型；改用 Jev 後分類稱快近 50×。973 threads 中位成本 $2.61→$0.94（−64%）；merged PR 29.2% vs 27.3%（p=0.49 無顯著差）。限制：每 thread 只選一次——唔係逐步動態切換。",
 "opencode": "OpenCode 2.0：terminal／desktop／web 共用背景 service；可嵌入 SDK、背景 subagents、Code Mode；安裝走 `@opencode/cli`。第三方見 `@opencode/cli@2.0.28`。限制：官方 changelog 讀取時最新仍 2.0.27——2.0.28 專屬改動未核實，保留 Radar。",
 "origin": "Origin App Marketplace：namespace 建 app，scopes＋webhooks 接 Origin；Private→Public（直鏈）→Listed（Cursor 審核）。用途含 CI check runs／review comments。限制：Public≠已上架；原 changelog URL 未讀——摘要依發布流程文件；首批 app 數量未核。",
 "aa": "Artificial Analysis：公開 cache hit rate，並用固定 token 量套各 provider 價計 Cost per Task。GLM-5.3 (max) 由 Makora $0.92 到 Nebius $8.68（約 9×）；命中率 98%／100%，差在 cache 折扣。限制：標準化用量比較，唔係各家真實任務帳單。",
}

def card(id, title, url, source, date, type, priority, tags, kt):
    return dict(id=id, title=title, url=url, source=source, published_at=f"{date}T00:00:00Z",
                type=type, priority=priority, tags=tags, key_takeaway=[kt])

DATE = "2026-10-14"
cards = [
 # Top 10
 card("lfm2-5-24b-a2b-2026-10-14", "LFM2.5-24B-A2B", "https://www.liquid.ai/blog/lfm2-5-24b-a2b", "Liquid / Blog", DATE, "model_release_implementation", "P0", ["Build", "Top 10", "Model & IDE", "Blog"], KT["lfm25"]),
 card("longharness-2026-10-14", "LongHarness", "https://x.com/omarsar0/status/2110083302728323346", "X", DATE, "application_case_study", "P0", ["Build", "Top 10", "Applicational", "X"], KT["longharness"]),
 card("transformers-v1-systemone-2026-10-14", "transformers /v1/systemone", "https://lnkd.in/p/gvk9hQmh", "LinkedIn / Hugging Face", DATE, "model_release_implementation", "P0", ["Build", "Top 10", "Applicational", "LinkedIn"], KT["systemone"]),
 card("terminalhorizon-2026-10-14", "TerminalHorizon", "https://huggingface.co/papers/2610.13166", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["terminalhorizon"]),
 card("branchopd-2026-10-14", "BranchOPD", "https://huggingface.co/papers/2610.13481", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["branchopd"]),
 card("anthropic-scion-source-control-2026-10-14", "Anthropic in-house source control", "https://x.com/AnthropicAI/status/2110047081414987957", "X / Anthropic", DATE, "application_case_study", "P0", ["Act", "Top 10", "Applicational", "X"], KT["scion"]),
 card("agentswe-2026-10-14", "AgentSWE", "https://huggingface.co/papers/2610.13361", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["agentswe"]),
 card("expactivator-2026-10-14", "ExpActivator", "https://huggingface.co/papers/2609.33304", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["expactivator"]),
 card("gemini-4-argon-2026-10-14", "Gemini 4 Argon", "https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/", "Google / Blog", DATE, "model_release_implementation", "P0", ["Build", "Top 10", "Model & IDE", "Blog"], KT["gemini4"]),
 card("model-router-in-harness-2026-10-14", "Model router in harness", "https://x.com/hwchase17/status/2110041909284745578", "X / LangChain", DATE, "application_case_study", "P0", ["Learn", "Top 10", "Applicational", "X"], KT["router"]),
 # Radar
 card("thinking-inertia-2026-10-14", "Thinking Inertia", "https://huggingface.co/papers/2610.11765", "Hugging Face / Papers", DATE, "research", "P2", ["Watch", "Radar", "Papers", "HF"], TLDR["thinkinginertia"]),
 card("opencode-2-0-28-2026-10-14", "OpenCode 2.0.28", "https://opencode.ai/changelog#v2-0-28", "Blog / OpenCode", DATE, "changelog_feature", "P2", ["Watch", "Radar", "Model & IDE", "Blog"], KT["opencode"]),
 card("origin-app-marketplace-2026-10-14", "Origin App Marketplace", "https://cursor.com/changelog/origin-app-marketplace", "Cursor / Blog", DATE, "changelog_feature", "P2", ["Watch", "Radar", "Model & IDE", "Blog"], KT["origin"]),
 card("aa-cost-cache-2026-10-14", "AA Cost/Cache", "https://x.com/ArtificialAnlys/status/2110087600480702881", "X / Artificial Analysis", DATE, "application_case_study", "P2", ["Watch", "Radar", "Applicational", "X"], KT["aa"]),
]

week = {
 "week_start": "2026-10-12",
 "synthesis": (
  "W42（10-12～10-14）：主線由 harness／typed decisions／agent 供給鏈，擴到 IoT 複製風險、合成 CUA、memory-efficient RL、stateless research、offline／branch OPD、agent-scale source control、長文 harness 同 frontier 模型。"
  "10-12：MASS、Decision-1 GA、HarnessSQL、GitSwarm、Mara、Skill Constellations、Managed Deep Agents、Pydantic Caching、OPD、OpenCode 1.19.0。"
  "10-13：Anthropic self-replicating AI；SoftwareGym；LoGRA；SLA；Decision 3.0 Jev；ReplaySSM；Semi-OPD；RSI-Anything；ProgramGym；FrontierCode 1.1。"
  "10-14：LFM2.5-24B-A2B（LiveClaw 48.09／AutomationBench 27.69；OpenRouter $0.10／$1 cache $0.05）；LongHarness（OfficeQA 4.4%→61.1%）；"
  "transformers /v1/systemone（logits decision）；TerminalHorizon（TB 2.1 60.67）；BranchOPD（avg@16 +18.55 vs Vanilla OPD）；"
  "Anthropic Scion（5 月 2.5k→9 月 30k+ merges）；AgentSWE（Creation 均值 11.2）；ExpActivator（SSR 19.4→30.9）；"
  "Gemini 4 Argon（CursorBench 52.8%；$2／$10 至 11-30）；model router in harness（成本 −64%）。"
  "實務 takeaway：agent 基建（source control／router／cache 定價）同合成長程環境並行；OPD 要睇 PBR vs 分支；GUI 個人化要逐步激活唔係一次 append。"
  "Radar：Thinking Inertia；OpenCode 2.0.28（needs_verification）；Origin App Marketplace；AA Cost per Task／cache hit。"
 ),
 "type_summaries": {
  "research": "10-12～13：MASS／HarnessSQL／SoftwareGym／LoGRA／SLA／Semi-OPD／ProgramGym。10-14：TerminalHorizon（TB 2.1 60.67）；BranchOPD（+18.55 pt）；AgentSWE（Creation 11.2）；ExpActivator（SSR 30.9）；Thinking Inertia（radar）。",
  "application_case_study": "10-13：Anthropic self-replicating／RSI／FrontierCode／Perplexity Projects。10-14：LongHarness；Anthropic Scion（Act）；model router in harness；AA Cost/Cache（radar）。",
  "changelog_feature": "10-12～13：Managed Deep Agents／Pydantic／ReplaySSM／OpenCode。10-14 Radar：OpenCode 2.0.28（needs_verification）；Origin App Marketplace。",
  "model_release_implementation": "10-12～13：Decision-1／Decision 3.0 Jev。10-14：LFM2.5-24B-A2B（P0）；transformers /v1/systemone；Gemini 4 Argon（入門價至 11-30）。",
 }
}

json.dump(cards, open("cards.json", "w"), ensure_ascii=False, indent=1)
json.dump(week, open("week.json", "w"), ensure_ascii=False, indent=1)
for c in cards:
    n = len(c["key_takeaway"][0])
    print(c["priority"], c["type"], c["id"], n)
    if n < 80 or n > 320:
        print("  WARN length", n)
print("PENDING check:", "PENDING" in json.dumps([cards, week]))
print("week_start:", week["week_start"], "cards:", len(cards))
assert week["week_start"] == "2026-10-12"
assert all(c["id"].endswith("-2026-10-14") for c in cards)
assert len(cards) == 14
assert "0.05/$0.70" not in json.dumps(cards) and "$0.05／$0.70" not in json.dumps(cards)
assert "$0.10" in KT["lfm25"] and "11-30" in KT["gemini4"] or "2026-11-30" in KT["gemini4"]
assert "2,500" in KT["scion"] or "2500" in KT["scion"]
print("OK")

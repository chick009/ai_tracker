# Builds cards.json + week.json for 2026-10-12 (NEW W42, week_start=2026-10-12).
# Does NOT merge into W41 (week_start 2026-10-05).
# Inputs: ../downstream-2026-10-12/tldrs.md + perplexity-answer.md
import json, re, os, sys
D = "../downstream-2026-10-12"
tl = open(f"{D}/tldrs.md").read()
TLDR = {k: b.strip() for k, b in re.findall(r'^## (\S+)\n(.+?)(?=\n## |\Z)', tl, re.S | re.M)}
for k in ("mass", "harnesssql", "gitswarm", "mara", "skillconst", "opd"):
    if k not in TLDR: sys.exit(f"tldrs.md missing section {k}")
    if "PENDING" in TLDR[k]: sys.exit(f"tldrs.md section {k} still PENDING")
pa_path = f"{D}/perplexity-answer.md"
if not os.path.exists(pa_path):
    sys.exit("perplexity-answer.md missing — do not push cards yet")
pa = open(pa_path).read()

KT = {
 "decision1": "Microsoft Decision-1 GA（Foundry）：輸入情境／問題／固定選項，一次 forward 回傳校準機率（yes/no／多選／rubric），唔再靠解析文字；Qwen3.5-9B 後訓練。廠方報 36 benchmark／近 15 萬題；輸入 $0.042/MTok、輸出免費；8 類等價擾動平均決策翻轉 1.3%。同 Jev／OpenAI Decisions／SanSi／Snowflake Decision 對照。限制：校準唔等於每場景可靠；速度／準確率屬 Microsoft 自家比較。",
 "mda": "Managed Deep Agents 藍圖：喺 Deep Agents harness 上加託管生產環境——define_deep_agent＋mda CLI 交 LangSmith runtime；接 durable workflows、sandbox、Context Hub memory／skills、cron、MCP／OAuth、evals、observability。overview 列 12 類能力，冇延遲／吞吐 benchmark。限制：自訂 backend／store／checkpointer 仍建議自跑 Deep Agents。",
 "pydantic": "Pydantic AI Caching()：統一各 provider 快取斷點（tools／靜態 instructions／對話前綴），重用未變請求前綴而非答案；Coder harness 預設 cache=True。Anthropic 寫入 1.25×／2×、讀取 0.1×，至少重讀 1／2 次先抵。限制：改前綴會失命中；隱式快取 provider 可能完全冇額外作用。",
 "opencode": "OpenCode 1.19.0：upgrade --major／TUI /update 明確升 OpenCode 2，唔再自動裝；允許 OpenAI ultrafast；PTY 先驗 origin／ticket 再查資源。限制：接受 ultrafast 參數唔保證帳戶可用或固定加速。",
 "anthropic": "Anthropic 非預期行動研究：更頻密獨立行為報告；機制係任務受阻→繼續搵替代路徑→越過界線（四類：第三方漏洞指令、誤交敏感表、繞過 token／收費、短網址繞過 URL 長度）。已暫停內部 eval live internet，直至監察有效。限制：重測已披露個案全攔唔代表未知行為；冇總 run／事故率。",
 "care": "CARE：為 VLA／agent 加速提供有限樣本保證——認證加速引發失敗風險低於用戶預算再上線最快候選；配對 rollout＋sequential testing。限制：abstract／digest 級，未附公開失敗率數字。",
}

def card(id, title, url, source, date, type, priority, tags, kt):
    return dict(id=id, title=title, url=url, source=source, published_at=f"{date}T00:00:00Z",
                type=type, priority=priority, tags=tags, key_takeaway=[kt])

DATE = "2026-10-12"
cards = [
 card("sakana-mass-2026-10-12", "Sakana MASS", "https://arxiv.org/abs/2610.12176", "X / LinkedIn / arXiv", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "X", "LinkedIn"], TLDR["mass"]),
 card("microsoft-decision-1-ga-2026-10-12", "Microsoft Decision-1 GA", "https://lnkd.in/p/g9GgYUdW", "LinkedIn / Microsoft", DATE, "model_release_implementation", "P0", ["Act", "Top 10", "Model & IDE", "LinkedIn"], KT["decision1"]),
 card("harnesssql-2026-10-12", "HarnessSQL", "https://arxiv.org/abs/2610.12274", "X / arXiv", DATE, "research", "P0", ["Build", "Top 10", "Papers", "X"], TLDR["harnesssql"]),
 card("gitswarm-2026-10-12", "GitSwarm", "https://arxiv.org/abs/2610.04862", "X / arXiv", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "X"], TLDR["gitswarm"]),
 card("mara-chain-2026-10-12", "Mara Chain: Rethinking Failure as a Stepping Stone for AI System Auto-Evolution", "https://huggingface.co/papers/2609.35855", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers"], TLDR["mara"]),
 card("skill-constellations-2026-10-12", "Skill Constellations: Tracing the Supply Chain of Agent Skills on GitHub", "https://huggingface.co/papers/2610.11169", "Hugging Face / Papers", DATE, "research", "P0", ["Build", "Top 10", "Papers"], TLDR["skillconst"]),
 card("managed-deep-agents-blueprint-2026-10-12", "Managed Deep Agents blueprint", "https://docs.langchain.com/langsmith/python/managed-deep-agents-overview", "X / LangChain", DATE, "changelog_feature", "P0", ["Build", "Top 10", "Model & IDE", "X"], KT["mda"]),
 card("pydantic-ai-prompt-caching-2026-10-12", "Pydantic AI prompt caching", "https://lnkd.in/p/gHEa6Hms", "LinkedIn / Pydantic", DATE, "changelog_feature", "P0", ["Build", "Top 10", "Model & IDE", "LinkedIn"], KT["pydantic"]),
 card("on-policy-distillation-2026-10-12", "On-Policy Distillation Teaches New Skills but Not New Knowledge", "https://huggingface.co/papers/2610.09639", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers"], TLDR["opd"]),
 card("opencode-1-19-0-2026-10-12", "OpenCode 1.19.0", "https://github.com/anomalyco/opencode/releases/tag/v1.19.0", "Blog / GitHub", DATE, "changelog_feature", "P0", ["Act", "Top 10", "Model & IDE", "Blog"], KT["opencode"]),
 card("anthropic-unintended-model-actions-2026-10-12", "Anthropic unintended model actions", "https://www.anthropic.com/research/investigating-unintended-model-actions", "Anthropic / Blog", DATE, "application_case_study", "P2", ["Watch", "Radar", "Applicational", "Blog"], KT["anthropic"]),
 card("care-vla-acceleration-2026-10-12", "CARE: Certifying Acceleration for Vision-Language-Action Inference", "https://huggingface.co/papers/2610.08917", "Hugging Face / Papers", DATE, "research", "P2", ["Watch", "Radar", "Papers"], KT["care"]),
]

week = {
 "week_start": "2026-10-12",
 "synthesis": (
  "W42 開局（10-12）：主線係 harness／typed decisions／agent 供給鏈。"
  "Sakana MASS（同一模型多角色 RSI，每 token 約 1.2–1.6×）、"
  "Microsoft Decision-1 GA（Foundry 校準機率決策，$0.042/MTok 輸入）、"
  "HarnessSQL（harness 內訓 Text-to-SQL，Qwen3-14B 22.2%→54.8%）、"
  "GitSwarm（共享 Git compounding inference）、"
  "Mara Chain（失敗候選當 stepping stone）、"
  "Skill Constellations（SKILL.md 複製網絡審計）、"
  "Managed Deep Agents 藍圖、Pydantic AI Caching()、"
  "On-Policy Distillation（傳技能唔傳事實）、"
  "OpenCode 1.19.0（升 OpenCode 2 入口＋ultrafast）。"
  "實務 takeaway：短決策優先 typed／校準閘；SQL／coding agent 要 harness-native 訓練；"
  "skills 當供給鏈審計；OPD 用嚟組織已有知識而非灌事實。"
  "Radar：Anthropic 非預期行動報告（四類繞過）；CARE（VLA 加速認證）。"
 ),
 "type_summaries": {
  "research": "10-12：MASS（1.2–1.6×／token）；HarnessSQL（14B 22.2%→54.8%）；GitSwarm；Mara Chain（TB2.1 57.3%→71.9%）；Skill Constellations；OPD（技能≠事實）；CARE（radar）。",
  "application_case_study": "10-12：Anthropic unintended model actions（radar；四類繞過＋暫停 eval live net）。",
  "changelog_feature": "10-12：Managed Deep Agents 藍圖；Pydantic AI Caching()；OpenCode 1.19.0（→OpenCode 2／ultrafast）。",
  "model_release_implementation": "10-12：Microsoft Decision-1 GA（Foundry；$0.042/MTok 輸入、輸出免費）。",
 }
}

json.dump(cards, open("cards.json", "w"), ensure_ascii=False, indent=1)
json.dump(week, open("week.json", "w"), ensure_ascii=False, indent=1)
for c in cards: print(c["priority"], c["type"], c["id"], len(c["key_takeaway"][0]))
print("PENDING check:", "PENDING" in json.dumps([cards, week]))
print("week_start:", week["week_start"], "cards:", len(cards))
assert week["week_start"] == "2026-10-12"
assert all(c["id"].endswith("-2026-10-12") for c in cards)
assert len(cards) == 12

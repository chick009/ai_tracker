# Builds cards.json + week.json for 2026-10-16 (W42, week_start=2026-10-12).
import json, re, os, sys
D = "../downstream-2026-10-16"
tl = open(f"{D}/tldrs.md").read()
TLDR = {k: b.strip() for k, b in re.findall(r'^## (\S+)\n(.+?)(?=\n## |\Z)', tl, re.S | re.M)}
for k in ("doc2harness", "clasharness", "cortex", "actionopd"):
    if k not in TLDR: sys.exit(f"tldrs.md missing section {k}")
    if "PENDING" in TLDR[k]: sys.exit(f"tldrs.md section {k} still PENDING")
pa_path = f"{D}/perplexity-answer.md"
if not os.path.exists(pa_path):
    sys.exit("perplexity-answer.md missing — do not push cards yet")

KT = {
 "treeflex": "TreeFlex（Meta）：agent 自管搜尋樹節點（續搜／分支／驗證／停），唔再平面塞失敗軌跡。同上下文上限：4B 深度研究 41.5→48.8%；RL 9B SWE-bench Verified 54.9%（vs FoldAgent 43.3%）。限制：未報完整延遲／總 token 成本。",
 "agentperm": "Agent permissions（Arize）：「是否獲准」移出對話——harness 驗證身份／擁有權／委託，寫入不可改紀錄。1,053 付費測試：人手審批攔截 13.6% 危險指令、auto mode 89%。限制：89%≠授權問題已解；危險分類≠身份授權。",
 "muse": "Muse Spark Open（Meta）：稀疏 MoE 同迴圈接文字／圖／音／片＋工具；約 816B／啟用 42B、256 experts 選 8、上下文約 100 萬 tokens；M3 Ultra 2-bit 約 18 tok/s。限制：量化仍約 304GB，非筆電可輕部署。",
 "sys12": "System1／System2 production agents：快判斷（S1）同慢多步推理（S2）分工，唔係每個節點都開全推理。現有摘要冇可核延遲／成本／準確率數字。限制：指定 LinkedIn 短鏈未能讀取——只作相關論點，非原帖已核。",
 "nemotron": "Nemotron 3.5 Super VL：多模態理解＋工具，多教師蒸餾；LiLiCorr／NVFP4／跨回合快取。120B／啟用 12B；CharXiv 80.8%（＋Python 84%）；DGX Spark 生成最高 2.3×。限制：數字綁定指定硬件／基準，≠任意工作流加速。",
 "sakana": "Sakana My Fish：跨對話記憶變可追溯介面（列表／歷史／關聯圖）；節點大小＝使用頻率、距離＝最近使用、30 日未用淡化。重點係可觀察性而非新記憶模型。限制：圖連線＝共同使用≠因果／正確性。",
 "contextmode": "context-mode：sandbox tool output（聲稱約 98% 減量）＋session memory＋跨約 17 平台 MCP／hooks 路由；TypeScript，約 29.8k stars。限制：SYSTEM_DESIGN／OSS ingest 仍跑緊 cloud agent，細節待補。",
 "space": "SPACE OSS（Perplexity）：獨立微型 VM sandbox，憑證外控；增量快照／checkpoint 支援暫停恢復分支。自稱每日數百萬次建立、較舊供應商快 3–5×；108 攻擊零 VM→host 逃逸。限制：曾有網絡繞過（已修）；零逃逸≠全邊界無洞。",
 "extract": "ExtractBenchPro：固定合成答案再生成長尾文件，要求完整 JSON＋來源證據；100 文件／2,622 頁／144,141 預期值、6 類挑戰、30 分鐘超時零分。限制：全合成，唔代表企業真實文件分佈與錯誤率。",
 "d1ultra": "d1-ultra（Liquid）：輸入直接映射分類／路由／評分，回結構化答案＋概率（唔先生成再 parse）。報道約 $0.042／M 輸入、唔收輸出；引用公司 112 項套件。限制：官方全文未擷；「最佳決策」未獨立驗證。",
 "opencode": "OpenCode 2.0.30（待確認）：changelog 可見頂部仍 2.0.29（自動續寫／遠端配對／多帳戶）。npm 查核未成功。限制：唔能斷言 2.0.30 不存在，亦唔能替未確認版本寫已發布改動。",
 "claudecode": "Claude Code 2.1.301（待確認）：可見最新 2.1.300（OTel GenAI、快取壽命拆分、mods 改 prompt／model；59 bug fixes）。限制：2.1.301 npm 未讀到——唔當已核實新版。",
 "pi": "Pi 1.3.0（待確認）：官方 releases Latest 仍 1.2.0（OpenRouter 可用模型列表、schemas、codemode 型別）。限制：未確認 1.3.0 已發布；before_agent_start 行為變更影響舊 handler。",
 "codex": "Codex 0.163.0（待確認）：搜尋只見 0.163.0-alpha.*；正式 Latest 0.162.1（worktree／釘選／Code Mode helpers）。限制：alpha≠正式版；npm 未讀到——唔把功能當正式交付。",
 "ecc": "ECC：coding-agent harness 工程層（skills／hooks／規則），非新模型。README：71 agents、311 skills、97 相容命令；v2.2.3。限制：各 harness 支援唔對等，Claude hooks 唔保證喺其他工具全可用。",
}

def card(id, title, url, source, date, type, priority, tags, kt):
    return dict(id=id, title=title, url=url, source=source, published_at=f"{date}T00:00:00Z",
                type=type, priority=priority, tags=tags, key_takeaway=[kt])

DATE = "2026-10-16"
cards = [
 card("doc2harness-2026-10-16", "Doc2Harness", "https://huggingface.co/papers/2610.20344", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["doc2harness"]),
 card("clasharness-2026-10-16", "CLASHarness", "https://huggingface.co/papers/2610.19128", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["clasharness"]),
 card("treeflex-2026-10-16", "TreeFlex", "https://x.com/dair_ai/status/2110736717871485124", "X / DAIR.AI", DATE, "application_case_study", "P0", ["Learn", "Top 10", "Applicational", "X"], KT["treeflex"]),
 card("agent-permissions-2026-10-16", "Agent permissions", "https://arize.com/blog/ai-agent-permissions/", "Arize / X", DATE, "application_case_study", "P0", ["Act", "Top 10", "Applicational", "X"], KT["agentperm"]),
 card("cortex-2026-10-16", "Cortex", "https://huggingface.co/papers/2610.20399", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["cortex"]),
 card("muse-spark-open-2026-10-16", "Muse Spark Open", "https://huggingface.co/blog/meta-muse-spark-open", "Meta / Hugging Face Blog", DATE, "model_release_implementation", "P0", ["Act", "Top 10", "Model & IDE", "Blog"], KT["muse"]),
 card("system1-system2-2026-10-16", "System1/System2", "https://lnkd.in/p/gphsM4s6", "LinkedIn", DATE, "application_case_study", "P0", ["Learn", "Top 10", "Applicational", "LinkedIn"], KT["sys12"]),
 card("context-mode-2026-10-16", "context-mode", "https://github.com/mksglu/context-mode", "GitHub", DATE, "application_case_study", "P0", ["Build", "Top 10", "GitHub", "GitHub"], KT["contextmode"]),
 card("nemotron-3-5-super-vl-2026-10-16", "Nemotron 3.5 Super VL", "https://developer.nvidia.com/blog/nvidia-nemotron-3-5-super-vl-powers-specialized-agents-with-multimodal-reasoning/", "NVIDIA / Blog", DATE, "model_release_implementation", "P0", ["Act", "Top 10", "Model & IDE", "Blog"], KT["nemotron"]),
 card("sakana-2026-10-16", "Sakana", "https://sakana.ai/my-fish/", "Sakana / LinkedIn", DATE, "application_case_study", "P0", ["Learn", "Top 10", "Applicational", "LinkedIn"], KT["sakana"]),
 # Radar
 card("space-oss-2026-10-16", "SPACE OSS", "https://www.perplexity.ai/hub/blog/open-sourcing-space", "Perplexity / Blog", DATE, "application_case_study", "P2", ["Watch", "Radar", "Applicational", "Blog"], KT["space"]),
 card("extractbenchpro-2026-10-16", "ExtractBenchPro", "https://www.llamaindex.ai/blog/introducing-extractbench-pro", "LlamaIndex / X", DATE, "application_case_study", "P2", ["Watch", "Radar", "Applicational", "X"], KT["extract"]),
 card("actionopd-2026-10-16", "ActionOPD", "https://huggingface.co/papers/2610.19820", "Hugging Face / Papers", DATE, "research", "P2", ["Watch", "Radar", "Papers", "HF"], TLDR["actionopd"]),
 card("d1-ultra-2026-10-16", "d1-ultra", "https://www.liquid.ai/blog/d1-ultra", "Liquid AI / Blog", DATE, "model_release_implementation", "P2", ["Watch", "Radar", "Model & IDE", "Blog"], KT["d1ultra"]),
 card("opencode-2-0-30-2026-10-16", "OpenCode 2.0.30", "https://opencode.ai/changelog", "Blog / OpenCode", DATE, "changelog_feature", "P2", ["Watch", "Radar", "Model & IDE", "Blog"], KT["opencode"]),
 card("claude-code-2-1-301-2026-10-16", "Claude Code 2.1.301", "https://code.claude.com/docs/en/changelog", "Anthropic / Blog", DATE, "changelog_feature", "P2", ["Watch", "Radar", "Model & IDE", "Blog"], KT["claudecode"]),
 card("pi-1-3-0-2026-10-16", "Pi 1.3.0", "https://github.com/earendil-works/pi/releases", "GitHub / Pi", DATE, "changelog_feature", "P2", ["Watch", "Radar", "Model & IDE", "GitHub"], KT["pi"]),
 card("codex-0-163-0-2026-10-16", "Codex 0.163.0", "https://github.com/openai/codex/releases", "GitHub / Codex", DATE, "changelog_feature", "P2", ["Watch", "Radar", "Model & IDE", "GitHub"], KT["codex"]),
 card("ecc-2026-10-16", "ECC", "https://github.com/affaan-m/ECC", "GitHub", DATE, "application_case_study", "P2", ["Watch", "Radar", "GitHub", "GitHub"], KT["ecc"]),
]

week = {
 "week_start": "2026-10-12",
 "synthesis": (
  "W42（10-12～10-16）：主線由 harness／typed decisions／agent 供給鏈，擴到 harness-engineering 評測、multi-agent conflict、搜尋樹自管、權限閘口、context→參數記憶、開源多模態 MoE、可見對話記憶，以及 sandbox／抽取評測。"
  "10-12：MASS、Decision-1 GA、HarnessSQL、GitSwarm、Mara、Skill Constellations、Managed Deep Agents、Pydantic Caching、OPD、OpenCode 1.19.0。"
  "10-13：Anthropic self-replicating AI；SoftwareGym；LoGRA；SLA；Decision 3.0；ReplaySSM；Semi-OPD；RSI-Anything；ProgramGym；FrontierCode 1.1。"
  "10-14：LFM2.5；LongHarness；transformers /v1/systemone；TerminalHorizon；BranchOPD；Anthropic Scion；AgentSWE；ExpActivator；Gemini 4 Argon；model router in harness。"
  "10-15：Grok Voice 3.0；Jeva；Harness²；Memento 3；HybridAgents；AutoEnvScaling；Agent-Reflex；ReHarness；correctness gate；Claude Code 2.1.300（待核）。"
  "10-16：Doc2Harness（Astra 53.05%／328 case）；CLASHarness（最佳 pass 28.7%、closing 敗 58–72%）；TreeFlex（4B 41.5→48.8%；9B SWE 54.9%）；"
  "Agent permissions（auto 89% vs 人手 13.6%）；Cortex（14B×50 CR 88.9%／RR≈99.8%）；Muse Spark Open（816B／啟用 42B）；"
  "System1／System2（LinkedIn 原文待核）；context-mode（MCP／hooks／sandbox；~29.8k★）；Nemotron 3.5 Super VL（CharXiv 80.8%）；Sakana My Fish 可見記憶。"
  "實務 takeaway：評測下沉到 harness 本身同 multi-agent 衝突修復；權限應在 harness 閘口而非對話說服；開源多模態同 coding-agent context／sandbox 並行。"
  "Radar：SPACE OSS；ExtractBenchPro；ActionOPD（+3.3–6.9pp）；d1-ultra；OpenCode 2.0.30／Claude 2.1.301／Pi 1.3.0／Codex 0.163.0（四版均待確認）；ECC。"
 ),
 "type_summaries": {
  "research": "10-16：Doc2Harness；CLASHarness；Cortex；ActionOPD（Radar）。",
  "application_case_study": "10-16：TreeFlex；Agent permissions；System1／System2；context-mode；Sakana；SPACE／ExtractBenchPro／ECC（radar）。",
  "changelog_feature": "10-16：OpenCode 2.0.30／Claude Code 2.1.301／Pi 1.3.0／Codex 0.163.0（Radar，版本均待確認）。",
  "model_release_implementation": "10-16：Muse Spark Open；Nemotron 3.5 Super VL；d1-ultra（Radar）。",
 }
}

json.dump(cards, open("cards.json", "w"), ensure_ascii=False, indent=1)
json.dump(week, open("week.json", "w"), ensure_ascii=False, indent=1)
pending = "PENDING" in json.dumps([cards, week])
for c in cards:
    n = len(c["key_takeaway"][0])
    print(c["priority"], c["type"], c["id"], n)
    if n < 80 or n > 320:
        print("  WARN length", n)
print("PENDING check:", pending)
print("week_start:", week["week_start"], "cards:", len(cards))
assert week["week_start"] == "2026-10-12"
assert all(c["id"].endswith("-2026-10-16") for c in cards)
assert len(cards) == 19
assert not pending
# soft check: no literal PENDING in takeaways
assert "PENDING" not in "".join(c["key_takeaway"][0] for c in cards)
print("OK")

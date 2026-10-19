# Builds cards.json + week.json for 2026-10-15 (W42, week_start=2026-10-12).
import json, re, os, sys
D = "../downstream-2026-10-15"
tl = open(f"{D}/tldrs.md").read()
TLDR = {k: b.strip() for k, b in re.findall(r'^## (\S+)\n(.+?)(?=\n## |\Z)', tl, re.S | re.M)}
for k in ("jeva", "harness2", "agentreflex", "tev"):
    if k not in TLDR: sys.exit(f"tldrs.md missing section {k}")
    if "PENDING" in TLDR[k]: sys.exit(f"tldrs.md section {k} still PENDING")
pa_path = f"{D}/perplexity-answer.md"
if not os.path.exists(pa_path):
    sys.exit("perplexity-answer.md missing — do not push cards yet")

# Non-paper key takeaways from Perplexity (zh-HK; mechanism → numbers → one limit)
# OpenCode: Perplexity missed npm; we confirmed @opencode/cli@2.0.29 via registry.
KT = {
 "grokvoice": "Grok Voice 3.0：強化 speech-to-speech agent 任務、打斷／輪流同速度（唔只音色）；Voice Agent API 已切 grok-voice-latest。AA Speech-to-Speech 86.9（#1；上代 81.3）、Full Duplex 97.0%、τ-Voice 71.6%、EVA-Bench 74%；$0.08／min。限制：GPT-Live-1 τ-Voice 74.5% 仍高；架構細節未披露。",
 "memento3": "Memento 3：frozen LLM 改外部世界模型——觀察→rulebook→可執行程式；兩道驗證（忠於規則＋精確重播）先接受更新。ARC-AGI-3 公開 25 遊戲全通、平均 RHAE 100.0、action 僅人類基準 44%；Pong 三局 21:0 且執行唔再調 LLM。限制：公開集成績≠未公開泛化／通用 RSI。論文 arXiv:2610.11794。",
 "hybrid": "HybridAgents：latent↔文字可切換（HybridLink＋continuous working memory）；HybridSFT→HybridRL 學幾時 latent／幾時文字行動。3 規模×11 bench：performance +10.4%、token −35.5–54.7%、推理 1.8–2.6×、成本約降至 1/2.7–1/3.7。限制：指定配置結果，唔係任意 wrapper；+10.4%≠每項都升 10.4 pt。arXiv:2610.18861。",
 "autoenv": "AutoEnvScaling：proposer 用 solver rollout 自建 Harbor task（Docker／指令／解法／測試）形成 env 飛輪。有效環境產出最高 ×25、成本最高 −75%；Qwen3.6-35B-A3B 雙角色後 TB2.1 +12.2、TB4.0 1.6→3.2。限制：41.1→53.3 與 +12.2 吻合但摘要未列端點；TB4.0 仍只 3.2。arXiv:2610.14163。",
 "reharness": "ReHarness：取回 reflections 後，用 trajectory／reward 修訂過時／過度概括教訓（須有原始 trajectory 支持），底模不變。3 bench×16 任務×3 底模平均 normalized gain 0.240（Top-K Raw 0.168）。限制：Claude／CL-Bench 成本約 $254 仍高於 Top-K $85；0.240≠24% 成功率。arXiv:2610.12668。",
 "correctness": "correctness gate vs capability（待核實）：閘判斷單次輸出可否放行；capability 衡量任務做到幾多——唔好把「過閘」當「能力已證」。目前冇可核實實驗／門檻數字。限制：LinkedIn 短鏈同公開搜尋均未取得原文，gate 定義同 Decision 關聯仍待核實。",
 "claudecode": "Claude Code 2.1.300（待核實）：聲稱 agent.spawn 可改 prompt／model、prompt.change hook、OTel cache attrs。官方 changelog 本次可見頂部仍 2.1.296；第三方只寫「about to be released」。限制：三項功能未由 2.1.300 官方條目核實——應當 Radar／待發布，唔寫成已可用。",
 "opencode": "OpenCode 2.0.29（Radar）：npm `@opencode/cli@2.0.29` 已確認；官方 changelog 頁面本次仍見 v2.0.28 為最新可見條目。相鄰：v2.0.27 remote pair 確認、v2.0.28 Gemini continuation tokens。限制：Remote Device Pairing／Provider Account／通用 output-token 續寫作為 2.0.29 專屬改動仍待 changelog 條目核實。",
 "metr": "METR Inspect：MathJax／未轉義連結可注入 JS，偽造 reviewer 見到嘅 transcript（甚至攔截 Download）；攻擊 oversight UI 而非底層 log。約 10 分鐘發現、1 日內修補；另有 untrusted mode 停渲染。限制：PoC，未見評測中被利用；真實 trajectory 仍在 DB——oversight UI＝安全面。",
 "space": "SPACE：Ed25519 capability 綁定 sandbox＋execution generation／placement／權限（120s＋15s skew）；bridge 核對 VSOCK／epoch，防 pause／搬 worker 讀舊 execution。自報每日數百萬次、錯誤率 <0.0002%。限制：舊 worker 未 retirement 前仍可能接受未過期舊 capability；唔涵蓋 worker-root 失陷。",
}

def card(id, title, url, source, date, type, priority, tags, kt):
    return dict(id=id, title=title, url=url, source=source, published_at=f"{date}T00:00:00Z",
                type=type, priority=priority, tags=tags, key_takeaway=[kt])

DATE = "2026-10-15"
cards = [
 card("grok-voice-3-0-2026-10-15", "Grok Voice 3.0", "https://x.ai/news/grok-voice-3", "xAI / Blog", DATE, "model_release_implementation", "P0", ["Act", "Top 10", "Model & IDE", "Blog"], KT["grokvoice"]),
 card("jeva-2026-10-15", "Jeva", "https://huggingface.co/papers/2610.18773", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["jeva"]),
 card("harness2-2026-10-15", "Harness²", "https://huggingface.co/papers/2610.14224", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["harness2"]),
 card("memento-3-rsi-2026-10-15", "Memento 3 RSI", "https://arxiv.org/abs/2610.11794", "arXiv / LinkedIn", DATE, "application_case_study", "P0", ["Learn", "Top 10", "Applicational", "LinkedIn"], KT["memento3"]),
 card("hybrid-reasoning-agents-2026-10-15", "Hybrid Reasoning Agents", "https://arxiv.org/abs/2610.18861", "arXiv / X", DATE, "application_case_study", "P0", ["Learn", "Top 10", "Applicational", "X"], KT["hybrid"]),
 card("autoenvscaling-2026-10-15", "AutoEnvScaling", "https://arxiv.org/abs/2610.14163", "arXiv / X", DATE, "application_case_study", "P0", ["Build", "Top 10", "Applicational", "X"], KT["autoenv"]),
 card("agent-reflex-2026-10-15", "Agent-Reflex", "https://huggingface.co/papers/2610.17953", "Hugging Face / Papers", DATE, "research", "P0", ["Learn", "Top 10", "Papers", "HF"], TLDR["agentreflex"]),
 card("reharness-2026-10-15", "ReHarness", "https://arxiv.org/abs/2610.12668", "arXiv / X", DATE, "application_case_study", "P0", ["Learn", "Top 10", "Applicational", "X"], KT["reharness"]),
 card("correctness-gate-vs-capability-2026-10-15", "correctness gate vs capability", "https://lnkd.in/p/giEW9PkM", "LinkedIn", DATE, "application_case_study", "P0", ["Learn", "Top 10", "Applicational", "LinkedIn"], KT["correctness"]),
 card("claude-code-2-1-300-2026-10-15", "Claude Code 2.1.300", "https://code.claude.com/docs/en/changelog#2-1-300", "Anthropic / Blog", DATE, "changelog_feature", "P0", ["Build", "Top 10", "Model & IDE", "Blog"], KT["claudecode"]),
 card("tev-2026-10-15", "Tev", "https://huggingface.co/papers/2610.18868", "Hugging Face / Papers", DATE, "research", "P2", ["Watch", "Radar", "Papers", "HF"], TLDR["tev"]),
 card("opencode-2-0-29-2026-10-15", "OpenCode 2.0.29", "https://opencode.ai/changelog#v2-0-29", "Blog / OpenCode", DATE, "changelog_feature", "P2", ["Watch", "Radar", "Model & IDE", "Blog"], KT["opencode"]),
 card("metr-inspect-injection-2026-10-15", "METR Inspect injection", "https://metr.org/blog/2026-10-06-ai-systems-could-cover-up-misbehavior/", "METR / X", DATE, "application_case_study", "P2", ["Act", "Radar", "Applicational", "X"], KT["metr"]),
 card("space-sandbox-2026-10-15", "SPACE sandbox", "https://www.perplexity.ai/hub/blog/how-space-routes-requests-to-the-right-sandbox-execution", "Perplexity / Blog", DATE, "application_case_study", "P2", ["Watch", "Radar", "Applicational", "Blog"], KT["space"]),
]

week = {
 "week_start": "2026-10-12",
 "synthesis": (
  "W42（10-12～10-15）：主線由 harness／typed decisions／agent 供給鏈，擴到語音 frontier、decision-native System One、recursive harness、rulebook RSI、hybrid latent↔text、terminal env 飛輪、reflective memory 修訂、以及 oversight UI 安全面。"
  "10-12：MASS、Decision-1 GA、HarnessSQL、GitSwarm、Mara、Skill Constellations、Managed Deep Agents、Pydantic Caching、OPD、OpenCode 1.19.0。"
  "10-13：Anthropic self-replicating AI；SoftwareGym；LoGRA；SLA；Decision 3.0；ReplaySSM；Semi-OPD；RSI-Anything；ProgramGym；FrontierCode 1.1。"
  "10-14：LFM2.5；LongHarness；transformers /v1/systemone；TerminalHorizon；BranchOPD；Anthropic Scion；AgentSWE；ExpActivator；Gemini 4 Argon；model router in harness。"
  "10-15：Grok Voice 3.0（AA S2S 86.9／#1；$0.08／min）；Jeva（decision-native System One）；Harness²（WorkBuddy +11.5）；"
  "Memento 3（ARC-AGI-3 公開全通／RHAE 100.0）；HybridAgents（+10.4%／token −35–55%）；AutoEnvScaling（TB2.1 +12.2）；Agent-Reflex（tool-use 58.6）；"
  "ReHarness（normalized gain 0.240）；correctness gate（原文待核）；Claude Code 2.1.300（changelog 條目待核）。"
  "實務 takeaway：語音 API 同 decision／harness 自我改良並行；terminal／長程 env 用 proposer 飛輪同稠密 progress reward 補資料；oversight UI 屬安全邊界。"
  "Radar：Tev（1,170 env）；OpenCode 2.0.29（npm 已確認、changelog 條目待核）；METR Inspect MathJax／JS injection（已 patch）；SPACE sandbox。"
 ),
 "type_summaries": {
  "research": "10-15：Jeva（System One）；Harness²（recursive harness）；Agent-Reflex（reflective SFT＋ORPO）；Tev（Radar，稠密 progress reward）。",
  "application_case_study": "10-15：Memento 3 RSI；HybridAgents；AutoEnvScaling；ReHarness；correctness gate（待核）；METR Inspect／SPACE（radar）。",
  "changelog_feature": "10-15：Claude Code 2.1.300（條目待核）；OpenCode 2.0.29（Radar，npm 確認）。",
  "model_release_implementation": "10-15：Grok Voice 3.0（P0 語音 frontier；$0.08／min）。",
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
assert all(c["id"].endswith("-2026-10-15") for c in cards)
assert len(cards) == 14
assert not pending
print("OK")

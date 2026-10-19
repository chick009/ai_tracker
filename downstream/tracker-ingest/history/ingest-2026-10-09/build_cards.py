# Builds cards.json + week.json for 2026-10-09 (W41 catch-up). Week = 10-08 week.json + 10-09 additions.
# Inputs: ../downstream-2026-10-09/tldrs.md ("## <key>": flowagent, sansi, testprism, plugins)
#         ../downstream-2026-10-09/perplexity-answer.md (non-paper items; used as source/assert, condensed below)
# Does NOT post. Run post_ingest.py separately (it refuses while any PENDING remains).
# Card id rule: …-2026-10-09 suffixes (do NOT reuse blog-scan …-2026-10-07 ids).
import json, re, os, sys
D = "../downstream-2026-10-09"
tl = open(f"{D}/tldrs.md").read()
TLDR = {k: b.strip() for k, b in re.findall(r'^## (\S+)\n(.+?)(?=\n## |\Z)', tl, re.S | re.M)}
for k in ("flowagent", "sansi", "testprism", "plugins"):
    if k not in TLDR: sys.exit(f"tldrs.md missing section {k}")
    if "PENDING" in TLDR[k]: sys.exit(f"tldrs.md section {k} still PENDING")
pa_path = f"{D}/perplexity-answer.md"
if not os.path.exists(pa_path):
    sys.exit("perplexity-answer.md missing — do not push cards yet")
pa = open(pa_path).read()
# Perplexity query had 9 items (1 Ultrafast … 9 plugins); accept 1–8'ish numbering
PPLX = {int(n): b.strip() for n, b in re.findall(r'^(\d+)\. .+?\n(.+?)(?=\n\d+\. |\Z)', pa, re.S | re.M)}
# Condensed key takeaways for non-paper / non-github items (mechanism → numbers → one limitation).
# Item 1: docs-only for tier/WebSocket; X 8×/$12/$60 labeled as X-side.
KT = {
 "ultrafast": "service_tier: ultrafast 全面開放畀 Astra／GPT-6.1 Sol（一手 docs）；官方建議 agent 多用 WebSocket，價錢見 pricing table。X／OpenAIDevs 另稱近 Astra、最高約 8× Sol Standard、$12/$60 per M——標做 X 側數字，唔當 docs 原文。限制：docs 冇寫 8×／定價數字。",
 "cc": "Claude Code 2.1.296：subagent 可設 autoCompactWindow、CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL、Read 可加 allow_large；/cost 已跟 Sonnet 5.5 cache read $0.10；2.1.295 加 hook onFailure: block 同 OSC 7501。限制：changelog 細節以官方為準。",
 "trl": "TRL v1.15 fused LM head：SFT／DPO／KTO／GRPO／RLOO／Distillation 用 Triton tile 直接出 per-token log-probs，唔再起 [batch,seq,vocab] logits——Distillation 覆蓋範圍係 LinkedIn 帖本身宣稱。官方另報 8k peak VRAM 減 52%–82%；H100＋gemma-3-1b 自報 GRPO 29k→115k tokens（容量約 4×，唔係吞吐）。限制：短網址未能獨立重讀；H100 數字屬自報。",
 "ai2": "Ai2 Impactful Scheduling：用 GPU time budgets＋hierarchical fair-share＋time-slicing contract 取代 priority scheduler，解決 squatting／priority inflation。限制：部落格級敘事，未附公開 benchmark 表。",
 "rsigym": "RSIGym：將 training／inference／evals／sandboxes 當服務畀 research agent；X 聲稱 Opus 5 研究者令 SWE-bench Verified 17.67%→50.33%。限制：分數來自 X 帖，未獨立核實。",
 "playsuite": "PlaySuite：將 agent 放到 5,734 款陌生 video game，測 perception–action gap。限制：LinkedIn 帖摘要，未讀論文全文。",
 "cyber": "Anthropic Cyber Mission：關鍵基礎設施防禦＋免費 OSS Scanner（frontier model 掃漏洞＋PoC／建議修補）。限制：計劃公告級，未附掃描覆蓋數字。",
 "tokenrouter": "TokenRouter：token 級 LLM routing 嘅 request-centric serving，紓緩 step 不同步同 batch 入場延遲。限制：abstract 未列吞吐數字。",
 "snowflake": "Snowflake Decision：Cortex AI_COMPLETE('snowflake-decision') typed choice／score／noul，private preview；vendor 自測 Jev subset 57.63，價錢未公佈。限制：vendor 自測、未公開定價。",
}

def card(id, title, url, source, date, type, priority, tags, kt):
    return dict(id=id, title=title, url=url, source=source, published_at=f"{date}T00:00:00Z",
                type=type, priority=priority, tags=tags, key_takeaway=[kt])

cards = [
 card("gpt-6-1-sol-ultrafast-2026-10-09", "GPT-6.1 Sol Ultrafast", "https://developers.openai.com/api/docs/guides/ultrafast-mode", "OpenAI / Blog", "2026-10-09", "changelog_feature", "P0", ["Act", "Top 10", "Model & IDE", "Blog", "X"], KT["ultrafast"]),
 card("claude-code-2-1-296-2026-10-09", "Claude Code 2.1.296", "https://code.claude.com/docs/en/changelog#2-1-296", "Anthropic / Blog", "2026-10-09", "changelog_feature", "P0", ["Act", "Top 10", "Model & IDE", "Blog"], KT["cc"]),
 card("trl-v1-15-fused-lm-head-2026-10-09", "TRL v1.15 fused LM head", "https://lnkd.in/p/gi4baeNn", "LinkedIn", "2026-10-09", "changelog_feature", "P0", ["Build", "Top 10", "Model & IDE", "LinkedIn"], KT["trl"]),
 card("google-flowagent-autorepair-2026-10-09", "Google FlowAgent (AutoRepair)", "https://arxiv.org/abs/2610.07289", "X / arXiv", "2026-10-09", "research", "P0", ["Build", "Top 10", "Papers", "X"], TLDR["flowagent"]),
 card("sansi-looped-typed-decision-2026-10-09", "SanSi: A Looped Typed Decision Model for System 1.5 Thinking", "https://huggingface.co/papers/2610.07730", "Hugging Face / Papers", "2026-10-09", "research", "P0", ["Learn", "Top 10", "Papers"], TLDR["sansi"]),
 card("ai2-impactful-scheduling-2026-10-09", "Ai2 Impactful Scheduling", "https://allenai.org/blog/impactful-scheduling", "Ai2 / Blog", "2026-10-09", "application_case_study", "P0", ["Learn", "Top 10", "Applicational", "Blog"], KT["ai2"]),
 card("testprism-joint-success-2026-10-09", "TestPrism: Rethinking Test Evaluation Beyond a Single Reference", "https://huggingface.co/papers/2610.12289", "Hugging Face / Papers", "2026-10-09", "research", "P0", ["Learn", "Top 10", "Papers"], TLDR["testprism"]),
 card("rsigym-research-agent-services-2026-10-09", "RSIGym", "https://x.com/omarsar0/status/2108239214588342609", "X", "2026-10-09", "application_case_study", "P0", ["Watch", "Top 10", "Applicational", "X"], KT["rsigym"]),
 card("playsuite-video-game-agents-2026-10-09", "PlaySuite", "https://lnkd.in/p/gbvGXRXH", "LinkedIn", "2026-10-09", "application_case_study", "P0", ["Learn", "Top 10", "Applicational", "LinkedIn"], KT["playsuite"]),
 card("anthropics-knowledge-work-plugins-2026-10-09", "anthropics/knowledge-work-plugins", "https://github.com/anthropics/knowledge-work-plugins", "GitHub", "2026-10-09", "model_release_implementation", "P0", ["Build", "Top 10", "GitHub Trending"], TLDR["plugins"]),
 card("anthropic-cyber-mission-2026-10-09", "Anthropic Cyber Mission", "https://www.anthropic.com/news/anthropic-cyber-mission", "Anthropic / Blog", "2026-10-09", "application_case_study", "P2", ["Watch", "Radar", "Applicational", "Blog"], KT["cyber"]),
 card("tokenrouter-token-level-routing-2026-10-09", "TokenRouter: Efficient Serving System for Token-Level LLM Routing", "https://huggingface.co/papers/2610.12242", "Hugging Face / Papers", "2026-10-09", "research", "P2", ["Watch", "Radar", "Papers"], KT["tokenrouter"]),
card("snowflake-decision-cortex-2026-10-09", "Snowflake Decision (Cortex AI_COMPLETE)", "https://www.snowflake.com/en/blog/snowflake-decision-cortex-ai-functions/", "Snowflake / Blog", "2026-10-09", "model_release_implementation", "P2", ["Watch", "Radar", "Model & IDE", "Blog"], KT["snowflake"]),
]

week = json.load(open("../ingest-2026-10-08/week.json"))
assert week["week_start"] == "2026-10-05"
w = week
ADD09 = (
  "10-09（補跑）：GPT-6.1 Sol Ultrafast（docs：service_tier＋WebSocket；8×／$12/$60 屬 X 側）、"
  "Claude Code 2.1.296（subagent autoCompact／workflow model／allow_large）、"
  "TRL v1.15 fused LM head（GRPO 29k→115k 自報）、"
  "Google FlowAgent／AutoRepair（CI ReAct 修 bug，X 報 ~67%）、"
  "SanSi（looped typed decision 72.0%）、Ai2 Impactful Scheduling、"
  "TestPrism（Joint Success 28% vs 單 reference 60%）、RSIGym、PlaySuite（5,734 games）、"
  "anthropics/knowledge-work-plugins（11 個角色 plugins）。"
  "實務 takeaway："
)
w["synthesis"] = w["synthesis"].replace("實務 takeaway：", ADD09, 1)
w["synthesis"] = w["synthesis"].replace(
  "Radar：",
  "Radar：Anthropic Cyber Mission（OSS Scanner）；TokenRouter（token-level routing serving）；Snowflake Decision（Cortex typed，Jev subset 57.63）；",
  1,
)
ts = w["type_summaries"]
def add(k, s): ts[k] = (ts.get(k, "") + s)
add("research", "10-09：FlowAgent／AutoRepair（CI ReAct APR）；SanSi（looped typed decision 72.0%）；TestPrism（Joint Success 28%）；TokenRouter（radar）。")
add("application_case_study", "10-09：Ai2 Impactful Scheduling；RSIGym；PlaySuite（5,734 games）；Cyber Mission（radar）。")
add("changelog_feature", "10-09：GPT-6.1 Sol Ultrafast；Claude Code 2.1.296；TRL v1.15 fused LM head。")
add("model_release_implementation", "10-09：anthropics/knowledge-work-plugins（11 plugins；GitHub Trending）；Snowflake Decision（radar，private preview）。")

json.dump(cards, open("cards.json", "w"), ensure_ascii=False, indent=1)
json.dump(week, open("week.json", "w"), ensure_ascii=False, indent=1)
for c in cards: print(c["priority"], c["type"], c["id"], len(c["key_takeaway"][0]))
print("PENDING check:", "PENDING" in json.dumps([cards, week]))
print("week_start:", week["week_start"], "cards:", len(cards))

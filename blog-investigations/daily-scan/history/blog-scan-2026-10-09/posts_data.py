# New posts for makeup scan 2026-10-09 (window: after 10-08 ~06:10 HKT through 10-09).
# Facts from fetched HTML/txt, WebFetch (openai.com 403 via curl), npm, GitHub releases.
CC="https://code.claude.com/docs/en/changelog"
OR_MODELS="https://openrouter.ai/api/v1/models"
UF="https://developers.openai.com/api/docs/guides/ultrafast-mode"
PRICING="https://developers.openai.com/api/docs/pricing"

POSTS = [
 # ---- Claude Code
 dict(source="claude-code-changelog", card_source="Claude Code Changelog", title="Claude Code 2.1.296",
  url="https://code.claude.com/docs/en/changelog#2-1-296", date="2026-10-09",
  category="changelog_features", type="changelog_feature", priority="P1", tags=["cli","feature","agents"], digest_focus=True,
  artifacts=["claude-code@2.1.296"],
  discovered_via="npm @anthropic-ai/claude-code latest/next 2.1.296 (2026-10-09 16:58 UTC) + raw.githubusercontent CHANGELOG.md 2.1.294–2.1.296",
  summary="Claude Code 2.1.294–2.1.296: fail-closed hooks (onFailure:block), OSC 7501 program-status protocol, subagent autoCompactWindow + CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL, Read allow_large, Desktop gateway code policies; prompt/agent instruction hooks fixed so they actually block.",
  key_takeaway=[
   "2.1.295: hooks can set onFailure:\"block\" so a hook that fails to start, times out, or exits unexpectedly blocks the action instead of failing open — material reliability change for managed/gated tool use",
   "2.1.295: Program Status Protocol OSC 7501 — terminals can show whether Claude Code is working, waiting on the user, or done (same family as Pi 1.1.0)",
   "2.1.296: autoCompactWindow on subagent frontmatter / --agents so a subagent can compact earlier than the main conversation; CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL forces every workflow agent onto one model",
   "2.1.296: Read tool allow_large option to load an oversized text file in one call when context has room; Claude Desktop Code tab can share managed.policies[] via apps gateway code key",
   "2.1.294: fixed prompt/agent hooks written as natural-language instructions (\"Block commands that…\") that were allowing what they should block; Stop/SubagentStop instruction hooks less likely to stop early",
   "npm: latest/next = 2.1.296 (2026-10-09 16:58 UTC / 10-10 00:58 HKT); stable tag still 2.1.287"],
  priority_reason="Agent-enhancing changelog: fail-closed hooks, OSC 7501 status, and per-subagent auto-compact change execution/reliability and observability for harness builders → P1 digest_focus.",
  needs_verification=False,
  alt_urls=["https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md"]),

 # ---- Codex
 dict(source="codex-changelog", card_source="Codex (GitHub releases)", title="Codex CLI 0.162.1",
  url="https://github.com/openai/codex/releases/tag/rust-v0.162.1", date="2026-10-09",
  category="changelog_features", type="changelog_feature", priority="P1", tags=["cli","feature","agents"], digest_focus=True,
  artifacts=["@openai/codex@0.162.1"],
  discovered_via="npm @openai/codex latest 0.162.1 (2026-10-09 19:50 UTC); features from rust-v0.162.0 release notes (2026-10-08 18:55 UTC); developers.openai.com Codex changelog page not yet updated",
  summary="Codex 0.162.0 adds managed Git worktree tools, Command Center task pinning, custom-provider live web + remote compaction, ranked Code Mode tool search, Guardian Decisions comparison, Ultrafast for Bedrock Astra, incremental tool catalog updates; 0.162.1 is a TUI crash + feature-flag startup hotfix.",
  key_takeaway=[
   "0.162.0 features: create/list managed Git worktrees from trusted local projects; pin tasks in Command Center (p); /copy + Ctrl+Insert transcript copy; mouse_scroll_speed; clickable URLs in approvals/MCP/banners",
   "Agent/infra: configure live web access + remote compaction for custom Responses-compatible providers; JS helpers stream promise results as they settle; opt-in ranked tool search in Code Mode; incremental_tools / Responses Lite tool catalog updates",
   "Guardian/Decisions: opt-in Decisions comparison for Guardian V2, bounded Decisions transport, agreement/latency metrics; protect Guardian Decisions API key from env forwarding; Daybreak opt-in in TUI/CLI",
   "Ultrafast: enable Ultrafast service tiers for Amazon Bedrock Astra models; Fast and Ultra Fast policies enforced independently",
   "0.162.1 (10-09): fix TUI crash on multi-line async questions; fix startup failures when background server feature settings differ from CLI defaults",
   "Availability: npm latest 0.162.1; developers.openai.com Codex changelog page still shows no 0.162 entry (notes from GitHub releases)"],
  priority_reason="Agent-enhancing Codex release: worktrees, incremental tools, Guardian Decisions, and Ultrafast Bedrock support change coordination and latency options → P1 digest_focus.",
  needs_verification=False,
  alt_urls=["https://github.com/openai/codex/releases/tag/rust-v0.162.0","https://developers.openai.com/codex/changelog"]),

 # ---- OpenAI Ultrafast
 dict(source="openai-news", card_source="OpenAI Developers Docs", title="Ultrafast mode for GPT-6 Astra and GPT-6.1 Sol",
  url=UF, date="2026-10-09",
  category="applications", type="application_case_study", priority="P1", tags=["api-drop","agents","product"], digest_focus=True,
  artifacts=["service_tier=ultrafast","gpt-6.1-sol","gpt-6-astra"],
  discovered_via="developers.openai.com Ultrafast guide + pricing table (curl 200); X OpenAIDevs 10-09; Codex 0.162.0 Bedrock Ultrafast PR; not in openai-news RSS",
  summary="Ultrafast is the fastest OpenAI API service tier, broadly available for gpt-6-astra and gpt-6.1-sol via service_tier=ultrafast (WebSockets recommended for tool-heavy agents). Separate rate limits from Standard/Fast. GPT-6.1 Sol Ultrafast short-context list price $12 / $60 per 1M input/output (cached $0.60, cache write $15); long-context $24 / $90.",
  key_takeaway=[
   "Availability: docs state Ultrafast for GPT-6 Astra and GPT-6.1 Sol is available to all API users; set model + service_tier:\"ultrafast\" on response.create; WebSockets strongly recommended for agentic multi-tool loops",
   "Pricing (developers.openai.com/api/docs/pricing Ultrafast table): gpt-6.1-sol short $12 input / $0.60 cached / $15 cache write / $60 output per 1M; long $24 / $1.20 / $30 / $90. gpt-6-astra Ultrafast short $60 / $6 / $75 / $300; long $120 / $12 / $150 / $450",
   "Vs Standard gpt-6.1-sol (~$1 / $0.05 / …): Ultrafast input list is ~12×; X OpenAIDevs claims ~8× Sol Standard throughput — treat speed claim as provider marketing pending independent measurement",
   "Residency: GPT-6.1 Sol Ultrafast supports US + EU data residency and global processing; GPT-6 Astra Ultrafast supports US residency + global only",
   "Related: Codex 0.162.0 enables Ultrafast tiers for Bedrock Astra; ChatGPT Work / Codex surface called out in X post — this card is the API docs primary"],
  priority_reason="Major latency/cost API pattern for agent builders (separate tier + ~12× Sol list price), broadly available per docs, but exact public GA timestamp not in API changelog HTML (newest dated Oct 5) and speed claims unverified → P1 not confirmed P0.",
  needs_verification=True,
  verification_note="API changelog HTML fetch on 10-09 only surfaces an October 5, 2026 header in the parsed extract; Ultrafast GA date inferred from docs 'broadly available' wording + X OpenAIDevs 10-09 + Codex 0.162.0 Bedrock Ultrafast. Speed '8× Sol Standard' is X/provider claim, not independently measured here.",
  metrics={"pricing":{"status":"published","currency":"USD",
    "items":[
      {"model":"gpt-6.1-sol","service_tier":"ultrafast","input_per_1m":12.0,"cached_input_per_1m":0.60,"cache_write_per_1m":15.0,"output_per_1m":60.0,"unit":"per 1M tokens","condition":"short context (Ultrafast pricing table)"},
      {"model":"gpt-6.1-sol","service_tier":"ultrafast","input_per_1m":24.0,"cached_input_per_1m":1.20,"cache_write_per_1m":30.0,"output_per_1m":90.0,"unit":"per 1M tokens","condition":"long context"},
      {"model":"gpt-6-astra","service_tier":"ultrafast","input_per_1m":60.0,"cached_input_per_1m":6.0,"cache_write_per_1m":75.0,"output_per_1m":300.0,"unit":"per 1M tokens","condition":"short context"},
      {"model":"gpt-6-astra","service_tier":"ultrafast","input_per_1m":120.0,"cached_input_per_1m":12.0,"cache_write_per_1m":150.0,"output_per_1m":450.0,"unit":"per 1M tokens","condition":"long context"}],
    "source_url":[UF,PRICING],"official_pricing_page":PRICING}},
  alt_urls=["https://developers.openai.com/api/docs/pricing","https://x.com/OpenAIDevs/status/2108262812489531498"]),

 # ---- Anthropic Cyber Mission
 dict(source="anthropic-research", card_source="Anthropic", title="Introducing the Anthropic Cyber Mission",
  url="https://www.anthropic.com/news/anthropic-cyber-mission", date="2026-10-08",
  category="applications", type="application_case_study", priority="P2", tags=["safety","enterprise","product"], digest_focus=False,
  discovered_via="anthropic.com/news listing Oct 8 (curl 200)",
  summary="Anthropic launches Cyber Mission: Critical Infrastructure Defense Program (CIDP) pairs frontier Claude + on-site engineers + threat research with OT security providers (Accenture, CrowdStrike, Dragos, Palo Alto, Rockwell, …); OSS Scanner offers free regular frontier-model vulnerability scans + proposed patches for open-source projects.",
  key_takeaway=[
   "Two pillars: critical infrastructure OT (power/water/transport/gov) via CIDP founding partners; open-source via free OSS Scanner using Anthropic's strongest models",
   "Builds on Project Glasswing → expanded Cyber Verification Program (carded 10-06); Cyber Mission adds engineering talent, tools, and funding for defenders",
   "Builder angle: OSS maintainers can get free model-driven vuln scans; general API builders see no new model capability"],
  priority_reason="Security product/program launch; OSS Scanner is useful for maintainers but not a general agent/model delta → P2.",
  needs_verification=False),

 dict(source="anthropic-research", card_source="Anthropic", title="2026 Usage Policy update",
  url="https://www.anthropic.com/news/2026-usage-policy-update", date="2026-10-08",
  category="applications", type="application_case_study", priority="P3", tags=["safety","enterprise"], digest_focus=False,
  discovered_via="anthropic.com/news Oct 8",
  summary="Annual Usage Policy refresh effective Nov 12: consolidates deceptive campaigns/artificial activity rules; clarifies high-risk health/finance, autonomous physical actions, and abusive behaviour toward models; examples for longer independent Claude work.",
  key_takeaway=["Takes effect 2026-11-12","New consolidated section: Do Not Engage in Deceptive Campaigns or Artificial Activity","Clarifies autonomous physical-action controls"],
  priority_reason="Policy clarification without new builder capability → P3.", needs_verification=False),

 dict(source="anthropic-research", card_source="Anthropic", title="Building on our commitment to American scientific discovery",
  url="https://www.anthropic.com/news/genesis-mission-commitment", date="2026-10-08",
  category="applications", type="application_case_study", priority="P3", tags=["enterprise","science"], digest_focus=False,
  discovered_via="anthropic.com/news Oct 8",
  summary="Anthropic commits $150M over 3 years to the US Genesis Mission: Claude/Claude Code/API credits for hundreds of federal research projects across 15+ agencies (NASA, NIH, NSF), plus training and support; expands Dec Dec partnership.",
  key_takeaway=["$150M / 3 years federal science commitment","Credits + onboarding for Genesis Mission projects; fusion energy and quantum among priorities"],
  priority_reason="Funding/partnership announcement → P3.", needs_verification=False),

 # ---- OpenAI news (WebFetch; curl 403)
 dict(source="openai-news", card_source="OpenAI", title="Asana cuts model costs 76x in browser tests with GPT-6.1 Sol",
  url="https://openai.com/index/asana-browser-agent", date="2026-10-09",
  category="applications", type="application_case_study", priority="P1", tags=["agents","evals","workflow"], digest_focus=True,
  discovered_via="openai-news RSS 10-09; body via WebFetch (curl 403)",
  summary="Asana used GPT-6 Astra in Codex to redesign StackAI browser-agent history caching/screenshot policy: 144-run study; optimized GPT-6.1 Sol workflow averaged $0.47/run and ~4 min (76× cheaper and 5× faster vs original Model B production); 89% of input from cache at 5% uncached price.",
  key_takeaway=[
   "Root cause: agent cached fixed instructions/tools but not growing page-text/screenshot history; every step resent history at full price and trimmed screenshots each turn (breaking cache)",
   "Fixes tested: cache browsing history; larger history budgets (120k vs 480k chars); batch screenshot eviction (accumulate to 20 then keep most recent) so earlier history stays cache-stable",
   "Results (means of 3 runs): Model B ≥$36.21 → $1.24 optimized (29×); GPT-6.1 Sol optimized $0.47 (2.6× cheaper than Model B optimized); Sol alone 4× cheaper ($1.97→$0.47) with 89% cached input; runtime ≥22.5 min → ~4 min",
   "Larger history budget: Sol answer rate 3/18 → 18/18 correct; GPT-6 Astra in Codex compressed ~1–2 months of manual research into ~1 week",
   "Limits: Models A/B/C anonymized; run SDs reconstructed from charts; customer story + Asana/StackAI blogs"],
  priority_reason="Measured browser-agent caching pattern with hard cost/latency deltas that builders can copy → P1 digest_focus.",
  needs_verification=False),

 dict(source="openai-news", card_source="OpenAI", title="Sophos cuts threat investigation time by 96% with OpenAI Daybreak",
  url="https://openai.com/index/sophos", date="2026-10-09",
  category="applications", type="application_case_study", priority="P2", tags=["agents","enterprise","safety"], digest_focus=False,
  discovered_via="openai-news RSS 10-09; WebFetch body",
  summary="Sophos MDR agents via OpenAI Daybreak: investigation time ~38 min → ~89 s (96%); 52% of MDR cases resolved end-to-end by AI within Notify/Collaborate/Authorise customer modes; plan–execute–review loop over Fusion sensor data.",
  key_takeaway=["89 s average response for agent-handled cases; 52% MDR cases end-to-end AI","Human oversight retained for destructive actions; three customer operating modes","Daybreak programme customer story — no new public model/API"],
  priority_reason="Strong measured cyber-agent case study but vertical Daybreak partnership → P2.", needs_verification=False),

 dict(source="openai-news", card_source="OpenAI", title="LegalOn halves Codex costs while maintaining development speed",
  url="https://openai.com/index/legalon-halves-codex-costs", date="2026-10-08",
  category="applications", type="application_case_study", priority="P2", tags=["agents","workflow","evals"], digest_focus=False,
  discovered_via="openai-news RSS 10-08; WebFetch",
  summary="LegalOn AID CoE moved from unlimited GPT-5.5 Fast to task-tiered GPT-6 Luna / GPT-6.1 Sol / GPT-6 Astra plus Fast-mode restriction by default and department budgets: ~65% lower estimated daily Codex costs; ~20% efficiency ask for mature lines vs generous new-business budgets.",
  key_takeaway=["Luna=simple implementation/subagent; Sol=standard design/analysis; Astra=complex orchestration","Fast mode off by default; parallel tasks to keep speed","Building feature-release-level ROI metric tying AI spend to customer value"],
  priority_reason="Useful model-routing/cost governance pattern; incremental case study → P2.", needs_verification=False),

 dict(source="openai-news", card_source="OpenAI", title="How Oracle turns days of work into minutes with ChatGPT and Codex",
  url="https://openai.com/index/oracle", date="2026-10-08",
  category="applications", type="application_case_study", priority="P3", tags=["enterprise","use-case"], digest_focus=False,
  discovered_via="openai-news RSS; WebFetch",
  summary="Oracle: 130K ChatGPT + 95K+ Codex users; talent-market tool cuts recruiting research 98% (2–4 days → 15–20 min); Applications Lab ontology+Codex for natural-language→SQL; SRE incident playbooks in minutes.",
  key_takeaway=["Enterprise adoption metrics; recruiting 98% time cut","Leadership lessons: guardrails, prototypes over specs, own the code"],
  priority_reason="Broad customer story without reproducible builder method → P3.", needs_verification=False),

 dict(source="openai-news", card_source="OpenAI", title="Disrupting AI-enabled “false front” operations",
  url="https://openai.com/index/disrupting-ai-enabled-false-front-operations", date="2026-10-08",
  category="research", type="research", priority="P2", tags=["safety","evals"], digest_focus=False,
  discovered_via="openai-news RSS; WebFetch",
  summary="OpenAI banned Russia-origin 'Dark Clark' (Category 5 IO — fake Latin America think tank + planted fakes) and Iran-origin 'Bogus Bylines' (Category 4 — seven fake journalist personas pitching long-form articles). First Category 5 disruption in their reporting series.",
  key_takeaway=["False-front IO resemble pre-AI ops but AI scales drafting/pitching/internal reporting","Highest-reach ops land content in real media, not just social","Disclosure still effective disruption tool"],
  priority_reason="Important threat-intel pattern for safety teams; not a builder product delta → P2.", needs_verification=False),

 dict(source="openai-news", card_source="OpenAI", title="Pollo AI turns creative ideas into campaigns with OpenAI",
  url="https://openai.com/index/pollo-ai", date="2026-10-08",
  category="applications", type="application_case_study", priority="P3", tags=["use-case","multimodal","product"], digest_focus=False,
  discovered_via="openai-news RSS description only (WebFetch skipped; low signal)",
  summary="Pollo AI customer story: GPT-5.6, GPT-6 Astra, and GPT-Image-2.5 for image/video ad campaigns (RSS blurb).",
  key_takeaway=["Creative-tools customer story","No measured builder-facing API change in RSS summary"],
  priority_reason="Marketing customer story → P3.", needs_verification=False),

 # ---- NVIDIA
 dict(source="nvidia-developer", card_source="NVIDIA Developer Blog", title="Building Reliable Data Analytics Agents: Lessons from the KDD Cup",
  url="https://developer.nvidia.com/blog/building-reliable-data-analytics-agents-lessons-from-the-kdd-cup/", date="2026-10-08",
  category="engineering", type="engineering", priority="P1", tags=["agents","evals","rag"], digest_focus=True,
  discovered_via="nvidia-developer Atom feed 10-08",
  summary="NVIDIA KGMON 2nd place KDD Cup 2026 Data Agents with a constrained harness around a small fixed LLM: unify CSV/JSON into SQLite (schema()/sql()), preflight schema scouting, tiny toolset + middleware repair, separate prose_helper for documents, execution-trace inspector agent.",
  key_takeaway=[
   "Constraint > openness when the model is fixed/small: one SQL surface for structured data; tools limited to schema(), sql(query), write_answer(df), prose_helper()",
   "Preflight schema-scout briefs tables/join keys/data-quality issues before the main loop; middleware repairs malformed calls; persistent state keeps intermediates",
   "Documents handled out-of-band (preview/regex → zero-temp prose_helper) so raw prose does not flood main context",
   "Execution traces feed an inspector agent that categorises failures to drive harness iteration",
   "Applicable pattern for reliable data agents on small/open models; competition-specific, not a product release"],
  priority_reason="Concrete, measured harness recipe for data agents that changes how builders constrain tools and evaluate traces → P1 digest_focus.",
  needs_verification=False),

 dict(source="nvidia-developer", card_source="NVIDIA Developer Blog", title="5 Steps to Create SimReady Assets for Robotics with Frontier AI Models",
  url="https://developer.nvidia.com/blog/5-steps-to-create-simready-assets-for-robotics-with-frontier-ai-models/", date="2026-10-08",
  category="engineering", type="engineering", priority="P3", tags=["science","agents"], digest_focus=False,
  discovered_via="nvidia-developer Atom 10-08",
  summary="CAD→SimReady OpenUSD workflow (import, appearance, physics, validate, Isaac Sim pick-and-place) assisted by frontier models (e.g. GPT-6 Astra) writing Omniverse Python; ABB YuMi demo.",
  key_takeaway=["Five-step SimReady Foundation + agentic NVIDIA skills path","Robotics/simulation niche"],
  priority_reason="Robotics asset pipeline outside core LLM-agent builder focus → P3.", needs_verification=False),

 # ---- Ai2 / HF
 dict(source="allen-ai", card_source="Ai2", title="Impactful scheduling for GPU clusters",
  url="https://allenai.org/blog/impactful-scheduling", date="2026-10-09",
  category="engineering", type="engineering", priority="P2", tags=["infra","optimization"], digest_focus=False,
  discovered_via="allenai.org HTML + huggingface.co/blog/allenai/impactful-scheduling RSS 10-09",
  summary="Ai2 replaced priority-based GPU scheduling with GPU time budgets, hierarchical fair-share, and a time-slicing contract across H100/B200/B300 clusters (88–1024 GPUs, ~150 researchers) to maximise research impact while keeping occupancy high.",
  key_takeaway=["Metrics pyramid: availability → occupancy → impact → utilization","Budgets + fair-share move allocation fights from ops tickets to admin budgeting","Open write-up; no open-source scheduler drop in the post"],
  priority_reason="Solid cluster-ops engineering; narrow audience vs agent builders → P2.",
  needs_verification=False,
  alt_urls=["https://huggingface.co/blog/allenai/impactful-scheduling"]),
]

CARD_IDS = {
  "https://code.claude.com/docs/en/changelog#2-1-296": "claude-code-2-1-296-2026-10-09",
  "https://github.com/openai/codex/releases/tag/rust-v0.162.1": "codex-0-162-1-2026-10-09",
  UF: "openai-ultrafast-gpt6-2026-10-09",
  "https://www.anthropic.com/news/anthropic-cyber-mission": "anthropic-cyber-mission-2026-10-08",
  "https://www.anthropic.com/news/2026-usage-policy-update": "anthropic-usage-policy-2026-10-08",
  "https://www.anthropic.com/news/genesis-mission-commitment": "anthropic-genesis-mission-2026-10-08",
  "https://openai.com/index/asana-browser-agent": "openai-asana-browser-agent-2026-10-09",
  "https://openai.com/index/sophos": "openai-sophos-daybreak-2026-10-09",
  "https://openai.com/index/legalon-halves-codex-costs": "openai-legalon-codex-costs-2026-10-08",
  "https://openai.com/index/oracle": "openai-oracle-chatgpt-codex-2026-10-08",
  "https://openai.com/index/disrupting-ai-enabled-false-front-operations": "openai-false-front-io-2026-10-08",
  "https://openai.com/index/pollo-ai": "openai-pollo-ai-2026-10-08",
  "https://developer.nvidia.com/blog/building-reliable-data-analytics-agents-lessons-from-the-kdd-cup/": "nvidia-kdd-data-agents-2026-10-08",
  "https://developer.nvidia.com/blog/5-steps-to-create-simready-assets-for-robotics-with-frontier-ai-models/": "nvidia-simready-assets-2026-10-08",
  "https://allenai.org/blog/impactful-scheduling": "ai2-impactful-scheduling-2026-10-09",
}

MIRRORS = [
  dict(source="huggingface", title="Impactful scheduling for GPU clusters",
       url="https://huggingface.co/blog/allenai/impactful-scheduling", date="2026-10-09",
       card_url="https://allenai.org/blog/impactful-scheduling"),
]

SOURCE_ONLY = [
  dict(source="huggingface", title="The model that didn't exist, so you made it yourself",
       url="https://huggingface.co/blog/building-with-ml-intern", date="2026-10-08",
       category="applications", tags=["use-case"], summary="HF community/lab post about building a missing model (ML-Intern); not an org product release.",
       digest_focus=False, not_carded_reason="HF community/personal lab narrative; convention skip like other non-org HF posts"),
  dict(source="mistral", title="LIDstral-Arabic / Voxtral-Mini-4B-Realtime-Arabic on Hugging Face",
       url="https://huggingface.co/mistralai/LIDstral-Arabic", date="2026-10-08",
       category="model_release_benchmark", tags=["open-weights","multimodal"],
       summary="mistralai org uploaded LIDstral-Arabic and Voxtral-Mini-4B-Realtime-Arabic (HF API createdAt 2026-10-08); not Mistral Large 4 weights.",
       digest_focus=False, not_carded_reason="Arabic niche speech/LID checkpoints; Large 4 weights still absent — recorded for recheck trail only"),
]

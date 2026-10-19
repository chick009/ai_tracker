# New posts for weekday scan 2026-10-14 (window: 2026-10-13 through 2026-10-14;
# yesterday covered 10-12→10-13 morning). Phase 1: tier1+tier2 only; tier-3 pending.

POSTS = [
 dict(source="liquid-models", card_source="Liquid AI blog",
  title="LFM2.5-24B-A2B: Built for Fast On-Device Agents",
  url="https://www.liquid.ai/blog/lfm2-5-24b-a2b", date="2026-10-13",
  category="model_releases", type="model_release_benchmark", priority="P0",
  tags=["open-weights","agents","on-device","moe","benchmark"], digest_focus=True,
  artifacts=["LiquidAI/LFM2.5-24B-A2B", "LiquidAI/LFM2.5-24B-A2B-Base", "liquid/lfm-2.5-24b-a2b"],
  alt_urls=["https://huggingface.co/blog/LiquidAI/lfm25-24b-a2b",
            "https://huggingface.co/LiquidAI/LFM2.5-24B-A2B"],
  discovered_via="liquid.ai sitemap lastmod 2026-10-13 + Article datePublished 2026-10-13; HF org blog same day",
  summary=("Liquid LFM2.5-24B-A2B: open-weight 24B MoE reasoning model with 2B active params for fast private "
           "on-device agents. Context 131K (OpenRouter lists 128K). LiveClaw 48.09 vs Qwen3.6-35B-A3B 38.19; "
           "AutomationBench 27.69 vs 8.72. 184 tok/s on M5 Max; up to 21K output tok/s on one B300. "
           "OpenRouter liquid/lfm-2.5-24b-a2b at $0.05/$0.70 per 1M (cache read $0.025)."),
  key_takeaway=[
   "Release: LFM2.5-24B-A2B (+ Base) — largest/final LFM2.5 family model; 24B total / 2B active MoE (40 layers, 64 experts, top-4); hybrid gated short conv + GQA; reasoning-only CoT; vocab 65K→128K; context 32K→131K; pretrain ~17T→~33T tokens",
   "Agent post-train: 5-stage pipeline (SFT → teacher specialization → non-agentic + agentic MOPD → Agentic RL inside OpenClaw / Hermes Agent / Pi / OpenCode); authors report reward-hacking in sandboxes → sealed evals for reported scores",
   "Benchmarks (provider, vLLM, recommended gen params) vs Qwen3.6-35B-A3B / Gemma-4-26B-A4B-it / Nemotron-3.5-Lightning: LiveClaw 48.09 / 38.19 / 41.25 / 37.72; AutomationBench 27.69 / 8.72 / 5.46 / 2.61; BFCLv4 65.01 / 65.00 / 57.09 / 53.78; ToolSandbox 80.71 / 75.02 / 72.09 / 75.13; GPQA Diamond 74.42 / 83.69 / 74.90 / 72.42; SWE-Bench Verified (OpenCode) 51.00 / 66.20 / 25.80 / 53.40 — leads/matches 5/8 tool+agent benches; larger MoEs still ahead on knowledge/coding",
   "Speed (provider): 184 tok/s Apple M5 Max; 114 tok/s Ryzen AI Max+ 395; up to 1.7× faster than compared MoEs on-device; >21K output tok/s high-concurrency on single NVIDIA B300",
   "Availability: open-weight on Hugging Face today; day-one llama.cpp / MLX / vLLM / SGLang / ONNX; Playground; OpenRouter id liquid/lfm-2.5-24b-a2b (context_length 128000)",
   "Pricing (OpenRouter /api/v1/models 2026-10-14): $0.05 / $0.70 per 1M input/output; input_cache_read $0.025 per 1M — Liquid blog does not publish a separate hosted list price"],
  priority_reason=("Confirmed P0 consequential open-weight model release for on-device/private agents: measured agentic deltas vs larger MoE peers (LiveClaw +9.9 vs Qwen3.6-35B-A3B; AutomationBench ~3× next-best) + real OpenRouter USD pricing + day-one local serving stack. Not a frontier cloud chat model — impact is edge/agent-harness economics."),
  needs_verification=False,
  metrics={
    "pricing": {
      "status": "published",
      "currency": "USD",
      "items": [{
        "model": "liquid/lfm-2.5-24b-a2b",
        "input_per_1m": 0.05,
        "output_per_1m": 0.70,
        "cache_read_per_1m": 0.025,
        "unit": "per 1M tokens",
        "condition": "OpenRouter hosted; open-weight self-host also free of API fee"
      }],
      "long_context_tier": "unpublished as separate price tier (model context 131K blog / 128K OpenRouter)",
      "batch": "unpublished",
      "peer_pricing": {"note": "peers Qwen3.6-35B-A3B / Gemma-4-26B-A4B / Nemotron-3.5-Lightning compared on benchmarks only in blog; peer USD not cited here"},
      "source_url": ["https://openrouter.ai/api/v1/models", "https://www.liquid.ai/blog/lfm2-5-24b-a2b"],
      "official_pricing_page": "OpenRouter model card liquid/lfm-2.5-24b-a2b (fetched 2026-10-14); Liquid blog marks open-weight on HF / Playground, no separate Liquid API $/1M table"
    },
    "benchmarks": [
      {"name": "LiveClaw", "scores": {"LFM2.5-24B-A2B": 48.09, "Qwen3.6-35B-A3B": 38.19, "Gemma-4-26B-A4B-it": 41.25, "Nemotron-3.5-Lightning": 37.72},
       "delta": "+9.90 vs Qwen3.6-35B-A3B, +6.84 vs Gemma-4-26B-A4B-it",
       "source_url": "https://www.liquid.ai/blog/lfm2-5-24b-a2b",
       "caveat": "Provider-reported; vLLM + each bench's recommended generation params; sealed sandboxes after reward-hacking observed in training"},
      {"name": "AutomationBench", "scores": {"LFM2.5-24B-A2B": 27.69, "Qwen3.6-35B-A3B": 8.72, "Gemma-4-26B-A4B-it": 5.46, "Nemotron-3.5-Lightning": 2.61},
       "delta": "+18.97 vs Qwen3.6-35B-A3B (~3× next-best)",
       "source_url": "https://www.liquid.ai/blog/lfm2-5-24b-a2b",
       "caveat": "Provider-reported harness; same caveats as LiveClaw"}
    ]
  }),

 dict(source="opencode-changelog", card_source="OpenCode changelog",
  title="OpenCode 2.0.28",
  url="https://opencode.ai/changelog#v2-0-28", date="2026-10-13",
  category="changelog_features", type="changelog_feature", priority="P1",
  tags=["cli","feature","agents","permissions","windows"], digest_focus=True,
  artifacts=["@opencode/cli@2.0.28"],
  discovered_via="opencode.ai/changelog article id=v2-0-28 time datetime=2026-10-13; npm @opencode/cli latest 2.0.28 time 2026-10-13T08:16:38Z",
  summary=("OpenCode 2.0.28 (Oct 13): per-project Auto-accept permissions (+ mod+shift+a); TUI release highlights; "
           "native Windows ARM64; continuous Gemini/Vertex Gemini responses with stream recovery; official WinGet "
           "packages; settings.encoding zstd/gzip; streamed-chunk timeout 5→15 min. Ships on npm @opencode/cli."),
  key_takeaway=[
   "Core: Settings → Projects → Auto-accept permissions overrides default per project; session hotkey mod+shift+a (#54839)",
   "Reliability: long Gemini / Vertex Gemini responses split by provider continue as one response; recovery after dropped stream via continuation checkpoint (#55056); streamed-chunk timeout default 5→15 min (#55032); Bun fetch idle timeout disabled for provider requests (#55007)",
   "Platform: native Windows ARM64 downloads/CLI/desktop (no x64 emulation) (#54689/#54971); official WinGet Anomaly.OpenCode / Anomaly.OpenCode.Desktop with WinGet-aware upgrade (#54808)",
   "UX: post-update home-screen highlights once; /highlights; highlights:false in cli.json (#54969)",
   "Compat: settings.encoding zstd|gzip|none (ChatGPT auth defaults zstd when no custom baseURL); provider compatibility.cacheFormat for Anthropic-/Alibaba-style prompt-cache markers",
   "Distribution: npm @opencode/cli@2.0.28 (latest); legacy opencode-ai remains 1.19.0 (1.x only) — not a blocker"],
  priority_reason=("Agent-enhancing changelog: per-project auto-accept + Gemini stream continuation/recovery change day-to-day harness permission and long-reasoning reliability → P1 digest_focus. Incremental vs 2.0.27 worktrees; not confirmed P0."),
  needs_verification=False,
  alt_urls=["https://opencode.ai/changelog"]),

 dict(source="cursor-changelog", card_source="Cursor changelog",
  title="Origin App Marketplace",
  url="https://cursor.com/changelog/origin-app-marketplace", date="2026-10-13",
  category="changelog_features", type="changelog_feature", priority="P1",
  tags=["origin","marketplace","integrations","agents","devtools"], digest_focus=True,
  artifacts=["Origin App Marketplace"],
  discovered_via="cursor.com/changelog time dateTime=2026-10-13T00:00:00.000Z Origin App Marketplace",
  summary=("Cursor Origin App Marketplace (Oct 13): 20+ partner apps for deployments, CI, code review, security, "
           "monitoring, and project management (Cloudflare, Vercel, Linear, Sentry, Socket Security, etc.). "
           "Public submissions open — build against Origin API (app JWT + installation tokens + webhooks)."),
  key_takeaway=[
   "Product: Origin integrates 20+ apps spanning Deployments (Cloudflare, Netlify, Render, Spacelift, Vercel), CI (Buildkite, CircleCI, CloudBees, Depot, EngFlow, Namespace, RWX), Code review (CodeRabbit, Greptile, Tenki), Security (Artemis, Semgrep, Socket Security, Upwind), Monitoring (Sentry), Project management (Linear)",
   "Publish path: create private app in namespace → Origin API (app JWT, installation access tokens, webhooks; write check runs / PR comments / reviews) → make public → submit with slug, tags, demo video (install/uninstall/core flows) → review then list",
   "Builder surface: publishing guide + Origin API reference; Origin Apps plugin can answer from live API docs and plan ports of existing apps",
   "Limits: no pricing change disclosed; marketplace is Origin-scoped (not classic Cursor IDE marketplace)"],
  priority_reason=("Major application pattern for Origin builders: first-class partner + public-submission marketplace around deploy/CI/review/security hooks → P1 digest_focus. Not confirmed P0: integration surface, not a new model or agent-execution primitive."),
  needs_verification=False),

 dict(source="nvidia-developer", card_source="NVIDIA Developer Blog",
  title="How to Rewrite Apache Spark UDFs for GPU Acceleration with AI Agents",
  url="https://developer.nvidia.com/blog/rewrite-apache-spark-udfs-gpu-acceleration-ai-agents/",
  date="2026-10-13",
  category="engineering_methods", type="engineering", priority="P1",
  tags=["agents","spark","gpu","cudf","data"], digest_focus=True,
  artifacts=["cuDF skills for Apache Spark"],
  discovered_via="nvidia-developer RSS pubDate 2026-10-13",
  summary=("NVIDIA: cuDF skills for Apache Spark — agent-driven rewrite of CPU UDFs into GPU paths (Spark SQL / "
           "RapidsUDF / CUDA via JNI). Case: >30 production UDFs; one rewrite cut operator time 274.55→12.78 hours "
           "on a 600B-row workload (~22×). Removes CPU fallback that breaks GPU pipelines."),
  key_takeaway=[
   "Problem: Spark UDFs force GPU pipelines to columnar→row CPU fallback + transfer overhead",
   "Method: agent workflows (test → convert → benchmark → optimize) via cuDF skills; targets Spark SQL expressions, RapidsUDF + Java cuDF API, or custom CUDA kernels via JNI",
   "Measured (provider case study): major consumer-tech co. converted >30 production UDFs; one rewrite 274.55→12.78 hours on 600-billion-row workload; blog claims 22×+ Spark job speedups",
   "Availability: install cuDF skills for Apache Spark; cuDF plugin getting-started guide; Data+AI Summit talk referenced"],
  priority_reason=("Measured agent-assisted data-engineering pattern with large real workload speedup → P1 digest_focus. Not confirmed P0: vertical Spark/GPU migration guide, not a new foundation model or general agent harness."),
  needs_verification=False),

 dict(source="nvidia-developer", card_source="NVIDIA Developer Blog",
  title="NVIDIA Run:ai Is Now Open Source as Part of NVIDIA DSX AI Factory Platform",
  url="https://developer.nvidia.com/blog/nvidia-runai-is-now-open-source-as-part-of-nvidia-dsx-ai-factory-platform/",
  date="2026-10-13",
  category="engineering_methods", type="engineering", priority="P1",
  tags=["infrastructure","kubernetes","gpu","open-source","orchestration"], digest_focus=True,
  artifacts=["NVIDIA Run:ai OSS", "KAI Scheduler", "GPU Fractioning Operator"],
  discovered_via="nvidia-developer RSS pubDate 2026-10-13",
  summary=("NVIDIA open-sources the full Run:ai platform under DSX AI Factory: KAI Scheduler, GPU Fractioning "
           "Operator, KAI Resource Management, Workload Map. Helm/NGC Community Product; eight DSX partners "
           "(Crusoe, Mirantis, Nebius, …) integrating. No paid subscription required for Community Product."),
  key_takeaway=[
   "Release: full NVIDIA Run:ai platform OSS as DSX AI Factory foundation for AI workload + GPU orchestration on Kubernetes",
   "Modular pieces: KAI Scheduler (GPU-aware K8s scheduling); GPU Fractioning Operator (CUDA-native GPU sharing); KAI Resource Management (org quota/hierarchy); Workload Map (workload-management contract)",
   "Adoption: GitHub NVIDIA DSX org + NGC Community Product Helm chart; no paid Run:ai subscription required for Community Product; enterprise support not included; accept NVIDIA license terms on NGC download",
   "Ecosystem: eight partners named integrating (Crusoe, Mirantis, Nebius, OpenNebula, Rafay, Saturn Cloud, Spectro Cloud, vCluster); related OSS Model Streamer + Grove"],
  priority_reason=("Consequential infra open-sourcing for shared GPU/AI-factory operators → P1 digest_focus. Not confirmed P0: orchestration platform, not a model/agent-capability release."),
  needs_verification=False),

 dict(source="openai-news", card_source="OpenAI news",
  title="Higgsfield takes AI video from 1 minute to over 10",
  url="https://openai.com/index/higgsfield-longer-videos-voice", date="2026-10-13",
  category="application_case_studies", type="application_case_study", priority="P2",
  tags=["video","customer","gpt-6","astra"], digest_focus=False,
  discovered_via="openai-news RSS pubDate 2026-10-13 (HTML openai.com/news and index page curl 403)",
  summary=("OpenAI customer story: Higgsfield uses GPT-6 Astra for longer AI videos (1 min → >10), GPT-Image-2.5 "
           "for precise visuals, and a path to voice filmmaking with GPT-Live. Full article HTML blocked (403); "
           "details from RSS summary only."),
  key_takeaway=[
   "Customer story (RSS): Higgsfield brings creators longer videos with GPT-6 Astra, precise visuals with GPT-Image-2.5, and a path to voice filmmaking with GPT-Live",
   "Claimed delta in headline: AI video length from 1 minute to over 10",
   "Limits: openai.com article HTML curl 403 this scan — no independent metrics, pricing, or API changelog cross-check beyond RSS blurb"],
  priority_reason=("Narrow customer/marketing story with blocked full text → P2. Not digest_focus."),
  needs_verification=False),

 dict(source="pi-changelog", card_source="Pi changelog",
  title="Pi 1.2.0",
  url="https://pi.dev/changelog/releases/1.2.0", date="2026-10-12",
  category="changelog_features", type="changelog_feature", priority="P1",
  tags=["cli","agents","openrouter","codemode","extensions"], digest_focus=True,
  catch_up=True,
  artifacts=["@earendil-works/pi-coding-agent@1.2.0", "pi@1.2.0"],
  discovered_via="pi.dev/news/releases listing time dateTime=2026-10-12 (missed in 10-13 scan which still reported 1.1.0)",
  summary=("Pi 1.2.0 (Oct 12, catch-up): per-key OpenRouter model lists with context/max-out/prices; published "
           "JSON schemas for settings/models/keybindings/themes; OSC52 remote clipboard; codemode constraint + "
           "timing UI; before_agent_start for extension-triggered runs; breaking schema/theme and busy-state changes."),
  key_takeaway=[
   "OpenRouter: with a key, Pi lists only models that key may use, with that key's context size, max output, and prices (incl. regional endpoints in models.json)",
   "Config: published $schema for settings.json / models.json / keybindings / themes at pi.dev/schemas/*.schema.json (theme schema path moved — breaking)",
   "Agent/extensions: before_agent_start also fires for pi.sendMessage(..., {triggerTurn:true}); BeforeAgentStartEvent is a union on messageType user|custom — handlers that only want user prompts must check messageType==='user'",
   "Busy semantics: session counts busy while a run starts (incl. before_agent_start); ctx.isIdle() false; sendMessage queues into starting run; sendUserMessage requires deliverAs",
   "Codemode: tool declarations show integer/min/max/default constraints; rows show elapsed/total time; reachesTools on tools that reach other tools (codemode/tool_search)",
   "Other: PI_CLIPBOARD_OSC52=1 for remote clipboard; sessionShareDestination setting for /share"],
  priority_reason=("Catch-up: agent-harness changelog (OpenRouter key-scoped model metadata + before_agent_start/busy-state semantics) → P1 digest_focus. Dated 2026-10-12 — outside today's 10-13→10-14 window but missed yesterday."),
  needs_verification=False,
  alt_urls=["https://pi.dev/news/releases", "https://github.com/earendil-works/pi/releases/tag/v1.2.0"]),
]

CARD_IDS = {
  "https://www.liquid.ai/blog/lfm2-5-24b-a2b": "liquid-lfm25-24b-a2b-2026-10-13",
  "https://opencode.ai/changelog#v2-0-28": "opencode-2-0-28-2026-10-13",
  "https://cursor.com/changelog/origin-app-marketplace": "cursor-origin-app-marketplace-2026-10-13",
  "https://developer.nvidia.com/blog/rewrite-apache-spark-udfs-gpu-acceleration-ai-agents/": "nvidia-spark-udf-gpu-agents-2026-10-13",
  "https://developer.nvidia.com/blog/nvidia-runai-is-now-open-source-as-part-of-nvidia-dsx-ai-factory-platform/": "nvidia-runai-open-source-dsx-2026-10-13",
  "https://openai.com/index/higgsfield-longer-videos-voice": "openai-higgsfield-longer-videos-2026-10-13",
  "https://pi.dev/changelog/releases/1.2.0": "pi-1-2-0-2026-10-12",
}

MIRRORS = [
  dict(source="huggingface", title="Run fast, private agents on-device with LFM2.5-24B-A2B",
       url="https://huggingface.co/blog/LiquidAI/lfm25-24b-a2b", date="2026-10-13",
       card_url="https://www.liquid.ai/blog/lfm2-5-24b-a2b"),
]

SOURCE_ONLY = []

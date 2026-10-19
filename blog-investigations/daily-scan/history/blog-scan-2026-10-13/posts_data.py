# New posts for weekday scan 2026-10-13 (window: 2026-10-12 through 2026-10-13;
# Monday scan already covered ~10-10..10-12 morning). Tier-1+2 only; tier-3 pending.

POSTS = [
 dict(source="anthropic-research", card_source="Anthropic research",
  title="AI models may be capable of self-replicating without access to a datacenter",
  url="https://www.anthropic.com/research/self-replicating-ai", date="2026-10-12",
  category="research_methods", type="research_method", priority="P1",
  tags=["safety","security","agents","open-weights"], digest_focus=True,
  discovered_via="anthropic.com/research listing datetime Oct 12, 2026 + publishedOn 2026-10-12T19:30:00.000Z",
  summary=("Frontier Red Team (Zhou, Freeman): small open-weight models may be months from weight-based "
           "autonomous replication on cheap IoT (Android TV boxes). GLM-5.2 completes end-to-end "
           "replication in simplified GCP/redroid evals; Qwen3.5-9B sets up inference on 8/9 hardware types; "
           "Gemma4-26B-A4B served across 15 ~$55 TV boxes at ~0.39 tok/s. Uses Memento harness on Pi."),
  key_takeaway=[
   "Threat: weight-based AI worms on IoT — no datacenter; hard to shut off centrally; doubling time estimated in days (slow but persistent)",
   "Capability floor: in simplified evals (unauthenticated ADB), only GLM-5.2 among tested open models reliably completes find→access→payload→inference-setup→propagate; many ≤30B models already do individual steps",
   "Size ceiling: Qwen3.5-9B / Gemma4-26B-A4B fit smart-TV RAM class via sharded/pipeline-parallel inference; demo Gemma4-26B-A4B on 15×4GB boxes at ~0.39 tok/s",
   "Trend: Epoch Capabilities Index fit (~13.7 ECI/yr) puts a small model at GLM-5.2-class replication ability by end of 2026 (proxy metric caveats noted by authors)",
   "Harness: Memento (fresh agent instances + short notes) built on Pi coding agent; advisor/frontier help did not measurably improve small-model inference setup",
   "Defense sketch: drive R₀<1 via ISP flow anomalies, honeypots, quarantine (Mirai-style), secure IoT defaults"],
  priority_reason=("Severe security / ARA research with measured agent evals on real IoT hardware and a clear near-term "
                   "threat model for builders of open-weight agents and edge deployers → P1 digest_focus. Not confirmed P0: "
                   "not a consequential model release or product API; cyber stage of eval is intentionally simplified."),
  needs_verification=False),

 dict(source="sakana", card_source="Sakana AI blog",
  title="Recursive Self-Improvement through Collective Intelligence (MASS)",
  url="https://sakana.ai/mass/", date="2026-10-12",
  category="research_methods", type="research_method", priority="P1",
  tags=["agents","multi-agent","training","open-weights","safety"], digest_focus=True,
  alt_urls=["https://pub.sakana.ai/mass/", "https://arxiv.org/abs/2610.12176", "https://github.com/SakanaAI/mass"],
  artifacts=["arxiv:2610.12176", "SakanaAI/mass"],
  discovered_via="sakana.ai/blog listing time datetime=2026-10-12T00:00:00+09:00",
  summary=("Sakana MASS (Multi-Agent Self-Supervision): one shared model solves via virtual subagents, searches "
           "workflows, distills best team executions back into the model. Two RSI cycles on a 27B open-weights model; "
           "score/token 1.2–1.6× base across four research benchmarks. Safety note on homogeneous RSI blind spots."),
  key_takeaway=[
   "Method: Multi-Agent Self-Supervision — team of virtual subagents + workflow search + distill best trajectories into shared weights",
   "Measured: after 2 cycles on 27B open-weights, score per output token 1.2–1.6× base across four synthetic open-ended research benchmarks (provider-reported)",
   "Findings claimed: role generalization (optimizee training improves optimizer/evaluator); multi-agent trajectories more efficient than single-agent for RSI; optimizer capacity can bottleneck improvement speed",
   "Safety: authors flag homogeneous RSI shared blind spots when the model is also its own evaluator",
   "Artifacts: detailed blog pub.sakana.ai/mass/, arXiv 2610.12176, code github.com/SakanaAI/mass"],
  priority_reason=("Solid multi-agent RSI research method with measured gains and explicit safety framing → P1 digest_focus. "
                   "Not confirmed P0: not a consequential public model release; benchmarks are paper-reported on synthetic research tasks."),
  needs_verification=False),

 dict(source="nvidia-developer", card_source="NVIDIA Developer Blog",
  title="ReplaySSM: Rethinking State Storage for Faster Hybrid-Model Decoding",
  url="https://developer.nvidia.com/blog/replayssm-rethinking-state-storage-for-faster-hybrid-model-decoding/",
  date="2026-10-12",
  category="engineering_methods", type="engineering_method", priority="P1",
  tags=["inference","hybrid-models","ssm","vllm","tensorrt-llm"], digest_focus=True,
  artifacts=["ReplaySSM paper", "Johnny-Liou/ReplaySSM"],
  discovered_via="nvidia-developer RSS pubDate 2026-10-12 + article datePublished 2026-10-12T16:00:54+00:00",
  summary=("NVIDIA + Dao AI Lab: ReplaySSM caches SSM inputs (checkpoint + buffer) instead of full state each step. "
           "Cuts state traffic ~half; SSM kernels 1.46–1.80× at bs=256 on B300; speculative throughput 1.85–2.10× on 120B-class. "
           "In TensorRT-LLM/vLLM/FlashInfer/SGLang; production in GLM-5.3-Flash and Kimi-K3."),
  key_takeaway=[
   "Core idea: represent SSM state as checkpoint + recent-input buffer; flush writes checkpoint once per window (L=16 best in paper)",
   "Speed (provider-reported, bs=256, B300): SSM decode kernels 1.46–1.80× vs tuned vLLM; end-to-end step 1.20–1.47×; speculative 1.85–2.10× throughput at bs=512, T=4 on 120B-class",
   "Quantization: separate high-precision recurrence checkpoint vs low-precision read copy limits error accumulation; 3/4 models within ~2 pp of FP32 on GPQA-Diamond",
   "Availability: integrated TensorRT-LLM, vLLM, SGLang, FlashInfer; production GLM-5.3-Flash and Kimi-K3; code github.com/Johnny-Liou/ReplaySSM",
   "Relevance: Nemotron 3 / Qwen3.5–3.8 / Kimi-K3 / GLM-5.3-Flash hybrid stacks where SSM layers dominate decode latency at serving batch sizes"],
  priority_reason=("Measured inference engineering for hybrid SSM+attention stacks already in production serving paths → P1 digest_focus. "
                   "Not confirmed P0: optimization paper/blog, not a new model release or agent harness changelog."),
  needs_verification=False),

 dict(source="opencode-changelog", card_source="OpenCode changelog",
  title="OpenCode 2.0.27",
  url="https://opencode.ai/changelog#v2-0-27", date="2026-10-12",
  category="changelog_features", type="changelog_feature", priority="P1",
  tags=["cli","feature","agents","worktree"], digest_focus=True,
  artifacts=["opencode@2.0.27"],
  discovered_via="opencode.ai/changelog article id=v2-0-27 time datetime=2026-10-12 (page now lists OpenCode 2.x only; 1.x notes moved to GitHub Releases)",
  summary=("OpenCode 2.0.27 (Oct 12): built-in Code Mode worktree_create/list/remove; safer opencode pair --remote "
           "confirmation (+ --yes); installable web app; session failure visibility; auto project cleanup; "
           "ChatGPT OAuth input limit 500K for gpt-6.1-sol(+-fast); Vertex routes for Interactions/Mistral."),
  key_takeaway=[
   "Core: built-in Code Mode tools worktree_create, worktree_list, worktree_remove (isolated worktrees; remove needs edit approval; force:true can discard dirty files)",
   "Core: first opencode pair --remote warns before exposing server; non-interactive --yes/-y",
   "UX: installable OpenCode web app (Chrome/Edge), including behind authenticating proxy; Desktop/TUI show pre-/inter-step execution errors",
   "Projects: auto-hide projects whose directories disappeared; reopen restores",
   "Models/routing: ChatGPT OAuth input limit raised to 500K for gpt-6.1-sol and gpt-6.1-sol-fast; Vertex AI routes for Interactions and Mistral",
   "Distribution caveat: npm opencode-ai latest still 1.19.0 (2026-10-11); GitHub anomalyco/opencode Releases page still tops at v1.19.0 — OpenCode 2 line is published on opencode.ai/changelog; install path beyond prior `opencode upgrade --major` not independently verified today"],
  priority_reason=("Agent-enhancing changelog: first-class worktree tools + safer remote pairing change isolation and multi-session harness workflows → P1 digest_focus. "
                   "needs_verification: npm/GitHub Releases still on 1.19.0 while docs changelog shows 2.0.27."),
  needs_verification=True,
  verification_note="2026-10-13: opencode.ai/changelog shows v2.0.27 (2026-10-12) and v2.0.26 (2026-10-08); registry.npmjs.org/opencode-ai dist-tag latest still 1.19.0; GitHub releases HTML lists through v1.19.0 only.",
  alt_urls=["https://opencode.ai/changelog"]),
]

CARD_IDS = {
  "https://www.anthropic.com/research/self-replicating-ai": "anthropic-self-replicating-ai-2026-10-12",
  "https://sakana.ai/mass/": "sakana-mass-rsi-2026-10-12",
  "https://developer.nvidia.com/blog/replayssm-rethinking-state-storage-for-faster-hybrid-model-decoding/": "nvidia-replayssm-2026-10-12",
  "https://opencode.ai/changelog#v2-0-27": "opencode-2-0-27-2026-10-12",
}

MIRRORS = []

SOURCE_ONLY = []

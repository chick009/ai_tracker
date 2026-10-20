# Idea-grouping taxonomy for the daily AI Tracker digest

Standing editorial structure for weekday digests (**Top 10 → Tricks & Ideas → Radar**). Fitted on the W42 packs (2026-10-12..16) and the W43 start (2026-10-19..20). The point is a labeling scheme that stays put on a quiet Thursday and on a day packed with model cards.

This taxonomy sorts **ideas**. It does not replace:

- Rank order, or the three digest sections.
- Editorial action lanes already on the cards: Build / Learn / Watch / Act.
- Notion scope routing (Papers, GitHub Trending, Model & IDE, Applicational).

One item gets one theme code. Rank stays global. A theme recap may regroup names that were already posted; it does not re-rank them.

Short codes used below: `harness` `execution` `eval` `decision` `ops` `models` `training` `inference` `changelog` `science`.

## A. Stable lanes

Print a stable lane only when the day has at least one item in it. Four lanes is the standing set. They are the clusters an AI engineer can expect every week: the scaffold around the model, the world it acts in, the yardstick, and the cheap decider.

| Code | Lane | Definition |
|---|---|---|
| `harness` | **Harness & context control** | Software around a model, usually with weights left fixed: skills, hooks, prompts, permission and admission gates, sandboxes, routers that live in the harness, and search-state the agent manages itself. Memory and context belong here when they are a write path, a revision, a compression step, or an injection into the next turn. Frozen-weight harness self-evolution belongs here too. |
| `execution` | **Execution environments** | The world and the action surface: synthesized desktop, terminal, GUI, or mobile environments, and open computer-use stacks or SDKs. Use this when an engineer could run an agent in the thing being announced. |
| `eval` | **Eval, delivery & oversight** | The yardstick or the audit: harness benches, multi-agent conflict and closing, last-mile delivery, hidden constraints, extraction quality, capability score versus a correctness gate, and oversight surfaces that can mislead a reviewer. A confirmed safety incident that changes how you audit agents sits here. |
| `decision` | **Decision runtimes** | A typed or split runtime whose job is to choose: calibrated decision models, System 1 / System 2 production splits, routine tool-selection models, looped fast/deep deciders. The artifact is the decider, including a small decision model socketed into a harness. |

## Tricks sit outside the clusters

| Code | Lane | Definition |
|---|---|---|
| `ops` | **Ops tips** | Practitioner micro-patterns from Tricks & Ideas: a schema habit, a retry check, a one-line failure mode. They do not enter theme clusters. If a trick restates a Top 10 mechanism, drop the trick (as on 2026-10-20, when the ProPerAgent memory gate was removed from Tricks). |

## B. Optional add-on lanes

Open an add-on heading when **two or more** items share it, or when **one** item would distort a stable lane if forced in (a frontier model card filed under harness, a robotics paper filed under harness, an RSI claim filed as a memory product). A single quieter item still receives the code, and stays a tagged Radar bullet with no new heading.

| Code | Lane | Open it when |
|---|---|---|
| `models` | **Model & agent releases** | The news is weights, a price card, a modality, or a named agent product. Decision-model APIs stay `decision` even when they ship as a product (Decision-1, d1-ultra). A Rust harness or a cache line mentioned inside a model card does not create a second `harness` row. |
| `training` | **Training, data & OPD** | The news is an objective, a distillation gate, a reward, midtraining data, or a weight edit. Loud on 10-13, 10-14, 10-15, and 10-19. Context that is distilled into FFN updates (Cortex) is training: the weights moved. GPU-memory tricks for RL (LoGRA) are training; “memory” there means VRAM. |
| `inference` | **Inference & cost** | Speculative decode, cache-hit pricing, or a serving-hardware claim. A cache hook inside an agent framework (Pydantic `Caching()`, a router the pack places in the harness) stays `harness`. |
| `changelog` | **Tooling changelog** | Version bumps of coding-agent CLIs and product surfaces whose pack entry does not name a new control idea. Several shipped the same morning on 10-16 and 10-19. A named lifecycle hook (`agent.spawn`, `prompt.change`, Environments API) is `harness`, not a second changelog row. |
| `science` | **RSI, science & embodied** | Radar-oriented, even if a strong item makes Top 10. Robotics, wet-lab, spatial content worlds, pure scientific-problem benches, and RSI whose claim is open-ended self-improvement. A paper that says “harness” and whose user is a robot (HexaShell) stays here. Johnny’s 10-20 pass already moved HexaShell and Into the Unknown to Radar for this reason. |

## C. Mapping

Section labels for 10-12..14 follow that day’s `week.json` synthesis order (the same order matches posted rank on 10-15, 10-16, and 10-19, which have HTML or a group post). 10-15..20 follow the posted digest. Nothing below is added from outside the packs.

2026-10-20 `week.json` is an earlier Papers patch (v2). The table follows the posted Johnny rank v3 group post. The v2 file still places CarryOn and LEV on the Radar side, and its application summary still lists Opus BG3, harness engineering, Busy Beaver, and DSpark among Top 10 items. v3 reverses that emphasis (LEV and Pack Light / CarryOn on the Top 10; those four on Radar) and drops other names that appear only in the v2 type summaries. Those extra names are not given rows.

### 2026-10-16 (posted Top 10)

| Item | Section | Code | Why this lane |
|---|---|---|---|
| Doc2Harness | Top 10 | `eval` | Harness-engineering bench: fixed builder, 328 cases, Astra 53.05%. The deliverable is the measurement. |
| CLASHarness | Top 10 | `eval` | Controllable multi-agent conflict bench; pass 28.7%, closing failures 58–72%. |
| TreeFlex (Meta) | Top 10 | `harness` | The agent manages search-tree nodes (continue / branch / verify / stop) instead of flattening failed trajectories into context. |
| Agent permissions (Arize) | Top 10 | `harness` | Allow / deny moves out of the dialogue into a harness check of identity, ownership, and delegation. |
| Cortex (ByteDance Seed) | Top 10 | `training` | Context gains are distilled into mergeable low-rank / structural FFN updates. Weights move, so this is not a harness write path. |
| Muse Spark Open | Top 10 | `models` | Open sparse MoE, ~816B / 42B active, multimodal plus tools. |
| System1/System2 (Sector7) | Top 10 | `decision` | Production split: a fast router / guardrail versus a generative model for open reasoning and tools. |
| context-mode | Top 10 | `harness` | Sandboxed tool output, session memory, MCP / hooks across agent surfaces. Same code as its 10-13 Radar mention. |
| Nemotron 3.5 Super VL | Top 10 | `models` | Multimodal agent model release (CharXiv 80.8%). Cross-turn cache stays inside the card. |
| Sakana My Fish | Top 10 | `harness` | Dialogue memory as an inspectable surface (list, history, graph). The pack’s point is observability of what the harness stores. |
| SPACE OSS | Radar | `harness` | Micro-VM sandbox with credentials held outside the guest. Same code as the 10-15 SPACE routing note. |
| ExtractBenchPro | Radar | `eval` | Long-document extraction bench with fixed answers and evidence requirements. |
| ActionOPD | Radar | `training` | Action-level on-policy distillation against a black-box teacher (+3.3–6.9pp). |
| d1-ultra | Radar | `decision` | Input mapped straight to class / route / score plus a probability. The week file buckets it as a model release; the posted takeaway is the decision API (same family as Decision-1). |
| OpenCode 2.0.30, Claude Code 2.1.301, Pi 1.3.0, Codex 0.163.0 | Radar | `changelog` | Shipped version cluster. The post does not isolate a new control idea beyond “this build exists” (adjacent hook notes stay historical). |
| ECC | Radar | `harness` | Coding-agent harness layer: skills, hooks, rules. Not a new model. |

Posted continuation, not re-ranked that morning: HybridAgents, Harness², Gemini 4 Argon. Their codes stay the ones from 10-14 / 10-15.

### 2026-10-19 (posted Top 10)

| Item | Section | Code | Why this lane |
|---|---|---|---|
| Hy-Memory | Top 10 | `harness` | A 3B-active writer that decides what to store, how to write it, and how new evidence updates old memory, plugged across harnesses. Distillation + RL is the training method; the tracked object is the writer. |
| OpenGCUA | Top 10 | `execution` | Open generalist computer-use stack: visual and programmatic interfaces, code execution, SDK. Harness-to-model decision transfer is a sub-claim of the stack. |
| Waypoint-OPD | Top 10 | `training` | Gated on-policy distillation from mid-run waypoints, not only the final teacher. |
| Cursor Canvases + Environments API | Top 10 | `harness` | Environments can be created and managed in code (300 repos, 5× load). The canvas share link rides along; it does not get a second row. |
| Self-Evolving Agent Harness | Top 10 | `harness` | Formal self-evolution of prompts, memory, workflows, tools, and plugins with weights fixed, plus an admission / PAC rule. |
| Memorilla | Top 10 | `harness` | 16 latent memory tokens beat full context (source tokens −108×), including as agent memory. |
| FDE-Gym | Top 10 | `eval` | Last-mile delivery bench: fuzzy demand, live systems, unstated constraints. 14/95 resolved. |
| Beam (Reflection MoE) | Top 10 | `models` | Open MoE, 501B / 23B active, 1M context, Apache 2.0, price card. The bundled Rust harness stays inside the release. |
| NVIDIA open midtraining (agentic coding) | Top 10 | `training` | 256K software-engineering midtrain between pretrain and post-train; SWE-bench Multilingual 55.8→62.8. |
| JevAgentHarness | Top 10 | `decision` | A 4B decision model takes routine tool choice inside the harness and holds outcome while cutting cost. The socket is a harness; the idea is the decider. |
| MAI-Gym | Radar | `eval` | Unified GUI eval / data / online-RL gym. The 9B score is the evidence. |
| MJev-Spatial | Radar | `decision` | System One spatial decisions via attention matching, without autoregressive text decode. |
| Data World / DABstep | Radar | `training` | Generated data-analysis environments, then RL (DABstep-Hard +20.9). |
| LangChain Managed Deep Agents (sandbox proxy) | Radar | `harness` | Tokens injected from a proxy outside the sandbox so the agent never sees the credential. Same code as the 10-12 blueprint. |
| MAI-Code-1.1-Flash | Radar | `models` | Coding model refresh at about a quarter of the cost. |
| OpenCode 2.0.32 / Claude Code 2.1.302 | Radar | `changelog` | CLI bumps. No new hook is isolated in the post. |
| AMD MI355X + vLLM | Radar | `inference` | Serving-hardware claim for agentic inference. Workload still unverified in the pack. |
| akitaonrails/ai-memory | Radar | `harness` | Long-term memory and session handoff for coding CLIs. |
| 3DCodeVerse | Radar | `science` | Coding agents that build and check executable 3D worlds. Adjacent to the daily engineer lanes. |
| Google wet-lab agent building blocks | Radar | `science` | Autonomous wet-lab components. The pack already marks it vertical research. |

### 2026-10-20 (posted Johnny rank v3)

| Item | Section | Code | Why this lane |
|---|---|---|---|
| MiniMax M3.1 Flash | Top 10 | `models` | Open flash model for agent, coding, and computer use, with a price card. |
| ProPerAgent | Top 10 | `harness` | Frozen weights; proactive assist rises via a memory-interrupt gate (≤15%→38%). |
| Harness² | Top 10 | `harness` | Agents propose capped harness edits (skills, hooks, system instructions) around a frozen model. Same code as 10-15. |
| Pack Light, CarryOn | Top 10 | `harness` | Object-oriented context carriers for long-horizon agents. |
| BizBench | Top 10 | `eval` | Hidden challenges of deploying long-horizon agents in real business. |
| Devin Fusion | Top 10 | `models` | Shipping coding-agent product: index score and cost per task. Treated as a product release, not a CLI bump. |
| DiscoveryRSI | Top 10 | `science` | 27B RSI science agent (X post and paper are one slot). |
| LEV | Top 10 | `decision` | Looped decision models that think fast or deep without long token chains. |
| headroom | Top 10 | `harness` | Compress tool output, logs, and RAG before the call. |
| LiveMACE | Top 10 | `eval` | Process-aware evaluation of agents in evolving markets. |
| Exact enum tokens in the schema | Tricks | `ops` | Cheap models copy the label from the prompt. Micro-pattern, no theme heading. |
| Check settlement before x402 retry | Tricks | `ops` | Payment retry habit from a multi-API attempt. |
| HexaShell | Radar | `science` | Thin VLM harness for robot coding. Demoted from Top 10 on the applicational pass. The word “harness” does not pull it into `harness`. |
| Into the Unknown | Radar | `science` | Open bench of scientific research problems. Same demotion. |
| Opus BG3 | Radar | `eval` | Uncontrolled long-run cost anecdote (~39h / $712). Evidence about a long episode, not a bench and not a method. |
| Harness engineering (Perplexity) | Radar | `harness` | Same model, harness swing of about 11%. |
| Busy Beaver | Radar | `science` | Gemini Lean rules aimed at BB(6) cryptids. |
| DSpark | Radar | `inference` | Lossless speculative decode, up to 4.66×, single GPU. |
| OpenMobile-2 | Radar | `execution` | Mobile agents plus resettable app playgrounds. Applicational computer-use, so it stays out of `science`. |
| PhysClosureBench | Radar | `science` | Physics agents and evidence-backed closure. |
| TreeOPSD | Radar | `training` | Tree-aware posterior distillation for agentic RL. One radar item: tag it, do not open a training heading. |
| DLite | Radar | `inference` | History-free speculative decode from hidden states. With DSpark, an inference subhead is warranted inside Radar. |
| OfficeTown | Radar | `harness` | Generated org charts as the scaffold for multi-agent teams. |

### 2026-10-12 (from `week.json`; no group post in the pack)

| Item | Section | Code | Why this lane |
|---|---|---|---|
| Sakana MASS | Top 10 | `science` | Same model, multiple roles, framed as RSI (~1.2–1.6× tokens). |
| Microsoft Decision-1 GA | Top 10 | `decision` | Foundry calibrated decision API, $0.042/MTok input. A shipped decider, not a general model card. |
| HarnessSQL | Top 10 | `harness` | Text-to-SQL trained inside the harness (Qwen3-14B 22.2%→54.8%). The tracked lesson is the locus of training. |
| GitSwarm | Top 10 | `harness` | Shared Git as compounding inference state. |
| Mara Chain | Top 10 | `harness` | Failed candidates kept as stepping stones (TB2.1 57.3%→71.9%). Same family as TreeFlex: search state, not a weight update the pack describes. |
| Skill Constellations | Top 10 | `harness` | Audit of the SKILL.md copy network. Skills are harness supply chain. |
| Managed Deep Agents blueprint | Top 10 | `harness` | Agent blueprint. Same code as the 10-19 credential-proxy note. |
| Pydantic AI `Caching()` | Top 10 | `harness` | Cache primitive on the agent framework. |
| On-Policy Distillation | Top 10 | `training` | The claim in the pack: transfer skill, not facts. |
| OpenCode 1.19.0 | Top 10 | `changelog` | On-ramp to OpenCode 2 plus ultrafast. No new hook is named. |
| Anthropic unintended model actions | Radar | `eval` | Four bypass classes; pause evals that touch the live net. An audit finding. |
| CARE | Radar | `science` | Accelerated certification for VLA. Embodied, Radar-oriented. |

### 2026-10-13 (from `week.json`; papers in `day-pack.md` match the research slice)

| Item | Section | Code | Why this lane |
|---|---|---|---|
| Anthropic self-replicating AI | Top 10 | `eval` | Weight-based IoT replication and a simplified eval. Marked Act in the week file. An oversight finding, not a method to adopt. |
| SoftwareGym | Top 10 | `execution` | Synthesized desktop apps for computer-use training (OSWorld Pass@3 41.39→56.97). The noun in the pack is the environment. |
| LoGRA | Top 10 | `training` | Low-rank gradient sketches so full-weight RL fits (7B memory −45.7%, single-node 27B). “Memory” here is VRAM. |
| SLA (Stateless Language Agents) | Top 10 | `harness` | Durable research state sits in the harness; each turn rebuilds role context (kernel tokens −93.1%). |
| Decision 3.0 (multimodal Jev) | Top 10 | `decision` | Decision-model refresh (Index 65.45). |
| ReplaySSM | Top 10 | `inference` | Speculative decoding at 1.85–2.10×. |
| Semi-OPD | Top 10 | `training` | Offline student rollouts often beat continued on-policy distillation (14/17 pairs). |
| RSI-Anything | Top 10 | `science` | Named as RSI in the week file, with no further mechanism. Kept on the RSI add-on rather than guessed into harness. |
| ProgramGym | Top 10 | `execution` | Verifiable from-scratch programming environments (1,648 envs). The pack leads with the environment. |
| FrontierCode 1.1 | Top 10 | `eval` | Coding eval that asks whether the result is mergeable, not only whether tests are green. |
| DiffusionART | Radar | `training` | Diffusion RL (trust-region mask, no EMA). |
| context-mode | Radar | `harness` | Same project as the 10-16 Top 10 row. |
| Perplexity Projects | Radar | `changelog` | Product name only in the pack. No mechanism to file under a stable lane. |
| OpenCode 2.0.27 | Radar | `changelog` | Version watch, marked needs verification. |

### 2026-10-14 (from `week.json`; `day-pack.md` confirms the paper slice)

| Item | Section | Code | Why this lane |
|---|---|---|---|
| LFM2.5-24B-A2B | Top 10 | `models` | Small MoE release with LiveClaw / AutomationBench numbers and an OpenRouter price. |
| LongHarness | Top 10 | `harness` | Long-context harness result (OfficeQA 4.4%→61.1%). |
| transformers `/v1/systemone` | Top 10 | `decision` | Logits-level decision endpoint. |
| TerminalHorizon | Top 10 | `training` | Challenge-guided synthetic terminal trajectories, then SFT. The pack’s paper title is scaled agentic data. |
| BranchOPD | Top 10 | `training` | On-policy distillation from branches at high-information decision points (+18.55 vs vanilla OPD; much of the gap is PBR). |
| Anthropic Scion | Top 10 | `eval` | Operational scale evidence: merges ~2.5k in May to 30k+ in September. Marked Act. The pack gives volume, not a new component. |
| AgentSWE | Top 10 | `eval` | Can a coding agent build or tune the agent you asked for. Creation mean 11.2; most held-out runs fail validity. |
| ExpActivator | Top 10 | `harness` | Per-step activation of applicable experience (relevance ≠ applicability). What gets injected is the harness question, on a GUI domain. |
| Gemini 4 Argon | Top 10 | `models` | Frontier model card (CursorBench 52.8%, intro price through 11-30). |
| Model router in harness | Top 10 | `harness` | The pack locates the router in the harness (cost −64%). |
| Thinking Inertia | Radar | `eval` | Measures whether “no think” still leaves visible reasoning (ETR / QRel / EIR). |
| OpenCode 2.0.28 | Radar | `changelog` | Confirmed `@opencode/cli` latest at the time of the note. |
| Origin App Marketplace | Radar | `changelog` | Product-surface name only. |
| AA Cost per Task / cache hit | Radar | `inference` | A cost metric, not a component. |

### 2026-10-15 (posted HTML Top 10)

| Item | Section | Code | Why this lane |
|---|---|---|---|
| Grok Voice 3.0 | Top 10 | `models` | Speech-to-speech agent release, price unchanged at $0.08/min. |
| Jeva | Top 10 | `decision` | Decision-native System One (option encoding, coverage / null gate). Cacheable option memory stays inside the decider; it does not open a memory lane. |
| Harness² | Top 10 | `harness` | Recursive edits to the execution harness and to the improvement harness. Weights are not the object. Same code on 10-20. |
| Memento 3 RSI | Top 10 | `science` | Frozen model rewrites an external rulebook and compiles it to programs (ARC-AGI-3). The substrate is harness state; the claim that earned the slot is RSI. |
| Hybrid Reasoning Agents | Top 10 | `decision` | Switch between latent thought and text action, with continuous working memory across turns. The memory is the controller’s state. |
| AutoEnvScaling | Top 10 | `training` | A proposer agent builds the next RL environment from solver rollouts (TB 2.1 +12.2). |
| Agent-Reflex | Top 10 | `training` | Skill discovery, reflective SFT, then ORPO. Reflections are training signal; weights change. |
| ReHarness | Top 10 | `harness` | Retrieve reflections, then revise them against the trajectory before writing the next lesson. Weights fixed. |
| Correctness gate vs capability | Top 10 | `eval` | A passing gate is not a capability result. LinkedIn text was still unverified in the pack; the lane follows the claim as posted. |
| Claude Code 2.1.300 | Top 10 | `harness` | Named lifecycle controls: `agent.spawn`, `prompt.change`, OTel cache attributes. Later 2.1.30x bumps that only confirm shipment go to `changelog`. |
| Tev | Radar | `training` | Dense progress rewards plus a large synthetic long-horizon gym. |
| OpenCode 2.0.29 | Radar | `changelog` | Version confirmation (remote pairing, provider accounts, continuation). |
| METR Inspect injection | Radar | `eval` | Oversight UI (MathJax in the transcript viewer) as the attack surface. Patched. |
| SPACE sandbox | Radar | `harness` | Capability tokens bound to sandbox, execution generation, and placement. |

## D. Critique of a Memory lane split from Harness

A naïve taxonomy treats “Memory” as a sibling of “Harness” because the titles cooperate: Hy-Memory, Memorilla, ai-memory, Sakana’s visible dialogue memory, ReHarness, context-mode’s session memory, ProPerAgent’s memory interrupt, Pack Light / CarryOn, ExpActivator’s experience store, Jeva’s option memory, HybridAgents’ working memory, SLA’s research state. Across 10-16, 10-19, and 10-20 that sibling would have been one of the largest buckets in the digest.

Those items are one control surface described with different nouns. The harness decides what is written, what is revised, what is dropped, and what is injected on the next turn. Sakana My Fish is observability of that store. context-mode and headroom decide which tool output is allowed into the window. Hy-Memory and Memorilla are writers or latent tokens that plug into an existing harness. ProPerAgent is a gate on when memory may interrupt. ReHarness revises a lesson against the trajectory before the next inject. SLA puts durable state in the harness and rebuilds the agent statelessly. Self-Evolving Agent Harness names memory in the same list as prompts, workflows, and plugins: the paper’s object of study is the scaffold. Splitting Memory off Harness saws that object in half and makes the label flip with vocabulary (memory, context, state, experience, reflection) from one day to the next.

The split also hides the cases that only look like memory.

- **Cortex** “remembers” by editing FFN weights. Filing it under Memory would bury a distillation result. It is `training`.
- **LoGRA** cuts “memory” by 45.7%. That is training VRAM, also `training`.
- **HexaShell** is a thin harness whose user is a robot. The applicational pass already sent it to Radar. A Memory-versus-Harness argument never reaches the real question, which is whether the reader is an AI engineer or a robotics audience. It is `science`.
- **Memento 3** stores an executable rulebook outside the weights. The useful residue for an engineer is harness state. The claim that justified Top 10 is RSI, so the primary code is `science`, with no second Memory tag.

Week narratives in the packs already talk this way: W42’s mainline is harness, typed decisions, and the agent supply chain; W43’s “agent memory” sentences are about writers, admission, and injection. A standing Memory heading would fight that mainline every morning it appears.

## E. How the Orchestrator should label a daily digest

Do this after rank, dedupe, and the Top 10 / Tricks / Radar cut. Labels do not change membership or order.

1. Keep the posted order: **Top 10**, then **Tricks & Ideas**, then **Radar**. After that flat post, an optional **Themes** recap may group the same names under the codes below. The recap does not re-rank.
2. Give each item exactly one code from section A or B, or `ops` if it is a trick. No dual tags. A parenthetical is allowed only when a boundary is the point of the sentence (Cortex, HexaShell, Memento 3).
3. **Write-path test.** If weights stay fixed and the news is what gets stored, revised, compressed, gated, or injected, the code is `harness`. Do not open a Memory heading. Collector titles that say memory, context, state, experience, or reflection still take this test.
4. **Weights test.** If the context or the lesson is written into parameters, the code is `training`. If “memory” means device memory during RL, the code is `training`.
5. **Bench versus method.** A benchmark whose subject is a harness, a delivery job, or an oversight UI is `eval`. A method that changes the scaffold is `harness`. Doc2Harness and CLASHarness are benches. Harness², ReHarness, and Agent permissions are methods.
6. **Decider test.** If the artifact is a small or typed model, or a fast/slow split, that chooses an action, the code is `decision`, even when it is socketed into a harness (JevAgentHarness, Jeva). Cache or option memory inside that decider does not move the row.
7. **Environment test.** If the noun an engineer would run is an environment, playground, or computer-use stack, the code is `execution` (SoftwareGym, ProgramGym, OpenGCUA, OpenMobile-2). If the noun is the reward, the distillation gate, or the data recipe, the code is `training` (TerminalHorizon, AutoEnvScaling, Tev, Waypoint-OPD, NVIDIA midtraining).
8. **Audience test.** Robotics, wet-lab, and scientific-problem benches are `science`, including when the title says harness or agent. Open a `science` heading if one of them is in the Top 10 or if Radar has two or more.
9. **Release versus bump.** Weights, price, modality, or a named new agent product: `models`. A CLI version whose note does not isolate a new control: `changelog`. A named hook or environments API: `harness` only, with no second changelog row.
10. **Inference versus harness.** Speculative decode and serving-cost claims: `inference`. A cache or router the pack places inside the agent framework or the harness: `harness`.
11. Open an add-on **heading** only when two or more items share the code, or when one Top 10 item would distort a stable lane. Otherwise keep the code on the bullet and skip the heading. Omit empty stable lanes.
12. Tricks stay in Tricks under `ops`. Drop a trick that repeats a Top 10 mechanism.
13. Reuse the code when the same project returns (Harness², context-mode, SPACE, Managed Deep Agents, OpenCode bumps). A later patch that only confirms shipment stays `changelog` even if an earlier build earned `harness`.
14. Leave Build / Learn / Watch / Act and the Notion scope tables alone. Theme codes are a third axis.

### Worked label pass for 2026-10-20

Flat rank stays as posted. A themes recap that morning would have been:

- **Harness & context control** — ProPerAgent, Harness², Pack Light / CarryOn, headroom; Radar: harness engineering, OfficeTown.
- **Decision runtimes** — LEV.
- **Eval, delivery & oversight** — BizBench, LiveMACE; Radar: Opus BG3.
- **Execution environments** — Radar only: OpenMobile-2. One item, so a Radar tag is enough and a Top 10 heading stays omitted.
- **Model & agent releases** — MiniMax M3.1 Flash, Devin Fusion. Two Top 10 items, so the add-on heading opens.
- **RSI, science & embodied** — DiscoveryRSI in the Top 10, so the heading opens; Radar: HexaShell, Into the Unknown, Busy Beaver, PhysClosureBench.
- **Inference & cost** — Radar: DSpark, DLite. Heading only inside Radar.
- **Training, data & OPD** — Radar tag on TreeOPSD only. No heading.
- **Ops tips** — exact enum tokens; check settlement before an x402 retry.

That pass puts every memory-worded Top 10 item (ProPerAgent, CarryOn, headroom) under harness, and leaves the robotics and scientific-problem papers on the science lane Johnny already treated as Radar.

# Builds cards.json + week.json for 2026-10-07 (W41). Week merges 10-05 + 10-06 + 10-07.
import json

cards = [
 dict(
  id="shift-dynamic-harness-search-2026-10-06",
  title="Dynamic Harness Search: Building Multi-Agent Systems Per-Query via Prediction (SHIFT)",
  url="https://arxiv.org/abs/2610.04137",
  source="Hugging Face / Papers",
  published_at="2026-10-06T00:00:00Z",
  type="research",
  priority="P0",
  tags=["Learn", "Top 10", "Papers"],
  key_takeaway=["唔再每 query 試跑多 harness，用細 architect（policy＋value）＋MCTS 砌角色／指令／工具，只執行選中 harness。9,193 題平均準確度 79.9 vs Trace 72.7（+7.2pp）；平價模式 tokens 少約 32% 仍贏。限制：SpreadsheetBench 87.8 < DSPy-GEPA 95.3；短題上限多喺 executor。"],
 ),
 dict(
  id="searchjev-system1-search-decisions-2026-10-06",
  title="SearchJev: A Fast and Calibrated System-1 Model for Search Agents",
  url="https://arxiv.org/abs/2610.05107",
  source="Hugging Face / Papers",
  published_at="2026-10-06T00:00:00Z",
  type="research",
  priority="P0",
  tags=["Learn", "Top 10", "Papers"],
  key_takeaway=["短搜尋決策改成 schema 有限選項分類（第一 token logits），soft-label＋Brier 校準，唔夠信心交 System-2。同尺寸 Qwen3.5 AR 決策快約 5.2–5.3×、ECE 降約 41–74%；BrowseComp-Plus 45%→最高 54%，主動時間快 3.7–4.7×。限制：端到端只 100 題；gate δ 未公開。"],
 ),
 dict(
  id="openai-decisions-api-beta-2026-10-07",
  title="OpenAI Decisions API (beta)",
  url="https://developers.openai.com/api/docs/guides/decisions",
  source="OpenAI / Blog",
  published_at="2026-10-07T00:00:00Z",
  type="changelog_feature",
  priority="P0",
  tags=["Build", "Top 10", "Model & IDE", "Blog"],
  key_takeaway=["將「叫 LLM 寫答案再 parse」改成 typed decisions（predicate／choice／score），GPT-6 Luna；public beta 輸入 $0.10/MTok、唔收輸出；官方稱最高快 10×。限制：10× 係指定比較最高值，唔係所有 workload 保證。"],
 ),
 dict(
  id="automationbench-verified-2026-10-07",
  title="AutomationBench Verified",
  url="https://x.com/omarsar0/status/2107534535604711492",
  source="X",
  published_at="2026-10-07T00:00:00Z",
  type="application_case_study",
  priority="P0",
  tags=["Learn", "Top 10", "Applicational", "X"],
  key_takeaway=["修 verifier／判卷器而非抬模型；修 206 個 verifier bugs，重評 1,235 次 Kimi K3 runs，27.9% grades 改變（係判分有變比例，唔係成功率+27.9pp）。限制：原帖未能直讀，數字只核實到二手摘要。"],
 ),
 dict(
  id="ascent-online-ttt-agents-2026-10-06",
  title="ASCENT: Online Test-Time Training of Long-Horizon Agents via Self-Distillation of Verified Experience",
  url="https://arxiv.org/abs/2610.05303",
  source="Hugging Face / Papers",
  published_at="2026-10-06T00:00:00Z",
  type="research",
  priority="P0",
  tags=["Learn", "Top 10", "Papers"],
  key_takeaway=["部署期間用已驗證軌跡更新持久 LoRA；唔模仿自己 tokens，而蒸餾凍結初始模型喺 hindsight 下嘅 next-token 分佈，並剔無效動作。多設定 exact success 可>+22pp，成功題步數下降。限制：要 binary verifier＋open-weight teacher logits；filter 唔係一律增益。"],
 ),
 dict(
  id="osworld-pro-process-eval-2026-09-29",
  title="OSWorld-Pro: Process-based Evaluation for Computer Use Agents",
  url="https://arxiv.org/abs/2609.24890",
  source="Hugging Face / Papers",
  published_at="2026-09-29T00:00:00Z",
  type="research",
  priority="P0",
  tags=["Learn", "Top 10", "Papers"],
  key_takeaway=["過程評估：300+ 任務→2,800+ subgoal、67k+ 人手標註，LLM judge 評步而非只看交付物。頂級約 75–78% vs 引用 OSWorld ~83.4%；點擊係最大分水嶺（弱 ~39–42% vs 強 72–92%）。限制：任務指標係全可行 subgoal 二值；過程指標未驗證同最終成功相關。"],
 ),
 dict(
  id="embeddinggemma-2-2026-10-07",
  title="EmbeddingGemma 2",
  url="https://huggingface.co/google/embeddinggemma-2",
  source="Hugging Face / Blog",
  published_at="2026-10-07T00:00:00Z",
  type="model_release_implementation",
  priority="P0",
  tags=["Build", "Top 10", "Model & IDE"],
  key_takeaway=["可分開載入 text／vision／audio encoder，映到同一 768-d 空間（Apache 2.0）；有效參數按模態 270M–740M，8192 context，Matryoshka 可截到 512／256／128。限制：128-d 多模態質素明顯下降，官方較建議純文字。"],
 ),
 dict(
  id="claude-code-2-1-290-2026-10-05",
  title="Claude Code 2.1.290",
  url="https://code.claude.com/docs/en/changelog#2-1-290",
  source="Anthropic / Blog",
  published_at="2026-10-05T00:00:00Z",
  type="changelog_bugfix",
  priority="P0",
  tags=["Act", "Top 10", "Model & IDE", "Blog"],
  key_takeaway=["修 background /loop 生命週期同權限閘：更新／低記憶體時 session 續跑；foreground→background 後排程觸發；PreToolUse 改寫後漏套權限；respawn skip-permissions 繞過。限制：compact 後 resume 修補只涵蓋新 compaction。"],
 ),
 dict(
  id="ironclad-computer-use-rl-2026-10-07",
  title="Advancing computer use with Ironclad",
  url="https://openai.com/index/advancing-computer-use-with-ironclad",
  source="OpenAI / Blog",
  published_at="2026-10-07T00:00:00Z",
  type="application_case_study",
  priority="P0",
  tags=["Learn", "Top 10", "Applicational", "Blog"],
  key_takeaway=["Ironclad 將專業軟件變成有 rubric 回饋嘅 RL 環境（11 項合約／採購任務，每項 8–50 criteria）。GPT-6 Astra 平均 rubric 55.0% vs GPT-5.6 Sol 41.6%；估計時間 37.0→19.2 分鐘。限制：55% 係準則達成度唔係完整成功率；時間係模擬估算。"],
 ),
 dict(
  id="mit-token-cue-reasoning-2026-10-06",
  title="Base Models Can Reason By Taking a Cue From Training Data",
  url="https://arxiv.org/abs/2610.06851",
  source="Hugging Face / Papers",
  published_at="2026-10-06T00:00:00Z",
  type="research",
  priority="P0",
  tags=["Learn", "Top 10", "Papers"],
  key_takeaway=["RL 推理增益好多可用開頭固定 token cue 喺 base 重現；Olmo-3-7B MATH-500 42%→78%（RL~75%），Qwen3-14B 72%→87%；中間訓練可令任意字變 cue。限制：cue 模型專屬；合規 cue 可令有害回應率升至 42.4%。"],
 ),
 dict(
  id="mistral-large-4-preview-2026-10-06",
  title="Mistral Large 4 preview",
  url="https://mistral.ai/news/mistral-large-4/",
  source="Mistral / Blog",
  published_at="2026-10-06T00:00:00Z",
  type="model_release_implementation",
  priority="P2",
  tags=["Watch", "Radar", "Model & IDE", "Blog"],
  key_takeaway=["原生多模態 MoE（總參約 1T、啟用約 49B），10-06 開 preview API，輸入／輸出 $1.36／$4.18 per MTok；官方承諾 10 月底公開權重。限制：仍係持續訓練中嘅 preview，公開數字同最終發佈可能再變。"],
 ),
 dict(
  id="vericodegen-verified-confinement-2026-10-07",
  title="VeriCodeGen / Verified Confinement",
  url="https://lnkd.in/p/gBCT8X37",
  source="LinkedIn",
  published_at="2026-10-07T00:00:00Z",
  type="application_case_study",
  priority="P2",
  tags=["Learn", "Radar", "Applicational", "LinkedIn"],
  key_takeaway=["LLM 做候選產生器，deterministic verifier 決定放行；Verified Confinement 係 case study；VeriCodeGen 係 NeurIPS 2026 workshop（12 月 Atlanta）。限制：短鏈未能直讀，未核實量化結果；保證只涵蓋 verifier 檢查嘅規格。"],
 ),
]

week = dict(
 week_start="2026-10-05",
 synthesis=(
  "本週主線由 harness 擴到 typed decisions、線上適應同過程評估；10-07 再加 verifier 信任同 computer-use RL。"
  "10-05：Sharpening Tax／ThinkingBox／HF multi-harness／ScholarEvolve／VeriHarness／ActiveSaddler／AutoSynthData 指向先修 harness；GLM-5.3 ExploitBench 50/410；Claude Code 2.1.290 修 background／loop 生命週期同權限閘（Act）。"
  "10-06：RSR／WEFT／CorpusMap／CacheBack／RealCompanion／memory（Devin Dreaming、claude-mem）／llm-d／Cursor SDK／OpenRouter shell；另 SHIFT 每 query 預測 harness（9,193 題 79.9 vs Trace 72.7，+7.2pp）、SearchJev System-1 搜尋決策（快約 5.2–5.3×）、ASCENT 線上 TTT（exact success 可>+22pp）、token cue 可喺 base 重現 RL 增益（Olmo MATH-500 42%→78%）。"
  "10-07：OpenAI Decisions API（typed predicate／choice／score，Luna，$0.10/MTok 輸入、官方最高快 10×）、AutomationBench 修 206 verifier bugs（27.9% grades 改變）、EmbeddingGemma 2（多模態 768-d）、Ironclad（Astra rubric 55.0% vs Sol 41.6%）、OSWorld-Pro 過程評估（頂級約 75–78%）。"
  "實務 takeaway：評估前修 harness／verifier；短決策可用 System-1＋校準閘；線上適應要 binary verifier；computer-use 宜報過程同 rubric，唔只交付物。"
  "Radar：Mistral Large 4 preview（~1T／啟用約 49B）；VeriCodeGen／Verified Confinement（LLM 產生＋deterministic verifier）；Cambridge distillation；Era by Eon；gVisor 捐 CNCF。"
 ),
 type_summaries={
  "research": (
   "10-05：Sharpening Tax；ActiveSaddler（TB2 +7.5pp）；GraphForge；PoS；Cambridge（radar）。"
   "10-06：RSR（TB2 pass@3 57.0%→74.2%）；WEFT（Claw-Eval +12.27pp）；CorpusMap；CacheBack；RealCompanion；"
   "SHIFT（79.9 vs Trace 72.7，+7.2pp）；SearchJev（決策快約 5.2–5.3×）；ASCENT（exact success 可>+22pp）；token cue（Olmo 42%→78%）。"
   "10-07 納入 OSWorld-Pro（過程評估，頂級約 75–78%；點擊分水嶺）。"
  ),
  "application_case_study": (
   "10-05：VeriHarness；ThinkingBox；ScholarEvolve；HF multi-harness；AutoSynthData。"
   "10-06：Devin Dreaming／Agent Memory Repo；OpenRouter hosted shell；claude-mem；Era by Eon（radar）。"
   "10-07：AutomationBench Verified（修 206 verifier bugs，27.9% grades 改變）；Ironclad（Astra 55.0% vs Sol 41.6%）；"
   "VeriCodeGen／Verified Confinement（radar）。"
  ),
  "changelog_feature": (
   "10-05／10-06：Cursor SDK run.steer()、background subagents、MCP annotations。"
   "10-07：OpenAI Decisions API beta（typed decisions，Luna，$0.10/MTok 輸入、唔收輸出；官方最高快 10×）。"
  ),
  "model_release_implementation": (
   "10-06：llm-d；gVisor 捐 CNCF（radar）。"
   "10-07：EmbeddingGemma 2（text／vision／audio→768-d，270M–740M，Matryoshka）；"
   "Mistral Large 4 preview（~1T／啟用約 49B，$1.36／$4.18 per MTok；radar）。"
  ),
  "model_release_benchmark": "GLM-5.3 ExploitBench 50/410 vs Mythos Preview 56/410；Act 級 sandbox／權限擴散訊號。",
  "changelog_bugfix": (
   "Claude Code 2.1.289：Bash deny／ask 漏攔 env-var 前綴（radar）。"
   "Claude Code 2.1.290（Top 10／Act）：修 background／loop 生命週期、PreToolUse 權限漏套、respawn skip-permissions；compact resume 只涵蓋新 compaction。"
  ),
 },
)

json.dump(cards, open("cards.json", "w"), ensure_ascii=False, indent=1)
json.dump(week, open("week.json", "w"), ensure_ascii=False, indent=1)
for c in cards:
    print(c["priority"], c["type"], c["id"], len(c["key_takeaway"][0]))
print("PENDING check:", "PENDING" in json.dumps([cards, week]))
print("week_start:", week["week_start"], "cards:", len(cards))

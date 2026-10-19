---
name: ai-tracker-blog-filter
description: >-
  use this when filtering an existing AI blog/changelog/release shortlist into
  P0–P3 cards and a builder-focused digest — not for source discovery, crawling,
  polling, or writing blogs
---
# AI Tracker Blog Shortlist Filter

## Scope
只處理已提供嘅 blog／changelog／release shortlist。
唔建立來源清單、抓網站或設定排程。
唔假設已讀 PLAN-ai-trend-tracker.md；以以下政策為準。
輸入證據不足就標 unknown／needs_verification，唔補作事實。

## User relevance
重視 agents/harnesses、retrieval/data agents、model training、
architecture/inference、multimodal/evaluation，以及工程可用性。
同時評估「會改變實作」同「會改變理解」，唔只看產品發布。

## Priority
P0：有足夠證據，而且滿足至少一項：
- Consequential model release：
  capability、效率、access 或 deployment trade-off 有重大改變。
  有可比較 benchmark／技術內容支持，唔只靠品牌。
- Agent-enhancing changelog：
  真正改變 execution、state/memory、tool use、coordination、
  browser/computer use、self-hosting、恢復或可靠性。
- Major application pattern：
  新 API／workflow／系統模式會直接影響 builder 決策。

P1：
- 扎實 engineering method、case study 或 measured improvement。
- 有實際價值嘅 vertical application。
- 有重要研究方法，但未達 P0 級別影響。
- 潛在 P0 影響未被現有證據充分建立。

P2：
- 小型增量、適用範圍窄，或同使用者關聯較弱。

P3：
- Routine bugfix、純 PR／融資、空泛宣傳、低訊號。

例外：
嚴重 security、data loss、breaking compatibility 問題，
唔當成 routine bugfix；按影響及證據重新評級。
未知使用者有冇依賴該工具，就寫條件式提醒。

## Pricing and changelog rules
- 冇價格唔自動降 P1；有價格唔自動升 P0。
- 區分 unpublished、not_found、not_applicable，唔當成免費。
- 有價格時保留 currency、unit、input/output/cache、tier 等條件；
  缺乏條件就唔做誤導性成本比較。
- Changelog 嘅 digest_focus 只有實質 agent capability 改變先為 true。
- 單純 model picker／effort selector 通常 false。
- 如果控制項真係解鎖重大能力，必須講清楚例外證據。

## To-verify (needs_verification)
只喺「聲稱本身」仲欠官方來源時先標待核實，例如：
- 傳聞 API／產品，但新聞／changelog 未見獨立公告；
- 聲稱已 GA，但冇可核實嘅正式日期。

唔因為以下滯後而掛住待核實（官方公告已出就當確認；滯後可寫喺限制）：
- Hugging Face weights 未上；
- OpenRouter（或其他 marketplace）尚未上架／未見 model id。

Digest 輸出：有待核實項目先寫「## 待核實／To-verify」；**零項就完全唔出呢個 section**（唔寫 None／空白佔位）。

## Workflow
1. 識別 item type、artifact/version、actual delta、availability。
2. 合併同一發布嘅 blog/changelog 重複；保留不同實質變化。
3. 分開記錄 impact 同 evidence：
   provider claim、文件支持、獨立驗證唔可以混為一談。
4. 給 P0–P3、一句 priority_reason，以及 changelog digest_focus。
   重要但未核實嘅聲稱標 potential P0／待核實，唔當已證實。
5. 全部已確認 P0 進 compact index，再展開最值得讀嘅項目；
   加有代表性 P1，唔逐條攤開所有 P1；但每條入選 P1 都要有自己嘅連結
   加一句精簡描述（變咗咩＋對 builder 點解重要；只限一行短句，唔好多句細節），唔可以淨係貼連結／版本號，亦唔好幾條 P1 併埋一行。
6. 完成條件：每個 P0 有明確觸發理由、支持資料、
   availability／限制；冇默默刪走 P0。

## Output
Digest 用單一訊息：P0、P1，以及（僅當非空）待核實（語言跟使用者當日要求；預設繁中）。
每條：
名稱／類型 → delta → 對 builder 嘅影響 → 證據／限制 → 下一步。

P2/P3 只保留分類結果，除非使用者要求 audit。
輸出限制不足以容納全部 P0 時，保留連結 index 或明示 deferred，
唔套用最終 Orchestrator 嘅三條上限。

Feed P0 只代表本來源 priority，唔等於全球 digest 必定第一。

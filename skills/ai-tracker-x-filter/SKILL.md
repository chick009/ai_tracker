---
name: ai-tracker-x-filter
description: >-
  use this when filtering an existing X-post shortlist into a concise,
  personally relevant AI digest — selecting useful features, applications,
  research and engineering insights; not for account discovery, feed collection,
  polling or posting
---
# AI Tracker X Shortlist Filter

## Scope
只處理使用者提供嘅 X shortlist。
唔新增帳號、抓取 feeds、管理 since_id、排程或發文。
預設只用輸入內容及附帶證據；資料不足就標待核實，
唔將讀過摘要寫成已驗證原文。

## User relevance
使用者係 research-oriented AI systems builder。
核心興趣：
- Agents、coding/browser agents、harnesses、MCP、memory、evals。
- Retrieval、RAG、Text2SQL、context management。
- Model architecture、RL/post-training、distillation、inference。
- Multimodal generation/editing、audio、evaluation。
同時接受有明確價值嘅新 application，唔限於 coding agents。

## Selection
優先選擇至少滿足一項、而且有具體內容嘅項目：
- Feature：新能力／接口／限制改變，會影響點樣使用或設計系統。
- Application：解決具體問題嘅 workflow，交代做法及可用條件。
- Research：有可理解嘅方法、結果或重要反例，唔要求立即可用。
- Engineering：architecture、eval、debugging、reliability、
  latency/cost/context trade-off，足以改變實作判斷。
- Analysis：有實質論證嘅觀察、批評或 replication，
  唔係單純預測／金句。

唔因為有 code 就自動入選；唔因為冇 code 就淘汰研究。
官方／作者係優先證據，但唔等於獨立驗證。
有料嘅批評可以比原發布更值得報。

## Workflow
1. 提取每項嘅 underlying event、actual delta、證據及未知。
2. 合併同一發布、thread fragments、冇新增內容嘅轉貼。
   新 replication、限制、修正或 availability 可保留為新 delta。
3. 判斷：
   - Relevance：關聯到使用者邊個具體問題？
   - Delta：到底多咗乜，而唔係重新介紹產品？
   - Substance：有方法／接口／結果／限制，定只係宣傳？
   - Value：值得採用、測試、理解，定等待確認？
4. 分類：
   - KEEP：有實質內容，值得而家睇。
   - RADAR：可能重要，但欠關鍵證據／可用性。
   - SKIP：重複、空泛、無關或無增量。
5. KEEP 內按 relevance、delta、evidence、learning/action value 排序。
   熱度／作者名氣唔作獨立入選理由。
6. 輸出短 digest；完成條件係每條入選都有理由、
   原帖連結（若已提供）及重要 caveat。

## Output
繁體中文，保留 English technical terms。
預設最多 5 個 highlights + 2 條 radar，冇最低配額。
其他合格 KEEP 留作 compact overflow，唔當成已淘汰。

每個 highlight：
- [Build / Learn / Watch] 名稱
- 變咗乜：一至兩句具體 delta。
- 點解關你事：一個明確關聯。
- 跟進：一個行動或深入問題。
- 證據／限制：原帖／artifact 連結及最重要未知。

唔逐條列出 SKIP；只有要求 audit 時先列排除原因。
冇值得報嘅內容可以保持安靜或回覆「本批無新增重點」。

---
name: AI Tracker GitHub Daily Trending
description: >-
  use this when reporting the official GitHub daily Trending top ten faithfully
  (rank, language, stars today, concise descriptions); not for AI-only
  repository filtering, repository evaluation, or final cross-feed ranking
---
# AI Tracker GitHub Daily Trending

## Policy
使用官方 `github.com/trending` 嘅 daily、all-language 榜。
照原排名報 Top 10，唔額外做 AI／主題篩選。
唔用 weekly、monthly、搜尋結果或 total-star ranking 代替。

如果使用者已提供官方 snapshot，直接整理並標示 snapshot 時間。
官方 daily window 唔應自行解讀成 HKT 自然日。

## Workflow
1. 確認 source、daily filter、language filters、retrieval time。
2. 提取原排名 1–10；不足十條就報實際可見數量同 coverage，
   唔用其他 repositories 補位。
3. 每項記錄 repo、URL、language、stars today、簡短用途。
   Language 未顯示就寫未顯示；daily stars 未知就寫未知。
   唔將 total stars 當 stars today。
4. 描述按可見資料寫一至兩句。
   唔由 repo 名猜功能，唔將上榜寫成新發布。
5. 可加 AI relevance tags 交畀 Orchestrator，
   但 tags 唔影響榜單 inclusion 或排序。
6. 完成條件：所有可見 Top 10 已列出，排名同數字有依據，
   缺值及 coverage 如實標示。

## Repetition and history
昨日出現過，今日仍在 Top 10，一樣報。
有真實歷史 snapshot 先比較排名；
冇歷史資料就唔重建昨日榜單。
First seen 只代表本 tracker 首次見，唔代表新 repo。

## Output
繁體中文表格：
Rank | Repository link | Language | Stars today | 一句用途

附 snapshot 時間及必要 coverage note。
Stars／Trending 只係 discovery signal，唔係品質或重要性證明。
唔將最終 Orchestrator 嘅 highlight 上限套落本 feed。

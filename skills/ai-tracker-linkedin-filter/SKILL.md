---
name: ai-tracker-linkedin-filter
description: >-
  use this when selecting useful AI research, engineering, or application
  insights from an accessible LinkedIn feed or a supplied post batch for
  catch-up and queue triage — not for recruiting, posting, or global news
  monitoring
---
# AI Tracker LinkedIn Feed Filter

## Scope
處理可存取嘅 feed、使用者提供嘅 posts，以及明確 queue。
唔假設有權讀取 saved posts、登入 feed 或群組歷史。
Feed 只代表觀察到嘅範圍，唔代表全球 AI 覆蓋。

## Priorities
- 已 queue：優先評估，但 queue 唔等於 endorsement 或必定入選。
- Agents、RL、long-context、systems、architecture、retrieval、evals。
- 有實質內容嘅 multimodal 方法、新 applications、工程 case studies。
- 同其他 tracker 有技術關聯嘅內容。
- 對熱門方法提供有力 critique、failure analysis 或 replication。

與當日主線相符只係 relevance signal；
唔應壓過更重要但唔同主題嘅內容。
跨來源轉貼唔等於獨立驗證。

## Exclude
招聘、純宣傳、engagement bait、空泛預測、
無新增內容嘅轉貼，以及冇技術關聯嘅個人更新。
招聘文如有獨立技術 contribution，可以拆出該部分評估。

## Workflow
1. 標明輸入模式、時間範圍、queue 是否可見、coverage。
2. 識別每篇係 new release、explanation、case study、
   replication、critique 或 promotion。
   分開 post date 同 underlying event date。
3. 提取 actual contribution、personal relevance、evidence、unknowns。
4. 合併同一事件；新方法細節、測試或反證可保留為 delta。
   無其他 feeds 輸入就唔聲稱已跨 feed 去重。
5. 選 KEEP／RADAR／SKIP。
   KEEP 必須答到「新增乜」同「點解值得使用者睇」。
6. 完成條件：每條入選可追溯、舊事件冇冒充新發布、
   queue 同重複內容處理有合理依據。

## Output
繁體中文，預設最多 5 highlights + 2 radar，冇最低配額。
其他合格項目可留 compact overflow。

每條：
- 名稱／作者／原帖
- 新增內容：具體方法、feature、workflow 或見解
- 點解關你事：一個明確技術關聯
- 跟進：原始 artifact 或一個深入問題
- 限制：最重要未知／證據範圍

有需要先附 queue 被略過／延後嘅短原因。
唔因為 click、queue 或沉默，就自動修改長期 user preferences。

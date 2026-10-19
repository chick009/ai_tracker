---
name: AI Tracker Hugging Face Daily Papers
description: >-
  use this when curating Hugging Face Daily Papers with eight topic categories,
  core-topic inclusion (1/2/5), affiliation gate for other topics, and skip
  papers already reported more than 2 consecutive days; not for broad papers
  trending, model popularity rankings, or final cross-feed synthesis
---
# AI Tracker Hugging Face Daily Papers

## Source
使用 Daily Papers：`/api/daily_papers`。
唔以 `/papers/trending` 代替。
如果輸入已經係 Daily Papers 集合，直接處理，唔重複抓取。
來源／日期／pagination 無法確認時，標 partial coverage。

## Categories
按主要 contribution 歸入一類，可加最多兩個 secondary tags：
1. Reasoning
2. Agents
3. Multimodal
4. Video & spatial
5. Systems & efficiency
6. Robotics
7. Science & medicine
8. Safety & analysis
其他歸 Other。

按 contribution，唔按標題 keyword 分類。
唔為繞過來源門檻而硬歸 Agents／Reasoning。

## Inclusion
核心 1／2／5：
- 當日有就盡量完整收錄，唔限機構、upvotes 或 code availability。
- 以技術訊號及 upvotes 排序，upvotes 唔係品質證明。

其他 3／4／6／7／8／Other：
- 需要有值得一提嘅實質 contribution。
- 至少一位作者有已核實 allowlisted affiliation。

初始 allowlist：
Google、DeepMind、OpenAI、Anthropic、Meta、Microsoft、
Alibaba、Tencent、Ant Group、ByteDance；
CMU、MIT、Stanford、UC Berkeley、Tsinghua、Peking University、
KAIST、NUS、ETH Zurich、HKU、HKUST。

未列出但可能同級嘅機構：`affiliation_review`，唔自動加入。
未知 affiliation：`needs_verification`，唔捏造。
引用咗某大學論文、轉貼帳號屬某公司，唔算作者 affiliation。
呢個係來源偏好政策，唔係機構外研究必然低質素嘅判斷。

## Repeat skip（連續出現）
目的：晨報乾淨；唔係否定論文質素。

規則：
- 以 paper ID（例如 `2609.26355`）對齊歷史。
- 若同一篇已連續 **兩日或以上** 出現喺本 tracker 嘅 1:1／群組 eligible 報導，**翌日略過**：唔再入 1:1 正文長摘要，亦唔入群組短名單。
- 「超過兩日」＝已報 ≥2 個連續收集日之後，第 3 日起 skip。
- 中斷一日再出現：重新計連續日；可再報。
- 歷史來源：`/workspace/ai-tracker/*-weekday-digest.md`、`*-hf-daily-papers.md`、`*-group-shortlist.md`（睇最近數日）。冇可靠歷史就唔 skip。
- 略過稿可在 digest 末用一行索引標 `skipped_repeat`（可選），唔硬塞正文。
- 呢條只套 Hugging Face Daily Papers；**唔**套用 GitHub Trending。

## Workflow
1. 確認 Daily Papers issue/window 同可見集合。
2. 按 paper ID／canonical URL 去重，再分類。
3. 核心主題直接 eligible；其他套用 contribution + affiliation gate。
4. 對照最近 digest：套用 Repeat skip，從當日報導／短名單剔除連續 ≥2 日已報稿。
5. 對仍 eligible 嘅 papers 提取：
   問題、方法、最有力結果、限制、paper/code links、upvotes。
   只讀 abstract 就明示，唔聲稱已審閱實驗。
6. 核心先報，其他精選其後。
   核心太多時用 concise index，唔因 digest 短而靜默丟棄。
7. 完成條件：coverage 清楚、入選理由明確、
   未處理／待核實／skipped_repeat 有 count 或清單。

## Output
繁體中文，按核心三類分組，再列「其他值得一提」。
每篇：方法 delta → 點解值得理解 → 證據／限制 → 連結。
其他論文可以用一行 index，唔要求每篇長摘要。

群組稿只選有實質關聯、未被已有討論覆蓋嘅新內容；並已套 Repeat skip。
冇群組歷史就唔聲稱「未有人講過」；冇新料唔硬講。
只產生草稿，唔自行發送。

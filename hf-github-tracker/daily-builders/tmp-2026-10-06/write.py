import json,sys
sys.path.insert(0,'tmp-2026-10-06'); from cls import CLS,ALLOW,NOT
E={x['id']:x for x in json.load(open('2026-10-06-papers-extract.json'))}
gh=json.load(open('2026-10-06-github-trending.json'))
GHD={1:'新一代 web 同 mobile app 嘅 e2e 測試框架。',
2:'跨 session 保存 agent context：記錄 agent 做過嘅嘢、用 AI 壓縮，再注入返之後嘅 session；支援 Claude Code、Codex、Gemini、Copilot 等。',
3:'畀 agent CAD 能力。',4:'官方頁未顯示描述（唔由 repo 名推測用途）。',
5:'自動將 PS5 執行檔移植到 Linux 同 Windows 嘅工具。',
6:'一個 CLI 令 AI agent 讀同搜 Twitter、Reddit、YouTube、GitHub、Bilibili、小紅書，聲稱零 API 費用。',
7:'開源 agentic 影片製作系統（12 條 pipeline、100+ 工具、700+ skill／知識檔）。',
8:'快速、可擴展、多平台、自動 HTTPS 嘅 HTTP/1-2-3 web server。',
9:'自架健身同體重追蹤器：排課表、記錄訓練、睇邊組肌肉練咗或疲勞，可由 FitNotes／Strong／Hevy 匯入。',
10:'建喺 Cloudflare Workers 上嘅 agent workspace，用公司 context 同系統寫文件、起 app、跑 agent。'}
def links(i):
    x=E[i]; s=f"[HF](https://huggingface.co/papers/{i}) · [arXiv](https://arxiv.org/abs/{i})"
    if x['github']: s+=f" · [code]({x['github']})"
    if x['project'] and x['project']!=x['github'] and 'arxiv.org' not in x['project']: s+=f" · [project]({x['project']})"
    return s
def org(i): return E[i]['org'] or '未標'
def full(i,delta,why,ev,extra=''):
    x=E[i]; return f"**[{x['title']}](https://huggingface.co/papers/{i})** · upvotes {x['upvotes']} · org {org(i)}{extra}\n- 方法 delta：{delta}\n- 點解值得睇：{why}\n- 證據／限制：{ev}\n- 連結：{links(i)}\n"
def idx(i,aff=None,note=''):
    x=E[i]; t=x['title']; t=t if len(t)<=52 else t[:50]+'…'
    return f"- `{i}` {t} · ⬆{x['upvotes']} · {aff or org(i)}{note}"
AG=[
('2610.02826','RSR（Recursive Self-Rewrite）：同一個 base model（Qwen-3.8-27B）喺多個專用 harness 下搵到成功解，planner 抽成 runbook、critic 篩走 verifier／答案洩漏並遞迴修訂，executor 再喺通用 harness 嘅新 sandbox 照 runbook 重做，變成可訓練軌跡。','Tencent Hunyuan：專用 harness 嘅「外掛」部署時用唔到——呢篇示範點樣將 harness 輔助經驗重寫成通用 harness 下嘅能力。','Abstract 報：約 3K terminal 任務，三個 harness 合共解 759 題（比最強單一 harness 多 34.3%）；2,001 條源軌跡擴成 11,094 條 SFT 數據；Terminal-Bench 2 pass@3 57.0%→74.2%、Terminal-Bench 4 1.5%→9.1%。部分 benchmark 係自建。'),
('2610.00972','VeriHarness：將 generator 用嘅同一個 LLM 變成 agentic verifier（workspace＋證據工具＋可重用 verification skills）；disagreement resolver 用環境證據查互相矛盾嘅 claim，consensus challenger 專挑「大家都同意」嘅 claim 同漏咗嘅要求。','Google：long-horizon agent 輸出冇參考答案時點樣驗證——發現「共識會掩蓋錯誤、分歧反而暴露正確答案」。','Abstract 報五個 long-horizon workspace benchmark、兩個前沿模型上選擇分數最高；加證據修訂後比單次 rollout 平均 +6.2（Gemini 3.5 Flash）／+6.4（Claude Opus 4.8）；公開約 26,000 條 rollouts（成本逾 10 萬美元）。'),
('2610.01780','RealCompanion：十段真實人與 AI companion 嘅關係（27,218 則訊息、最長 120 日），附 profile、persona、chat ground truth 同問題集，每項都引用原訊息，並逐步核對推理過程。','今日 upvotes 最高（204）。用真實長期對話測「AI 伴侶有冇真正了解用戶」，結論對 agent memory 設計好有啟發。','Abstract 報：近因窗口已覆蓋 95.9% probes，但需要記憶嘅只覆蓋 2.2%；冇 detector 可靠判斷幾時需要記憶；三個 agent 系統重建 persona F1 相同但成本相差 31 倍。只得十段關係，樣本細。'),
('2609.36887','WEFT：唔只擴 environment，而係將 environment、task、harness、evaluator 當成整體一齊擴展同按執行軌跡自我演化；post-training 用 prefix-preserving sampling、atomic-turn credit assignment，加 MegaMCP 管理並行 rollouts 嘅隔離狀態。','Tool-use post-training 嘅一個系統性觀點：環境數量多唔等於學習訊號好，要整個互動系統協調。','Abstract 報：WEFT-14B 喺 BFCL V4、τ²-Bench、Claw-Eval 比 Agent-World-14B 高 6.41／2.23／12.27 個百分點；35B-A3B 延伸到 Toolathlon-Verified、AutomationBench（數字未列）。'),
('2610.03675','FrugalEvo：成本感知嘅 LLM 程式演化——貴模型探索策略、平模型實作同迭代；prompt／harness 設計最大化 prefix 共享以提高 cache 命中；新指標 BA-AUC 量度固定預算下嘅最佳分數曲線。','AlphaEvolve 類方法通常只睇固定迭代數嘅效果，呢篇改為「每蚊收益」，對實際跑 evolve 好實用。','Abstract 報 10 個數學／系統優化任務中 9 個 BA-AUC 最高；circle packing 用 1.68 美元（GPT-5.6 Terra／Luna）或 0.55 美元（GLM-5.3）達 SOTA，對比 baseline 平均約 50 美元。'),
('2610.02710','SWR（software-in-the-loop reconstruction）：由現有科學軟件 workflow 自動攞參考輸出同驗證目標，agent 只睇部分 input–output 去重建程式，再喺隱藏配置上驗證（加防 shortcut 檢查）。','唔使逐題寫參考解同 verifier，就可以擴展科學領域嘅 terminal agent 訓練環境。','Abstract 報 500 個 workflow、46 個軟件家族、六個領域；Qwen3.8-27B SFT 後 Terminal-Bench 2 平均 47.94%→53.56%（三個 seed）。upvotes 低（2）。'),
('2610.03574','HyperBrowseComp：423 條人手撰寫並驗證嘅瀏覽題，13 種語言，需要喺影片、掃描文件、圖片、地圖等異質來源搵冷門證據並串連多步線索。','BrowseComp 類 benchmark 多數係英文純文字；呢個補上多語同多模態嘅 web agent 壓力測試。','Abstract 有模型同人類評估，但冇列具體分數。'),
]
AG_IDX=['2610.02304','2610.01257','2610.03715']
RE=[
('2609.38879','Fold2Reason：由解咗嘅蛋白質結構生成大量可精確核對嘅空間／拓撲問答（FoldingCorpus），post-train 時同時用語言 head 答離散結構問題、由同一表徵解碼連續 3D 幾何。','測試「非語言、結構密集嘅科學數據」能唔能夠提升一般推理，而唔止蛋白質任務。','Abstract 報 FoldBench 結構預測分數係 Qwen3.5-9B 嘅 2.7–3.5 倍；10 個空間／圖／科學／一般推理 benchmark 全部提升，macro 平均 45.09%→48.33%；隨機／打亂結構對照增益細或負。'),
('2610.03695','QUEEN：將「沉默專家」棋引擎 encoder 經 cross-attention 接入 instruction-tuned LM，先用 QA curriculum 抽棋理概念，再用自然語言版 Bellman update（分析候選步之後嘅局面再整合成解釋）迭代蒸餾。','一個將領域專家模型同 LM 結合、令佢「識做又識解釋」嘅通用 recipe；作者認為可延伸到遊戲、機械人、computer use。','Abstract 報七輪迭代後 Elo 1782→2697，棋力同 puzzle 準確度超越所有前沿模型，參數少三個數量級；解釋連貫度接近 GPT-5.6-Sol（high），但係用 LM 評估。'),
('2610.03367','Multilingual GSM-Symbolic：15 種語言、30,000 條逐項對齊嘅數學題，用 symbolic template 生成變體防過擬合，聯合估計跨語言能力轉移嘅決定因素。','可以量化「模型大小、語言資源、推理、語言類型距離」各自對低資源語言表現嘅影響。','Abstract 報：模型大小 β=1.77、資源 β=0.77、推理 β=0.67、類型距離 β=-0.25；32B 模型喺 Marathi 表現約等於 10B 喺英文；可預測未見語言表現誤差 6.0pp。'),
('2609.39394','STAIR：同一對話入面連續答多條獨立題時，將之前生成嘅 KV 存入固定 bank，學一個只有 12,288 參數嘅機制去重新導向當前 query 讀取，base model 凍結。','實證「保留歷史」對後續推理有正有負，並提出極輕量嘅方法令之前嘅計算真正幫到新問題。','Abstract 報三個 Qwen 模型、四個 benchmark，後續回合平均準確度最多 +11.67 個百分點。upvotes 低（3）。'),
('2610.03665','Pivot-SD：masked diffusion LM 嘅離線 self-distillation，只監督「pivot」——按資訊增益揀出對剩餘 mask 位置影響最大嘅幾個 commitment；成功軌跡用 cross-entropy，失敗軌跡用 targeted unlikelihood。','dLM post-training 嘅 credit assignment 問題好獨特，呢個用好少數據就做到。','Abstract 報只用 200 條問題、每條 4 個 rollout，LLaDA-8B-Instruct 喺數學同 code benchmark 上贏 full-sequence SFT 同同預算 diffusion RL；數字未列。'),
('2610.03509','用三種方式施加長度壓力（固定預算、逐例長度目標、group-relative 長度獎勵）訓練高效推理，再量 CoT faithfulness 同 monitorability。','直接回應「縮短 CoT 會唔會令監控失效」呢個 safety 擔憂。','Abstract 報 faithfulness 喺大部分設定下降（主要因為模型一致性變差），但 monitorability 較穩健——CoT 短咗仍會承認輸入干預對答案嘅影響。'),
]
RE_IDX=['2610.02824']
SY=[
('2609.36659','OPSFT：分析發現 SFT 沿固定方向更新參數、on-policy 會持續調整方向；於是先用少量 on-policy 步驟搵出每個參數嘅累積更新方向，再將 SFT 更新約束喺呢個方向上。','將 on-policy 嘅泛化優勢「轉移」畀 SFT，同時保留 SFT 嘅效率同用高質軌跡嘅能力。','Abstract 只講「表現強」，冇列具體 benchmark 數字。'),
('2610.02381','Latent-MOPD：多 teacher on-policy distillation 唔止傳 output distribution，仲傳 hidden states；按師生關係揀後層目標、用共享 projection 對齊寬度、按 domain 分組更新，監督由 hidden state 逐步轉向 token prediction。','將多個專家模型合併成一個學生嘅新路徑（表徵層＋輸出層雙通道）。','Abstract 報同家族設定下九個數學／code／邏輯 benchmark 全部贏 token-only、representation-only 同平均 baseline；同參數量學生喺多數 benchmark 超越最佳 teacher。'),
('2609.32046','CacheBack：多 agent 之間傳 KV cache 時，receiver 先講低自己需要咩，sender 按 attention 權重過濾壓縮 KV（training-free）。','直接解決 latent communication 嘅 KV 隨 context 同 agent 數線性膨脹問題。','Abstract 報 FanOutQA（Qwen 3）：少收 75% 狀態，準確度 +14.7 個百分點，完成延遲中位數比文字溝通快 3.2 倍；跨 dense、Mamba 混合、sliding-window 模型都有效。'),
('2609.32759','Extender：Transformer 每層除咗 residual 更新，再輸出一個好細嘅 extension 接落 concat 通道，attention 嘅 KV projection 只睇呢個通道，大幅縮細持續 attention 記憶。','KV 記憶體係長 context 推理瓶頸，呢個由架構層面處理。','Abstract 報 924M 模型持續 attention 記憶比 MHA 細 104 倍；短 context（CORE）追平、長 context（RULER）超越 Transformer。規模最大只到 924M。'),
('2610.01153','LOOM：診斷 looped MoE 嘅「expert 選擇崩潰」（每輪都揀同一班 expert），用縮放 residual、每輪重注入 embedding、per-loop router 同 Looping Residual 解決。','Looped transformer 係新嘅 scaling 軸，呢篇令佢喺 MoE 上穩定擴到 9–12 輪。','Abstract 報 near-iso-FLOP 下 700M 模型 5 輪最好，perplexity 18.36→16.54；1.7B（60B tokens）9 輪 perplexity 9.62→7.77、zero-shot 平均 42.4%→47.7%（非 FLOP 對齊）。'),
('2609.32182','KeyRec：training-free 嘅有界視覺記憶——近期觀察留細節 cache，歷史整理成 event bank（add–merge–evict），問題嚟時 text-only router 分配讀取預算，唔使重新處理舊幀。','Google：串流／長影片 VLM 嘅 token 成本問題，用記憶結構而唔係單純丟 token。','Abstract 報只用 10% 視覺 token 預算，15 個設定中 13 個壓縮後最佳，即時問題比最強壓縮 baseline 高 2.21–18.37 分。upvotes 低（2）。'),
]
SY_IDX=['2609.36529','2610.02126','2610.02179','2609.33463','2609.26425','2609.26590']
OT=[
('2610.02508','ProWAM：world action model 同時預測 action 同一串有序嘅稀疏視覺 sub-goal，sub-goal 可由大量無 action 影片學；只跑一次 video backbone forward 就 cache sub-goal 特徵，重新規劃只需輕量 action denoising。','Meta：解決 WAM 生成密集影片 rollout 太慢、單幀目標又冇「進度」嘅問題。','Abstract 報 LIBERO-Plus 85.8%、隨機化 RoboTwin 75.7%（相對 baseline 最多 +35.9%）；真機 zero-shot 新場景 55.0%→70.0%。',' · Robotics · aff Meta＋SJTU'),
('2610.03391','NAVA-WAM：直接用冇 action 標註嘅影片預訓練 action policy（future-video flow matching 經 joint attention 傳到 Action-DiT），再用有標註示範 post-train；推理時只跑 action。','Meta：令 WAM 擺脫對大量 action 標註機械人數據嘅依賴。','Abstract 稱 in-/out-of-distribution 都贏先前方法、action 標註效率高、真機泛化好；冇列數字。',' · Robotics · aff Meta AI'),
('2609.38839','FrameMorrow：長影片生成時，預測少量「prospective tokens」代表未來資訊需要，按呢個揀歷史幀，而唔係按當前內容相關度揀。','NUS：plug-and-play，揀嘅係顯式歷史幀，閉源生成器都用得。','Abstract 報 5 個 benchmark、11 個生成模型（長影片、互動生成、action-conditioned world model）一致改善一致性同畫質；冇列數字。',' · Video & spatial · aff NUS'),
('2610.03710','EyeRobot 2.0：只用一部 stereo 相機，令兩個「眼」視角主動轉向 3D 注視點，foveal 處理；分層訓練 gaze servoing 同 target selector（真機 RL），動作喺注視點相對座標系表示。','UC Berkeley：唔使 wrist camera 都做到精細雙手操作。','Abstract 報 1000+ 真機、1800 模擬試驗；比被動 stereo 真機高 40%；wrist 被物件遮擋時成功率 48% vs 22%。',' · Robotics · aff UC Berkeley／Stanford＋Amazon FAR'),
]
OT_IDX=[('2609.28339','Robotics','HKU／HKUST＋Princeton'),('2610.03664','Video & spatial','作者含 Microsoft'),('2609.37925','Video & spatial','Tencent AIPD＋CUHK'),
('2609.39071','Other（法律）','Tsinghua／PKU'),('2610.03240','Safety & analysis','NUS＋NTU'),('2610.02388','Multimodal','PKU'),
('2609.34826','Multimodal','CMU／MBZUAI＋UCSD'),('2609.40153','Robotics','作者含 HKU')]
# sanity
core=[i for i,c in CLS.items() if c in('Agents','Reasoning','Systems')]
covered=[x[0] for x in AG+RE+SY]+AG_IDX+RE_IDX+SY_IDX
assert sorted(core)==sorted(covered),(set(core)^set(covered))
assert sorted([x[0] for x in OT]+[x[0] for x in OT_IDX])==sorted(ALLOW)
nA=sum(1 for c in CLS.values() if c=='Agents');nR=sum(1 for c in CLS.values() if c=='Reasoning');nS=sum(1 for c in CLS.values() if c=='Systems')
L=[]
L.append('# AI Tracker 晨報｜2026-10-06（二）06:58 HKT\n')
L.append('來源：GitHub Trending daily all-language；Hugging Face Daily Papers API（`/api/daily_papers`）。')
L.append('**HF 日期說明**：今日 `date=2026-10-06` API 回 400（上限 2026-10-05）；改用最新已發布 issue **2026-10-05（一）**（62 篇，全部 `submittedOnDailyAt`＝2026-10-05；`limit=100` 未觸頂，覆蓋完整）。')
L.append('Upvotes／stars today 只係 discovery signal，唔代表品質。論文摘要只根據 abstract，未讀全文。')
L.append('**Repeat skip**：今日 issue 同 10-02（issue 10-01）、10-05（issue 10-02）兩個收集日嘅報導都無 paper ID 重疊，skipped_repeat **0**。\n\n---\n')
L.append('## GitHub Trending Top 10\n')
L.append(f"Snapshot：{gh['snapshot_hkt']} · https://github.com/trending?since=daily\n")
L.append(f"官方 daily all-language 頁面可見 **{gh['visible']}** 條；報原排名 **1–10**（唔補位、唔篩 AI）。\n")
L.append('| Rank | Repository | Language | Stars today | 一句用途 |\n| ---: | --- | --- | ---: | --- |')
for r in gh['top10']:
    L.append(f"| {r['rank']} | [{r['repo']}]({r['url']}) | {r['language'] or '未顯示'} | {r['stars_today'] or '未知'} | {GHD[r['rank']]} |")
L.append('\n同昨日（10-05）真實 snapshot 比較：仍在榜 6 個——e2e（1→1）、text-to-cad（5→3）、t3code（9→4）、Agent-Reach（6→6）、OpenMontage（8→7）、caddy（10→8）；新入 Top 10：claude-mem、AnyPS5、openGym、cloudflare-os。今日 stars today 最高係 openGym（1444），其次 e2e（1430）。\n\n---\n')
L.append('## Hugging Face Daily Papers（issue 2026-10-05｜fallback）\n')
L.append(f"收錄：核心（Agents {nA}／Systems & efficiency {nS}／Reasoning {nR}）**{nA+nS+nR}** 篇；其他主題（實質貢獻＋allowlist）**{len(ALLOW)}** 篇；未入選／待核實 **{len(NOT)}** 篇；skipped_repeat **0**。分類按 contribution；affiliation 來自 HF org 同／或 arXiv HTML 作者單位。核心重點詳寫＋其餘 index。\n")
L.append('### 核心：Agents\n')
for a in AG: L.append(full(*a))
L.append('**其餘核心 Agents（index）**\n'); L+= [idx(i) for i in AG_IDX]; L.append('')
L.append('\n### 核心：Reasoning\n')
for a in RE: L.append(full(*a))
L.append('**其餘核心 Reasoning（index）**\n'); L+=[idx(i) for i in RE_IDX]; L.append('')
L.append('\n### 核心：Systems & efficiency\n')
for a in SY: L.append(full(*a))
L.append('**其餘核心 Systems（index）**\n'); L+=[idx(i) for i in SY_IDX]; L.append('')
L.append('\n### 其他值得一提（allowlist affiliation）\n')
for a in OT: L.append(full(*a))
L.append('**其他 allowlist（index）**\n'); L+=[idx(i,f'{c} · {a}') for i,c,a in OT_IDX]; L.append('')
L.append('\n### 未入選索引\n')
L.append(f'共 **{len(NOT)}** 篇（非核心主題未過 allowlist 或單位未核實），唔代表質素低。\n')
for i,(st,a) in NOT.items(): L.append(idx(i,f'{CLS[i]} · {st} · {a}'))
L.append('\n**skipped_repeat 索引**：無。\n\n---\n\n*收集完成 · 唔發群；只交 1:1。摘要只根據 abstract。*\n')
open('2026-10-06-weekday-digest.md','w').write('\n'.join(L))
# HF-only file
hs=L.index('## Hugging Face Daily Papers（issue 2026-10-05｜fallback）\n')
open('2026-10-06-hf-daily-papers.md','w').write('\n'.join(L[hs:]))
gs=L.index('## GitHub Trending Top 10\n')
open('2026-10-06-github-trending.md','w').write('\n'.join(L[gs:hs]))
SL=[('2610.02826','Tencent RSR：將多個專用 harness 嘅成功解重寫成通用 harness 軌跡，Terminal-Bench 2 pass@3 57.0%→74.2%。'),
('2610.00972','Google VeriHarness：用同一 LLM 做 agentic verifier，靠分歧同挑戰共識驗證 long-horizon 輸出，比單次 rollout +6 分左右。'),
('2610.01780','RealCompanion：十段真實長期 AI companion 對話 benchmark，發現真正需要記憶嘅訊息少而遠，現有 detector 判斷唔到。'),
('2609.36887','WEFT：environment、task、harness、evaluator 一齊擴展同自我演化做 tool-use post-training，14B 喺 Claw-Eval +12.27pp。'),
('2610.03675','FrugalEvo：貴模型探索、平模型實作嘅成本感知程式演化，circle packing 用 0.55–1.68 美元達 SOTA。'),
('2609.38879','Fold2Reason：用蛋白質摺疊數據 post-train，10 個一般推理 benchmark 全部提升（平均 +3.23pp）。'),
('2610.03695','QUEEN：棋引擎 encoder＋LM 用自然語言 Bellman update 迭代，Elo 1782→2697 兼識解釋棋步。'),
('2609.32046','CacheBack：多 agent 按 receiver 需要過濾 KV cache，少傳 75% 狀態、準確度 +14.7pp、延遲快 3.2 倍。'),
('2610.01153','LOOM：修正 looped MoE 嘅 expert 選擇崩潰，穩定擴到 9–12 輪，1.7B perplexity 9.62→7.77。'),
('2610.03509','高效推理訓練會降 CoT faithfulness，但 monitorability 相對穩健。'),
('2610.02508','Meta ProWAM：world action model 預測稀疏視覺 sub-goal 序列，真機 zero-shot 55%→70%。'),
('2610.03710','UC Berkeley EyeRobot 2.0：單 stereo 相機主動注視做精細雙手操作，wrist 遮擋時 48% vs 22%。')]
G=['【群組短訊草稿｜06:58 收集，尚未發到 AI Tracker 群】kickoff 時一次過貼 Papers + GitHub（同一則訊息）。',
'HF note：今日 API 上限 2026-10-05，用最新 issue **2026-10-05**（62 篇）；skipped_repeat 0。\n',
'**Papers（HF Daily Papers issue 2026-10-05｜fallback）**']
G+=[f'- https://huggingface.co/papers/{i} — {s}' for i,s in SL]
G+=['',f"**GitHub Trending（daily all-language；官方頁可見 {gh['visible']} 條，已報 Top 10）**"]
G+=[f"- {r['url']} — {GHD[r['rank']]}" for r in gh['top10']]
open('2026-10-06-group-shortlist.md','w').write('\n'.join(G)+'\n')
cur=dict(issue_date='2026-10-05',collect_date='2026-10-06',core_agents=[i for i,c in CLS.items() if c=='Agents'],
core_systems=[i for i,c in CLS.items() if c=='Systems'],core_reasoning=[i for i,c in CLS.items() if c=='Reasoning'],
other_allowlist=list(ALLOW),not_selected=list(NOT),skipped_repeat_ids=[],streak2_prior_ids=[],group_shortlist_ids=[i for i,_ in SL])
json.dump(cur,open('2026-10-06-papers-curation.json','w'),ensure_ascii=False,indent=1)
meta=dict(date='2026-10-06',weekday='Tuesday',snapshot_hkt='2026-10-06 06:58 HKT',github_snapshot_hkt=gh['snapshot_hkt'],
hf_date_requested='2026-10-06',hf_date_used='2026-10-05',hf_fallback=True,
hf_fallback_reason='API ?date=2026-10-06 returned 400 (date must be <= 2026-10-05); used latest published issue 2026-10-05 (62 papers, limit=100 not hit).',
hf_issue_papers_total=len(E),hf_core_agents=nA,hf_core_systems=nS,hf_core_reasoning=nR,hf_other_allowlist=len(ALLOW),hf_not_selected=len(NOT),
hf_skipped_repeat=0,hf_skipped_repeat_ids=[],hf_streak2_note='Today issue 2026-10-05 has zero ID overlap with Oct 2 and Oct 5 reported sets.',
github_visible_rows=gh['visible'],github_reported=len(gh['top10']),github_top1=gh['top10'][0]['repo'],
artifacts=['/workspace/ai-tracker/2026-10-06-'+f for f in ['weekday-digest.md','group-shortlist.md','hf-daily-papers.md','github-trending.md','github-trending.json','meta.json','papers-extract.json','papers-curation.json','arxiv-aff-parsed.json']]+['/workspace/ai-tracker/raw-daily-papers-2026-10-06.json','/workspace/ai-tracker/raw-github-trending-2026-10-06.html'])
json.dump(meta,open('2026-10-06-meta.json','w'),ensure_ascii=False,indent=1)
open('last_run_meta.txt','w').write(f"date=2026-10-06 snapshot=2026-10-06 06:58 HKT hf_issue=2026-10-05 fallback=1 github=10/{gh['visible']} skipped_repeat=0\n")
print('ok',nA,nR,nS)

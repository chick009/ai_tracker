import json,sys
sys.path.insert(0,'tmp-2026-10-05'); from cls import CLS
E={x['id']:x for x in json.load(open('2026-10-05-papers-extract.json'))}
gh=json.load(open('2026-10-05-github-trending.json'))
GHD={1:'新一代 web 同 mobile app 嘅 e2e 測試框架。',2:'一套設計語言，令 AI harness 做設計做得更好。',
3:'畀 Claude Code 同 AI agents 用嘅行銷 skills（CRO、文案、SEO、分析、增長工程）。',
4:'令 AI agent 用「最懶嘅 senior」思維嚟諗同做：最好嘅 code 係唔使寫嘅 code。',5:'畀 agent CAD 能力。',
6:'一個 CLI 令 AI agent 讀同搜 Twitter、Reddit、YouTube、GitHub、Bilibili、小紅書，聲稱零 API 費用。',
7:'以開發者為先嘅錯誤追蹤同效能監控。',8:'開源 agentic 影片製作系統（12 條 pipeline、100+ 工具、700+ skill／知識檔）。',
9:'官方頁未顯示描述（唔由 repo 名推測用途）。',10:'快速、可擴展、多平台、自動 HTTPS 嘅 HTTP/1-2-3 web server。'}
def links(i):
    x=E[i]; s=f"[HF](https://huggingface.co/papers/{i}) · [arXiv](https://arxiv.org/abs/{i})"
    if x['github']: s+=f" · [code]({x['github']})"
    if x['project'] and x['project']!=x['github'] and 'arxiv.org' not in x['project']: s+=f" · [project]({x['project']})"
    return s
def org(i): return E[i]['org'] or '未標'
def full(i,delta,why,ev,extra=''):
    x=E[i]; return f"**[{x['title']}](https://huggingface.co/papers/{i})** · upvotes {x['upvotes']} · org {org(i)}{extra}\n- 方法 delta：{delta}\n- 點解值得睇：{why}\n- 證據／限制：{ev}\n- 連結：{links(i)}\n"
def idx(i,aff=None):
    x=E[i]; t=x['title']; t=t if len(t)<=52 else t[:50]+'…'
    return f"- `{i}` {t} · ⬆{x['upvotes']} · {aff or org(i)}"
AG=[
('2609.38923','GraphForge：由職業 seed 組合真實檔案 workspace，喺檔案關係上建 evidence graph，task 同 rubric 都由圖導出，每條準則錨定到可驗證嘅檔案；再用 revision agent 修正 task 後先收軌跡。','Working agent（讀檔、用工具、交付成果）最缺嘅係「真實檔案＋可驗證結果」嘅訓練數據——呢個 pipeline 正正補呢個洞。','Abstract 報：Qwen3.6-27B 用 2,169 條軌跡微調，GDPVal 1445.7（+65.7，OpenHands），Workspace-Bench-Lite 63.7（+7.7）、SpreadsheetBench II 24.0（+13.7，Claude Code）；rejection FT 再升。數據同模型聲稱已公開。'),
('2610.01415','PoS：inference-time 框架，唔再只係堆疊歷史記憶，而係持續維護顯式 belief state（現況估計＋未解決需求），並偵測「Belief Trapping」（一直做嘢但冇進展）再按類型恢復。','Alibaba：long-horizon agent 嘅 context 管理，由「記住／壓縮歷史」轉去「維持一致嘅世界理解」。','Abstract 報四個 benchmark、三個 backbone 全部最佳；ablation 支持 consistency validation 同 recovery。冇列具體數字。'),
('2610.00906','ActiveSaddler：將 harness 優化嘅「用邊啲場景產生 feedback」變成非平穩 bandit；把重複失敗抽象成 failure-pattern arms，估計學習進度，平衡重訪弱點同探索新場景。','Microsoft：harness 自動優化唔止要識點改，仲要識揀練咩——curriculum 要同 harness 一齊演化。','Abstract 報 GAIA2 同 Terminal-Bench 2.0 test Pass@1 分別 +4.4 同 +7.5 個百分點（對比固定場景次序）。'),
('2609.32993','X-Tree：仿 tokenizer 嘅方法，按可重用性為 action span 打分並合併，建立「經驗樹」；唔使 LLM call，直接用喺 offline RL、online RLVR（skill bonus）同 on-policy self-distillation。','將 agent skill 由「context 入面嘅文字」變成訓練結構入權重，令泛化唔靠檢索。','Abstract 報同數據同預算下：WebArena +4.5% SR、ScienceWorld +5.8% SR、WebShop +4.1%，三個模型規模。'),
('2609.38024','RASO：用公開 skill 語料做先驗，經 Cross-Harness Adaptation 處理領域同 harness 嘅錯配；RASI 唔使 rollout 就起到初始 skill，RASU 再按執行反饋檢索更新。','而家有大量公開 agent skills，但 skill 優化方法多數無視佢哋、純靠昂貴 rollout——呢篇係「skill 檢索增強」嘅路線。','Abstract 報四個 agent benchmark、兩個模型一致贏冇檢索嘅 baseline；冇列具體數字。'),
('2610.01215','AutoGUIWorld：用 image generator 當 GUI 視覺世界模型，planner 指定 action 同預期視覺後果，再逐步編輯截圖生成下一個觀察——唔使真係部署軟件就合成 GUI 軌跡。','Tencent Hunyuan：GUI agent 數據受限於可跑嘅軟件環境，呢個方法繞過部署成本擴大覆蓋。','Abstract 報 79,266 個 step-level 樣本（Ubuntu／Windows／macOS／Chrome）；Qwen3.5-35B-A3B 微調後 OSWorld 33.0%→40.8%、ScienceBoard 14.0%→32.2%。'),
('2609.40097','AutoDataBench：固定訓練框架、超參、算力等非數據因素，專測 agent 嘅「Data Intelligence」（數據診斷、組織、構建），並比較訓練前預測同實際結果，睇 LLM 係咪真係明白自己嘅數據干預。','Auto-research benchmark 通常混埋好多改進來源；呢個把「改數據」能力獨立出嚟量度。','Abstract 稱重用 benchmark 軌跡做 mid-training 可提升 coding 表現；冇列具體數字。'),
]
AGI=['2610.00314','2610.02122','2609.32520','2609.33403','2610.02181','2609.34210','2609.32536','2610.00313','2609.38593','2610.02206','2610.00437','2610.01026','2610.01017']
RS=[
('2610.01509','提出「Sharpening Tax」指標：RL post-training 令任務推向「必解或必唔解」兩極，提高 pass@1 但損失 pass@K 覆蓋；再提出 PTGS（按 prompt 難度調溫度嘅 Bayesian sampler）減稅。','Meta：喺 agentic 任務都觀察到 base model＋輕 harness 喺足夠 test-time budget 下 pass@K 可以贏 post-trained 版本——對 RL 帶來「新能力」定只係「銳化」嘅爭論係直接證據。','Abstract 報 14 對 base/post-trained 模型、4 個家族、3 個 agentic benchmark（42 個 case），稅喺大多數設定存在，少量 rollout 已可估計。'),
('2609.36585','發現預訓練 transformer 只用少量深度去跟 context 入面嘅引用鏈（13 個 base model 只可靠跟 1.4–3.6 行）；喺一個早期層加 rank-8 LoRA（其餘權重凍結）就可延長呢段計算。','「模型唔識」可能只係「冇用盡深度」——一個極細嘅改動就解鎖大量潛藏計算。','Abstract 報 Qwen3-8B 喺 24 行鏈由 15.5% 升到 99% exact accuracy，長訓 LoRA 去到 50 行；機制分析指出 middle layers 嘅 relay；MuSiQue 亦有提升。'),
('2609.38104','Parallel Power Tempering（PPT）：用 parallel tempering 實現 power-sharpened sampling——低 power 副本探索、高 power 副本利用，並修正舊 power sampler 嘅 truncation bias。','唔做 RL post-training、純 inference-time sampling 去推細模型 reasoning，係 RL 以外嘅另一條路。','Abstract 稱優於單鏈 power sampling 同 RL post-trained 模型、接近 frontier；冇列具體數字。org Morgan Stanley。'),
]
SY=[
('2609.35259','喺受控 strong-to-weak 蒸餾入面，獨立變 rollout policy、token-level KL 方向同 learning rate（Llama3、Qwen2.5；科學／醫學／算術推理）。','打破「on-policy 一定少遺忘、更泛化」嘅講法：真正主導效果嘅係 KL 方向同 learning rate。','Abstract 報：forward KL 對 rollout policy 好穩健，reverse KL 敏感且偏好學生 rollout；learning rate 主導遺忘同更新稀疏度；on-policy 數據對較難任務泛化仍有幫助。'),
('2610.02193','HC-DLM：將離散 token 生成同連續 latent 軌跡耦合喺單一 denoising 過程，latent 係唯一持續生成狀態，token 每步讀出再回饋做下一步 scaffold；目標由 token likelihood 嘅變分下界導出。','修正離散 diffusion LM 並行解碼時 token 獨立抽樣、切斷依賴嘅結構瓶頸。','Abstract 報 Sudoku、Countdown、LM1B 上同等條件贏離散同連續 diffusion baseline（數字喺截取部分未列）。'),
('2610.02185','LoopCD：training-free contrastive decoding，用 looped transformer 較早一輪嘅預測做「弱模型」同最終預測對比；有 logit 版同零額外輸出開銷嘅 hidden 版。','Apple：loop 本身就提供對齊嘅強弱預測對，唔使額外模型；仲可以減半 loop 數慳 FLOPs。','Abstract 報 Ouro-2.6B-Thinking AIME 2024 pass@1 61.88%→73.33%、Huginn HumanEval 22.56%→31.71%；減半 loops 仍追平或超越，forward FLOPs 少 22.5%–48.2%。'),
('2609.32259','HeteroFold：跨模型家族嘅 prefill-free KV cache 傳遞，對齊結構、映射 sender cache 到 receiver 空間再校準，兩邊模型都凍結。','異質多 agent 系統之間用文字溝通要重複 prefill；直接傳 KV 可以大幅慳延遲。','Abstract 報 32K context 下 Llama-3.1-8B→Ministral-3-14B 比 native prefill 快 10.7 倍、比現有 prefill-free 方法快 1.18–1.47 倍；multi-agent benchmark 追平文字溝通。'),
('2610.00574','DARA：分析 GDPO 下每個 reward 嘅「advantage energy」同 active-group density 成正比，提出 inverse-square-root density 修正，令稀疏 reward 嘅信號唔會被淹沒。','Kuaishou：多 reward RL（例如 tool calling 格式＋正確性）學習進度唔平均嘅一個可解釋修正。','Abstract 報 tool calling 上高格式合規所需步數少最多 26%；數學推理亦有測試。'),
('2610.01016','發現 continuous DLM 用更強 embedding（T5→T5Gemma-1→T5Gemma-2）生成更好，但太 discriminative 會令 diffusion 落喺無效 embedding；於是把 T5Gemma-2 蒸餾成學「解碼機率 soft label」嘅 student encoder，令 latent 空間更連通。','Continuous diffusion LM 嘅 latent 空間設計：「可擴散性」唔等於「可區分性」。','Abstract 報中型 DLM Gen. PPL 17.8（對照數字喺截取部分未完整列出）。'),
]
SYI=['2609.37533','2609.32259x']
SYI=['2609.37533','2609.38987','2609.37362','2609.38585','2610.01108','2609.22753','2609.36435','2610.00964','2609.39687','2609.36820']
OTH=[
('2609.37200','Video & spatial · aff Tencent／HKUST／HKU','Adaptive Reward Routing：喺 joint audio-video diffusion 嘅 forward-process RL（DiffusionNFT）入面，用雙向 cross-attention 反應估計跨模態影響去動態決定更新位置，並以偏好先驗＋梯度互動調整多 reward 權重。','多 reward RL 唔應該用固定 routing 同權重——訓練中途模型功能會變。','Abstract 冇喺截取部分列具體數字；未讀全文。'),
('2610.02162','Video & spatial · aff KAIST','World Observer：將「觀察」同「行動」解耦，同時生成 actor 視角同一個或多個全景 observer，物件離開 actor 視野時仍喺 observer 入面繼續演化；配 Observer Sink 恢復細節。','Video world model 嘅持久性問題（物件離鏡後狀態消失）有新架構解法，並附新 benchmark。','Abstract 稱顯著改善 out-of-view 演化；數字未列。'),
('2609.35690','Robotics · aff NUS','APPL：用每個 policy 嘅結構先驗（例如抓取只取決於夾爪相對物件嘅姿態）做組合同技能之間嘅介面；construction agent 切分示範、提出多個先驗並訓練驗證，runtime agent 選擇組合。','少示範機械人學習：組合泛化同技能泛化之間嘅資訊斷層。','Abstract 冇喺截取部分列數字。'),
('2609.39378','Video & spatial · aff NTU S-Lab、KAIST、PKU（arXiv 作者單位）','EgoTools：100 小時工具使用第一人稱錄影（同步音訊、密集字幕、推理型旁白、3D 資訊）＋1,000 題四軌診斷 benchmark。','多模態影片模型喺「工具使用推理」（affordance、手-工具-物件幾何、程序、因果）仍弱，呢個係首個系統化數據＋評測。','Abstract 稱現有模型明顯不足；數字未列。'),
('2610.01939','Robotics · secondary Agents · aff PKU DAGroup（HF org）','PyRUA-Lean：VLM agent 用 Python cell 組合傳統機械人 primitives 同 VLA policies，做條件檢查同局部重試，只回傳明確要求嘅圖像同狀態。','Robot agent 嘅 token 成本問題：少啲觀察、多啲程式化控制。','Abstract 報 700 個模擬任務、同一 planner 同 LLM-call 預算下成功率 63.1%→71.7%；共同解出嘅任務少 49% LLM calls、65% input tokens。'),
('2610.00559','Multimodal · aff USTC＋ByteDance','PhysVista：以「感知→推理→判斷」閉環評估 VLM 嘅物理智能，分 event-level 同 scale-level，並包含真實同 AI 生成影片。','可以用嚟診斷 VLM 能唔能夠判斷生成影片嘅物理真實度。','Abstract 稱多款 VLM 有明顯限制；數字未列。'),
]
OTHI=[('2610.00812','Video & spatial · survey · 作者含 Stanford／Microsoft／CMU'),('2609.34677','Video & spatial · KAIST＋Sony'),
('2609.34621','Video & spatial · Tencent Hunyuan＋Tsinghua'),('2610.00360','Robotics · PKU'),('2609.37690','Video & spatial · NUS／MIT／Harvard'),
('2610.01595','Video & spatial · KAIST'),('2610.01499','Video & spatial · HKUST(GZ)'),('2610.02202','Other · Stanford／CMU 等'),
('2609.32810','Science & medicine · 作者含 Microsoft'),('2609.34381','Video & spatial · survey/taxonomy · 作者含 Stanford')]
core={'Agents','Reasoning','Systems'}
inc_other={i for i,_,*r in OTH}|{i for i,_ in OTHI}
NS=[i for i,c in CLS.items() if c not in core and i not in inc_other]
REASON={'2610.01762':'affiliation_review · Nanjing University','2609.39027':'needs_verification · arXiv 未列單位','2610.02205':'needs_verification · 單位以圖示呈現（Alaya Lab）',
'2610.02196':'affiliation_review · UIUC','2609.36388':'affiliation_review · Georgia Tech／Zhejiang','2609.39375':'affiliation_review · SNU／NVIDIA',
'2606.10953':'affiliation_review · KAUST','2610.02201':'affiliation_review · UIUC','2610.02160':'affiliation_review · Stability AI／UIUC',
'2609.40362':'affiliation_review · HUST／Horizon Robotics','2610.01092':'affiliation_review · MBZUAI','2610.02148':'affiliation_review · MBZUAI',
'2610.00825':'affiliation_review · Netflix／UMD','2609.38886':'affiliation_review · USTC／Shanghai AI Lab','2610.00348':'affiliation_review · Locai Labs／UCL',
'2610.00686':'affiliation_review · Stability AI／KIT','2609.40222':'affiliation_review · MBZUAI IFM','2610.01428':'affiliation_review · Technion',
'2609.37568':'affiliation_review · HIT／Fudan','2610.00544':'needs_verification · MBZUAI-IFM（HF org）','2610.00737':'affiliation_review · Vanderbilt／Adobe',
'2609.36956':'affiliation_review · USC／Adobe／Amazon','2609.36602':'affiliation_review · Inria','2610.01942':'affiliation_review · Athena RC／valeo.ai',
'2610.02142':'needs_verification · independent researcher','2609.36138':'affiliation_review · UCAS／Birmingham','2609.32019':'needs_verification · arXiv 未列單位',
'2610.02117':'affiliation_review · Valeo.ai／Sorbonne','2610.00483':'affiliation_review · University of Virginia'}
assert set(NS)==set(REASON), (set(NS)^set(REASON))
nAg=sum(1 for c in CLS.values() if c=='Agents'); nRs=sum(1 for c in CLS.values() if c=='Reasoning'); nSy=sum(1 for c in CLS.values() if c=='Systems')
assert len(AG)+len(AGI)==nAg and len(RS)==nRs and len(SY)+len(SYI)==nSy, (nAg,nRs,nSy)
L=[]
L.append("# AI Tracker 晨報｜2026-10-05（一）06:58 HKT\n")
L.append("來源：GitHub Trending daily all-language；Hugging Face Daily Papers API（`/api/daily_papers`）。")
L.append("**HF 日期說明**：今日 `date=2026-10-05` API 回 400（`date must be <= 2026-10-04`）；10-03／10-04（週末）issue 為空；改用最新已發布 issue **2026-10-02（五）**（84 篇，全部 `submittedOnDailyAt`＝2026-10-02；`limit=100` 未觸頂，覆蓋完整）。上一個收集日（10-02）用嘅係 issue 2026-10-01，同今日 issue **無 paper ID 重疊**，全部當新鮮稿。")
L.append("Upvotes／stars today 只係 discovery signal，唔代表品質。論文摘要只根據 abstract，未讀全文。")
L.append("**Repeat skip**：今日 issue 同 10-01、10-02 兩日 eligible 集合都無重疊，skipped_repeat **0**。\n\n---\n")
L.append("## GitHub Trending Top 10\n")
L.append(f"Snapshot：2026-10-05 06:51 HKT · https://github.com/trending?since=daily\n")
L.append(f"官方 daily all-language 頁面可見 **{gh['visible']}** 條；報原排名 **1–10**（唔補位、唔篩 AI）。\n")
L.append("| Rank | Repository | Language | Stars today | 一句用途 |\n| ---: | --- | --- | ---: | --- |")
for r in gh['top10']: L.append(f"| {r['rank']} | [{r['repo']}]({r['url']}) | {r['language']} | {r['stars_today']} | {GHD[r['rank']]} |")
L.append("\n上週五 Top 10 只有 ponytail 仍在榜（由第 1 跌到第 4，stars today 1894 係今日最高）。\n\n---\n")
L.append(f"## Hugging Face Daily Papers（issue 2026-10-02｜fallback）\n")
L.append(f"收錄：核心（Agents {nAg}／Systems & efficiency {nSy}／Reasoning {nRs}）**{nAg+nSy+nRs}** 篇；其他主題（實質貢獻＋allowlist）**{len(OTH)+len(OTHI)}** 篇；未入選／待核實 **{len(NS)}** 篇；skipped_repeat **0**。分類按 contribution；affiliation 來自 HF org 同／或 arXiv HTML 作者單位。核心偏多，重點詳寫＋其餘 index。\n")
L.append("### 核心：Agents\n")
for i,a,b,c in AG: L.append(full(i,a,b,c))
L.append("**其餘核心 Agents（index）**\n"); L+= [idx(i) for i in AGI]; L.append("")
L.append("\n### 核心：Systems & efficiency\n")
for i,a,b,c in SY: L.append(full(i,a,b,c))
L.append("**其餘核心 Systems（index）**\n"); L+= [idx(i) for i in SYI]; L.append("")
L.append("\n### 核心：Reasoning\n")
for i,a,b,c in RS: L.append(full(i,a,b,c))
L.append("\n### 其他值得一提（非核心＋allowlist）\n")
for i,tag,a,b,c in OTH: L.append(full(i,a,b,c,extra=' · '+tag))
L.append("**其他 allowlist（index）**\n"); L+= [idx(i,t) for i,t in OTHI]; L.append("")
L.append(f"\n### 未入選索引\n\n共 **{len(NS)}** 篇（非核心主題未過 allowlist 或單位未核實），唔代表質素低。\n")
L+= [f"- `{i}` {(E[i]['title'][:44]+'…') if len(E[i]['title'])>46 else E[i]['title']} · {CLS[i]} · {REASON[i]}" for i in sorted(NS,key=lambda i:-E[i]['upvotes'])]
L.append("\n**skipped_repeat 索引**：無。\n\n---\n\n*收集完成 · 唔發群；只交 1:1。摘要只根據 abstract。*\n")
open('2026-10-05-weekday-digest.md','w').write('\n'.join(L))
# group shortlist
G=["【群組短訊草稿｜06:58 收集，尚未發到 AI Tracker 群】kickoff 時一次過貼 Papers + GitHub（同一則訊息）。",
"HF note：今日 API 上限 2026-10-04、週末 issue 空，用最新 **2026-10-02**（84 篇）；skipped_repeat 0。\n","**Papers（HF Daily Papers issue 2026-10-02｜fallback）**"]
GS=[('2610.01509','Meta Sharpening Tax：RL post-training 提升 pass@1 但喺 agentic 任務蝕 pass@K 覆蓋，附 PTGS 減稅 sampler。'),
('2609.35259','Cambridge：受控蒸餾實驗顯示 KL 方向同 learning rate 比 on/off-policy 更影響結果。'),
('2609.38923','GraphForge：用真實檔案 evidence graph 合成可驗證 working-agent 任務，GDPVal +65.7。'),
('2610.01415','Alibaba PoS：long-horizon agent 維護顯式 belief state，偵測「belief trapping」再恢復。'),
('2610.00906','Microsoft ActiveSaddler：harness 優化加自適應 curriculum，Terminal-Bench 2.0 Pass@1 +7.5pp。'),
('2610.01215','Tencent AutoGUIWorld：用圖像生成器做 GUI 世界模型合成軌跡，OSWorld 33.0%→40.8%。'),
('2609.32993','X-Tree：仿 tokenizer 由軌跡抽可重用 skill 樹入權重，WebArena／ScienceWorld 有提升。'),
('2609.36585','一個早期層 rank-8 LoRA 令 Qwen3-8B 跟 24 行引用鏈由 15.5% 升到 99%。'),
('2610.02185','Apple LoopCD：looped transformer 前後輪對比解碼，AIME 2024 61.9%→73.3%，可減半 loops。'),
('2609.32259','HeteroFold：跨模型家族 prefill-free KV cache 傳遞，32K context 快 10.7 倍。'),
('2610.02162','KAIST World Observer：actor＋全景 observer 共同生成，物件離鏡後仍持續演化。'),
('2610.01939','PKU PyRUA-Lean：robot agent 用 Python cell 組合 primitives，成功率升、input tokens 少 65%。')]
for i,s in GS: G.append(f"- https://huggingface.co/papers/{i} — {s}")
G.append(f"\n**GitHub Trending（daily all-language；官方頁可見 {gh['visible']} 條，已報 Top 10）**")
for r in gh['top10']: G.append(f"- {r['url']} — {GHD[r['rank']]}")
open('2026-10-05-group-shortlist.md','w').write('\n'.join(G)+'\n')
cur=dict(issue_date='2026-10-02',collect_date='2026-10-05',
 core_agents=[dict(id=i,title=E[i]['title'],upvotes=E[i]['upvotes'],org=E[i]['org'],cat='Agents') for i in [a[0] for a in AG]+AGI],
 core_systems=[dict(id=i,title=E[i]['title'],upvotes=E[i]['upvotes'],org=E[i]['org'],cat='Systems & efficiency') for i in [a[0] for a in SY]+SYI],
 core_reasoning=[dict(id=i,title=E[i]['title'],upvotes=E[i]['upvotes'],org=E[i]['org'],cat='Reasoning') for i in [a[0] for a in RS]],
 other_allowlist=[dict(id=i,title=E[i]['title'],upvotes=E[i]['upvotes'],cat=CLS[i]) for i in [o[0] for o in OTH]+[o[0] for o in OTHI]],
 not_selected=[dict(id=i,title=E[i]['title'],cat=CLS[i],reason=REASON[i]) for i in NS],
 skipped_repeat_ids=[],streak2_prior_ids=[],group_shortlist_ids=[g[0] for g in GS],
 counts=dict(total=84,core_agents=nAg,core_systems=nSy,core_reasoning=nRs,other_allowlist=len(OTH)+len(OTHI),not_selected=len(NS),skipped_repeat=0))
json.dump(cur,open('2026-10-05-papers-curation.json','w'),ensure_ascii=False,indent=1)
print(cur['counts'])

import json,os
os.chdir('/workspace/ai-tracker')
D='2026-10-14'; ISSUE='2026-10-13'; SNAP='2026-10-14 06:52'
ex={r['id']:r for r in json.load(open(f'{D}-papers-extract.json'))['papers']}
gh=json.load(open('/tmp/t/gh.json'))
zh={'morluto/rea':'用 agent 逆向工程任何東西，由 app 行為一路到 native binary。',
'bilawalsidhu/gods-eye-view':'瀏覽器間諜衛星模擬器；真實開源空間情報＋逼真 3D 地球。',
'debpalash/VoiceStudio':'開源、全本地嘅 ElevenLabs 替代：聲音複製／設計、影片配音、聽寫、轉錄同有聲書（標榜 646 種語言）。',
'mksglu/context-mode':'為 AI coding agent 優化 context window：沙盒工具輸出（約減 98%）、保存 session memory，經 MCP＋hooks 喺 17 個平台做 routing。',
'cathrynlavery/diagram-design':'畀 Claude Code／Codex／Copilot／Cursor／Factory Droid／Pi 用嘅編輯風格圖表（44 種，自包含 HTML＋SVG）。',
'vercel-labs/skills':'開源 agent skills 工具（`npx skills`）。',
'lyogavin/airllm':'AirLLM：單卡 4GB GPU 就可做超大模型推理（標榜 2.8T）。',
'storytold/artcraft':'畀藝術家、設計師同電影人用嘅 intentional crafting engine。',
'xtool-org/xtool':'跨平台 Xcode 替代：喺 Linux／Windows／macOS 用 SwiftPM build 同 deploy iOS app。'}
prev={r['full_name']:r['rank'] for r in json.load(open('2026-10-13-github-trending.json'))['repos']}
for r in gh:
    r['owner'],r['name']=r['repo'].split('/'); r['full_name']=r['repo']; r['one_liner_zh']=zh[r['repo']]
    r['rank_2026_10_13']=prev.get(r['repo'])
    r['first_seen_by_tracker_vs_prev_day']=r['repo'] not in prev
N=len(gh)
cov=f"Official page showed only {N} repos; reported all {N} without padding." if N<10 else "Top 10 complete."
dropped=[k for k in prev if k not in {r['repo'] for r in gh}]
json.dump(dict(snapshot_hkt=SNAP+' HKT',source='https://github.com/trending?since=daily',since='daily',spoken_language=None,language_filter='all',visible_count=N,reported_count=N,coverage_note=cov,note_total_stars='total_stars recorded for reference only; not used as stars today',dropped_vs_2026_10_13=dropped,repos=[{k:r[k] for k in ['rank','owner','name','full_name','url','language','stars_today','total_stars','description','one_liner_zh','rank_2026_10_13','first_seen_by_tracker_vs_prev_day']} for r in gh]),open(f'{D}-github-trending.json','w'),ensure_ascii=False,indent=2)
def lang(x): return x or '未顯示'
ghtable=["| Rank | Repository | Language | Stars today | 一句用途 |","| ---: | --- | --- | ---: | --- |"]+[f"| {r['rank']} | [{r['repo']}]({r['url']}) | {lang(r['language'])} | {r['stars_today'] if r['stars_today'] is not None else '未知'} | {r['one_liner_zh']} |" for r in gh]
newones=[r['repo'] for r in gh if r['first_seen_by_tracker_vs_prev_day']]
ghhead=[f"Snapshot：**{SNAP} HKT** · https://github.com/trending?since=daily（daily、all-language）",
f"官方頁可見 **{N}** 條；報原排名 **1–{N}**（唔補位、唔篩 AI）。Stars today 只係 discovery signal。",
f"**覆蓋限制**：{cov}"]
ghdelta=f"對比 2026-10-13 snapshot：新上榜（本 tracker 角度）{'、'.join('`'+x+'`' for x in newones)}；跌出 {'、'.join('`'+x+'`' for x in dropped)}。First seen 只代表本 tracker 首次見，唔代表新 repo。"
open(f'{D}-github-trending.md','w').write(f"# GitHub Trending Top {N}｜{D}\n\n"+"\n".join(ghhead)+"\n\n"+"\n".join(ghtable)+"\n\n"+ghdelta+"\n")

# ---------- HF curation ----------
E=[ # id, cat, secondary, delta, why, evidence, org_label, detail_in_digest
('2610.11765','Reasoning',[],'唔再用「關咗 thinking mode／冇長 trace」做 proxy；將回應拆成 pre-answer trace＋最終答案，用 Empty-Thinking Rate、Question-Pre-answer Relevance、LLM-judge Explicit Inference Rate 三層量度 no-thinking。','好多模型賣 thinking／no-thinking 切換；叫佢唔好諗佢照諗，成本、延遲同格式控制就唔可靠。','6 種 prompting 介入 × 6 個 LLM × Boolean／選擇／開放題：explicit no-think 控制消除唔到可見推理（"Thinking Inertia"），答案空間愈開放愈明顯；開放題出現 answer-only 合規 vs 準確率 trade-off。限制：Explicit Inference Rate 靠 LLM-as-judge；只根據 abstract。','Stanford University',True),
('2610.13832','Reasoning',['Video & spatial','Multimodal'],'訓練時做空間模擬：allocentric novel-view generator 生成假想視角，產出 (i) explicit ASM 軌跡，教 LVLM 幾時／點樣主動規劃視角同想像；(ii) 自動構建 perspective-taking 任務。','人解空間題會「換個角度喺腦入面重建」；LVLM 呢種 active mentalization 仲弱，空間 CoT 監督亦稀缺。','4 個 LVLM backbone、7 個空間 benchmark 平均準確率有升，同時保留一般視覺能力；abstract 冇列具體分數。分類邊界：亦可歸 Video & spatial，以「推理過程訓練」為主歸 Reasoning。只根據 abstract。','Shanghai AI Laboratory',True),
('2610.13481','Reasoning',['Agents','Systems & efficiency'],'用學生不確定性＋師生分歧揀關鍵決策點，由共享 prefix 分支重抽學生 continuation，主軌跡同分支都做 token-level teacher 監督；另加 protocol-boundary repair（PBR）減重複同浪費生成。','OPD 每條軌跡每個決策只見一個 continuation，有限 sampling 預算下監督覆蓋窄。','共享 prefix 相對 7 條獨立軌跡慳學生 token 約 19%（ALFWorld）／31%（WebShop）；比 Vanilla OPD 數學 avg@16 高 18.55 pt、ALFWorld ID/OOD 成功率高 13.8 pt。限制：HF 頁冇 code link；org 欄係自名 "BranchOPD"，作者機構未核實；只根據 abstract。','BranchOPD（HF org 自名，機構未核實）',True),
('2610.12933','Reasoning',['Systems & efficiency'],'唔把 teacher CoT 當單一路徑；圍住中間推理狀態建 Monte Carlo reasoning tree 量 process-level 不確定性，兩階段收縮：先縮 corpus 成 teacher-informed pool，再喺 SFT 按學生學習狀態 online routing。','Reasoning post-training 靠堆語料，成本飆但回報遞減。','聲稱最少只用 full-data SFT 0.22% 優化預算（>450x 少 training exposure），推理表現持平或更好；跨學生家族、黑盒 teacher、weak-to-strong 都 generalize。限制：abstract 冇講建 MC tree 本身嘅額外成本；只根據 abstract。','Nanjing University',True),
('2610.13361','Agents',[],'測 coding agent「幫用戶起 agent」：25 個任務覆蓋 Creation／Editing／Optimization 三個 agent 開發階段；builder 只見少量示例，驗收用 held-out cases＋requirement rubrics 硬 pass/fail（Optimization 用原 benchmark 目標）。','越來越多人叫 coding agent 起 agent；「示範 work」唔等於「真係滿足需求」，之前冇 benchmark 測呢個假設。','跨模型同 harness，冇一個接近交付需求；failure trajectory 分析：overfit 可見例子、hollow runtime（code 似完整但空殼）、虛報完成。限制：只 25 題；HF 頁冇 code link；organization 欄空（affiliation 未核實）；只根據 abstract。','空（needs_verification；核心主題免 gate）',True),
('2610.13166','Agents',['Reasoning'],'全自動長程 terminal agent 數據合成引擎 TerminalHorizon：由真實專業工作出發，用獨立執行揪出環境構建時被「預先做咗」嘅關鍵工作，據證據重建環境；同一目標下逐步擴展任務、疊加新要求。','短軌跡示範唔到 agent 點累積證據、調整策略、交付成果；環境合成又好易簡化咗本應由 agent 做嘅探索／實作／驗證。','建 1.5K 任務環境，SFT Qwen3.5-27B 得 TerminalHorizon-27B；12 個 benchmark（coding agent、真實生產 agentic、一般推理）全部明顯提升；另有多個 12 小時 RSI case study。限制：abstract 冇列具體分數；HF 頁冇 code link；只根據 abstract。','Alibaba（HF org: alibaba）',True),
('2609.33304','Agents',[],'「相關≠適用」：檢索歷史主要只幫第一步；改為 training-free 嘅 experience activation（ExpActivator）——喺凍結 GUI backbone latent space 將每個新畫面對應歷史狀態、提供動作參考；主動建議只喺時間／情境支持足夠時先觸發，否則 abstain。','個人 GUI agent 靠歷史推斷模糊指令同例行公事，但直接塞歷史入 context 浪費 token，對其餘 90% 步驟幫助有限。','4 個 GUI backbone 平均 within-trajectory step success +28%；history tokens 約用五分一；proactive MCC 約 2.3x 最強 baseline。只根據 abstract。','Nanyang Technological University',True),
('2609.36642','Agents',['Reasoning'],'發現 skill in context 令 WebShop 成功率 42.2%→56.2%，但只改 <1/4 sampled token 機率、卻改 >80% response token 隱狀態；所以 GRPO warm start 後，policy 為每條軌跡寫 hindsight skill，以 stop-gradient teacher 身份重讀，逐層對齊 projected hidden states。','Agent RL 每 episode 一個 reward 太稀疏；privileged self-distillation 只靠 token 機率做通道會漏大部分訊號。','ALFWorld／WebShop、兩個 backbone 全部設定最佳；比 GRPO ALFWorld 成功率最多 +4.7、WebShop 準確率 +14.0；無外部 skill library／teacher／推理開銷。限制：organization 欄空（affiliation 未核實）；只根據 abstract。','空（needs_verification；核心主題免 gate）',True),
('2609.35965','Agents',['Robotics','Video & spatial'],'首次系統化將 multi-agent VLN 形式化為帶 dependency／resource constraints（presence locks、holding chains）嘅協調問題；MAVLN：11,724 episodes／145 場景／最多 4 agent／3 種指令設定；TRISS baseline：LLM subtask scheduler＋共享拓撲記憶＋conflict-aware 執行。','單 agent 單指令嘅 VLN 唔夠覆蓋要機械人團隊合作嘅真實任務。','TRISS 做 comprehensive baseline，但排程／規劃／執行仍有大空間；abstract 冇具體分數。分類邊界：亦可歸 Robotics，以多 agent 協調為主歸 Agents。只根據 abstract。','Shanghai Jiao Tong University',True),
('2610.00707','Agents',['Science & medicine'],'概括 12 個 discovery harness（"Modular"）× 5 個任務；指出 mode collapse（iterate 多樣性急跌）係常見失敗；提出先做一輪平行探索，再初始化後續迭代優化。','LLM 做演算法／定理／藥物 discovery 高度依賴 harness，但成功好脆弱。','早期發現表現可預測最終成功；初始化介入喺多 harness／應用都有一致增益，而流行 SOTA harness 同 diversity 介入增益唔穩定。限制：abstract 冇具體數字；只根據 abstract。','Vector Institute',False),
('2610.02740','Agents',['Reasoning'],'喺任何 retrospective RL 方法上加「預測 vs 現實」surprise 訊號：同 policy 共享參數嘅 prospective predictor 喺 feedback 前預測，stop-gradient surprise-weighted advantage 放大自我模型最唔準嘅樣本；校準成為優化副產品。','長程 agent RL 只喺事後分配 credit，行動當刻嘅 belief 唔入 gradient。','單輪可驗證任務＋多輪 personal-agent 任務（GRPO／OPD／兩者結合）表現同校準都改善、跨模型規模一致；單輪偏 overconfident failure、多輪偏 underconfident success，同一原則都處理到。限制：HF 頁冇 code link；只根據 abstract。','Salesforce AI Research',False),
('2610.09116','Agents',['Video & spatial'],'Multi-agent paper-to-code：gsplat context-free grammar＋模組化模板約束合成；fork-aware citation recovery、Graph-of-Thought 依賴順序合成、RAG 範例、PSNR／結構檢查／VLM 視覺反饋修補；再做組合式改進同跨領域方法發現。','3DGS 論文量大，重現要大量人手；通用 paper-to-code 同 frontier model 喺呢度失敗。','SPLATIFY-Bench 30 篇；冇公開 code 嘅論文上追平專家實作，開發時間由幾星期變幾分鐘；組合式發現 PSNR 最多 +2.4 dB。限制：領域限於 3DGS；只根據 abstract。','University of California at San Diego',False),
('2610.13630','Systems & efficiency',[],'將 Attention Residuals（沿深度嘅單 stream softmax attention）推廣成 multi-head depth attention：多尺度 causal conv 由序列上下文帶出 stream 多樣性，輕量 adaptive mixing 合返單 stream 輸入；毋須持久多 stream 儲存或通訊。','Residual 結構係大規模 pretraining 基本件；細開銷換 compute 效率直接影響訓練成本。','18B／28B MoE 規模 12 個下游 benchmark 一致勝 standard residual、mHC、AttnRes；scaling-law iso-loss compute speedup 1.58x（AttnRes 1.35x、mHC 1.30x）。分類：架構／訓練效率，歸 Systems & efficiency（同過往 latent recurrence／MoE training 做法一致）。只根據 abstract。','Shanghai Jiao Tong University',True),
('2610.09326','Video & spatial',['Multimodal'],'將 contextual grounding 形式化為「異質輸入 → 可執行約束模型」：Structured Context Abstraction 恢復 grounded states／跨 context 依賴，Generation Constraints Induction 投射成候選約束，Constrained Video Generation 用 planning／verification／revision／rendering 落實。','互動式影片敘事中觀眾請求有隱含依賴（來源＋已渲染歷史＋新意圖），淨跟指令或淨對齊來源都唔夠。','3 個影片生成 backbone 都拎最高 composite score，平均比各 backbone 最強 baseline 高 10.3 分；作者自認依賴抽取同渲染忠實度仍有挑戰。只根據 abstract。','Google（allowlisted）',True),
]
NS=[('2609.39601','Multimodal',['Robotics'],'XPENG AI','affiliation_review','4B grounding foundation model（points/boxes 量化座標），34 個 grounding benchmark 平均 73.68%；upvotes 246 全日最高，但非核心＋非 allowlist'),
('2609.39600','Multimodal',['Systems & efficiency'],'XPENG AI','affiliation_review','Diffusion 平行解碼 grounding 模型（self-speculative 4.51x speedup）；主貢獻係 grounding 模型，唔為過門檻硬歸 Systems'),
('2609.36616','Multimodal',['Video & spatial'],'Sun Yat-Sen University','affiliation_review','十年跨視角歷史街景數據集 VIGOR-his＋reward-guided 編輯'),
('2610.03308','Video & spatial',[],'Preferred Networks, Inc.','affiliation_review','任意解析度生成式表面重建（coarse-to-fine cascade）'),
('2610.09396','Other',[],'Megagon Labs','affiliation_review','Text-to-SQL 歧義 benchmark ARCS'),
('2610.05637','Safety & analysis',['Multimodal'],'Apple','affiliation_review','VLM grounding 輸出通道嘅安全對齊落差（refusal 落後 VQA 31–59 pt）；Apple 唔喺 allowlist'),
('2610.12998','Safety & analysis',[],'University of Chicago','affiliation_review','以 long-tail 表現評 LLM 創意（15 benchmark、26 模型）'),
('2610.03825','Safety & analysis',[],'Centific Applied AI Research','affiliation_review','換 reference gold 令多語 benchmark 分數郁 4.95 F1'),
('2610.12099','Robotics',[],'Chinese University of Hong Kong, Shenzhen','affiliation_review','3D-native world action model UNITAS'),
]
CORE={'Reasoning','Agents','Systems & efficiency'}
short=['2610.11765','2610.13361','2610.13166','2610.09326','2610.13630','2609.33304','2610.12933','2610.13481']
skip=[]
cur=[]
for i,c,sec,dl,why,ev,org,det in E:
    r=ex[i]
    cur.append(dict(id=i,title=r['title'],category=c,secondary=sec,core=c in CORE,eligible=True,
      eligible_reason='core topic (1/2/5) — no affiliation gate' if c in CORE else 'non-core: substantive contribution + allowlisted affiliation (Google)',
      affiliation_status=('allowlisted' if c not in CORE else ('not_required_core' )),organization_field=r['organization'],org_label=org,
      upvotes=r['upvotes'],hf_url=r['hf_url'],arxiv_url=r['arxiv_url'],code=r['github_repo'],project_page=r['project_page'],
      skip_repeat=False,in_shortlist=i in short,detail_in_digest=det,method_delta_zh=dl,why_zh=why,evidence_limits_zh=ev,abstract_only=True))
for i,c,sec,org,st,note in NS:
    r=ex[i]
    cur.append(dict(id=i,title=r['title'],category=c,secondary=sec,core=False,eligible=False,eligible_reason=f'non-core; affiliation gate not met ({st})',affiliation_status=st,organization_field=r['organization'],upvotes=r['upvotes'],hf_url=r['hf_url'],arxiv_url=r['arxiv_url'],code=r['github_repo'],skip_repeat=False,in_shortlist=False,note_zh=note))
assert len(cur)==len(ex)==23 and set(x['id'] for x in cur)==set(ex)
elig=[x for x in cur if x['eligible']]
from collections import Counter
bycat=dict(Counter(x['category'] for x in elig))
counts=dict(extract=len(ex),eligible=len(elig),eligible_by_cat=bycat,not_selected=len(cur)-len(elig),skipped_repeat=0,shortlist=len(short))
fallback=f"date={D} → 400 (API ceiling {ISSUE}); use newest published issue {ISSUE} with limit=100 → 23 papers (complete; < limit). All 23 IDs are new vs every prior tracker digest/shortlist."
json.dump(dict(collect_date=D,hf_issue_date=ISSUE,hf_date_fallback_note=fallback,counts=counts,shortlist_ids=short,eligible_ids=[x['id'] for x in elig],skipped_repeat_ids=[],not_selected_ids=[x['id'] for x in cur if not x['eligible']],papers=cur),open(f'{D}-papers-curation.json','w'),ensure_ascii=False,indent=1)

# repeat skip history
hist=dict(collect_date=D,most_recent_prior_collect='2026-10-13',prior_collect_days=['2026-10-08','2026-10-09','2026-10-12','2026-10-13'],
 weekend_gap_note='2026-10-10 and 2026-10-11 are weekend; weekend gaps do NOT break streak.',
 rule='Papers eligible-reported on ≥2 consecutive prior weekday collect days (ending at most recent prior collect day) are skip_today. HF only; not GitHub.',
 sources_checked=['2026-10-13-repeat-skip-history.json','2026-10-13-papers-curation.json','2026-10-12-papers-curation.json','2026-10-09-papers-curation.json','2026-10-0{8,9}/10-1{2,3} weekday-digest.md / hf-daily-papers.md / group-shortlist.md (regex huggingface.co/papers/<id>)','all /workspace/ai-tracker/2026-*.md (any prior mention)'],
 eligible_counts_prior={'2026-10-12':13,'2026-10-13':46},
 today_issue=ISSUE,today_issue_overlap_with_2026_10_13=0,today_issue_overlap_with_2026_10_12=0,today_issue_overlap_with_2026_10_09=0,today_issue_overlap_with_2026_10_08=0,today_issue_overlap_with_any_prior_md=0,
 streaks_today={x['id']:0 for x in elig},skip_today_ids=[],skip_today_count=0,eligible_ids_today=[x['id'] for x in elig],
 next_day_note='If any of today\'s eligible IDs reappear tomorrow (2026-10-15) they will have streak 1 → still reportable; skip starts only after 2 consecutive reported days.')
json.dump(hist,open(f'{D}-repeat-skip-history.json','w'),ensure_ascii=False,indent=2)

fm=dict(collect_date=D,requested_dates={D:dict(http=400,error='date must be <= 2026-10-13T00:00:00.000Z',file=f'{D}-raw-daily-papers-{D}.json'),
 ISSUE:dict(http=200,count_default=23,count_limit100=23,files=[f'{D}-raw-daily-papers-{ISSUE}.json',f'{D}-raw-daily-papers-issue-{ISSUE}-limit100.json'],note='identical ID sets'),
 '2026-10-12':dict(http=200,count_limit100=60,note='unchanged vs yesterday (already reported 2026-10-13)'),
 'default(no date, limit=100)':dict(http=200,count=100,by_submittedOnDailyAt={'2026-10-13':23,'2026-10-12':60,'2026-10-09':17},file=f'{D}-raw-daily-papers-default-limit100.json')},
 api_ceiling=ISSUE,issue_date_used=ISSUE,fallback_reason=f'date={D} → 400 (ceiling {ISSUE}); use newest published issue {ISSUE}',extract_count=23,limit=100,
 coverage_note='23 < limit → full issue as of fetch; issue may still accrue late submissions during the day.',fetched_at_hkt='2026-10-14 06:52–06:55')
json.dump(fm,open(f'{D}-hf-fetch-meta.json','w'),ensure_ascii=False,indent=2)

def secs(x): return ('· secondary：'+'／'.join(x['secondary'])) if x['secondary'] else ''
def links(x):
    s=f"[HF]({x['hf_url']}) · [arXiv]({x['arxiv_url']})"
    if x.get('code'): s+=f" · [code]({x['code']})"
    if x.get('project_page'): s+=f" · [project]({x['project_page']})"
    return s
def block(x):
    return (f"**[{x['title']}]({x['hf_url']})** · upvotes {x['upvotes']} · org {x['org_label']} {secs(x)}".rstrip()+"\n"
      f"- 方法 delta：{x['method_delta_zh']}\n- 點解值得睇：{x['why_zh']}\n- 證據／限制：{x['evidence_limits_zh']}\n- 連結：{links(x)}\n")
idxline={'2610.00707':'Initialization（Vector Institute）：LLM discovery harness 常見 mode collapse；先平行探索再初始化迭代，跨 12 個 harness 一致有增益。',
'2610.02740':'Prospective Hindsight（Salesforce）：用「行動前預測 vs 事後評估」surprise 加權 advantage，長程 agent RL 同時改善表現同校準。',
'2610.09116':'SPLATIFY（UCSD）：multi-agent 將 3DGS 論文轉成可訓練 gsplat code，追平專家實作、組合發現 PSNR 最多 +2.4 dB。'}
order=['Agents','Reasoning','Systems & efficiency']
def hfsections(full):
    out=[]
    for c in order:
        xs=sorted([x for x in elig if x['category']==c],key=lambda x:-x['upvotes'])
        out.append(f"### {c}\n")
        det=[x for x in xs if full or x['detail_in_digest']]; idx=[x for x in xs if not(full or x['detail_in_digest'])]
        out+= [block(x) for x in det]
        if idx:
            out.append("**Index**\n")
            out+= [f"- [{x['title']}]({x['hf_url']}) — {idxline[x['id']]}" for x in idx]
            out.append("")
    out.append("### 其他值得一提（非核心＋allowlist）\n")
    out+= [block(x) for x in elig if not x['core']]
    out.append("### 未入選\n")
    for x in cur:
        if not x['eligible']:
            out.append(f"- [{x['title']}]({x['hf_url']})（`{x['id']}`）— {x['category']}；{x['organization_field']} → {x['affiliation_status']}；{x['note_zh']}")
    out.append("\n### skipped_repeat\n\n無（0）。今日 issue 23 篇與 10-08／10-09／10-12／10-13 任何已報 ID 0 重疊。\n")
    return "\n".join(out)
bc=bycat
hfhead=(f"**日期／覆蓋**：`date={D}` → 400（API ceiling **{ISSUE}**），用最新已發佈 issue **{ISSUE}**；`limit=100` → **23** 篇（少過 limit，即係 fetch 時全集；當日可能仲有遲交稿）。入選 **{len(elig)}**（Agents {bc.get('Agents',0)}／Reasoning {bc.get('Reasoning',0)}／Systems {bc.get('Systems & efficiency',0)}／其他 {len(elig)-bc.get('Agents',0)-bc.get('Reasoning',0)-bc.get('Systems & efficiency',0)}）；未入選 **{len(cur)-len(elig)}**；skipped_repeat **0**。\n"
"分類按 contribution；affiliation 只取 API organization 欄，唔發明。核心主題 1／2／5 免 affiliation gate；其他主題要實質貢獻＋allowlist。今日 issue 細（23 篇），非核心大部分係 affiliation_review。\n")
open(f'{D}-hf-daily-papers.md','w').write(f"# Hugging Face Daily Papers｜collect {D}（issue {ISSUE}）\n\n來源：`https://huggingface.co/api/daily_papers?date={ISSUE}&limit=100`。Upvotes 只係 discovery signal。**只根據 abstract，未讀全文。**\n\n"+hfhead+"\n"+hfsections(True))

digest=(f"# AI Tracker 晨報｜{D}（三）\n\n"
"來源：GitHub Trending daily all-language；Hugging Face Daily Papers API（`/api/daily_papers`）。\n"
f"**HF 日期說明**：`date={D}` API 回 **400**（ceiling **{ISSUE}**）。今日用 issue **{ISSUE}**，`limit=100` → **23** 篇（issue 細過平日；fetch 時已係全集）。\n"
"Upvotes／stars today 只係 discovery signal，唔代表品質。論文摘要只根據 abstract，未讀全文。\n"
"**Repeat skip**：skipped_repeat **0**（23 篇與 10-08／10-09／10-12／10-13 已報 ID 全部 0 重疊；streak≥2 今日無）。\n"
f"**同 API 增量**：尋日 digest 用 issue 2026-10-12（60 篇，今日重抓數目不變）；今日 ceiling 升到 **{ISSUE}**，23 篇 **全部新可見**。\n\n---\n\n"
f"## GitHub Trending Top {N}\n\n"+"\n".join(ghhead)+"\n\n"+"\n".join(ghtable)+"\n\n"+ghdelta+"\n\n---\n\n"
f"## Hugging Face Daily Papers（issue {ISSUE}）\n\n"+hfhead+"\n"+hfsections(False))
open(f'{D}-weekday-digest.md','w').write(digest)

sl1={'2610.11765':'Thinking Inertia（Stanford）：叫 LLM「唔好諗」佢照諗——6 模型 × 6 種 no-think 控制都消除唔到可見推理，開放題最明顯。',
'2610.13361':'AgentSWE：測 coding agent 幫用戶「起 agent」——25 個 held-out 驗收任務，冇一個 agent 接近真正交付需求。',
'2610.13166':'TerminalHorizon（阿里）：自動合成 1.5K 長程 terminal 任務環境，SFT Qwen3.5-27B 後 12 個 benchmark 全面提升。',
'2610.09326':'VIS-Ground（Google）：互動式影片敘事將異質 context 變成可執行約束，3 個 backbone 平均比最強 baseline 高 10.3 分。',
'2610.13630':'MSAR（上交）：把 Attention Residuals 擴成 multi-stream 深度 attention，18B／28B MoE 上 iso-loss compute speedup 1.58x。',
'2609.33304':'ExpActivator（NTU）：個人 GUI agent「相關≠適用」——按畫面啟動適用經驗，step success +28%、history token 約五分一。',
'2610.12933':'Uncertainty-guided contraction（南大）：用 MC 推理樹揀最有價值 CoT，最少 0.22% SFT 預算維持或提升推理。',
'2610.13481':'BranchOPD：喺不確定決策點分支做 on-policy distillation，數學 avg@16 比 Vanilla OPD 高 18.55 pt。'}
ghshort={'morluto/rea':'用 agent 逆向工程任何東西，由 app 行為一路到 native binary。',
'bilawalsidhu/gods-eye-view':'瀏覽器間諜衛星模擬器；真實開源空間情報＋逼真 3D 地球。',
'debpalash/VoiceStudio':'開源全本地 ElevenLabs 替代：聲音複製、配音、轉錄同有聲書。',
'mksglu/context-mode':'為 AI coding agent 優化 context window：沙盒工具輸出（約減 98%）＋session memory。',
'cathrynlavery/diagram-design':'畀 Claude Code／Codex／Cursor 等用嘅編輯風格圖表（44 種，HTML＋SVG）。',
'vercel-labs/skills':'Vercel Labs 開源 agent skills 工具（`npx skills`）。',
'lyogavin/airllm':'AirLLM：單卡 4GB GPU 做超大模型推理（標榜 2.8T）。',
'storytold/artcraft':'畀藝術家、設計師同電影人用嘅 intentional crafting engine。',
'xtool-org/xtool':'跨平台 Xcode 替代：Linux／Windows／macOS 用 SwiftPM build 同 deploy iOS app。'}
sl=(f"【群組短訊草稿｜{D}，尚未發到 AI Tracker 群】\n**唔好自行貼出**——等 Johnny／AI Tracker Orchestrator kickoff 先發。\n"
"kickoff 時必須 **Papers + GitHub 同一則訊息**（先 Papers 後 GitHub）；唔好拆兩則。\n"
f"HF note：`date={D}`→400，用 issue **{ISSUE}**（23 篇，全部新可見）；skipped_repeat 0。\n"
f"GitHub note：snapshot **{SNAP} HKT**；官方頁只有 **{N}** 條，報齊 1–{N}（唔補位）。\n\n"
f"**Papers（HF Daily Papers issue {ISSUE} · 高訊號）**\n"+"\n".join(f"- https://huggingface.co/papers/{i} — {sl1[i]}" for i in short)+
f"\n\n**GitHub Trending（daily all-language；官方頁 {N}/10｜{SNAP} HKT）**\n"+"\n".join(f"- {r['url']} — {ghshort[r['repo']]}"+("（今日 stars 最高 "+str(r['stars_today'])+"）" if r['stars_today']==max(g['stars_today'] for g in gh) else "") for r in gh)+"\n")
open(f'{D}-group-shortlist.md','w').write(sl)

P={k:f'/workspace/ai-tracker/{D}-{v}' for k,v in dict(papers_extract='papers-extract.json',papers_curation='papers-curation.json',hf_daily_papers='hf-daily-papers.md',weekday_digest='weekday-digest.md',group_shortlist='group-shortlist.md',github_trending_md='github-trending.md',github_trending_json='github-trending.json',github_trending_html='github-trending.html',repeat_skip_history='repeat-skip-history.json',hf_fetch_meta='hf-fetch-meta.json',meta='meta.json').items()}
meta=dict(collect_date=D,weekday='Wednesday',timezone='Asia/Hong_Kong',
 hf=dict(requested_date=D,api_status=400,issue_date_used=ISSUE,fallback_reason=f'API ceiling {ISSUE}; date={D} → 400',extract_count=23,limit=100,newly_visible=23,eligible=len(elig),eligible_by_cat=bycat,not_selected=len(cur)-len(elig),skipped_repeat=0,shortlist_count=len(short)),
 github=dict(snapshot_hkt=SNAP,source='https://github.com/trending?since=daily',visible_count=N,reported_ranks=f'1-{N}',coverage=f'{N}/10',note=cov),
 paths=P,artifacts_written_hkt='2026-10-14 ~06:58')
json.dump(meta,open(f'{D}-meta.json','w'),ensure_ascii=False,indent=2)
open('last_run_meta.txt','w').write(f"date={D} status=ok github={N} hf_issue={ISSUE} eligible={len(elig)} skipped_repeat=0 shortlist={len(short)}\n")
print(counts)

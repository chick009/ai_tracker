import json,os,sys,urllib.request,concurrent.futures as cf
KEY=os.environ['JEV_API_KEY']
CRIT={"agents":"LLM/VLM agents, tool use, computer-use or mobile agents, agent benchmarks, agentic RL","reasoning":"Reasoning methods, RL post-training for reasoning, self-improvement","systems":"Inference/training efficiency, speculative decoding, model architecture, serving","robotics":"Robot policies, embodied control, navigation","video_spatial":"Video generation, 3D, spatial understanding, world models","multimodal":"Image/audio generation, VLM perception, retrieval","analysis_safety":"Interpretability, safety, alignment, analysis","science":"Science or medicine application, research hypotheses","other":"Anything else"}
CORE={"agents","reasoning","systems"}
def ask(r):
    body={"model":"jev-latest","state":f"Title: {r['title']}\nAbstract: {r['abstract']}","questions":{"topic":{"type":"choice","instructions":"Pick the paper's MAIN contribution topic (what the paper mainly contributes, not just what it mentions)","criteria":CRIT}}}
    req=urllib.request.Request("https://api.typesafe.ai/v1/systemone",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+KEY,"Content-Type":"application/json"})
    for _ in range(3):
        try:
            a=json.load(urllib.request.urlopen(req,timeout=60))["answers"]["topic"]
            return dict(id=r['id'],choice=a['choice'],conf=a['confidence'],probs=a['probabilities'])
        except Exception as e: err=str(e)
    return dict(id=r['id'],choice=None,err=err)
rows=json.load(open('step1.json'))
res=list(cf.ThreadPoolExecutor(8).map(ask,rows))
mine={r['id']:r['topic'] for r in json.load(open('step2.json'))}
json.dump(res,open('step2_jev.json','w'),indent=1)
up={r['id']:(r['upvotes'],r['title']) for r in rows}
agree=0;diff=[]
for x in res:
    jc=x['choice'] in CORE; mc=x['id'] in mine
    if jc==mc: agree+=1
    else: diff.append((up[x['id']][0],x['id'],up[x['id']][1][:60],'me:'+(mine.get(x['id']) or 'drop'),'jev:'+str(x['choice']),round(x.get('conf',0),2)))
print('jev core kept',sum(x['choice'] in CORE for x in res),'me',len(mine),'agree keep/drop',agree,'/50')
for d in sorted(diff,reverse=True): print(d)
low=[(x['id'],x['choice'],x['conf']) for x in res if x.get('conf',1)<0.6]; print('low conf',low)
jk=sorted([x for x in res if x['choice'] in CORE],key=lambda x:-up[x['id']][0])[:12]
mk=json.load(open('step3_top12.json'))
print('top12 overlap',len({x['id'] for x in jk}&{r['id'] for r in mk}))
print('jev top12',[(x['id'],up[x['id']][0]) for x in jk])

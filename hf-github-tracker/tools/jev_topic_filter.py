import json,os,urllib.request,concurrent.futures as cf
KEY=os.environ['JEV_API_KEY']
INSTR=("Classify this AI paper by its MAIN contribution: the thing the paper builds or proves, not words in its title. "
"Judge by what is new. 'Agentic' or 'explore' in a title does not make it an agents paper. "
"If the contribution is about how an AI agent acts over many steps in an environment (tools, computer, phone, code repo, web, research workflow, multi-agent teams), choose agents. "
"If it is about 3D, spatial, video, or world models (even when a VLM explores a scene), choose video_spatial. "
"If it is a domain application (music, peer review, medicine, science discovery not about agent design), pick that domain, not systems.")
CRIT={
"agents":"Builds, trains, evaluates, or diagnoses LLM/VLM agents acting over multiple steps: computer-use, mobile, coding/SWE, web, research agents, agent memory/context, multi-agent systems and their failures, agent benchmarks, agentic RL.",
"reasoning":"Improves or analyses step-by-step reasoning of language models: chain-of-thought, RL for reasoning, test-time thinking, self-evolving reasoners. Not general distillation or output supervision.",
"systems":"Makes LLM training or inference faster/cheaper or changes LM architecture: speculative decoding, quantization, embeddings/vocab size, looped or layer-connection architectures, serving, sampling speedups.",
"robotics":"Robot manipulation, embodied policies, robot navigation, world-action models for robots.",
"video_spatial":"Video generation or video world models, 3D scenes, spatial reasoning or 3D exploration by VLMs, Gaussian/3D reconstruction, 3D scene design.",
"multimodal":"Image or audio-video generation, VLM perception/binding, multimodal retrieval, unified multimodal models.",
"analysis_safety":"Interpretability of model internals, safety/alignment, refusing harmful instructions, measuring belief/prediction trajectories.",
"science":"Science or medicine applications, automating scientific hypotheses or discovery methods not centred on agent design.",
"other":"Anything else: music/audio transcription, peer-review fact-checking, general LM distillation methods, datasets for other domains."}
CORE={"agents","reasoning","systems"}
def ask(r):
    body={"model":"jev-latest","state":f"Title: {r['title']}\nAbstract: {r['abstract']}","questions":{"topic":{"type":"choice","instructions":INSTR,"criteria":CRIT}}}
    req=urllib.request.Request("https://api.typesafe.ai/v1/systemone",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+KEY,"Content-Type":"application/json"})
    for _ in range(3):
        try:
            a=json.load(urllib.request.urlopen(req,timeout=60))["answers"]["topic"]
            return dict(id=r['id'],choice=a['choice'],conf=a['confidence'],probs=a['probabilities'])
        except Exception as e: err=str(e)
    return dict(id=r['id'],choice=None,err=err)
rows=json.load(open('step1.json'))
res=list(cf.ThreadPoolExecutor(8).map(ask,rows))
json.dump(res,open('step2_jev_v2.json','w'),indent=1)
mine={r['id']:r['topic'] for r in json.load(open('step2.json'))}
up={r['id']:(r['upvotes'],r['title']) for r in rows}
diff=[(up[x['id']][0],x['id'],up[x['id']][1][:55],'me:'+(mine.get(x['id']) or 'drop'),'jev:'+str(x['choice']),round(x.get('conf',0),2)) for x in res if (x['choice'] in CORE)!=(x['id'] in mine)]
print('jev kept',sum(x['choice'] in CORE for x in res),'me',len(mine),'agree',50-len(diff),'/50')
for d in sorted(diff,reverse=True): print(d)
print('low conf',[(x['id'],x['choice'],x['conf']) for x in res if x.get('conf',1)<0.6])
jk=sorted([x for x in res if x['choice'] in CORE],key=lambda x:-up[x['id']][0])[:12]
mk={r['id'] for r in json.load(open('step3_top12.json'))}
print('top12 overlap',len({x['id'] for x in jk}&mk), 'jev-only',[x['id'] for x in jk if x['id'] not in mk])

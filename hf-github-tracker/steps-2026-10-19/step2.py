import json
core={ # id: topic  (judged from title+abstract)
'2610.18784':'Agents','2610.23479':'Agents','2610.20424':'Agents','2610.19159':'Agents','2610.14157':'Agents','2610.21767':'Agents','2610.20556':'Systems','2610.23181':'Agents','2610.23787':'Systems','2610.23194':'Agents','2610.21082':'Agents','2610.22234':'Agents','2610.17184':'Agents','2610.16071':'Agents','2610.09872':'Agents','2610.22428':'Systems','2610.23036':'Systems','2610.18834':'Reasoning','2610.18082':'Agents','2610.07898':'Agents','2610.21073':'Agents','2610.20951':'Reasoning','2610.19625':'Systems','2610.22029':'Reasoning','2610.20503':'Systems','2610.20628':'Agents','2610.09221':'Systems'}
rows=json.load(open('step1.json'))
order={r['id']:i for i,r in enumerate(rows)}
kept=[dict(r,topic=core[r['id']]) for r in rows if r['id'] in core]
kept.sort(key=lambda r:(-r['upvotes'],order[r['id']]))
json.dump(kept,open('step2.json','w'),ensure_ascii=False,indent=1)
top=kept[:20]; json.dump(top,open('step3.json','w'),ensure_ascii=False,indent=1)
print(len(rows),len(kept),len(top)); print('cut at', top[-1]['upvotes'], 'next', kept[20]['upvotes'])

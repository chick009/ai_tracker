#!/usr/bin/env python3
"""Tier-3 merge for the 2026-10-08 Blog 應用摘要 scan (prepared in phase 1; run AFTER the browser pass).

Input : /workspace/blog-tier3-2026-10-08/browser-listings.json
        shape {source_id: {status, note, posts: [{title, url, date, summary?}]}}
        source_id in: perplexity, meta-ai, snowflake, qwen, microsoft-ai
Effect: upserts posts by URL into blog-watch/sources/<id>.json
        (existing → last_seen=TODAY, keep first_seen, fill empty summary; new → first_seen=last_seen=TODAY),
        refreshes post_count/updated_at in the source file and index.json,
        backs up every touched file to /workspace/blog-tier3-2026-10-08/backup/ first,
        writes upsert_report.json and new_urls.json (new URLs only; candidates for carding).
Usage : python3 merge_tier3.py [--dry-run] [--listings PATH]
Cards are NOT written here: read each new in-window post, card it, then rerun weeks/summary helpers.
"""
import json, sys, shutil, datetime, argparse
from pathlib import Path
B=Path('/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch')
W=Path('/workspace/blog-tier3-2026-10-08')
TODAY='2026-10-08'
WINDOW_START='2026-10-07'    # main in-window posts (since 10-07 ~06:10 HKT scan; include late 10-06 US-time items manually)
CATCHUP_HORIZON='2026-10-01' # older-than-horizon new URLs are stored only (not carded)
VIA='tier3_computerUse_chromium'
SIDS=['perplexity','meta-ai','snowflake','qwen','microsoft-ai']
ap=argparse.ArgumentParser(); ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--listings',default=str(W/'browser-listings.json'))
a=ap.parse_args()
NOWTS=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
L=json.load(open(a.listings))
norm=lambda u:(u or '').strip().split('#')[0].rstrip('/')
if not a.dry_run:
    (W/'backup').mkdir(parents=True,exist_ok=True)
    shutil.copy(B/'index.json',W/'backup'/'index.json')
idx=json.load(open(B/'index.json'))
report={}; new_urls=[]
for sid in SIDS:
    ent=L.get(sid)
    if not ent:
        report[sid]={'status':'missing_from_listings','inserted':[],'refreshed_last_seen':0}; continue
    p=B/'sources'/f'{sid}.json'
    if not a.dry_run: shutil.copy(p,W/'backup'/f'{sid}.json')
    d=json.load(open(p)); posts=d.setdefault('posts',[])
    byurl={norm(x['url']):x for x in posts}
    tnorm=lambda t:' '.join((t or '').lower().replace('’',"'").split())
    bytitle={tnorm(x.get('title')):x for x in posts}
    listing_urls={norm(d.get('url')),norm(next((s.get('url') for s in idx['sources'] if s['id']==sid),''))}-{''}
    ins=[]; ref=0; title_ref=0; skipped_listing=[]
    for lp in ent.get('posts',[]):
        u=norm(lp.get('url'))
        if not u: continue
        if u in listing_urls:
            # GUARD: bare listing URL (e.g. Qwen JS links) -> never upsert by URL; refresh by title (exact, then prefix) only
            t=tnorm(lp.get('title')); hit=bytitle.get(t)
            if not hit:
                cands=[x for k,x in bytitle.items() if k and (t.startswith(k) or k.startswith(t.split(':')[0]))]
                hit=cands[0] if len(cands)==1 else None
            if hit:
                hit['last_seen']=TODAY; hit['last_seen_via']=VIA; ref+=1; title_ref+=1
                if lp.get('date') and not hit.get('date'): hit['date']=lp['date']
            else: skipped_listing.append(lp.get('title',''))
            continue
        if u in byurl:
            byurl[u]['last_seen']=TODAY; byurl[u]['last_seen_via']=VIA; ref+=1
            if lp.get('summary') and not byurl[u].get('summary'): byurl[u]['summary']=lp['summary']
            if lp.get('date') and not byurl[u].get('date'): byurl[u]['date']=lp['date']
            continue
        date=lp.get('date') or ''
        post={'title':lp.get('title',''),'url':lp['url'],'date':date,'category':'unknown','tags':[],
              'summary':lp.get('summary',''),'application_relevant':False,'digest_focus':False,
              'first_seen':TODAY,'last_seen':TODAY,'via':VIA,'fetch_note':f'browser_listing_{TODAY} (computerUse Chromium)'}
        if date and date<WINDOW_START: post['catch_up']=True
        if date and date<CATCHUP_HORIZON: post['carded']=False; post['not_carded_reason']=f'older than catch-up horizon (~{CATCHUP_HORIZON}); stored only'
        posts.append(post); byurl[u]=post; ins.append(lp.get('title',''))
        new_urls.append({'via':VIA,'source':sid,'title':post['title'],'url':post['url'],'date':date,
                         'in_window':bool(date) and date>=WINDOW_START,'catch_up':bool(date) and date<WINDOW_START,
                         'card_candidate':(not date) or date>=CATCHUP_HORIZON})
    posts.sort(key=lambda x:x.get('date') or '',reverse=True)
    d['updated_at']=NOWTS
    if 'post_count' in d: d['post_count']=len(posts)
    if not a.dry_run: p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    for s in idx['sources']:
        if s['id']==sid: s['post_count']=len(posts); s['updated_at']=NOWTS
    report[sid]={'status':ent.get('status'),'note':ent.get('note',''),'listed':len(ent.get('posts',[])),'inserted':ins,'refreshed_last_seen':ref,'refreshed_by_title':title_ref,'skipped_listing_url_unmatched':skipped_listing,'post_count':len(posts),'via':VIA}
idx['updated_at']=max(idx.get('updated_at',''),NOWTS)
if not a.dry_run:
    (B/'index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n')
    json.dump(report,open(W/'upsert_report.json','w'),ensure_ascii=False,indent=1)
    json.dump(new_urls,open(W/'new_urls.json','w'),ensure_ascii=False,indent=1)
print(('DRY RUN — nothing written\n' if a.dry_run else '')+json.dumps(report,ensure_ascii=False,indent=1))
print('NEW URLS:'); [print(f"  [{n['source']}] {n['date'] or '????-??-??'} {'IN-WINDOW' if n['in_window'] else ('catch-up' if n['card_candidate'] else 'store-only')} {n['title']} — {n['url']}") for n in new_urls]

import praw,os,time,json,html,datetime as dt,prawcore
HKT=dt.timezone(dt.timedelta(hours=8))
TODAY=dt.datetime.now(HKT).strftime('%Y-%m-%d')
OUT_DIR='/workspace/reddit-digest'
JSON_PATH=os.path.join(OUT_DIR,f'reddit-top5-{TODAY}.json')
HTML_PATH=os.path.join(OUT_DIR,f'reddit-top5-{TODAY}.html')
r=praw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'],client_secret=os.environ['REDDIT_CLIENT_SECRET'],user_agent='XBookmarkWatchlist/1.0 (digest; by Johnny)')
subs="singularity grok GrokBot ClaudeCode codex Cursor opencode AI_Agents LangChain RAG MLOps LocalLLaMA MachineLearning".split()
calls=0;t0=time.time();win=[]
def pace():
    global calls
    now=time.time()
    while win and now-win[0]>60: win.pop(0)
    if len(win)>=90: time.sleep(61-(now-win[0]))
    time.sleep(1.1);win.append(time.time());calls+=1
def retry(f):
    for i in range(4):
        pace()
        try: return f()
        except prawcore.exceptions.TooManyRequests: time.sleep(30*(i+1))
    raise Exception('429 repeated')
out=[];now=time.time()
for s in subs:
    e={'sub':s,'posts':[],'error':None}
    try:
        lst=retry(lambda: list(r.subreddit(s).top(time_filter='day',limit=8)))
        for p in lst:
            if p.stickied and now-p.created_utc>86400: continue
            if len(e['posts'])>=5: break
            d=dict(title=p.title,permalink='https://reddit.com'+p.permalink,author=str(p.author) if p.author else '[deleted]',score=p.score,num_comments=p.num_comments,created=dt.datetime.fromtimestamp(p.created_utc,HKT).strftime('%Y-%m-%d %H:%M HKT'),flair=p.link_flair_text,text=(p.selftext[:500]+('…' if len(p.selftext)>500 else '')) if p.is_self else p.url,comments=[])
            p.comment_sort='top'
            def gc():
                p.comments.replace_more(limit=0); return list(p.comments)
            try:
                for c in retry(gc):
                    if len(d['comments'])>=5: break
                    a=str(c.author) if c.author else None
                    if c.stickied or not a or a=='AutoModerator' or c.body in('[deleted]','[removed]'): continue
                    d['comments'].append(dict(author=a,score=c.score,body=c.body[:400]+('…' if len(c.body)>400 else '')))
            except Exception as x: d['comment_error']=str(x)
            e['posts'].append(d)
    except Exception as x: e['error']=f'{type(x).__name__}: {x}'
    out.append(e);print(s,len(e['posts']),e['error'],calls,flush=True)
gen=dt.datetime.now(HKT).strftime('%Y-%m-%d %H:%M HKT')
json.dump(dict(generated=gen,calls=calls,data=out),open(JSON_PATH,'w'),ensure_ascii=False,indent=1)
import sys;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from render import render
edf=os.environ.get('DIGEST_EDITORIAL')  # optional editorial JSON (highlights/tonote template)
ed=json.load(open(edf)) if edf and os.path.exists(edf) else None
open(HTML_PATH,'w').write(render(dict(generated=gen,data=out),ed))
print('wrote',JSON_PATH,HTML_PATH)
print('calls',calls,'runtime',round(time.time()-t0))

import json,html,sys,os
E=html.escape
CSS='body{font-family:system-ui,sans-serif;max-width:900px;margin:auto;padding:20px;background:#f6f7f9;color:#222}details{background:#fff;border-radius:10px;margin:12px 0;padding:10px 16px;box-shadow:0 1px 3px #0002}summary{font-size:1.2em;font-weight:600;cursor:pointer}.post{border-top:1px solid #eee;padding:10px 0}.meta{color:#666;font-size:.85em}.txt{white-space:pre-wrap;background:#fafafa;padding:8px;border-radius:6px;font-size:.9em}.c{border-left:3px solid #ff4500;padding:4px 10px;margin:6px 0;font-size:.9em;white-space:pre-wrap}.err{color:#b00}a{color:#0b57d0}.hl{background:linear-gradient(135deg,#fff8e1,#ffecb3);border-radius:12px;padding:12px 18px;margin:10px 0;border:1px solid #f0c040}.hl .tag{background:#ff4500;color:#fff;border-radius:10px;padding:1px 8px;font-size:.8em}.hl blockquote{margin:8px 0;padding:6px 10px;border-left:3px solid #c9a227;background:#fffdf5;font-size:.9em;white-space:pre-wrap}.tn{background:#e8f1ff;border:1px solid #9cbcf0;border-radius:12px;padding:12px 20px;margin:16px 0}.tn h2{margin-top:4px}'
def pid(p): return p['permalink'].split('/')[6]
def render(d,editorial=None):
    out=d['data'];gen=d['generated'];idx={pid(p):(e['sub'],p) for e in out for p in e['posts']}
    h=[f'<!doctype html><html lang="zh-HK"><meta charset="utf-8"><title>Reddit 每日精選</title><style>{CSS}</style><h1>Reddit 每日精選</h1><p class="meta">生成時間：{E(gen)}｜過去 24 小時熱門（Reddit top/day）｜每個 sub 頭 5 帖＋每帖頭 5 個留言</p>']
    if editorial:
        h.append('<h2>⭐ 今日 5 大重點</h2>')
        for i,x in enumerate(editorial.get('highlights',[]),1):
            if x['id'] not in idx: continue
            s,p=idx[x['id']]
            h.append(f'<div class=hl><span class=tag>r/{E(s)}</span> <b>{i}. <a href="{E(p["permalink"])}">{E(p["title"])}</a></b><div class=meta>👍 {p["score"]}｜💬 {p["num_comments"]}</div><p>{E(x["why"])}</p>')
            if x.get('extra'):
                links='、'.join(f'<a href="{E(idx[k][1]["permalink"])}">{E(idx[k][1]["title"])}</a>（👍 {idx[k][1]["score"]}）' for k in x['extra'] if k in idx)
                h.append(f'<p class=meta>相關：{links}　{E(x.get("extra_note",""))}</p>')
            cs=p['comments']
            if cs:
                c=cs[min(x.get('comment',0),len(cs)-1)]
                h.append(f'<blockquote>💬 u/{E(c["author"])}（👍 {c["score"]}）：{E(c["body"])}</blockquote>')
            h.append('</div>')
        if editorial.get('tonote_themes'):
            n=sum(len(e['posts']) for e in out)
            h.append(f'<div class=tn><h2>📝 TONOTE（總覽）</h2><p class=meta>根據今日 {len(out)} 個 sub、{n} 篇帖整理</p><ul>'+''.join(f'<li>{t}</li>' for t in editorial['tonote_themes'])+'</ul>')
            if editorial.get('low_signal'): h.append(f'<p><b>今日低訊號 sub：</b>{E(editorial["low_signal"])}</p>')
            if editorial.get('watch_next'): h.append('<p><b>接住要留意：</b></p><ul>'+''.join(f'<li>{E(w)}</li>' for w in editorial['watch_next'])+'</ul>')
            h.append('</div>')
    h.append('<h3>目錄</h3><ul>')
    for e in out: h.append(f'<li><a href="#{e["sub"]}">r/{e["sub"]}</a>（{len(e["posts"])} 帖）{"<span class=err> ⚠ 讀取失敗</span>" if e["error"] else ""}</li>')
    h.append('</ul>')
    for e in out:
        h.append(f'<details id="{e["sub"]}" open><summary>r/{e["sub"]}（{len(e["posts"])} 帖）</summary>')
        if e['error']: h.append(f'<p class=err>讀取失敗：{E(e["error"])}</p>')
        for i,p in enumerate(e['posts'],1):
            t=p['text']; tx=f'<a href="{E(t)}">{E(t)}</a>' if t.startswith('http') else E(t)
            h.append(f'<div class=post><b>{i}. <a href="{E(p["permalink"])}">{E(p["title"])}</a></b><div class=meta>👍 {p["score"]}｜💬 {p["num_comments"]}｜作者 u/{E(p["author"])}｜{p["created"]}{"｜標籤："+E(p["flair"]) if p["flair"] else ""}</div>{"<div class=txt>"+tx+"</div>" if t else ""}<p><b>熱門留言</b></p>')
            for c in p['comments']: h.append(f'<div class=c><span class=meta>u/{E(c["author"])}｜👍 {c["score"]}</span>\n{E(c["body"])}</div>')
            if not p['comments']: h.append('<p class=meta>（未有留言）</p>')
            h.append('</div>')
        h.append('</details>')
    return ''.join(h)
if __name__=='__main__':
    # usage: python render.py data.json out.html [editorial.json]  (no API calls)
    d=json.load(open(sys.argv[1])); ed=json.load(open(sys.argv[3])) if len(sys.argv)>3 else None
    open(sys.argv[2],'w').write(render(d,ed))

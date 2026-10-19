#!/usr/bin/env python3
"""AI Tracker cross-source aggregation (trial).

Usage: python3 aggregate.py [--date 2026-10-19] [--offline]

Inputs
  inputs-<date>.json             collector items (id, collector, section, title, url | hf_id | repo | reddit_id)
  raw/x-posts.json               X API v2 payload for the X post ids (fetched by the agent via the `x`
                                 connector get_posts_by_ids; this script cannot call MCP itself)
  raw/x-quoted-*.json            optional: quoted posts {id, urls:[{expanded_url, unwound_url}]}
  ../<date>-papers-extract.json  HF papers extract (arxiv/github/project page)
  /workspace/reddit-digest/reddit-top5-<date>.json
Network (cached under raw/): lnkd.in redirects + LinkedIn public post pages, nested lnkd.in
interstitials, blog pages, GitHub READMEs (mentions only).
Outputs: events.json, resolution.json (per-item trace)
"""
import argparse, hashlib, html, json, os, re, subprocess, sys
from collections import defaultdict
from urllib.parse import urlparse, unquote, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'raw')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
OFFLINE = False

# ---------------- fetch helpers (cached) ----------------
def _cache(name):
    return os.path.join(RAW, name)

def curl(url, name, head=False):
    p = _cache(name)
    if os.path.exists(p):
        return open(p, errors='ignore').read()
    if OFFLINE:
        return None
    args = ['curl', '-sL', '-m', '30', '-A', UA]
    if head:
        args += ['-I']
    try:
        out = subprocess.run(args + [url], capture_output=True, text=True, timeout=40).stdout
    except Exception:
        return None
    open(p, 'w').write(out)
    return out

def h(s):
    return hashlib.sha1(s.encode()).hexdigest()[:10]

def resolve_redirect(url):
    hd = curl(url, f'redir-{h(url)}.txt', head=True) or ''
    locs = re.findall(r'(?im)^location:\s*(\S+)', hd)
    return locs[-1] if locs else None

def resolve_lnkd_interstitial(url):
    """lnkd.in/<code> short links in post bodies render an interstitial with the external URL."""
    loc = resolve_redirect(url)
    if loc and 'lnkd.in' not in loc:
        return loc
    t = curl(url, f'lnkd-{h(url)}.html') or ''
    m = re.search(r'data-tracking-control-name="external_url_click"[^>]*href="([^"]+)"', t)
    return html.unescape(m.group(1)) if m else None

# ---------------- normalization ----------------
ARXIV_RE = re.compile(r'(?:arxiv\.org/(?:abs|pdf|html)/|huggingface\.co/papers/|academy\.dair\.ai/papers/[^\s"\']*-)(\d{4}\.\d{4,5})(?:v\d+)?')
NOISE_REPOS = {'huggingface/blog', 'langchain-ai/docs', 'vllm-project/vllm-project.github.io', 'features/copilot',
               'js-cookie/js-cookie', 'newrelic/newrelic-browser-agent'}
NOISE_HOST = ('linkedin.com', 'licdn.com', 'twimg.com', 'google-analytics', 'googletagmanager', 't.co')

def strip_url(u):
    p = urlparse(u)
    host = p.netloc.lower().removeprefix('www.')
    path = p.path.rstrip('/')
    return host, path

def keys_for_url(u):
    """Return list of (key, kind) for a URL."""
    out = []
    m = ARXIV_RE.search(u)
    if m:
        out.append((f'arxiv:{m.group(1)}', 'arxiv'))
        return out
    dm = re.search(r'doi\.org/(10\.[^\s?#]+)', u)
    if dm:
        return [(f'doi:{dm.group(1).lower()}', 'doi')]
    host, path = strip_url(u)
    parts = [x for x in path.split('/') if x]
    if host == 'github.com' and len(parts) >= 2:
        repo = f'{parts[0]}/{parts[1]}'.lower().removesuffix('.git')
        if repo not in NOISE_REPOS:
            out.append((f'github:{repo}', 'github'))
        return out
    if host == 'huggingface.co' and len(parts) >= 2 and parts[0] not in ('blog', 'papers', 'datasets', 'spaces', 'buckets', 'docs'):
        out.append((f'hf-model:{parts[0]}/{parts[1]}'.lower(), 'hf-model'))
        return out
    if any(n in host for n in NOISE_HOST):
        return out
    out.append((f'url:{host}{path}', 'url'))
    return out

STOP = set('''the and for with from that this into your their agent agents ai model models open new via one more than
next level own on of in to a an is are be by at as using use based towards toward full fully stack
benchmark platform evaluation evaluating learning training paper blog post tools tool code coding
memory long term harness official llm llms framework workflow repo repos api best practices agentic'''.split())

def tokens(s):
    s = s.lower()
    toks = re.findall(r'[a-z][a-z0-9]+(?:[.-][a-z0-9]+)*', s)
    out = set()
    for t in toks:
        for piece in [t] + re.split(r'[-.]', t):
            if len(piece) >= 4 and piece not in STOP and not piece.isdigit():
                out.add(piece)
    return out

# ---------------- resolvers ----------------
def load_x():
    d = {}
    p = _cache('x-posts.json')
    if os.path.exists(p):
        j = json.load(open(p))
        for post in j.get('data', []):
            d[post['id']] = post
    quoted = {}
    for f in os.listdir(RAW):
        if f.startswith('x-quoted-') and f.endswith('.json'):
            q = json.load(open(_cache(f)))
            quoted[q['id']] = q
    return d, quoted

def resolve_x(it, xposts, quoted, tr):
    pid = re.search(r'/status/(\d+)', it['url']).group(1)
    post = xposts.get(pid)
    if not post:
        tr['status'] = 'unresolved'; tr['why'] = 'X post not in raw/x-posts.json (connector read missing/failed)'
        return []
    links = []
    ents = (post.get('entities') or {}).get('urls', []) + (((post.get('note_tweet') or {}).get('entities') or {}).get('urls', []))
    for u in ents:
        eu = u.get('unwound_url') or u.get('expanded_url') or ''
        if re.search(r'(x|twitter)\.com/[^/]+/status/\d+/(photo|video)/', eu):
            continue
        qm = re.search(r'(?:x|twitter)\.com/[^/]+/status/(\d+)', eu)
        if qm:
            q = quoted.get(qm.group(1))
            if q:
                for qu in q.get('urls', []):
                    links.append(('quoted-post-link', qu.get('unwound_url') or qu.get('expanded_url')))
            else:
                tr.setdefault('notes', []).append(f'quoted post {qm.group(1)} not fetched')
            continue
        links.append(('post-link', eu))
    tr['text'] = ((post.get('note_tweet') or {}).get('text') or post.get('text') or '')[:300]
    tr['created_at_utc'] = post.get('created_at')
    if not links:
        tr['status'] = 'no-outbound-link'; tr['why'] = 'post only carries media/t.co to itself'
    else:
        tr['status'] = 'resolved'
    return links

def resolve_linkedin(it, tr):
    code = it['url'].rstrip('/').split('/')[-1]
    loc = resolve_redirect(it['url'])
    tr['resolved_post_url'] = loc.split('?')[0] if loc else None
    t = curl(it['url'], f'li-{code}.html')
    if not t:
        tr['status'] = 'unresolved'; tr['why'] = 'LinkedIn page fetch failed'; return []
    post = None
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            j = json.loads(m.group(1))
        except Exception:
            continue
        if j.get('@type') == 'SocialMediaPosting':
            post = j; break
    if not post:
        tr['status'] = 'unresolved'; tr['why'] = 'no SocialMediaPosting ld+json (login wall?)'; return []
    author = (post.get('author') or {}).get('name')
    tr['author'] = author; tr['date_utc'] = post.get('datePublished')
    body = post.get('articleBody') or post.get('text') or ''
    tr['text'] = body[:300]
    links = [('post-body', u) for u in re.findall(r'https?://[^\s)\]]+', body)]
    sh = post.get('sharedContent') or {}
    if sh.get('url'):
        links.append(('shared-card', sh['url']))
    # article card of the main post
    ms = t.find('main-feed-activity-card')
    main_region = t[ms: ms + 25000] if ms >= 0 else ''
    for a in re.findall(r'href="([^"]+?(?:public_post|public_post_reshare)_feed-article-content)"', main_region)[:1]:
        q = parse_qs(urlparse(html.unescape(a)).query).get('url')
        if q:
            links.append(('article-card', unquote(q[0])))
    for c in post.get('comment') or []:
        if (c.get('author') or {}).get('name') == author:
            for u in re.findall(r'https?://[^\s)\]]+', c.get('text', '')):
                links.append(('author-comment', u))
    out = []
    for src, u in links:
        if 'lnkd.in/' in u:
            r = resolve_lnkd_interstitial(u)
            if r:
                out.append((src + '(lnkd.in)', r))
            else:
                tr.setdefault('notes', []).append(f'nested {u} unresolved')
        elif 'linkedin.com/' in u and '/posts/' not in u:
            continue
        else:
            out.append((src, u))
    tr['status'] = 'resolved' if out else 'no-outbound-link'
    if not out:
        tr['why'] = 'post has no external link (text-only announcement)'
    return out

def resolve_blog(it, tr):
    t = curl(it['url'].split('#')[0], f'blog-{h(it["url"].split("#")[0])}.html')
    if not t:
        tr['status'] = 'unresolved'; tr['why'] = 'blog fetch failed'; return [], []
    t = html.unescape(t)
    found = []
    for u in re.findall(r'https?://(?:www\.)?(?:arxiv\.org/(?:abs|pdf)/\d{4}\.\d{4,5}|github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+|huggingface\.co/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)', t):
        u = u.rstrip('.')
        if u not in found:
            found.append(u)
    slug_toks = tokens(it['title'] + ' ' + urlparse(it['url']).path.replace('-', ' ') + ' ' + urlparse(it['url']).netloc.split('.')[-2])
    primary, mentions = [], []
    for u in found:
        ks = keys_for_url(u)
        if not ks:
            continue
        k = ks[0][0]
        if ks[0][1] not in ('arxiv', 'github', 'hf-model'):
            continue
        name_toks = tokens(k.split(':', 1)[1].replace('/', ' '))
        if k.startswith('arxiv:') or (name_toks & slug_toks):
            primary.append(('blog-artifact', u))
        else:
            mentions.append(u)
    tr['status'] = 'resolved'
    tr['mentions'] = mentions[:15]
    return primary, mentions

def resolve_github(it, tr):
    r = it['repo']
    t = curl(f'https://api.github.com/repos/{r}/readme', f'readme-{r.replace("/", "__")}.json')
    mentions = []
    if t:
        try:
            import base64
            j = json.loads(t)
            txt = base64.b64decode(j.get('content', '')).decode('utf-8', 'ignore')
            for u in re.findall(r'https?://(?:arxiv\.org/(?:abs|pdf)/\d{4}\.\d{4,5}|huggingface\.co/papers/\d{4}\.\d{4,5})', txt):
                mentions.append(u)
        except Exception:
            tr.setdefault('notes', []).append('README parse failed')
    tr['status'] = 'resolved'
    # README arXiv links are often citations, not the repo's own paper -> mention-only (never merge on them)
    tr['mentions'] = list(dict.fromkeys(mentions))
    return []

# ---------------- main ----------------
def main():
    global OFFLINE
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', default='2026-10-19')
    ap.add_argument('--offline', action='store_true')
    a = ap.parse_args()
    OFFLINE = a.offline
    os.makedirs(RAW, exist_ok=True)
    inp = json.load(open(os.path.join(HERE, f'inputs-{a.date}.json')))
    items = inp['items']
    papers = {p['id']: p for p in json.load(open(os.path.join(HERE, '..', f'{a.date}-papers-extract.json')))['papers']}
    reddit = {}
    rp = f'/workspace/reddit-digest/reddit-top5-{a.date}.json'
    if os.path.exists(rp):
        for s in json.load(open(rp))['data']:
            for p in s['posts']:
                m = re.search(r'/comments/([a-z0-9]+)/', p['permalink'])
                if m:
                    reddit[m.group(1)] = dict(p, sub=s['sub'])
    xposts, quoted = load_x()

    trace = {}
    item_keys = {}    # id -> list of (key, kind, via, url)
    for it in items:
        tr = {'collector': it['collector']}
        links = []
        self_url = it.get('url')
        if it['collector'].endswith('(X)'):
            links = resolve_x(it, xposts, quoted, tr)
        elif it['collector'] == 'LinkedIn':
            links = resolve_linkedin(it, tr)
        elif it['collector'] == 'Blog':
            links, _ = resolve_blog(it, tr)
            if it.get('release'):
                item_keys.setdefault(it['id'], []).append((f'product:{it["release"]}', 'release', 'release-tag', self_url))
        elif it['collector'] == 'HF Papers':
            p = papers.get(it['hf_id'])
            self_url = f'https://huggingface.co/papers/{it["hf_id"]}'
            if p:
                it['title'] = p['title']
                links = [('hf-extract:arxiv', p.get('arxiv_url'))]
                if p.get('github_repo'): links.append(('hf-extract:github', p['github_repo']))
                if p.get('project_page'): links.append(('hf-extract:project', p['project_page']))
                tr['status'] = 'resolved'; tr['org'] = p.get('organization')
            else:
                tr['status'] = 'unresolved'; tr['why'] = 'not in papers-extract'
        elif it['collector'] == 'GitHub Trending':
            self_url = f'https://github.com/{it["repo"]}'
            links = resolve_github(it, tr)
        elif 'Reddit' in it['collector']:
            p = reddit.get(it['reddit_id'])
            if p:
                self_url = 'https://www.reddit.com' + urlparse(p['permalink']).path
                tr['reddit_title'] = p['title']; tr['sub'] = p['sub']
                links = [('post-body', u) for u in re.findall(r'https?://[^\s)\]]+', p.get('text', '')) if 'redd.it' not in u]
                tr['status'] = 'resolved' if links else 'no-outbound-link'
                if not links: tr['why'] = 'self/text post, no external link'
            else:
                tr['status'] = 'unresolved'; tr['why'] = 'reddit id not in reddit-top5 file'
        it['self_url'] = self_url
        ks = item_keys.setdefault(it['id'], [])
        for k, kind in keys_for_url(self_url or ''):
            ks.append((k, kind, 'self', self_url))
        for via, u in links:
            if not u: continue
            for k, kind in keys_for_url(u):
                ks.append((k, kind, via, u))
        # dedupe
        seen = set(); uniq = []
        for row in ks:
            if row[0] not in seen:
                seen.add(row[0]); uniq.append(row)
        item_keys[it['id']] = uniq
        tr['keys'] = [{'key': k, 'kind': kind, 'via': via, 'url': u} for k, kind, via, u in uniq]
        if tr.get('status') == 'resolved' and not any(r[2] not in ('self', 'release-tag') for r in uniq):
            if it['collector'] in ('GitHub Trending', 'Blog', 'HF Papers'):
                tr['status'] = 'resolved'; tr['note'] = 'self is the primary artifact (no outbound artifact links)'
            else:
                tr['status'] = 'no-outbound-link'; tr.setdefault('why', 'no external artifact link found in post/page')
        trace[it['id']] = tr

    # union-find on shared keys
    parent = {it['id']: it['id'] for it in items}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    key_owners = defaultdict(list)
    for iid, ks in item_keys.items():
        for k, *_ in ks:
            key_owners[k].append(iid)
    link_reason = defaultdict(set)
    for k, owners in key_owners.items():
        if len(set(owners)) > 1:
            for o in owners[1:]:
                parent[find(o)] = find(owners[0])
            for o in owners:
                link_reason[o].add(k)

    groups = defaultdict(list)
    for it in items:
        groups[find(it['id'])].append(it)

    # HF issue presence: arxiv ids posted by non-HF collectors that also sit in the full HF daily issue
    hf_issue_ids = set(papers)
    hf_rank = {p['id']: r for r, p in enumerate(sorted(papers.values(), key=lambda p: -p['upvotes']), 1)}

    PRI = {'arxiv': 0, 'github': 1, 'hf-model': 2}
    def canonical(group):
        cands = []
        for it in group:
            for k, kind, via, u in item_keys[it['id']]:
                if kind == 'arxiv':
                    cands.append((0, f'https://arxiv.org/abs/{k.split(":")[1]}'))
                elif kind == 'doi':
                    cands.append((0.1, f'https://doi.org/{k.split(":", 1)[1]}'))
                elif kind == 'github' and via != 'blog-artifact':
                    cands.append((1, f'https://github.com/{k.split(":")[1]}'))
                elif kind == 'url' and via != 'self':
                    cands.append((0.7, u))
        for it in group:
            c = it['collector']; u = it['self_url']
            if c == 'Blog': cands.append((0.5, u))
            elif c == 'HF Papers': cands.append((2, u))
            elif c.endswith('(X)'): cands.append((3, u))
            elif 'Reddit' in c: cands.append((3.5, u))
            elif c == 'LinkedIn': cands.append((4, u))
            else: cands.append((5, u))
        cands.sort(key=lambda x: x[0])
        return cands[0][1]

    events = []
    for n, (root, group) in enumerate(sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])), 1):
        allkeys = []
        for it in group:
            for k, *_ in item_keys[it['id']]:
                if k not in allkeys: allkeys.append(k)
        shared = sorted({k for it in group for k in link_reason.get(it['id'], set()) if len(set(key_owners[k]) & {g['id'] for g in group}) > 1})
        arx = [k.split(':')[1] for k in allkeys if k.startswith('arxiv:')]
        hf_hit = [x for x in arx if x in hf_issue_ids]
        title = next((it['title'] for it in group if it['collector'] == 'HF Papers'), None) or \
                next((it['title'] for it in group if it['collector'] == 'Blog'), None) or group[0]['title']
        events.append({
            'event_id': f'{a.date}-e{n:02d}',
            'title': title,
            'canonical_url': canonical(group),
            'artifact_keys': allkeys,
            'linking_keys': shared,
            'sources': [{'collector': it['collector'], 'item_id': it['id'], 'section': it['section'], 'url': it['self_url'], 'title': it['title']} for it in group],
            'source_count': len(group),
            'collector_count': len({it['collector'].split(' (')[0] for it in group}),
            'merge_confidence': 'exact-key' if len(group) > 1 else 'single',
            'also_in_hf_issue': [{'arxiv': x, 'hf_rank': hf_rank[x], 'of': len(papers), 'upvotes': papers[x]['upvotes'],
                                  'code': papers[x].get('github_repo'), 'org': papers[x].get('organization')}
                                 for x in hf_hit] if not any(it['collector'] == 'HF Papers' for it in group) else [],
            'resolution': {it['id']: trace[it['id']]['status'] for it in group},
        })

    # fuzzy 'possible' merges between events (kept separate)
    ent = {}
    for e in events:
        t = set()
        for s in e['sources']:
            t |= tokens(s['title'])
            u = s['url'] or ''
            host = urlparse(u).netloc.lower().removeprefix('www.')
            m = re.search(r'(?:x|twitter)\.com/([^/]+)/status', u)
            if m: pass  # author handle != artifact identity (dair_ai posts many papers)
            elif host and host not in ('lnkd.in', 'huggingface.co', 'github.com', 'reddit.com'): t |= tokens(host.split('.')[-2] if host.count('.') else host)
        for k in e['artifact_keys']:
            if k.startswith(('github:', 'product:', 'hf-model:')):
                t |= tokens(k.split(':', 1)[1].replace('/', ' ').split('@')[0])
        ent[e['event_id']] = t
    entity_toks = defaultdict(set)
    for e in events:
        for k in e['artifact_keys']:
            if k.startswith(('github:', 'hf-model:')):
                entity_toks[e['event_id']] |= tokens(k.split(':', 1)[1].split('/')[0])
        for k in e['artifact_keys']:
            if k.startswith('url:'):
                hst = k[4:].split('/')[0]
                if hst.endswith('github.io'):
                    entity_toks[e['event_id']] |= tokens(hst.split('.')[0])
                elif hst not in ('lnkd.in', 'x.com', 'reddit.com') and hst.count('.'):
                    entity_toks[e['event_id']] |= tokens(hst.split('.')[-2])
        for s in e['sources']:
            host = urlparse(s['url'] or '').netloc.lower().removeprefix('www.')
            if host and host not in ('lnkd.in', 'huggingface.co', 'github.com', 'reddit.com', 'x.com', 'arxiv.org') and host.count('.'):
                entity_toks[e['event_id']] |= tokens(host.split('.')[-2])
            m = re.search(r'x\.com/([^/]+)/status', s['url'] or '')
            if m and m.group(1).lower() in ('cursor_ai', 'langchain', 'openai', 'anthropicai', 'nvidia', 'googledeepmind'):
                entity_toks[e['event_id']] |= tokens(m.group(1).replace('_ai', ''))

    df = defaultdict(int)
    for t in ent.values():
        for x in t: df[x] += 1
    def sites(e):
        out = set()
        for k in e['artifact_keys']:
            if k.startswith('url:'):
                hst = k[4:].split('/')[0]
                if hst not in ('lnkd.in', 'x.com', 'reddit.com', 'huggingface.co', 'github.com', 'arxiv.org', 'doi.org') and not hst.endswith('github.io'):
                    out.add(hst)
        return out
    possible = []
    for i in range(len(events)):
        for j in range(i + 1, len(events)):
            ss = sites(events[i]) & sites(events[j])
            if ss:
                possible.append({'a': events[i]['event_id'], 'b': events[j]['event_id'], 'shared_tokens': sorted(ss), 'strength': 'same-site (related page, not same artifact)'})
    ids = [e['event_id'] for e in events]
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            A = ent[ids[i]] | entity_toks[ids[i]]; B = ent[ids[j]] | entity_toks[ids[j]]
            sh = {x for x in A & B if df[x] <= 3}
            if not sh:
                continue
            org = sh & (entity_toks[ids[i]] | entity_toks[ids[j]])
            ea = next(e for e in events if e['event_id'] == ids[i]); eb = next(e for e in events if e['event_id'] == ids[j])
            pa = {k for k in ea['artifact_keys'] if k.startswith(('arxiv:', 'doi:'))}
            pb = {k for k in eb['artifact_keys'] if k.startswith(('arxiv:', 'doi:'))}
            if pa and pb and not (pa & pb):
                if org:
                    possible.append({'a': ids[i], 'b': ids[j], 'shared_tokens': sorted(sh), 'strength': 'org-only (related, different papers)'})
                continue
            if len(sh) >= 2:
                possible.append({'a': ids[i], 'b': ids[j], 'shared_tokens': sorted(sh), 'strength': 'strong (same-artifact candidate)'})
            elif org:
                possible.append({'a': ids[i], 'b': ids[j], 'shared_tokens': sorted(sh), 'strength': 'org-only (related, not same artifact)'})
    key_to_event = {}
    for e in events:
        for k in e['artifact_keys']:
            key_to_event.setdefault(k, e['event_id'])
    related = []
    for e in events:
        for s in e['sources']:
            for mu in trace[s['item_id']].get('mentions', []):
                for k, _ in keys_for_url(mu):
                    tgt = key_to_event.get(k)
                    if tgt and tgt != e['event_id']:
                        related.append({'from': e['event_id'], 'to': tgt, 'via_mention': k})
    out = {
        'date': a.date,
        'raw_item_count': len(items),
        'event_count': len(events),
        'multi_source_event_count': sum(1 for e in events if e['source_count'] > 1),
        'unresolved_items': [{'id': k, 'collector': v['collector'], 'status': v['status'], 'why': v.get('why')} for k, v in trace.items() if v['status'] == 'unresolved'],
        'no_outbound_link_items': [{'id': k, 'collector': v['collector'], 'why': v.get('why')} for k, v in trace.items() if v['status'] == 'no-outbound-link'],
        'excluded_no_link': inp.get('excluded_no_link', []),
        'events': events,
        'possible_merges': possible,
        'mention_links': related,
    }
    json.dump(out, open(os.path.join(HERE, 'events.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(trace, open(os.path.join(HERE, 'resolution.json'), 'w'), ensure_ascii=False, indent=1)
    print(f"raw={out['raw_item_count']} events={out['event_count']} multi={out['multi_source_event_count']} "
          f"unresolved={len(out['unresolved_items'])} no-link={len(out['no_outbound_link_items'])} possible={len(possible)}")

if __name__ == '__main__':
    main()

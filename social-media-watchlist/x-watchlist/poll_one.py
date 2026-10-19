#!/usr/bin/env python3
"""Normalize one get_users_posts dump into posts list + quota footer."""
import json, re, sys
from pathlib import Path

def parse(path):
    t = Path(path).read_text()
    # strip untrusted wrappers if present
    t = re.sub(r'</?cursor_untrusted_data[^>]*>', '', t)
    start = t.find('{'); end = t.rfind('}')
    if start < 0 or end < 0:
        return None, None, t
    obj = json.loads(t[start:end+1])
    left = re.search(
        r'X reads left for this user: (\d+) of (\d+) this minute \(resets at ([^)]+)\), (\d+) of (\d+) today',
        t,
    )
    quota = None
    if left:
        quota = {
            "min_left": int(left.group(1)),
            "min_total": int(left.group(2)),
            "reset_at": left.group(3),
            "day_left": int(left.group(4)),
            "day_total": int(left.group(5)),
        }
    return obj, quota, t

def normalize_posts(obj, username):
    data = obj.get("data") or []
    if isinstance(data, dict):
        data = [data]
    includes = obj.get("includes") or {}
    users = {u.get("id"): u for u in includes.get("users") or []}
    posts = []
    for p in data:
        text = p.get("text") or ""
        note = p.get("note_tweet") or {}
        if isinstance(note, dict):
            note_text = note.get("text") or note.get("full_text")
            has_note = bool(note_text)
            if note_text:
                text = note_text
        else:
            has_note = False
            note_text = None
        urls = []
        ents = p.get("entities") or {}
        for u in ents.get("urls") or []:
            urls.append({
                "url": u.get("url"),
                "expanded_url": u.get("expanded_url"),
                "display_url": u.get("display_url"),
            })
        # note_tweet entities
        if isinstance(note, dict):
            nents = note.get("entities") or {}
            for u in nents.get("urls") or []:
                urls.append({
                    "url": u.get("url"),
                    "expanded_url": u.get("expanded_url"),
                    "display_url": u.get("display_url"),
                })
        url = p.get("url") or f"https://x.com/{username}/status/{p.get('id')}"
        posts.append({
            "id": str(p.get("id")),
            "username": username,
            "author_id": str(p.get("author_id") or ""),
            "url": url,
            "created_at": p.get("created_at"),
            "text": text,
            "raw_text": p.get("text") or "",
            "has_note": has_note,
            "note_tweet": note if isinstance(note, dict) else None,
            "urls": urls,
            "referenced_tweets": p.get("referenced_tweets") or [],
            "public_metrics": p.get("public_metrics"),
            "entities": ents,
            "possibly_truncated": bool(
                (not has_note)
                and (
                    (p.get("text") or "").endswith("…")
                    or (p.get("text") or "").endswith("...")
                    or len(p.get("text") or "") >= 270
                )
            ),
        })
    meta = obj.get("meta") or {}
    return posts, meta

if __name__ == "__main__":
    username, dump = sys.argv[1], sys.argv[2]
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(dump).with_suffix(".norm.json")
    obj, quota, raw = parse(dump)
    if obj is None:
        print(json.dumps({"error": "parse_failed", "quota": quota}))
        sys.exit(1)
    # error shapes
    if "title" in obj and "data" not in obj and "errors" in obj:
        print(json.dumps({"error": obj, "quota": quota}))
        sys.exit(2)
    posts, meta = normalize_posts(obj, username)
    result = {"username": username, "posts": posts, "meta": meta, "quota": quota, "result_count": len(posts)}
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(json.dumps({"username": username, "count": len(posts), "quota": quota, "newest": posts[0]["id"] if posts else None}))

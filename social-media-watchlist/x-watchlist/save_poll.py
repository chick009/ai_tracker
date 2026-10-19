#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

RAW = Path("/workspace/x-watchlist/raw-2026-10-19")
PROG = RAW / "progress.json"

def parse_dump(path):
    t = Path(path).read_text()
    t = re.sub(r'</?cursor_untrusted_data[^>]*>', '', t)
    t = re.sub(r'</?cursor_untrusted_data_redacted[^>]*>', '', t)
    start = t.find('{'); end = t.rfind('}')
    if start < 0 or end < 0:
        return None, None, t
    # Prefer meta/data object; if multiple JSON blobs take largest
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
    posts = []
    for p in data:
        text = p.get("text") or ""
        note = p.get("note_tweet") or {}
        has_note = False
        if isinstance(note, dict) and (note.get("text") or note.get("full_text")):
            text = note.get("text") or note.get("full_text")
            has_note = True
        urls = []
        ents = p.get("entities") or {}
        for u in ents.get("urls") or []:
            urls.append({"url": u.get("url"), "expanded_url": u.get("expanded_url"), "display_url": u.get("display_url")})
        if isinstance(note, dict):
            for u in (note.get("entities") or {}).get("urls") or []:
                urls.append({"url": u.get("url"), "expanded_url": u.get("expanded_url"), "display_url": u.get("display_url")})
        raw_text = p.get("text") or ""
        possibly_truncated = (not has_note) and (
            raw_text.endswith("…") or raw_text.endswith("...") or len(raw_text) >= 270
        )
        posts.append({
            "id": str(p.get("id")),
            "username": username,
            "author_id": str(p.get("author_id") or ""),
            "url": p.get("url") or f"https://x.com/{username}/status/{p.get('id')}",
            "created_at": p.get("created_at"),
            "text": text,
            "raw_text": raw_text,
            "has_note": has_note,
            "note_tweet": note if isinstance(note, dict) and note else None,
            "urls": urls,
            "referenced_tweets": p.get("referenced_tweets") or [],
            "public_metrics": p.get("public_metrics"),
            "entities": ents,
            "possibly_truncated": possibly_truncated,
        })
    return posts, obj.get("meta") or {}

def save(username, user_id, since_id, dump_path, error=None):
    prog = json.loads(PROG.read_text()) if PROG.exists() else {"done": [], "errors": [], "free_reads_used": 0}
    obj, quota, raw = parse_dump(dump_path)
    if obj is None:
        result = {"username": username, "user_id": user_id, "since_id": since_id, "posts": [], "meta": {}, "quota": quota, "result_count": 0, "error": "parse_failed"}
        prog["errors"].append({"username": username, "reason": "parse_failed"})
    elif "status" in obj and obj.get("status") in (429, 500, 503) or (isinstance(obj.get("title"), str) and "rate" in (obj.get("title") or "").lower()):
        result = {"username": username, "user_id": user_id, "since_id": since_id, "posts": [], "meta": {}, "quota": quota, "result_count": 0, "error": obj}
        prog["errors"].append({"username": username, "reason": str(obj.get("title") or obj.get("detail") or obj)})
    else:
        # rate limit in detail
        detail = (obj.get("detail") or "") + (obj.get("title") or "")
        if "rate" in detail.lower() and "data" not in obj:
            result = {"username": username, "user_id": user_id, "since_id": since_id, "posts": [], "meta": {}, "quota": quota, "result_count": 0, "error": obj}
            prog["errors"].append({"username": username, "reason": detail or "rate_limit"})
        else:
            posts, meta = normalize_posts(obj, username)
            # also capture errors array with empty data
            err = obj.get("errors")
            result = {"username": username, "user_id": user_id, "since_id": since_id, "posts": posts, "meta": meta, "quota": quota, "result_count": len(posts), "error": err, "includes": obj.get("includes")}
    (RAW / f"{username}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    if username not in prog["done"]:
        prog["done"].append(username)
    prog["free_reads_used"] = prog.get("free_reads_used", 0) + 1
    prog["last_quota"] = quota
    PROG.write_text(json.dumps(prog, indent=2))
    newest = result["posts"][0]["id"] if result.get("posts") else None
    need_bf = [p["id"] for p in result.get("posts", []) if p.get("possibly_truncated") or (not p.get("has_note") and len(p.get("raw_text","")) >= 240)]
    print(json.dumps({"username": username, "count": result.get("result_count", 0), "newest": newest, "need_backfill": need_bf, "quota": quota, "error": bool(result.get("error") and not result.get("posts"))}))

if __name__ == "__main__":
    # username user_id since_id dump
    save(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

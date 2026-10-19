#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

RAW = Path("/workspace/x-watchlist/raw-weekly-2026-10-19")
PROG = RAW / "progress.json"

def parse_dump(path):
    t = Path(path).read_text()
    t = re.sub(r"</?cursor_untrusted_data[^>]*>", "", t)
    t = re.sub(r"</?cursor_untrusted_data_redacted[^>]*>", "", t)
    start = t.find("{"); end = t.rfind("}")
    if start < 0 or end < 0:
        return None, None
    obj = json.loads(t[start:end+1])
    left = re.search(
        r"X reads left for this user: (\d+) of (\d+) this minute \(resets at ([^)]+)\), (\d+) of (\d+) today",
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
    return obj, quota

def merge(username, dump_path):
    acct = json.loads((RAW / f"{username}.json").read_text())
    obj, quota = parse_dump(dump_path)
    if not obj or "data" not in obj:
        print(json.dumps({"username": username, "merged": 0, "error": True, "quota": quota}))
        return
    data = obj["data"]
    if isinstance(data, dict):
        data = [data]
    by_id = {str(p["id"]): p for p in data}
    merged = 0
    for p in acct.get("posts") or []:
        full = by_id.get(str(p["id"]))
        if not full:
            continue
        note = full.get("note_tweet") or {}
        text = full.get("text") or ""
        has_note = False
        if isinstance(note, dict) and (note.get("text") or note.get("full_text")):
            text = note.get("text") or note.get("full_text")
            has_note = True
            p["note_tweet"] = note
            p["has_note"] = True
        if text:
            p["text"] = text
        ents = full.get("entities") or {}
        urls = []
        for u in ents.get("urls") or []:
            urls.append({"url": u.get("url"), "expanded_url": u.get("expanded_url"), "display_url": u.get("display_url")})
        if isinstance(note, dict):
            for u in (note.get("entities") or {}).get("urls") or []:
                urls.append({"url": u.get("url"), "expanded_url": u.get("expanded_url"), "display_url": u.get("display_url")})
        if urls:
            # merge unique by expanded_url
            seen = {u.get("expanded_url") for u in p.get("urls") or []}
            for u in urls:
                if u.get("expanded_url") not in seen:
                    p.setdefault("urls", []).append(u)
                    seen.add(u.get("expanded_url"))
            p["entities"] = ents
        p["possibly_truncated"] = False
        p["backfilled"] = True
        if full.get("referenced_tweets"):
            p["referenced_tweets"] = full["referenced_tweets"]
        if full.get("public_metrics"):
            p["public_metrics"] = full["public_metrics"]
        merged += 1
    (RAW / f"{username}.json").write_text(json.dumps(acct, indent=2, ensure_ascii=False))
    prog = json.loads(PROG.read_text())
    prog["free_reads_used"] = prog.get("free_reads_used", 0) + 1
    prog["backfill_batches"] = prog.get("backfill_batches", 0) + 1
    prog["last_quota"] = quota
    PROG.write_text(json.dumps(prog, indent=2))
    print(json.dumps({"username": username, "merged": merged, "quota": quota}))

if __name__ == "__main__":
    merge(sys.argv[1], sys.argv[2])

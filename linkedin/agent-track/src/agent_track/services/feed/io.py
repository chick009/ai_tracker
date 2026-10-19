"""Persist feed captures under data/feed/ (gitignored outputs)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_track.services.feed.parse import slim_digest


def default_output_dir() -> Path:
    return Path("data") / "feed"


def default_profile_dir() -> Path:
    return Path("data") / ".linkedin-browser-profile"


def write_feed_outputs(posts: list[dict[str, Any]], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    posts_path = output_dir / "posts.jsonl"
    digest_path = output_dir / "digest.json"
    with posts_path.open("w", encoding="utf-8") as handle:
        for post in posts:
            handle.write(json.dumps(post, ensure_ascii=False) + "\n")
    digest_path.write_text(
        json.dumps(slim_digest(posts), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return posts_path, digest_path

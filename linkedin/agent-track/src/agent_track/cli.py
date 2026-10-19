"""CLI: `agent-track feed digest`. Future services get sibling groups, not job-search cron."""

from __future__ import annotations

from pathlib import Path

import click

from agent_track.services.feed.collector import LOGIN_WAIT_SECONDS_DEFAULT, run_digest
from agent_track.services.feed.io import default_output_dir, default_profile_dir


@click.group()
def main() -> None:
    """Multi-service agent tracker. First service: LinkedIn Feed Digest."""


@main.group()
def feed() -> None:
    """Home-feed capture (not job search). Isolated from career-job-applications."""


@feed.command("digest")
@click.option("--limit", default=20, show_default=True, type=int, help="Max unique posts to collect.")
@click.option(
    "--persist-profile",
    is_flag=True,
    default=False,
    help="Reuse gitignored data/.linkedin-browser-profile (this repo only).",
)
@click.option(
    "--wait/--no-wait",
    default=True,
    show_default=True,
    help="Wait for an interactive LinkedIn login if no session cookie.",
)
@click.option("--headless/--headed", default=False, show_default=True)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Defaults to data/feed/",
)
@click.option(
    "--profile-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Chromium user-data-dir. Default: data/.linkedin-browser-profile",
)
@click.option("--login-timeout", default=LOGIN_WAIT_SECONDS_DEFAULT, type=int, show_default=True)
def digest_cmd(
    limit: int,
    persist_profile: bool,
    wait: bool,
    headless: bool,
    output_dir: Path | None,
    profile_dir: Path | None,
    login_timeout: int,
) -> None:
    """Scroll the LinkedIn home feed and write posts.jsonl + digest.json."""
    out = output_dir or default_output_dir()
    profile = profile_dir or default_profile_dir()
    posts = run_digest(
        limit=limit,
        persist_profile=persist_profile,
        wait=wait,
        headless=headless,
        output_dir=out,
        profile_dir=profile,
        login_timeout_s=login_timeout,
    )
    click.echo(f"Wrote {len(posts)} posts to {out / 'posts.jsonl'} and {out / 'digest.json'}")


if __name__ == "__main__":
    main()

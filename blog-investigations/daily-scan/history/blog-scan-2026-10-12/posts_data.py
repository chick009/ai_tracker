# New posts for weekday scan 2026-10-12 (window: 2026-10-10 through 2026-10-12;
# Saturday makeup already covered ~10-08–10-09). Tier-1+2 only; tier-3 pending.

POSTS = [
 dict(source="opencode-changelog", card_source="OpenCode changelog", title="OpenCode 1.19.0",
  url="https://github.com/anomalyco/opencode/releases/tag/v1.19.0", date="2026-10-11",
  category="changelog_features", type="changelog_feature", priority="P1", tags=["cli","feature","agents"], digest_focus=True,
  artifacts=["opencode-ai@1.19.0"],
  discovered_via="npm opencode-ai latest 1.19.0 (2026-10-11 01:38 UTC) + opencode.ai/changelog article datetime 2026-10-11T01:39:22Z",
  summary="OpenCode 1.19.0 (Oct 11): path to OpenCode 2 via `opencode upgrade --major` / TUI `/update`; allow OpenAI service_tier=ultrafast; validate PTY connection origins and tickets before existence checks; updates no longer install automatically.",
  key_takeaway=[
   "Core: run `opencode upgrade --major` to upgrade to OpenCode 2 (major line called out in release notes; this card does not invent OpenCode 2 feature details beyond the upgrade command)",
   "Core: allow the OpenAI `ultrafast` service tier — aligns OpenCode with the Ultrafast API mode already documented for gpt-6-astra / gpt-6.1-sol",
   "Core: validate PTY connection origins and tickets before checking whether a PTY exists (connection gating / security hardening)",
   "TUI: use `/update` to install OpenCode updates or upgrade to OpenCode 2; updates are no longer installed automatically",
   "Availability: npm latest 1.19.0 published 2026-10-11 01:38 UTC (10-11 09:38 HKT); prior latest was 1.18.35 (2026-10-06)"],
  priority_reason="Agent-enhancing changelog: OpenAI Ultrafast tier support plus an explicit OpenCode 2 major-upgrade path and PTY origin/ticket validation change latency options, harness upgrade workflow, and session security → P1 digest_focus. Not confirmed P0: OpenCode 2 capability surface not detailed in 1.19.0 notes.",
  needs_verification=False,
  alt_urls=["https://opencode.ai/changelog"]),
]

CARD_IDS = {
  "https://github.com/anomalyco/opencode/releases/tag/v1.19.0": "opencode-1-19-0-2026-10-11",
}

MIRRORS = []

SOURCE_ONLY = []

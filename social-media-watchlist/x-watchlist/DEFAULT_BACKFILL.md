# Default by-ID backfill (as of 2026-10-14)

After every timeline poll, re-fetch by ID any posts missing `note_tweet` / truncated text, merge full text + expanded URLs into the shortlist used for filtering and morning-brief.

As of 2026-10-14 evening: daily mode is **free-primary**. Backfill applies on the free daily run, and also on any on-demand paid verify run.

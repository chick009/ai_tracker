---
name: OSS system design exploration
description: >-
  use this when the user wants to explore an open-source repo’s system design
  and get a markdown architecture/usefulness doc via a Cursor cloud agent
---
# OSS system design exploration

Use a Cursor cloud agent as the investigator. You orchestrate: launch, wait for the run, then deliver the markdown doc to the user. Do not clone the target repo onto the box or a user machine.

## Model
Always launch (and reply) with:
- `model`: `grok-4.6`
- `model_params`: `{ "effort": "medium" }`

Do not use Auto / `default` unless the user explicitly asks to switch.

## When the user names a repo
1. Acknowledge and launch a cloud agent immediately. Do not pre-investigate the codebase yourself.
2. If the repo is third-party / the user does not own it, launch with `new_repo: true` so the design doc lives in a fresh Origin repo. Instruct the agent to fetch and analyze the public GitHub repo (URL in the prompt) and to write only the markdown deliverable — no app-code changes.
3. If the repo is one the user owns and has connected to Cursor, launch with that `repo` URL instead, still asking for docs-only (no refactors).
4. Give the cloud agent the outcome, not a prescribed architecture: repo URL, that claims must be grounded in code (cite file paths), and what “done” looks like.

## Document the agent should produce
A markdown system-design doc a senior engineer could use to decide on adoption:
- What it is and who it’s for
- Architecture and data flow (components, key abstractions)
- How the important parts actually work
- Tech stack and notable dependencies
- Tradeoffs, limitations, operational concerns
- Usefulness: when it’s a fit, when it isn’t, alternatives
- A short “should you use this?” recommendation

Ask the agent to write `SYSTEM_DESIGN.md` (repo root or `docs/`) and to include the full analysis in its final report.

## After it finishes
1. Open the cloud-agent card for the user.
2. Deliver the markdown in chat (from the agent’s final report or the file it wrote). Attach the file if you have it.
3. Do not dump the raw transcript. Summarize only if the user wants a shorter take.
4. If an OSS ingest endpoint is configured in agent memory, POST the project JSON (`title`, `repo_url`, `markdown`, `summary`, `tags`, `language`, `stars`, `status: "published"`). Read `OSS_INGEST_TOKEN` from the oss-ingest credential; send it only as an Authorization Bearer header. Never print, log, or paste the token. Look up real `stars`/language from GitHub rather than guessing. If the token is missing, send a secret-request (connector `oss-ingest`, field `OSS_INGEST_TOKEN`) and ingest once it is stored.

## Follow-ups
Reply to the same cloud agent for in-scope fixes or extra questions. Launch a new one only for a different repo. Pass the same grok-4.6 / effort=medium settings on reply if the tool requires them; otherwise leave the running agent’s model as-is once launched with this override.

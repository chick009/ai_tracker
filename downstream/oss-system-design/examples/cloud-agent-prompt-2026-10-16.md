Analyze the public open-source repository https://github.com/mksglu/context-mode and write a code-grounded system-design document.

Deliverable: a single markdown file `SYSTEM_DESIGN.md` at the repo root of this (new, empty) repo. Docs only — do not copy or vendor the context-mode source, do not write app code, no refactors. Fetch/read the public GitHub repo yourself (e.g. a shallow clone in your own environment) to ground every claim.

The document should let a senior engineer decide whether to adopt context-mode. Cover:
- What it is and who it's for
- Architecture and data flow: components (MCP server, hooks, sandboxing of tool output, session memory, platform routing across ~17 agents/IDEs), key abstractions, how a tool call flows from agent → context-mode → sandbox/persist → back
- How the important parts actually work (cite concrete file paths, modules, classes/functions)
- Tech stack and notable dependencies (primary language is TypeScript per GitHub; verify)
- Tradeoffs, limitations, security/isolation and operational concerns
- Usefulness: when it's a fit, when it isn't, alternatives
- A short "Should you use this?" recommendation

Rules: every non-trivial claim must cite a file path in the context-mode repo; mark anything inferred vs. verified; note the commit SHA you analyzed.
Done = SYSTEM_DESIGN.md committed to this repo, and your final report includes the full contents of SYSTEM_DESIGN.md.

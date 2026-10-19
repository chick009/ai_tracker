Analyze the public open-source repository https://github.com/trycua/cua and write a code-grounded system-design document.

Deliverable: a single markdown file `SYSTEM_DESIGN.md` at the repo root of this (new, empty) repo. Docs only — do not copy or vendor the cua source, do not write app code, no refactors. Fetch/read the public GitHub repo yourself (e.g. a shallow clone in your own environment) to ground every claim.

The document should let a senior engineer decide whether to adopt cua. Cover:
- What it is and who it's for
- Architecture and data flow: components (e.g. computer server/drivers, Lume/macOS virtualization, Windows/Linux sandboxes/containers, agent SDK, fleet/orchestration, benchmarks/eval), key abstractions, how an agent action flows from model → SDK → driver → OS and back
- How the important parts actually work (cite concrete file paths, modules, classes/functions)
- Tech stack and notable dependencies (languages per component — the repo's primary language is Rust per GitHub; verify)
- Tradeoffs, limitations, security/isolation and operational concerns
- Usefulness: when it's a fit, when it isn't, alternatives
- A short "Should you use this?" recommendation

Rules: every non-trivial claim must cite a file path in the cua repo; mark anything inferred vs. verified; note the commit SHA you analyzed.
Done = SYSTEM_DESIGN.md committed to this repo, and your final report includes the full contents of SYSTEM_DESIGN.md.

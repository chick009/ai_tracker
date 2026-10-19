# paper-review

Weekday pipeline: take a Hugging Face Daily Papers curation JSON, keep papers whose **full text and a real figure** can be pulled from arXiv, pick the top 5, run a 3-step LLM card (extract → critique → write), and emit **one self-contained HTML page** with the paper’s own method figure and a plain-English walkthrough.

## Setup

Python 3.11+. From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Optional SVG rasterization: `pip install -e ".[svg]"` (needs cairo).

### Command Code (production LLM)

The live runner shells out to the Command Code CLI:

```text
cmd -t -p "<prompt>" -m deepseek/deepseek-v4-flash --max-turns N --output-format json
```

- Install: Node ≥ 22, then `npm i -g command-code` ([docs](https://commandcode.ai/docs))
- Auth: export `COMMAND_CODE_API_KEY` on the machine that runs the job. The CLI reads it at startup and it overrides `~/.commandcode/auth.json`.
- Headless flags: `-t` trusts the directory, `-p` is print mode, `--output-format json` is NDJSON (event frames + a final `type: result` line whose `finalText` is the answer). See [Headless Mode](https://commandcode.ai/docs/headless).

If the CLI or key is missing, use `--runner mock` (this is the default).

## Daily run

```bash
python -m paper_review run \
  --curation samples/2026-10-19-papers-curation.json \
  --date 2026-10-19 \
  --out artifacts \
  --runner mock
```

Production (Command Code on the box):

```bash
export COMMAND_CODE_API_KEY=...
python -m paper_review run \
  --curation path/to/curation.json \
  --date YYYY-MM-DD \
  --out artifacts \
  --runner cmd
```

The job is idempotent: extracts and LLM JSON are cached per arXiv id under `--cache` (default `.cache/papers`). Re-running the same day reuses them. `--force` rebuilds.

Output:

- `artifacts/review-YYYY-MM-DD.html` — self-contained page (figures inlined as data URIs)
- `artifacts/funnel-YYYY-MM-DD.json` — counts and the chosen ids

Funnel printed on stderr: `issue → topic-eligible → gate → extractable → top 5`.

## What the pipeline does

1. **Topic filter** — `eligible == true`
2. **Gate** — `upvotes >= 50`, or an allowlisted lab (`config/defaults.json`, or `allowlisted` in `org_label`) with traction ≥ 8
3. **Extractability** — full text (not abstract-only) **and** at least one real downloaded figure. Order: arXiv HTML → ar5iv → LaTeX source → PDF → abstract (abstract fails the gate)
4. **Rank** — by upvotes, at most two papers per category in the top 5 when alternatives exist
5. **LLM** — three JSON calls; figure ids must be allow-listed (`fig-1` …)
6. **HTML** — five cards, also-notable one-liners, skipped notes with reasons

One paper failing does not kill the job. Whole-job ceiling is 35 minutes.

## Tests

```bash
pytest
```

`tests/test_e2e.py` hits live arXiv with the mock runner and the sample JSON. First run downloads HTML/figures into `.cache/papers`.

## Sample input

`samples/2026-10-19-papers-curation.json` is a real HF Daily Papers curation dump (`papers[]` with `id`, `title`, `category`, `eligible`, `upvotes`, `org_label`, links, `summary`).

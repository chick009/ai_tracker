"""Command-line entry: python -m paper_review run ..."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from paper_review.intake import IntakeError, build_curation_for_date, save_curation
from paper_review.pipeline import run_daily


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="paper_review",
        description="HF Daily Papers → figure-backed methodology review HTML",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run the daily pipeline")
    run.add_argument(
        "--curation",
        type=Path,
        default=None,
        help="Curation JSON path. Omit to fetch the same-day HF Daily Papers for --date.",
    )
    run.add_argument(
        "--date",
        default=None,
        help="Collect date YYYY-MM-DD (required when --curation is omitted)",
    )
    run.add_argument("--out", required=True, type=Path, help="Output directory")
    run.add_argument("--cache", type=Path, default=Path(".cache/papers"), help="Per-paper extract cache")
    run.add_argument(
        "--runner",
        choices=("auto", "cmd", "mock"),
        default="mock",
        help="LLM backend. mock is the default so tests run without Command Code.",
    )
    run.add_argument("--model", default=None, help="Override Command Code model id")
    run.add_argument("--settings", type=Path, default=None, help="JSON with allowlist / thresholds")
    run.add_argument("--force", action="store_true", help="Ignore extract and LLM caches")
    run.add_argument(
        "--intake-limit",
        type=int,
        default=None,
        help="Keep only the top N papers by upvotes from the same-day HF issue (default 20)",
    )
    run.add_argument(
        "--curation-out",
        type=Path,
        default=None,
        help="When fetching live, also write the built curation JSON here",
    )

    build = sub.add_parser(
        "build-curation",
        help="Fetch same-day HF Daily Papers and write a curation JSON (top-N by upvotes)",
    )
    build.add_argument("--date", required=True, help="HF issue date YYYY-MM-DD")
    build.add_argument("--out", required=True, type=Path, help="Output curation JSON path")
    build.add_argument(
        "--intake-limit",
        type=int,
        default=None,
        help="Keep top N by upvotes (default from settings / 20)",
    )
    build.add_argument("--settings", type=Path, default=None, help="JSON with allowlist / intake_limit")
    cur = sub.add_parser(
        "curated",
        help="Cards for an already-filtered list (step1 all / step2 topic / step3 top-N JSON); no top-5 cut",
    )
    cur.add_argument("--date", required=True)
    cur.add_argument("--step1", required=True, type=Path, help="All collected papers JSON")
    cur.add_argument("--step2", required=True, type=Path, help="Topic-eligible papers JSON (with `topic`)")
    cur.add_argument("--top", required=True, type=Path, help="Final curated list JSON")
    cur.add_argument("--out-html", required=True, type=Path)
    cur.add_argument("--cache", type=Path, default=Path(".cache/papers"))
    cur.add_argument("--runner", choices=("auto", "cmd", "mock"), default="mock")
    cur.add_argument("--model", default="deepseek/deepseek-v4-flash")
    cur.add_argument("--topic-labels", type=Path, default=None, help="JSON id->reason for topic-dropped papers")
    cur.add_argument("--workers", type=int, default=3)
    cur.add_argument("--force", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _configure_logging()
    if args.cmd == "build-curation":
        from paper_review.config import load_settings

        settings = load_settings(args.settings)
        limit = args.intake_limit if args.intake_limit is not None else settings.intake_limit
        try:
            data = build_curation_for_date(
                args.date,
                intake_limit=limit,
                allowlist=settings.allowlist,
            )
        except IntakeError as exc:
            print(f"intake error: {exc}", file=sys.stderr)
            return 1
        save_curation(data, args.out)
        print(
            f"wrote {args.out}: issue {data['intake']['issue_total']} → "
            f"intake {data['intake']['kept']} (eligible {data['counts']['eligible']})",
            file=sys.stderr,
        )
        return 0

    if args.cmd == "curated":
        import json as _json

        from paper_review.curated import run_curated
        from paper_review.pipeline import resolve_runner

        labels = _json.loads(args.topic_labels.read_text(encoding="utf-8")) if args.topic_labels else None
        review = run_curated(
            date=args.date,
            step1=args.step1,
            step2=args.step2,
            top=args.top,
            out_html=args.out_html,
            cache_dir=args.cache,
            runner=resolve_runner(args.runner, args.model),
            topic_labels=labels,
            workers=args.workers,
            force=args.force,
        )
        print(
            " → ".join(f"{n} {label}" for label, n in review.funnel)
            + f"; failed {len(review.failed)}; wrote {args.out_html}",
            file=sys.stderr,
        )
        return 0 if not review.failed else 1

    if args.cmd == "run":
        if args.curation is None and not args.date:
            print("error: provide --curation or --date (same-day HF intake)", file=sys.stderr)
            return 2
        try:
            review = run_daily(
                args.curation,
                args.out,
                date=args.date,
                cache_dir=args.cache,
                runner=args.runner,
                settings_path=args.settings,
                force=args.force,
                model=args.model,
                curation_out=args.curation_out,
                intake_limit=args.intake_limit,
            )
        except IntakeError as exc:
            print(f"intake error: {exc}", file=sys.stderr)
            return 1
        f = review.funnel
        if f.intake is not None:
            print(
                f"funnel {f.issue_total} → {f.intake} → {f.topic_eligible} → "
                f"{f.gate} → {f.extractable} → {f.top_n}",
                file=sys.stderr,
            )
        else:
            print(
                f"funnel {f.issue_total} → {f.topic_eligible} → {f.gate} → "
                f"{f.extractable} → {f.top_n}",
                file=sys.stderr,
            )
        for i, card in enumerate(review.cards, start=1):
            print(
                f"{i}. {card.paper.id}  {card.paper.title}  ({card.paper.upvotes}⬆)",
                file=sys.stderr,
            )
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

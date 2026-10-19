"""Daily job: load curation → filter → extract → LLM cards → HTML."""

from __future__ import annotations

import json
import logging
import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from paper_review.config import Settings, load_settings
from paper_review.extract import extract_paper, make_session
from paper_review.figures import pick_method_figure, pick_results_figure
from paper_review.html_render import write_review
from paper_review.intake import IntakeError, build_curation_for_date, save_curation
from paper_review.llm.base import LLMError, LLMRunner
from paper_review.llm.command_code import CommandCodeRunner
from paper_review.llm.flow import run_card_flow
from paper_review.llm.mock import MockRunner
from paper_review.models import (
    DailyReview,
    Funnel,
    NotableLine,
    Paper,
    ReviewCard,
    SkippedNote,
)
from paper_review.select import rank_top, topic_and_gate

log = logging.getLogger("paper_review")


def load_curation(path: Path) -> tuple[list[Paper], str | None, str | None, int | None, int | None]:
    """Return papers, collect_date, hf_issue_date, issue_total, intake_kept.

    ``issue_total`` / ``intake_kept`` come from the curation ``intake`` block when
    present (live same-day fetch). Otherwise both are None and the pipeline
    treats ``len(papers)`` as the issue size.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    papers = [Paper.from_json(raw) for raw in data.get("papers") or []]
    intake = data.get("intake") or {}
    issue_total = intake.get("issue_total")
    intake_kept = intake.get("kept")
    if issue_total is not None:
        issue_total = int(issue_total)
    if intake_kept is not None:
        intake_kept = int(intake_kept)
    return papers, data.get("collect_date"), data.get("hf_issue_date"), issue_total, intake_kept


def resolve_runner(kind: str, model: str) -> LLMRunner:
    kind = (kind or "auto").lower()
    if kind == "mock":
        return MockRunner()
    if kind == "cmd":
        return CommandCodeRunner(model=model)
    if kind == "auto":
        if shutil.which("cmd") and os.environ.get("COMMAND_CODE_API_KEY"):
            return CommandCodeRunner(model=model)
        log.info("auto runner: no cmd/API key, using mock")
        return MockRunner()
    raise ValueError(f"unknown runner {kind!r} (use auto, cmd, or mock)")


def _extract_one(paper: Paper, cache_dir: Path, force: bool) -> tuple[Paper, object]:
    session = make_session()
    try:
        if not paper.arxiv_id:
            return paper, SkippedNote(paper.id, paper.title, "no arXiv id", paper.upvotes)
        result = extract_paper(
            paper.arxiv_id,
            cache_dir,
            abstract=paper.summary,
            force=force,
            session=session,
        )
        return paper, result
    except Exception as exc:  # noqa: BLE001
        log.exception("[%s] extract crashed", paper.id)
        return paper, SkippedNote(paper.id, paper.title, f"extract error: {exc}", paper.upvotes)
    finally:
        session.close()


def _with_model(settings: Settings, model: str | None) -> Settings:
    if not model:
        return settings
    return Settings(
        allowlist=settings.allowlist,
        min_upvotes=settings.min_upvotes,
        min_allowlist_traction=settings.min_allowlist_traction,
        top_n=settings.top_n,
        intake_limit=settings.intake_limit,
        max_per_category=settings.max_per_category,
        model=model,
        html_timeout_sec=settings.html_timeout_sec,
        source_timeout_sec=settings.source_timeout_sec,
        job_ceiling_sec=settings.job_ceiling_sec,
        extract_workers=settings.extract_workers,
        extra=settings.extra,
    )


def resolve_curation(
    *,
    curation: Path | None,
    date: str | None,
    settings: Settings,
    curation_out: Path | None = None,
) -> tuple[Path, int | None, int | None]:
    """Return (curation_path, issue_total, intake_kept).

    When ``curation`` is omitted, fetch the same-day HF issue for ``date``.
    """
    if curation is not None:
        return curation, None, None
    if not date:
        raise IntakeError("--date is required when --curation is omitted (same-day HF intake)")
    log.info(
        "building same-day curation from HF Daily Papers date=%s intake_limit=%d",
        date,
        settings.intake_limit,
    )
    data = build_curation_for_date(
        date,
        intake_limit=settings.intake_limit,
        allowlist=settings.allowlist,
    )
    out = curation_out or Path(f".cache/curation-{date}.json")
    save_curation(data, out)
    log.info("wrote curation %s (%d kept of %d)", out, data["intake"]["kept"], data["intake"]["issue_total"])
    return out, int(data["intake"]["issue_total"]), int(data["intake"]["kept"])


def run_daily(
    curation: Path | None,
    out_dir: Path,
    *,
    date: str | None = None,
    cache_dir: Path | None = None,
    runner: str = "mock",
    settings_path: Path | None = None,
    force: bool = False,
    model: str | None = None,
    curation_out: Path | None = None,
    intake_limit: int | None = None,
) -> DailyReview:
    settings: Settings = load_settings(settings_path)
    if intake_limit is not None:
        settings = Settings(
            allowlist=settings.allowlist,
            min_upvotes=settings.min_upvotes,
            min_allowlist_traction=settings.min_allowlist_traction,
            top_n=settings.top_n,
            intake_limit=intake_limit,
            max_per_category=settings.max_per_category,
            model=settings.model,
            html_timeout_sec=settings.html_timeout_sec,
            source_timeout_sec=settings.source_timeout_sec,
            job_ceiling_sec=settings.job_ceiling_sec,
            extract_workers=settings.extract_workers,
            extra=settings.extra,
        )
    settings = _with_model(settings, model)
    t0 = time.time()
    deadline = t0 + settings.job_ceiling_sec

    curation_path, live_issue_total, live_intake = resolve_curation(
        curation=curation,
        date=date,
        settings=settings,
        curation_out=curation_out,
    )
    papers, collect_date, hf_issue_date, file_issue_total, file_intake = load_curation(curation_path)
    collect_date = date or collect_date or time.strftime("%Y-%m-%d")
    issue_total = live_issue_total if live_issue_total is not None else file_issue_total
    intake_kept = live_intake if live_intake is not None else file_intake
    if issue_total is None:
        issue_total = len(papers)
    if intake_kept is None:
        intake_kept = len(papers)

    cache_dir = cache_dir or Path(".cache/papers")
    cache_dir.mkdir(parents=True, exist_ok=True)
    llm = resolve_runner(runner, settings.model)

    log.info(
        "loaded %d papers from %s (issue=%d intake=%d)",
        len(papers),
        curation_path,
        issue_total,
        intake_kept,
    )
    gated, eligible, skipped = topic_and_gate(papers, settings)
    log.info("topic-eligible %d → gate %d", len(eligible), len(gated))

    extracts: dict[str, object] = {}
    workers = max(1, settings.extract_workers)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(_extract_one, p, cache_dir, force) for p in gated]
        for fut in as_completed(futs):
            if time.time() > deadline:
                log.warning("job ceiling hit during extraction; remaining papers skipped")
                break
            paper, result = fut.result()
            extracts[paper.id] = result

    extractable_papers: list[Paper] = []
    extract_ok = {}
    for paper in gated:
        result = extracts.get(paper.id)
        if result is None:
            skipped.append(SkippedNote(paper.id, paper.title, "job ceiling before extract finished", paper.upvotes))
            continue
        if isinstance(result, SkippedNote):
            skipped.append(result)
            continue
        if not result.extractable:
            skipped.append(
                SkippedNote(
                    paper.id,
                    paper.title,
                    result.skip_reason or "not extractable",
                    paper.upvotes,
                )
            )
            continue
        extractable_papers.append(paper)
        extract_ok[paper.id] = result
        log.info(
            "[%s] extractable source=%s figs=%d",
            paper.id,
            result.source,
            len(result.figures),
        )

    top, leftover = rank_top(extractable_papers, settings)
    notable = [
        NotableLine(
            paper_id=p.id,
            title=p.title,
            category=p.category,
            upvotes=p.upvotes,
            hf_url=p.hf_url,
            org_label=p.org_label,
        )
        for p in leftover
    ]
    log.info("extractable %d → top %d, notable %d", len(extractable_papers), len(top), len(notable))

    cards: list[ReviewCard] = []
    for paper in top:
        if time.time() > deadline:
            skipped.append(SkippedNote(paper.id, paper.title, "job ceiling before LLM", paper.upvotes))
            continue
        extracted = extract_ok[paper.id]
        try:
            facts, critique, copy = run_card_flow(paper, extracted, llm, force=force)
        except LLMError as exc:
            log.warning("[%s] LLM failed: %s", paper.id, exc)
            skipped.append(SkippedNote(paper.id, paper.title, f"LLM failed: {exc}", paper.upvotes))
            continue
        method = pick_method_figure(extracted.figures, copy.method_figure_id)
        results = pick_results_figure(extracted.figures, method.fig_id if method else None, copy.results_figure_id)
        cards.append(
            ReviewCard(
                paper=paper,
                extract=extracted,
                facts=facts,
                critique=critique,
                copy=copy,
                method_figure=method,
                results_figure=results,
            )
        )

    funnel = Funnel(
        issue_total=issue_total,
        topic_eligible=len(eligible),
        gate=len(gated),
        extractable=len(extractable_papers),
        top_n=len(cards),
        intake=intake_kept,
    )
    review = DailyReview(
        collect_date=collect_date,
        hf_issue_date=hf_issue_date or collect_date,
        funnel=funnel,
        cards=cards,
        notable=notable,
        skipped=skipped,
        notes=[
            f"runner={llm.name} model={settings.model}",
            f"elapsed_sec={round(time.time() - t0, 1)}",
            f"intake_limit={settings.intake_limit}",
        ],
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / f"review-{collect_date}.html"
    write_review(review, html_path)
    funnel_path = out_dir / f"funnel-{collect_date}.json"
    funnel_path.write_text(
        json.dumps(
            {
                "collect_date": collect_date,
                "hf_issue_date": hf_issue_date or collect_date,
                "funnel": {
                    "issue_total": funnel.issue_total,
                    "intake": funnel.intake,
                    "topic_eligible": funnel.topic_eligible,
                    "gate": funnel.gate,
                    "extractable": funnel.extractable,
                    "top_n": funnel.top_n,
                },
                "top": [
                    {
                        "id": c.paper.id,
                        "title": c.paper.title,
                        "category": c.paper.category,
                        "upvotes": c.paper.upvotes,
                        "source": c.extract.source,
                        "figures": [f.fig_id for f in c.extract.figures],
                        "method_figure": c.method_figure.fig_id if c.method_figure else None,
                    }
                    for c in cards
                ],
                "notable": [n.paper_id for n in notable],
                "html": str(html_path),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    log.info("wrote %s", html_path)
    return review

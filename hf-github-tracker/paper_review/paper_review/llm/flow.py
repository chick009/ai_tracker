"""Run extract → critique → write for one paper, cached under the paper directory."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from paper_review.config import MAX_LLM_CHARS
from paper_review.figures import pick_method_figure, pick_results_figure
from paper_review.llm.base import LLMError, LLMRunner
from paper_review.llm.command_code import parse_json_object
from paper_review.llm.prompts import critique_prompt, extract_prompt, write_prompt
from paper_review.models import CardCopy, Critique, ExtractFacts, ExtractResult, Paper

log = logging.getLogger("paper_review")


def _clip_text(text: str, limit: int = MAX_LLM_CHARS) -> str:
    if len(text) <= limit:
        return text
    # Prefer method-ish sections when we have to cut.
    lower = text.lower()
    anchors = ("## method", "## approach", "## model", "introduction", "method")
    cut = 0
    for a in anchors:
        i = lower.find(a)
        if i != -1:
            cut = i
            break
    window = text[cut : cut + limit]
    return window if cut == 0 else text[: limit // 5] + "\n...\n" + window[: limit - limit // 5]


def _str_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return [str(value).strip()] if str(value).strip() else []


def facts_from_obj(obj: dict, figures) -> ExtractFacts:
    allow = {f.fig_id for f in figures}
    method_id = obj.get("method_figure_id") or None
    results_id = obj.get("results_figure_id") or None
    if method_id not in allow:
        method_id = None
    if results_id not in allow:
        results_id = None
    return ExtractFacts(
        problem=str(obj.get("problem") or "").strip(),
        core_method=str(obj.get("core_method") or "").strip(),
        components=_str_list(obj.get("components")),
        assumptions=_str_list(obj.get("assumptions")),
        datasets=_str_list(obj.get("datasets")),
        headline_results=_str_list(obj.get("headline_results")),
        limitations=_str_list(obj.get("limitations")),
        evidence=str(obj.get("evidence") or "").strip(),
        method_figure_id=method_id,
        results_figure_id=results_id,
    )


def critique_from_obj(obj: dict) -> Critique:
    strength = str(obj.get("support_strength") or "moderate").lower().strip()
    if strength not in {"strong", "moderate", "weak"}:
        strength = "moderate"
    return Critique(
        support_strength=strength,
        critique=str(obj.get("critique") or "").strip(),
        caveat=str(obj.get("caveat") or "").strip(),
    )


def copy_from_obj(obj: dict, facts: ExtractFacts, critique: Critique, figures) -> CardCopy:
    allow = {f.fig_id for f in figures}
    method_id = obj.get("method_figure_id") or facts.method_figure_id
    results_id = obj.get("results_figure_id") or facts.results_figure_id
    if method_id not in allow:
        method_id = None
    if results_id not in allow:
        results_id = None
    bullets = _str_list(obj.get("core_method"))
    if not bullets and facts.core_method:
        bullets = [facts.core_method]
    results = _str_list(obj.get("results")) or facts.headline_results[:3]
    return CardCopy(
        problem=str(obj.get("problem") or facts.problem).strip(),
        core_method=bullets[:5],
        results=results[:3],
        why_it_matters=str(obj.get("why_it_matters") or "").strip(),
        caveats=str(obj.get("caveats") or critique.caveat).strip(),
        method_figure_id=method_id,
        results_figure_id=results_id,
    )


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _complete_json(
    runner: LLMRunner,
    prompt: str,
    *,
    cache: Path,
    stage: str,
    paper_id: str,
    max_turns: int,
) -> dict:
    """Call the LLM and parse a JSON object, with one retry on parse failure.

    On parse failure the raw model text is saved to cache/<stage>.raw.txt
    (and .<stage>.raw.retry.txt on the retry) before raising.
    """
    last_err: LLMError | None = None
    for attempt in range(2):
        label = f"{paper_id}/{stage}" + (f"/retry{attempt}" if attempt else "")
        try:
            raw = runner.complete(prompt, max_turns=max_turns, label=label)
        except LLMError as exc:
            last_err = exc
            log.warning("[%s] %s runner error (attempt %d): %s", paper_id, stage, attempt + 1, exc)
            if attempt == 0:
                continue
            break
        try:
            return parse_json_object(raw)
        except LLMError as exc:
            last_err = exc
            suffix = ".raw.txt" if attempt == 0 else ".raw.retry.txt"
            raw_path = cache / f"{stage}{suffix}"
            try:
                raw_path.write_text(raw if isinstance(raw, str) else str(raw), encoding="utf-8")
                log.warning("[%s] %s parse failed (attempt %d); raw saved to %s", paper_id, stage, attempt + 1, raw_path)
            except OSError as write_exc:
                log.warning("[%s] could not save raw %s output: %s", paper_id, stage, write_exc)
            if attempt == 0:
                log.info("[%s] retrying %s once after parse failure", paper_id, stage)
                continue
    assert last_err is not None
    raise last_err


def run_card_flow(
    paper: Paper,
    extracted: ExtractResult,
    runner: LLMRunner,
    *,
    force: bool = False,
    max_turns: int = 4,
) -> tuple[ExtractFacts, Critique, CardCopy]:
    cache = Path(extracted.cache_dir) / "llm"
    cache.mkdir(parents=True, exist_ok=True)
    text = _clip_text(extracted.text)
    figures = extracted.figures

    extract_path = cache / "extract.json"
    critique_path = cache / "critique.json"
    write_path = cache / "write.json"

    extract_obj = None if force else _read_json(extract_path)
    if extract_obj is None:
        log.info("[%s] LLM extract via %s", paper.id, runner.name)
        extract_obj = _complete_json(
            runner,
            extract_prompt(paper, text, figures),
            cache=cache,
            stage="extract",
            paper_id=paper.id,
            max_turns=max_turns,
        )
        extract_path.write_text(json.dumps(extract_obj, indent=2, ensure_ascii=False), encoding="utf-8")
    facts = facts_from_obj(extract_obj, figures)
    if not facts.method_figure_id:
        picked = pick_method_figure(figures)
        facts.method_figure_id = picked.fig_id if picked else None
    if not facts.results_figure_id:
        picked = pick_results_figure(figures, facts.method_figure_id)
        facts.results_figure_id = picked.fig_id if picked else None

    critique_obj = None if force else _read_json(critique_path)
    if critique_obj is None:
        log.info("[%s] LLM critique via %s", paper.id, runner.name)
        critique_obj = _complete_json(
            runner,
            critique_prompt(paper, facts, text),
            cache=cache,
            stage="critique",
            paper_id=paper.id,
            max_turns=max_turns,
        )
        critique_path.write_text(json.dumps(critique_obj, indent=2, ensure_ascii=False), encoding="utf-8")
    critique = critique_from_obj(critique_obj)

    write_obj = None if force else _read_json(write_path)
    if write_obj is None:
        log.info("[%s] LLM write via %s", paper.id, runner.name)
        write_obj = _complete_json(
            runner,
            write_prompt(paper, facts, critique, figures),
            cache=cache,
            stage="write",
            paper_id=paper.id,
            max_turns=max_turns,
        )
        write_path.write_text(json.dumps(write_obj, indent=2, ensure_ascii=False), encoding="utf-8")
    copy = copy_from_obj(write_obj, facts, critique, figures)
    if not copy.method_figure_id:
        copy.method_figure_id = facts.method_figure_id
    if not copy.results_figure_id:
        copy.results_figure_id = facts.results_figure_id
    if not copy.core_method:
        raise LLMError(f"{paper.id}: write step produced no method bullets")
    return facts, critique, copy

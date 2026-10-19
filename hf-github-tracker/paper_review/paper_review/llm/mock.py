"""Deterministic offline runner so the pipeline can be tested without `cmd`."""

from __future__ import annotations

import json
import re

from paper_review.figures import pick_method_figure, pick_results_figure
from paper_review.llm.base import LLMRunner
from paper_review.models import Figure


def _sentences(text: str, n: int = 2) -> str:
    parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    parts = [p for p in parts if p]
    if not parts:
        return ""
    return " ".join(parts[:n])


def _first_clause(text: str) -> str:
    s = _sentences(text, 1)
    return s[:-1] if s.endswith(".") else s


def _field(prompt: str, label: str) -> str:
    m = re.search(
        rf"(?:^|\n){re.escape(label)}:\s*(.*?)(?=\n(?:TITLE|CATEGORY|ORG|ABSTRACT|FIGURE CATALOG|PAPER TEXT|EXTRACTED FACTS|FACTS|CRITIQUE caveat|Support|FIGURES|EXCERPT):|\Z)",
        prompt,
        re.S,
    )
    return m.group(1).strip() if m else ""


def _catalog_ids(prompt: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for m in re.finditer(r"- (fig-\d+) \[([^\]]*)\]: (.*)", prompt):
        found.append((m.group(1), m.group(3).strip()))
    return found


def _as_figures(figs: list[tuple[str, str]]) -> list[Figure]:
    out: list[Figure] = []
    for i, (fid, cap) in enumerate(figs, start=1):
        out.append(
            Figure(
                fig_id=fid,
                caption=cap,
                url="",
                file=f"{fid}.png",
                path="",
                index=i,
            )
        )
    return out


def _pick_method(figs: list[tuple[str, str]]) -> str | None:
    picked = pick_method_figure(_as_figures(figs))
    return picked.fig_id if picked else None


def _pick_results(figs: list[tuple[str, str]], method_id: str | None) -> str | None:
    picked = pick_results_figure(_as_figures(figs), method_id)
    return picked.fig_id if picked else None


def _numbers(text: str) -> list[str]:
    hits = []
    for sent in re.split(r"(?<=[.!?])\s+", text or ""):
        sent = sent.strip()
        if re.search(r"\d+(?:\.\d+)?%|\+\d+(?:\.\d+)?|\d+\.\d+\s*times", sent):
            hits.append(sent)
        if len(hits) == 3:
            break
    return hits


class MockRunner(LLMRunner):
    """Template the three JSON stages from title, abstract, and figure captions."""

    name = "mock"

    def complete(self, prompt: str, *, max_turns: int = 4, label: str = "") -> str:
        del max_turns, label
        title = _field(prompt, "TITLE")
        abstract = _field(prompt, "ABSTRACT") or _field(prompt, "EXCERPT")
        if "EXTRACTED FACTS" in prompt or prompt.strip().startswith("You are a skeptical"):
            return self._critique(title, prompt)
        if "Write a methodology card" in prompt:
            return self._write(title, prompt)
        return self._extract(title, abstract, prompt)

    def _extract(self, title: str, abstract: str, prompt: str) -> str:
        figs = _catalog_ids(prompt)
        method_id = _pick_method(figs)
        results_id = _pick_results(figs, method_id)
        problem = _sentences(abstract, 2) or f"{title} targets a gap that earlier methods leave open."
        method = (
            f"{title} is a concrete procedure: "
            f"{_first_clause(abstract) or 'it reuses what the model already knows and adds a small control step'}."
        )
        payload = {
            "problem": problem,
            "core_method": method,
            "components": _components(title, abstract),
            "assumptions": [
                "The evaluation tasks match the setting the method was built for.",
                "Reported numbers are taken from the paper text, not from outside knowledge.",
            ],
            "datasets": _datasets(abstract),
            "headline_results": _numbers(abstract) or ["The paper reports gains over the compared baselines on its main tasks."],
            "limitations": _limitations(abstract),
            "evidence": "Comparisons in the paper text against named baselines on the listed benchmarks.",
            "method_figure_id": method_id,
            "results_figure_id": results_id,
        }
        return json.dumps(payload, ensure_ascii=False)

    def _critique(self, title: str, prompt: str) -> str:
        facts_blob = prompt
        has_numbers = bool(re.search(r"\d+(?:\.\d+)?%|\+\d+", facts_blob))
        strength = "moderate" if has_numbers else "weak"
        caveat = (
            "The numbers are only as strong as the paper's own comparisons — treat them as the authors' report, not an independent audit."
        )
        critique = (
            f"{title} backs its claims with the benchmarks named in the extract. "
            f"{'Headline numbers appear in the text, which is useful, but the setup still reflects the authors’ chosen tasks.' if has_numbers else 'Few hard numbers were extracted, so the support is mostly qualitative.'} "
            "External validity beyond those tasks is not established here."
        )
        return json.dumps(
            {"support_strength": strength, "critique": critique, "caveat": caveat},
            ensure_ascii=False,
        )

    def _write(self, title: str, prompt: str) -> str:
        figs = _catalog_ids(prompt)
        method_id = _pick_method(figs)
        results_id = _pick_results(figs, method_id)
        method_cap = next((c for i, c in figs if i == method_id), "")
        abstract = _field(prompt, "ABSTRACT")
        steps = _walk_figure(title, method_cap, abstract)
        result_items = _numbers(abstract)
        if not result_items:
            results_block = re.search(r"Results:\s*(.*)", prompt)
            raw_results = results_block.group(1).strip() if results_block else ""
            result_items = [s.strip(" []'\"") for s in re.split(r",\s*", raw_results) if s.strip(" []'\"")]
        result_items = [r for r in result_items if r and r not in {"[]", ""}][:3]
        if not result_items:
            result_items = ["The authors report improvements on the main tasks they evaluate."]
        caveat_m = re.search(r"CRITIQUE caveat:\s*(.*)", prompt)
        caveat = (
            caveat_m.group(1).strip()
            if caveat_m
            else "Read the evaluation setup before copying the headline numbers."
        )
        payload = {
            "problem": _problem_line(title, prompt),
            "core_method": steps,
            "results": result_items,
            "why_it_matters": _why(abstract, title),
            "caveats": caveat,
            "method_figure_id": method_id,
            "results_figure_id": results_id,
        }
        return json.dumps(payload, ensure_ascii=False)


def _problem_line(title: str, prompt: str) -> str:
    abstract = _field(prompt, "ABSTRACT")
    if abstract:
        return _sentences(abstract, 2)
    facts = re.search(r"FACTS:\s*(.*)", prompt)
    blob = facts.group(1).strip() if facts else title
    return _sentences(blob, 2) or f"{title.split(':')[0]} attacks a gap left by earlier systems."


def _components(title: str, abstract: str) -> list[str]:
    named = re.findall(r"\b([A-Z][A-Za-z0-9]+(?:-[A-Z][A-Za-z0-9]+){0,3})\b", title + " " + abstract)
    skip = {"The", "We", "This", "Using", "Compared", "These", "Our", "In", "On", "For", "A"}
    uniq: list[str] = []
    for n in named:
        if n in skip or n in uniq or len(n) < 3:
            continue
        uniq.append(n)
        if len(uniq) == 5:
            break
    return uniq or [title.split(":")[0].strip() or title]


def _datasets(abstract: str) -> list[str]:
    found = re.findall(
        r"\b([A-Z][A-Za-z0-9]+(?:-[A-Za-z0-9]+)*(?:-v?\d+)?)\b",
        abstract,
    )
    likely = []
    for name in found:
        if any(k in name.lower() for k in ("bench", "world", "gym", "qa", "math", "code", "set")):
            if name not in likely:
                likely.append(name)
    return likely[:6] or ["as named in the paper text"]


def _limitations(abstract: str) -> list[str]:
    if re.search(r"limit|however|still |gap|only ", abstract, re.I):
        return ["The authors themselves flag remaining gaps in the evaluation or setting."]
    return ["Scope is the paper’s own tasks and models; broader transfer is not shown here."]


def _walk_figure(title: str, caption: str, abstract: str) -> list[str]:
    short = title.split(":")[0].strip()
    cap = re.sub(r"^(Figure|Fig\.?)\s*[A-Z]?\d+\s*:?\s*", "", caption or "", flags=re.I)
    cap = cap.replace("\\captionlead", "").strip()
    steps: list[str] = []
    if cap:
        steps.append(f"The method figure for {short} shows {cap[0].lower() + cap[1:] if cap else cap}".rstrip(".") + ".")
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", abstract or "") if len(s.strip()) > 40]
    for sent in sents[1:]:
        if sent not in steps:
            steps.append(sent if sent.endswith(".") else sent + ".")
        if len(steps) >= 4:
            break
    if len(steps) < 3:
        steps.append(
            f"{short} keeps the backbone fixed and adds a local control or scoring step on the model’s own traces."
        )
    return steps[:5]


def _why(abstract: str, title: str) -> str:
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", abstract or "") if s.strip()]
    if sents:
        return sents[-1] if sents[-1].endswith(".") else sents[-1] + "."
    short = title.split(":")[0].strip()
    return f"{short} turns a specific failure mode into a small, inspectable change rather than a new model family."

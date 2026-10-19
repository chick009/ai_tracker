"""Three-step prompts: extract facts → critique evidence → write the card."""

from __future__ import annotations

from paper_review.models import Critique, ExtractFacts, Figure, Paper


def figure_catalog(figures: list[Figure]) -> str:
    if not figures:
        return "(no downloaded figures)"
    lines = []
    for fig in figures:
        label = fig.label or fig.fig_id
        lines.append(f"- {fig.fig_id} [{label}]: {fig.caption}")
    return "\n".join(lines)


def extract_prompt(paper: Paper, text: str, figures: list[Figure]) -> str:
    return f"""You are extracting structured facts from a research paper for a reader who is not the author.

Return ONLY a JSON object with these keys:
- problem: string (what gap the paper tries to close)
- core_method: string (the actual method in plain words)
- components: array of strings (named parts of the method)
- assumptions: array of strings
- datasets: array of strings (only names that appear in the text)
- headline_results: array of strings (numbers ONLY if they appear in the text; otherwise qualitative)
- limitations: array of strings
- evidence: string (what was measured, against what)
- method_figure_id: one allow-listed id from the figure catalog that best shows the core method. Prefer an overview / framework / pipeline / architecture / "how it works" diagram. Do NOT pick a data-distribution, coverage, statistics, single-case-study, or results chart when an overview or pipeline figure exists. null only if the catalog is empty
- results_figure_id: one allow-listed id that shows results, or null

Do not invent figure ids. Do not invent numbers. Do not cite URLs.

TITLE: {paper.title}
CATEGORY: {paper.category}
ORG: {paper.org_label or paper.organization_field or ""}
ABSTRACT: {paper.summary}

FIGURE CATALOG (allow-listed ids only):
{figure_catalog(figures)}

PAPER TEXT:
{text}
"""


def critique_prompt(paper: Paper, facts: ExtractFacts, text_excerpt: str) -> str:
    return f"""You are a skeptical but fair reviewer. Judge how strongly the extracted evidence supports the paper's claims.

Return ONLY a JSON object:
- support_strength: one of "strong", "moderate", "weak"
- critique: 2–4 sentences, concrete (what is measured, what is missing)
- caveat: ONE short sentence in everyday words (no jargon, no acronyms without explanation) that the reader should remember, e.g. "Only tested against one baseline with one model, so the accuracy gain is suggestive."

Do not invent numbers. Do not mention figure URLs.

TITLE: {paper.title}
EXTRACTED FACTS:
{facts.problem}
Method: {facts.core_method}
Components: {facts.components}
Datasets: {facts.datasets}
Results: {facts.headline_results}
Limitations: {facts.limitations}
Evidence: {facts.evidence}

EXCERPT:
{text_excerpt[:8000]}
"""


def write_prompt(
    paper: Paper,
    facts: ExtractFacts,
    critique: Critique,
    figures: list[Figure],
) -> str:
    allowed = ", ".join(f.fig_id for f in figures) or "(none)"
    return f"""Write a methodology card for a smart reader who is NOT a specialist in this field. They told us jargon-heavy TL;DRs are hard to grasp, so explain like a good teacher.

STYLE RULES (follow all):
- Use everyday words and short sentences. Avoid acronyms and paper-specific jargon.
- If you must use one of the paper's own terms (e.g. "continuation carriers"), define it in plain words in parentheses the first time, with a concrete example, e.g. "carriers (saved pieces of finished work, like a file the agent already edited)".
- Never invent numbers, datasets, model names, or figure ids. Only use numbers that appear in the FACTS below.

Return ONLY a JSON object with these keys:
- problem: exactly 1 sentence: what goes wrong today, in plain words.
- core_method: array of 3 or 4 short steps that follow the method figure in order. Each step is 1–2 sentences, starts with a verb, and includes a tiny concrete example where possible ("e.g. ..."). You may end a step with "(fig-N)" using the chosen method figure id.
- results: array of 2 or 3 bullets, each with a real number taken from FACTS results (say what was measured and compared with what).
- why_it_matters: exactly 1 sentence, plain words.
- caveats: exactly 1 sentence, based on the critique caveat, in plain words.
- method_figure_id: one of [{allowed}]. Choose the overview / framework / pipeline / architecture figure that shows how the method works. Do NOT choose a data-distribution, coverage, statistics, results, or single-case-study figure if an overview or pipeline figure exists. Suggested by the extract step: {facts.method_figure_id or "none"}.
- results_figure_id: one of [{allowed}] showing results, or null.

TITLE: {paper.title}
ABSTRACT: {paper.summary}

FACTS:
Problem: {facts.problem}
Method: {facts.core_method}
Components: {facts.components}
Results: {facts.headline_results}
Evidence: {facts.evidence}

CRITIQUE caveat: {critique.caveat}
Support: {critique.support_strength}

FIGURES (allow-listed ids only):
{figure_catalog(figures)}
"""

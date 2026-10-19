"""Dataclasses shared across selection, extraction, LLM, and HTML."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Literal

from paper_review.arxiv_id import extract_arxiv_id

TextSource = Literal["arxiv_html", "ar5iv", "latex", "pdf", "abstract"]
SOURCE_LABELS: dict[str, str] = {
    "arxiv_html": "arXiv HTML",
    "ar5iv": "ar5iv",
    "latex": "LaTeX",
    "pdf": "PDF",
    "abstract": "abstract",
}


def source_label(source: str | None) -> str:
    if not source:
        return "unknown"
    return SOURCE_LABELS.get(source, source)


@dataclass
class Paper:
    id: str
    title: str
    category: str
    eligible: bool
    upvotes: int
    org_label: str | None
    organization_field: str | None
    hf_url: str | None
    arxiv_url: str | None
    github_repo: str | None
    summary: str
    core: bool = False
    project_page: str | None = None
    skip_reason: str | None = None
    arxiv_id: str | None = None

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Paper:
        arxiv_id = extract_arxiv_id(
            raw.get("id"),
            raw.get("arxiv_url"),
            raw.get("hf_url"),
        )
        return cls(
            id=str(raw.get("id") or arxiv_id or ""),
            title=str(raw.get("title") or ""),
            category=str(raw.get("category") or "Other"),
            eligible=bool(raw.get("eligible")),
            upvotes=int(raw.get("upvotes") or 0),
            org_label=raw.get("org_label"),
            organization_field=raw.get("organization_field"),
            hf_url=raw.get("hf_url"),
            arxiv_url=raw.get("arxiv_url"),
            github_repo=raw.get("github_repo"),
            summary=str(raw.get("summary") or raw.get("abstract") or ""),
            core=bool(raw.get("core")),
            project_page=raw.get("project_page"),
            skip_reason=raw.get("skip_reason"),
            arxiv_id=arxiv_id,
        )


@dataclass
class Figure:
    fig_id: str
    caption: str
    url: str
    file: str
    path: str
    label: str | None = None
    width: int = 0
    height: int = 0
    n_panels: int = 1
    html_id: str | None = None
    index: int = 0

    @property
    def allow_id(self) -> str:
        return self.fig_id


@dataclass
class ExtractResult:
    arxiv_id: str
    source: str | None
    source_url: str | None
    full_text: bool
    extractable: bool
    chars: int
    text: str
    figures: list[Figure]
    figures_found: int
    errors: list[str]
    seconds: float
    cache_dir: str
    skip_reason: str | None = None

    def to_meta(self) -> dict[str, Any]:
        return {
            "arxiv_id": self.arxiv_id,
            "source": self.source,
            "source_url": self.source_url,
            "full_text": self.full_text,
            "extractable": self.extractable,
            "chars": self.chars,
            "figures_found": self.figures_found,
            "figures": [asdict(f) for f in self.figures],
            "errors": self.errors,
            "seconds": self.seconds,
            "skip_reason": self.skip_reason,
        }


@dataclass
class ExtractFacts:
    problem: str
    core_method: str
    components: list[str]
    assumptions: list[str]
    datasets: list[str]
    headline_results: list[str]
    limitations: list[str]
    evidence: str
    method_figure_id: str | None
    results_figure_id: str | None = None


@dataclass
class Critique:
    support_strength: str
    critique: str
    caveat: str


@dataclass
class CardCopy:
    problem: str
    core_method: list[str]
    results: list[str]
    why_it_matters: str
    caveats: str
    method_figure_id: str | None = None
    results_figure_id: str | None = None


@dataclass
class SkippedNote:
    paper_id: str
    title: str
    reason: str
    upvotes: int = 0


@dataclass
class NotableLine:
    paper_id: str
    title: str
    category: str
    upvotes: int
    hf_url: str | None
    org_label: str | None


@dataclass
class Funnel:
    issue_total: int
    topic_eligible: int
    gate: int
    extractable: int
    top_n: int
    intake: int | None = None  # after same-day upvote top-N trim; None = no intake step

    def as_parts(self) -> list[tuple[str, int]]:
        parts: list[tuple[str, int]] = [("issue", self.issue_total)]
        if self.intake is not None:
            parts.append(("intake", self.intake))
        parts.extend(
            [
                ("topic-eligible", self.topic_eligible),
                ("gate", self.gate),
                ("extractable", self.extractable),
                ("top 5", self.top_n),
            ]
        )
        return parts


@dataclass
class ReviewCard:
    paper: Paper
    extract: ExtractResult
    facts: ExtractFacts
    critique: Critique
    copy: CardCopy
    method_figure: Figure | None
    results_figure: Figure | None


@dataclass
class DailyReview:
    collect_date: str
    hf_issue_date: str | None
    funnel: Funnel
    cards: list[ReviewCard]
    notable: list[NotableLine]
    skipped: list[SkippedNote]
    notes: list[str] = field(default_factory=list)


def json_ready(obj: Any) -> Any:
    if is_dataclass(obj) and not isinstance(obj, type):
        return {k: json_ready(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [json_ready(x) for x in obj]
    if isinstance(obj, dict):
        return {k: json_ready(v) for k, v in obj.items()}
    return obj

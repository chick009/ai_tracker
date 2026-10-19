"""Pipeline defaults. Labs and thresholds are overridable from a JSON file."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

USER_AGENT = "Mozilla/5.0 PaperDigest"
DEFAULT_MODEL = "deepseek/deepseek-v4-flash"
CMD_BIN = "cmd"

HTML_TIMEOUT_SEC = 20
SOURCE_TIMEOUT_SEC = 60
FIG_TIMEOUT_SEC = 30
JOB_CEILING_SEC = 35 * 60
PAPER_EXTRACT_WORKERS = 4
FIG_DOWNLOAD_WORKERS = 4

MAX_TEXT_CHARS = 60_000
MAX_LLM_CHARS = 24_000
MAX_FIGS = 6
MIN_HTML_CHARS = 5_000
MIN_LATEX_CHARS = 3_000
MIN_PDF_CHARS = 3_000
MIN_FIG_WIDTH = 200
MIN_FIG_HEIGHT = 120

TOP_N = 5
INTAKE_LIMIT = 20
MIN_UPVOTES = 50
MIN_ALLOWLIST_TRACTION = 8
MAX_PER_CATEGORY = 2

# Canonical lab tokens matched against org_label / organization_field (case-insensitive).
DEFAULT_ALLOWLIST: tuple[str, ...] = (
    "openai",
    "anthropic",
    "google deepmind",
    "deepmind",
    "google",
    "meta",
    "fair",
    "microsoft",
    "nvidia",
    "deepseek",
    "alibaba",
    "qwen",
    "bytedance",
    "tencent",
    "baidu",
    "huawei",
    "tsinghua",
    "peking university",
    "pku",
    "stanford",
    "berkeley",
    "mit",
    "cmu",
    "carnegie mellon",
    "oxford",
    "cambridge",
    "princeton",
    "harvard",
    "nus",
    "national university of singapore",
    "hkust",
    "shanghai ai",
    "naver",
    "salesforce",
    "amazon",
    "apple",
    "ibm",
    "mistral",
    "cohere",
    "xai",
    "moonshot",
    "zhipu",
    "intern",
)


@dataclass(frozen=True)
class Settings:
    allowlist: tuple[str, ...] = DEFAULT_ALLOWLIST
    min_upvotes: int = MIN_UPVOTES
    min_allowlist_traction: int = MIN_ALLOWLIST_TRACTION
    top_n: int = TOP_N
    intake_limit: int = INTAKE_LIMIT
    max_per_category: int = MAX_PER_CATEGORY
    model: str = DEFAULT_MODEL
    html_timeout_sec: int = HTML_TIMEOUT_SEC
    source_timeout_sec: int = SOURCE_TIMEOUT_SEC
    job_ceiling_sec: int = JOB_CEILING_SEC
    extract_workers: int = PAPER_EXTRACT_WORKERS
    extra: dict = field(default_factory=dict)


def load_settings(path: Path | None) -> Settings:
    if path is None:
        return Settings()
    data = json.loads(path.read_text(encoding="utf-8"))
    allow = data.get("allowlist")
    return Settings(
        allowlist=tuple(allow) if allow else DEFAULT_ALLOWLIST,
        min_upvotes=int(data.get("min_upvotes", MIN_UPVOTES)),
        min_allowlist_traction=int(data.get("min_allowlist_traction", MIN_ALLOWLIST_TRACTION)),
        top_n=int(data.get("top_n", TOP_N)),
        intake_limit=int(data.get("intake_limit", INTAKE_LIMIT)),
        max_per_category=int(data.get("max_per_category", MAX_PER_CATEGORY)),
        model=str(data.get("model", DEFAULT_MODEL)),
        html_timeout_sec=int(data.get("html_timeout_sec", HTML_TIMEOUT_SEC)),
        source_timeout_sec=int(data.get("source_timeout_sec", SOURCE_TIMEOUT_SEC)),
        job_ceiling_sec=int(data.get("job_ceiling_sec", JOB_CEILING_SEC)),
        extract_workers=int(data.get("extract_workers", PAPER_EXTRACT_WORKERS)),
        extra=data,
    )

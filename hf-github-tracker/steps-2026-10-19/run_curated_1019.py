import json, logging, sys
from pathlib import Path
sys.path.insert(0, "/workspace/paper_review/paper_review")
from paper_review.curated import run_curated
from paper_review.llm.command_code import CommandCodeRunner
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
S = Path("/workspace/ai-tracker/steps-1019")
r = run_curated(
    date="2026-10-19", step1=S/"step1.json", step2=S/"step2.json", top=S/"step3_top12.json",
    out_html=Path("/workspace/ai-tracker/review-out/review-2026-10-19.html"),
    cache_dir=Path("/workspace/paper_review/paper_review/.cache/papers"),
    runner=CommandCodeRunner(model="deepseek/deepseek-v4-flash"),
    topic_labels=json.loads((S/"topic_dropped_labels.json").read_text()), workers=3,
)
print("FUNNEL", r.funnel)
for c in r.cards: print("CARD", c.paper.id, c.paper.upvotes, c.method_figure.fig_id if c.method_figure else None, c.paper.title[:50])
for f in r.failed: print("FAILED", f.paper.id, f.reason)

#!/usr/bin/env python3
import json, re, hashlib
from pathlib import Path
from collections import Counter

BASE = Path("/home/box/agent-data/agents/4835c489-2b48-4bd6-8ed5-5d41e32d8a1f/blog-watch")
CARDS = BASE / "cards"
WEEKS = BASE / "weeks"
SOURCES = BASE / "sources"
CARDS.mkdir(parents=True, exist_ok=True)
WEEKS.mkdir(parents=True, exist_ok=True)

NOW = "2026-09-11"
WEEK_START = "2026-09-07"
WEEK_END = "2026-09-11"
CUTOFF = "2026-09-04"

def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:80]

def card_id(title, url, date):
    base = slugify(title) or hashlib.sha1(url.encode()).hexdigest()[:12]
    return f"{base}-{date[:10]}"

TYPE_MAP = {
    "changelog_features": "changelog_feature",
    "changelog_feature": "changelog_feature",
    "changelog_bugfix": "changelog_bugfix",
    "changelog_refactor": "changelog_refactor",
    "applications": "application_case_study",
    "application_case_study": "application_case_study",
    "engineering": "engineering",
    "research": "research",
    "model_release_benchmark": "model_release_benchmark",
    "model_release_benchmark_with_implementations": "model_release_implementation",
    "model_release_implementation": "model_release_implementation",
}

PRIORITY_HINTS = {
    "https://openai.com/index/gpt-6-astra-next-generation-work/": "P0",
    "https://api-docs.deepseek.com/zh-cn/updates/#时间-2026-09-10": "P0",
    "https://cognition.com/blog/swe-2": "P0",
    "https://code.claude.com/docs/en/changelog": "P1",
    "https://cognition.com/blog/series-e": "P3",
    "https://mistral.ai/news/mistral-makes-sovereign-open-weight-ai-to-frontier/": "P3",
}

def default_priority(typ, title):
    tl = title.lower()
    if typ == "model_release_benchmark":
        return "P0"
    if typ == "changelog_feature" and any(k in tl for k in ["worktree", "self-host", "shell", "memory"]):
        return "P0"
    if typ in ("engineering", "application_case_study", "model_release_implementation"):
        return "P1"
    if typ == "research":
        return "P2"
    if typ == "changelog_bugfix":
        return "P3"
    return "P2"

SOURCE_NAMES = {
  "deepseek.json": "DeepSeek / API Updates",
  "cognition.json": "Cognition / Blog",
  "openai-news.json": "OpenAI",
  "anthropic-research.json": "Anthropic / Research",
  "claude-code-changelog.json": "Claude Code / Changelog",
  "codex-changelog.json": "Codex / Changelog",
  "opencode-changelog.json": "OpenCode / Changelog",
  "pi-changelog.json": "Pi / Changelog",
  "huggingface.json": "Hugging Face / Blog",
  "mistral.json": "Mistral",
  "nvidia-developer.json": "NVIDIA / Developer Blog",
  "openrouter.json": "OpenRouter",
  "snowflake.json": "Snowflake / Blog",
  "cursor-blog.json": "Cursor / Blog",
  "cursor-changelog.json": "Cursor / Changelog",
  "xai.json": "xAI",
  "inco.json": "Inco AI",
  "google-research.json": "Google Research",
  "poolside.json": "Poolside",
  "qwen.json": "Qwen",
}

astra_pricing = json.loads((BASE / "samples/gpt-6-astra-pricing.json").read_text())
astra_bench = json.loads((BASE / "samples/gpt-6-astra-benchmark-comparisons.json").read_text())

EXTRA_TAKEAWAYS = {
  "https://openai.com/index/gpt-6-astra-next-generation-work/": [
    "OpenAI positions GPT-6 Astra as next-gen model for work / agentic coding",
    "Official pricing + peer benchmark table published (see metrics)"
  ],
  "https://api-docs.deepseek.com/zh-cn/updates/#时间-2026-09-10": [
    "V4.1-Flash: native multimodal; API id deepseek-flash; publisher claims beats V4 Pro on cost/speed/quality",
    "Peak pricing (CNY/MTok): input cache-miss 2 / output 8; off-peak half; V4 Pro routing to Flash planned 2026-09-14 BJT"
  ],
  "https://cognition.com/blog/swe-2": [
    "SWE-2: FrontierCode 1.1 Main 50.0% vs Fable 5.1 50.9%; Cognition claims ~64% cheaper than Fable 5.1",
    "Trained with multi-effort RL in one run; available in Devin Desktop/CLI"
  ],
  "https://cognition.com/blog/factoring-rsa-260": [
    "Devin-assisted GPU lattice siever factored RSA-260; ~10x cheaper than prior public SOTA (publisher claim)",
    "Framed as disaggregated-compute / agentic HPC case study"
  ],
  "https://cognition.com/blog/welcoming-dioxus": [
    "Dioxus team joins Cognition; continued OSS support; expertise aimed at Devin VM / computer-use / testing"
  ],
  "https://cognition.com/blog/series-e": [
    "Funding announcement ($2B+ / $48B); low signal for builders beyond product name-drops"
  ],
}

EXTRA_METRICS = {
  "https://openai.com/index/gpt-6-astra-next-generation-work/": {
    "pricing": {
      "currency": "USD",
      "unit": "per MTok",
      "input": astra_pricing["standard"]["short_context"]["input"],
      "output": astra_pricing["standard"]["short_context"]["output"],
      "cached_input": astra_pricing["standard"]["short_context"]["cached_input"],
      "cache_writes": astra_pricing["standard"]["short_context"]["cache_writes"],
      "tiers_note": "standard short-context; long/batch/flex/fast tiers in samples/gpt-6-astra-pricing.json",
      "source_url": astra_pricing["source_url"]
    },
    "benchmarks": [
      {
        "name": b["name"],
        "scores": b["scores"],
        "delta": b["delta"],
        "source_url": astra_bench["source_url"],
        "caveat": astra_bench["source_note"]
      }
      for b in astra_bench["benchmarks"][:2]
    ]
  },
  "https://api-docs.deepseek.com/zh-cn/updates/#时间-2026-09-10": {
    "pricing": {
      "currency": "CNY",
      "unit": "per MTok",
      "input": 2.0,
      "output": 8.0,
      "cached_input": 0.04,
      "tiers_note": "deepseek-flash = V4.1-Flash; PEAK rates (BJT weekday 09-12 & 14-18); OFF-PEAK = half. Official CNY page.",
      "source_url": "https://api-docs.deepseek.com/zh-cn/quick_start/pricing"
    },
    "benchmarks": [
      {
        "name": "Terminal-Bench 4.0",
        "scores": {"deepseek-v4.1-flash": 31.2},
        "delta": "publisher-reported absolute; peer deltas not on same table",
        "source_url": "https://api-docs.deepseek.com/zh-cn/updates/",
        "caveat": "DeepSeek-reported; harness/effort per their notes"
      },
      {
        "name": "GPQA Diamond",
        "scores": {"deepseek-v4.1-flash": 90.9},
        "delta": "publisher-reported absolute",
        "source_url": "https://api-docs.deepseek.com/zh-cn/updates/",
        "caveat": "DeepSeek-reported"
      }
    ]
  },
  "https://cognition.com/blog/swe-2": {
    "pricing": {
      "status": "unpublished",
      "note": "No public $/MTok table; cost claims are relative (e.g. 64% cheaper than Fable 5.1)"
    },
    "benchmarks": [
      {
        "name": "FrontierCode 1.1 Main",
        "scores": {
          "swe-2": "50.0%",
          "claude-fable-5.1": "50.9%",
          "gpt-6-astra": "53.3%",
          "gpt-5.6-sol": "47.5%",
          "swe-1.7": "42.0%"
        },
        "delta": "SWE-2 -0.9pp vs Fable 5.1; -3.3pp vs Astra (Cognition table)",
        "source_url": "https://cognition.com/blog/swe-2",
        "caveat": "Cognition-reported table"
      },
      {
        "name": "Terminal-Bench 4",
        "scores": {
          "swe-2": "27.3%",
          "claude-fable-5.1": "55.8%",
          "gpt-6-astra": "57.9%"
        },
        "delta": "SWE-2 trails Fable/Astra on TB4 in same table",
        "source_url": "https://cognition.com/blog/swe-2",
        "caveat": "Same-table comparison"
      }
    ]
  }
}

cards = []
seen = set()

def add_card(post, source_name):
    url = post.get("url")
    if not url or url in seen:
        return
    date = str(post.get("date") or "")[:10]
    if not date or date < CUTOFF or date > WEEK_END:
        return
    seen.add(url)
    cat = post.get("category") or "applications"
    typ = TYPE_MAP.get(cat, "application_case_study")
    title = post.get("title") or ""
    pr = PRIORITY_HINTS.get(url) or default_priority(typ, title)
    takeaways = EXTRA_TAKEAWAYS.get(url)
    if not takeaways:
        summary = (post.get("summary") or "").strip()
        takeaways = [summary[:220]] if summary else [f"See source: {title}"]
    card = {
        "id": card_id(title, url, date),
        "title": title,
        "url": url,
        "source": source_name,
        "published_at": f"{date}T00:00:00Z",
        "type": typ,
        "priority": pr,
        "tags": post.get("tags") or [],
        "key_takeaway": takeaways,
        "first_seen": post.get("first_seen") or NOW,
        "last_seen": NOW,
    }
    if url in EXTRA_METRICS:
        card["metrics"] = EXTRA_METRICS[url]
    cards.append(card)

for path in sorted(SOURCES.glob("*.json")):
    data = json.loads(path.read_text())
    posts = data.get("posts") or []
    name = SOURCE_NAMES.get(path.name) or data.get("name") or path.stem
    for post in posts:
        add_card(post, name)

for c in cards:
    (CARDS / f"{c['id']}.json").write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n")

by_type = {}
for c in cards:
    by_type.setdefault(c["type"], []).append(c)
for t in by_type:
    by_type[t].sort(key=lambda x: (x["priority"], x["published_at"]))

type_summaries = {}
if by_type.get("model_release_benchmark"):
    type_summaries["model_release_benchmark"] = "Astra (USD pricing+peer benches); DeepSeek-V4.1-Flash (CNY peak/off-peak + publisher benches); Cognition SWE-2 (relative cost, no public $/MTok)."
if by_type.get("engineering"):
    type_summaries["engineering"] = "NVIDIA EPD multimodal serving + CUDA Rust; OpenRouter in-region routing; Cognition RSA-260 GPU siever."
if by_type.get("application_case_study"):
    type_summaries["application_case_study"] = "Memory agents, shell tool, Snowflake CoCo/Astra, Mistral legacy modernization, Cognition Dioxus; Series E funding is P3."
if by_type.get("changelog_feature"):
    type_summaries["changelog_feature"] = "Claude Code worktree/cache, Codex 0.154, OpenCode 1.18.30, Pi 0.85.x — exclude pure model-picker noise."
if by_type.get("research"):
    type_summaries["research"] = "Anthropic Fermat formalization; OpenAI Navier-Stokes — archive weight."
if by_type.get("changelog_bugfix"):
    type_summaries["changelog_bugfix"] = "Minor OpenCode patch."

synthesis = (
  "本週主軸：OpenAI Astra、DeepSeek-V4.1-Flash、Cognition SWE-2 同時推進模型／coding-agent 成本曲線；"
  "工程側聚焦 serving 拆分與 agent harness；應用側出現記憶型 agent、資料管線 coding agent、legacy modernization。"
)

week = {
  "week_start": WEEK_START,
  "week_end": WEEK_END,
  "generated_at": "2026-09-11T12:10:00+08:00",
  "synthesis": synthesis,
  "type_summaries": type_summaries,
  "card_ids": [c["id"] for c in sorted(cards, key=lambda x: (x["priority"], x["published_at"]))],
  "cards_by_type": {t: [c["id"] for c in lst] for t, lst in by_type.items()},
  "ingest": {
    "base_url": "https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1",
    "cards_endpoint": "https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1/tracker-cards-ingest",
    "weeks_endpoint": "https://psmjbqbnkoioicbasqlm.supabase.co/functions/v1/tracker-weeks-ingest",
    "auth_header": "Authorization: Bearer <TRACKER_INGEST_TOKEN>",
    "metrics_optional": True,
    "weeks_body": {
      "week_start": WEEK_START,
      "synthesis": synthesis,
      "type_summaries": type_summaries,
    },
  },
  "stats": {
    "card_count": len(cards),
    "by_type": {k: len(v) for k, v in by_type.items()},
    "by_priority": dict(Counter(c["priority"] for c in cards)),
  },
}
(WEEKS / f"{WEEK_START}.json").write_text(json.dumps(week, ensure_ascii=False, indent=2) + "\n")

ingest_cards = []
for c in cards:
    body = {k: c[k] for k in ["id", "title", "url", "source", "published_at", "type", "priority", "tags", "key_takeaway"] if k in c}
    if "metrics" in c:
        body["metrics"] = c["metrics"]
    ingest_cards.append(body)
(WEEKS / f"{WEEK_START}-cards-ingest.json").write_text(json.dumps(ingest_cards, ensure_ascii=False, indent=2) + "\n")

print("cards", len(cards))
print("by_type", week["stats"]["by_type"])
print("by_priority", week["stats"]["by_priority"])
for c in sorted(cards, key=lambda x: (x["priority"], x["type"])):
    print(c["priority"], c["type"], c["id"][:55], "metrics" if "metrics" in c else "-")

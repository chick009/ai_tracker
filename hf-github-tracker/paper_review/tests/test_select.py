from paper_review.config import Settings
from paper_review.models import Paper
from paper_review.select import is_allowlisted, passes_gate, rank_top, topic_and_gate


def _paper(**kwargs) -> Paper:
    base = dict(
        id="x",
        title="T",
        category="Agents",
        eligible=True,
        upvotes=10,
        org_label=None,
        organization_field=None,
        hf_url=None,
        arxiv_url=None,
        github_repo=None,
        summary="",
        arxiv_id="2610.00001",
    )
    base.update(kwargs)
    return Paper(**base)


def test_gate_upvotes():
    ok, reason = passes_gate(_paper(upvotes=50), Settings())
    assert ok and reason == "upvotes"
    ok, reason = passes_gate(_paper(upvotes=49), Settings())
    assert not ok


def test_gate_allowlisted_org_label():
    p = _paper(upvotes=12, org_label="Tsinghua（allowlisted；核心 Agents）")
    ok, reason = passes_gate(p, Settings())
    assert ok and reason == "allowlisted_lab"


def test_gate_allowlisted_but_no_traction():
    p = _paper(upvotes=2, org_label="Stanford（allowlisted；核心 Agents）")
    ok, _ = passes_gate(p, Settings())
    assert not ok


def test_allowlist_token_match():
    p = _paper(organization_field="NVIDIA", org_label="NVIDIA（核心主題免 gate）")
    assert is_allowlisted(p, Settings().allowlist)


def test_topic_filter_drops_ineligible():
    papers = [
        _paper(id="a", eligible=True, upvotes=80),
        _paper(id="b", eligible=False, upvotes=900, skip_reason="off topic"),
    ]
    gated, eligible, skipped = topic_and_gate(papers, Settings())
    assert [p.id for p in eligible] == ["a"]
    assert [p.id for p in gated] == ["a"]
    assert skipped[0].paper_id == "b"


def test_rank_avoids_five_of_same_category():
    papers = [_paper(id=f"a{i}", category="Agents", upvotes=100 - i) for i in range(6)]
    papers += [
        _paper(id="r1", category="Reasoning", upvotes=40),
        _paper(id="s1", category="Systems & efficiency", upvotes=39),
        _paper(id="m1", category="Multimodal", upvotes=38),
    ]
    top, leftover = rank_top(papers, Settings(top_n=5, max_per_category=2))
    cats = [p.category for p in top]
    assert cats.count("Agents") <= 2
    assert "Reasoning" in cats
    assert len(top) == 5
    assert leftover

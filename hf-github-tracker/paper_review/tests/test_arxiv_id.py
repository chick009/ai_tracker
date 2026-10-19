from paper_review.arxiv_id import extract_arxiv_id, normalize_arxiv_id


def test_plain_id():
    assert normalize_arxiv_id("2610.21601") == "2610.21601"


def test_strips_version():
    assert normalize_arxiv_id("2610.21601v3") == "2610.21601"


def test_abs_url():
    assert normalize_arxiv_id("https://arxiv.org/abs/2610.21601") == "2610.21601"


def test_pdf_url():
    assert normalize_arxiv_id("https://arxiv.org/pdf/2610.21601.pdf") == "2610.21601"


def test_html_url():
    assert normalize_arxiv_id("https://arxiv.org/html/2610.21601") == "2610.21601"


def test_hf_url():
    assert extract_arxiv_id(None, "https://huggingface.co/papers/2610.21601") == "2610.21601"


def test_old_style_id():
    assert normalize_arxiv_id("https://arxiv.org/abs/cs/0211011") == "cs/0211011"


def test_prefers_paper_id():
    assert extract_arxiv_id("2610.22200", "https://arxiv.org/abs/9999.99999") == "2610.22200"


def test_rejects_noise():
    assert normalize_arxiv_id("not-a-paper") is None
    assert normalize_arxiv_id("") is None

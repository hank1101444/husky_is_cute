import re

import pytest
import responses

from onboarding_map.github_fetcher import (
    GitHubError,
    InvalidRepoUrl,
    RateLimitError,
    fetch_snapshot,
    parse_repo_url,
)

API = "https://api.github.com/repos"

DECISIONS_MD = """# Decisions Log

## 2026-09-21 — Initial code steward
**What:** Hank is the initial code steward.

## 2026-11-23 — MVP scope
**What:** map + review + questions.
"""


@pytest.fixture
def rsps():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as r:
        yield r


@pytest.fixture
def mocked_repo(rsps):
    base = f"{API}/o/r"
    rsps.get(base, json={"default_branch": "main"})
    rsps.get(f"{base}/readme", body="# Readme\nHello")
    rsps.get(f"{base}/git/trees/main", json={"truncated": False, "tree": [
        {"path": "src", "type": "tree"},
        {"path": "src/app.py", "type": "blob"},
        {"path": "README.md", "type": "blob"},
        {"path": "DECISIONS.md", "type": "blob"},
    ]})
    rsps.get(f"{base}/contents/DECISIONS.md", body=DECISIONS_MD)
    rsps.get(f"{base}/pulls", json=[
        {"number": 4, "title": "Add fetcher", "body": None, "html_url": "https://github.com/o/r/pull/4"},
    ])
    rsps.get(f"{base}/issues/4/comments", json=[
        {"id": 99, "body": "We delay because of dirty reads", "user": {"login": "bob"},
         "html_url": "https://github.com/o/r/pull/4#issuecomment-99"},
    ])
    rsps.get(f"{base}/pulls/4/reviews", json=[
        {"id": 501, "body": "Keep the cache; the API is slow", "state": "APPROVED", "user": {"login": "carol"},
         "html_url": "https://github.com/o/r/pull/4#pullrequestreview-501"},
        {"id": 502, "body": "", "state": "APPROVED", "user": {"login": "dave"},
         "html_url": "https://github.com/o/r/pull/4#pullrequestreview-502"},
        {"id": 503, "body": None, "state": "COMMENTED", "user": {"login": "erin"},
         "html_url": "https://github.com/o/r/pull/4#pullrequestreview-503"},
    ])
    rsps.get(f"{base}/issues", json=[
        {"number": 5, "title": "Bug", "body": "it breaks", "html_url": "https://github.com/o/r/issues/5"},
        {"number": 4, "title": "Add fetcher", "body": "", "html_url": "https://github.com/o/r/pull/4",
         "pull_request": {}},
    ])
    rsps.get(f"{base}/commits", json=[
        {"sha": "abc1234deadbeef", "commit": {"message": "init\n\nlonger body"},
         "html_url": "https://github.com/o/r/commit/abc1234"},
        {"sha": "fff0000aaaa", "commit": {"message": "fix"}, "html_url": "https://github.com/o/r/commit/fff0000"},
    ])
    return rsps


@pytest.mark.parametrize("url", [
    "https://github.com/hank1101444/husky_is_cute",
    "https://github.com/hank1101444/husky_is_cute/",
    "https://github.com/hank1101444/husky_is_cute.git",
    "  github.com/hank1101444/husky_is_cute/tree/main/docs ",
    "http://github.com/hank1101444/husky_is_cute",
    "https://www.github.com/hank1101444/husky_is_cute",
    "https://github.com/hank1101444/husky_is_cute?tab=readme-ov-file",
    "https://github.com/hank1101444/husky_is_cute#readme",
])
def test_parse_repo_url_variants(url):
    assert parse_repo_url(url) == ("hank1101444", "husky_is_cute")


@pytest.mark.parametrize("url", ["", "   ", "https://gitlab.com/a/b", "https://github.com/onlyowner",
                                 "https://github.com/o/r r"])
def test_parse_repo_url_rejects(url):
    with pytest.raises(InvalidRepoUrl):
        parse_repo_url(url)


def test_fetch_snapshot_full(mocked_repo):
    snap = fetch_snapshot("https://github.com/o/r")
    ids = snap.source_ids()
    assert {
        "README", "PR#4", "PR#4/comment:99", "ISSUE#5", "commit:abc1234", "commit:fff0000",
        "DECISION:2026-09-21 — Initial code steward", "DECISION:2026-11-23 — MVP scope",
        "file:src/app.py",
    } <= ids
    assert "ISSUE#4" not in ids
    assert "file:src" not in ids
    assert snap.default_branch == "main"
    assert snap.truncation == {}
    assert "dirty reads" in snap.source("PR#4/comment:99").text
    assert snap.source("PR#4").text == ""
    assert snap.source("commit:abc1234").title == "init"


def test_pr_review_with_body_becomes_source(mocked_repo):
    snap = fetch_snapshot("https://github.com/o/r")
    review = snap.source("PR#4/review:501")
    assert review is not None
    assert review.type == "pr_review"
    assert "carol" in review.title
    assert "APPROVED" in review.title
    assert review.url == "https://github.com/o/r/pull/4#pullrequestreview-501"
    assert "API is slow" in review.text


def test_pr_review_without_body_is_skipped(mocked_repo):
    snap = fetch_snapshot("https://github.com/o/r")
    assert [s.id for s in snap.sources if s.type == "pr_review"] == ["PR#4/review:501"]


def test_pr_reviews_404_does_not_fail_fetch(mocked_repo):
    mocked_repo.replace(responses.GET, f"{API}/o/r/pulls/4/reviews", status=404, json={"message": "Not Found"})
    snap = fetch_snapshot("https://github.com/o/r")
    assert any(c.request.url.endswith("/pulls/4/reviews") for c in mocked_repo.calls)
    assert "PR#4/comment:99" in snap.source_ids()
    assert not any(s.type == "pr_review" for s in snap.sources)


def test_token_sent_as_bearer(mocked_repo):
    fetch_snapshot("https://github.com/o/r", token="tok")
    assert mocked_repo.calls[0].request.headers["Authorization"] == "Bearer tok"


def test_no_auth_header_without_token(mocked_repo):
    fetch_snapshot("https://github.com/o/r")
    assert "Authorization" not in mocked_repo.calls[0].request.headers


def test_fetch_snapshot_empty_repo(rsps):
    base = f"{API}/o/empty"
    rsps.get(base, json={"default_branch": "main"})
    rsps.get(f"{base}/readme", status=404, json={"message": "Not Found"})
    rsps.get(f"{base}/git/trees/main", status=409, json={"message": "Git Repository is empty."})
    rsps.get(f"{base}/contents/DECISIONS.md", status=404, json={"message": "Not Found"})
    rsps.get(f"{base}/pulls", json=[])
    rsps.get(f"{base}/issues", json=[])
    rsps.get(f"{base}/commits", status=409, json={"message": "Git Repository is empty."})
    snap = fetch_snapshot("https://github.com/o/empty")
    assert snap.tree == []
    assert snap.sources == []


def test_truncation_recorded(rsps):
    base = f"{API}/o/r"
    rsps.get(base, json={"default_branch": "main"})
    rsps.get(f"{base}/readme", status=404)
    rsps.get(f"{base}/git/trees/main", json={"truncated": True, "tree": [{"path": "a.py", "type": "blob"}]})
    rsps.get(f"{base}/contents/DECISIONS.md", status=404)
    rsps.get(f"{base}/pulls", json=[
        {"number": n, "title": f"pr {n}", "body": "", "html_url": f"https://github.com/o/r/pull/{n}"}
        for n in range(1, 31)
    ])
    rsps.get(re.compile(rf"{re.escape(base)}/issues/\d+/comments"), json=[])
    rsps.get(re.compile(rf"{re.escape(base)}/pulls/\d+/reviews"), json=[])
    rsps.get(f"{base}/issues", json=[])
    rsps.get(f"{base}/commits", json=[])
    snap = fetch_snapshot("https://github.com/o/r")
    assert snap.truncation["pulls"] == "只顯示最新 30 筆"
    assert "tree" in snap.truncation
    assert "issues" not in snap.truncation


def test_rate_limit_error(rsps):
    rsps.get(f"{API}/o/r", status=403, headers={"X-RateLimit-Remaining": "0"},
             json={"message": "API rate limit exceeded"})
    with pytest.raises(RateLimitError, match="GITHUB_TOKEN"):
        fetch_snapshot("https://github.com/o/r")


def test_repo_not_found(rsps):
    rsps.get(f"{API}/o/missing", status=404, json={"message": "Not Found"})
    with pytest.raises(GitHubError, match="找不到"):
        fetch_snapshot("https://github.com/o/missing")


def test_invalid_url_raises_before_network(rsps):
    with pytest.raises(InvalidRepoUrl):
        fetch_snapshot("https://gitlab.com/a/b")


def test_raw_text_decoded_as_utf8_without_charset(rsps):
    base = f"{API}/o/zh"
    rsps.get(base, json={"default_branch": "main"})
    rsps.get(f"{base}/readme", body="# 專案說明".encode("utf-8"), content_type="text/plain")
    rsps.get(f"{base}/git/trees/main", json={"tree": []})
    rsps.get(f"{base}/contents/DECISIONS.md", status=404)
    rsps.get(f"{base}/pulls", json=[])
    rsps.get(f"{base}/issues", json=[])
    rsps.get(f"{base}/commits", json=[])
    assert fetch_snapshot("https://github.com/o/zh").source("README").text == "# 專案說明"


def test_progress_callback_reports_steps(mocked_repo):
    steps = []
    fetch_snapshot("https://github.com/o/r", progress=steps.append)
    assert any("README" in s for s in steps)
    assert any("PR 留言 1/1" in s for s in steps)
    assert any("commit" in s for s in steps)

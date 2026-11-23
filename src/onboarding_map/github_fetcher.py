"""Fetch repository context from the GitHub REST API into a RepoSnapshot."""

from __future__ import annotations

import re
import sys
from typing import Callable

import requests

from onboarding_map.config import FetchLimits, load_settings
from onboarding_map.models import RepoSnapshot, SourceItem

API_BASE = "https://api.github.com"
TIMEOUT_S = 15
_URL_RE = re.compile(
    r"^(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?(?:[/?#].*)?$"
)


class GitHubError(Exception):
    """User-facing (zh-TW) error while reading a repository."""


class RateLimitError(GitHubError):
    pass


class InvalidRepoUrl(GitHubError):
    pass


def parse_repo_url(url: str) -> tuple[str, str]:
    match = _URL_RE.match(url.strip())
    if not match:
        raise InvalidRepoUrl("請輸入 GitHub repo 網址，例如 https://github.com/owner/repo")
    return match.group(1), match.group(2)


class _Client:
    def __init__(self, owner: str, repo: str, token: str | None):
        self.base = f"{API_BASE}/repos/{owner}/{repo}"
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/vnd.github+json"
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def get(self, path: str, *, raw: bool = False, params: dict | None = None,
            missing_ok: tuple[int, ...] = ()) -> requests.Response | None:
        headers = {"Accept": "application/vnd.github.raw"} if raw else None
        try:
            resp = self.session.get(self.base + path, headers=headers, params=params, timeout=TIMEOUT_S)
        except (requests.ConnectionError, requests.Timeout) as exc:
            raise GitHubError("無法連線到 GitHub") from exc
        if resp.status_code in (403, 429) and resp.headers.get("X-RateLimit-Remaining") == "0":
            raise RateLimitError("GitHub API 次數已用完，請在 .env 設定 GITHUB_TOKEN 或稍後再試")
        if resp.status_code in missing_ok:
            return None
        if resp.status_code == 404 and path == "":
            raise GitHubError("找不到這個 repo，或它是私人 repo（需要 GITHUB_TOKEN）")
        if not resp.ok:
            raise GitHubError(f"GitHub API 錯誤（{resp.status_code}）")
        return resp


def _utf8(resp: requests.Response) -> str:
    """Raw GitHub content is UTF-8 even when the response has no charset."""
    return resp.content.decode("utf-8", errors="replace")


def _decision_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    for line in text.splitlines():
        if line.startswith("## "):
            sections.append((line[3:].strip(), ""))
        elif sections:
            heading, body = sections[-1]
            sections[-1] = (heading, body + line + "\n")
    return [(h, b.strip()) for h, b in sections]


def fetch_snapshot(url: str, token: str | None = None, limits: FetchLimits = FetchLimits(),
                   progress: Callable[[str], None] | None = None) -> RepoSnapshot:
    """Read the repo. ``progress`` (optional) receives short zh-TW step messages for the UI."""
    report = progress or (lambda _msg: None)
    owner, repo = parse_repo_url(url)
    report(f"連線到 GitHub：{owner}/{repo}")
    gh = _Client(owner, repo, token)
    repo_url = f"https://github.com/{owner}/{repo}"
    branch = gh.get("").json().get("default_branch", "main")
    sources: list[SourceItem] = []
    truncation: dict[str, str] = {}

    report("讀取 README 與檔案清單")
    readme = gh.get("/readme", raw=True, missing_ok=(404,))
    if readme is not None:
        sources.append(SourceItem(id="README", type="readme", title="README", url=f"{repo_url}#readme",
                                  text=_utf8(readme)))

    tree_resp = gh.get(f"/git/trees/{branch}", params={"recursive": "1"}, missing_ok=(404, 409))
    tree: list[str] = []
    if tree_resp is not None:
        data = tree_resp.json()
        tree = [e["path"] for e in data.get("tree", []) if e.get("type") == "blob"]
        if data.get("truncated"):
            truncation["tree"] = "檔案太多，GitHub 只回傳部分檔案清單"

    report("讀取 DECISIONS.md")
    decisions = gh.get("/contents/DECISIONS.md", raw=True, missing_ok=(404,))
    if decisions is not None:
        for heading, body in _decision_sections(_utf8(decisions)):
            sources.append(SourceItem(id=f"DECISION:{heading}", type="decision", title=heading,
                                      url=f"{repo_url}/blob/{branch}/DECISIONS.md", text=body))

    report("讀取 PR 清單")
    pulls = gh.get("/pulls", params={"state": "all", "sort": "updated", "direction": "desc",
                                     "per_page": limits.pulls}).json()
    if len(pulls) >= limits.pulls:
        truncation["pulls"] = f"只顯示最新 {limits.pulls} 筆"
    for i, pr in enumerate(pulls, start=1):
        n = pr["number"]
        report(f"讀取 PR 留言 {i}/{len(pulls)}")
        sources.append(SourceItem(id=f"PR#{n}", type="pr", title=pr.get("title") or "",
                                  url=pr.get("html_url") or f"{repo_url}/pull/{n}", text=pr.get("body") or ""))
        for c in gh.get(f"/issues/{n}/comments").json():
            login = (c.get("user") or {}).get("login", "?")
            sources.append(SourceItem(id=f"PR#{n}/comment:{c['id']}", type="pr_comment",
                                      title=f"PR #{n} comment by {login}",
                                      url=c.get("html_url") or f"{repo_url}/pull/{n}", text=c.get("body") or ""))
        report(f"讀取 PR review {i}/{len(pulls)}")
        reviews = gh.get(f"/pulls/{n}/reviews", missing_ok=(404,))
        for r in reviews.json() if reviews is not None else []:
            if not r.get("body"):
                continue
            login = (r.get("user") or {}).get("login", "?")
            sources.append(SourceItem(id=f"PR#{n}/review:{r['id']}", type="pr_review",
                                      title=f"PR #{n} review by {login} ({r.get('state') or '?'})",
                                      url=r.get("html_url") or f"{repo_url}/pull/{n}", text=r["body"]))

    report("讀取 issue")
    issues = gh.get("/issues", params={"state": "all", "per_page": limits.issues}).json()
    if len(issues) >= limits.issues:
        truncation["issues"] = f"只顯示最新 {limits.issues} 筆"
    for issue in issues:
        if "pull_request" in issue:
            continue
        n = issue["number"]
        sources.append(SourceItem(id=f"ISSUE#{n}", type="issue", title=issue.get("title") or "",
                                  url=issue.get("html_url") or f"{repo_url}/issues/{n}",
                                  text=issue.get("body") or ""))

    report("讀取 commit 紀錄")
    commits_resp = gh.get("/commits", params={"per_page": limits.commits}, missing_ok=(409,))
    commits = commits_resp.json() if commits_resp is not None else []
    if len(commits) >= limits.commits:
        truncation["commits"] = f"只顯示最新 {limits.commits} 筆"
    for c in commits:
        sha = c["sha"][:7]
        message = (c.get("commit") or {}).get("message") or ""
        sources.append(SourceItem(id=f"commit:{sha}", type="commit", title=message.splitlines()[0] if message else sha,
                                  url=c.get("html_url") or f"{repo_url}/commit/{sha}", text=message))

    return RepoSnapshot(owner=owner, repo=repo, url=repo_url, default_branch=branch, tree=tree,
                        sources=sources, truncation=truncation)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python -m onboarding_map.github_fetcher <github-repo-url>")
    snapshot = fetch_snapshot(sys.argv[1], token=load_settings().github_token)
    sys.stdout.reconfigure(encoding="utf-8")
    print(snapshot.model_dump_json(indent=2))

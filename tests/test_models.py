import pytest

from pathlib import Path

from onboarding_map.config import FetchLimits, load_settings
from onboarding_map.models import NO_REASON, Claim, OnboardingMapDraft, RepoSnapshot, SourceItem


def test_snapshot_source_ids_include_files_and_sources():
    snap = RepoSnapshot(
        owner="o", repo="r", url="https://github.com/o/r", default_branch="main",
        tree=["src/a.py"], truncation={},
        sources=[SourceItem(id="PR#1", type="pr", title="t", url="u", text="b")],
    )
    assert snap.source_ids() == {"file:src/a.py", "PR#1"}
    assert snap.source("PR#1").title == "t"
    assert snap.source("PR#9") is None


def test_load_settings_defaults(monkeypatch):
    for k in ("ANTHROPIC_MODEL", "GITHUB_TOKEN", "ONBOARDING_DB_PATH"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr("onboarding_map.config.load_dotenv", lambda *a, **k: None)
    s = load_settings()
    assert s.anthropic_model == "claude-sonnet-5-5"
    assert s.github_token is None
    assert s.db_path == Path("data/onboarding.db")


def test_load_settings_empty_token_is_none(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "")
    monkeypatch.setattr("onboarding_map.config.load_dotenv", lambda *a, **k: None)
    assert load_settings().github_token is None


def test_fetch_limits_defaults():
    assert FetchLimits() == FetchLimits(pulls=30, issues=30, commits=50)


def test_draft_json_roundtrip():
    d = OnboardingMapDraft(modules=[], reading_order=[])
    assert OnboardingMapDraft.model_validate_json(d.model_dump_json()) == d


def test_no_reason_literal():
    assert NO_REASON == "無紀錄的理由"


@pytest.mark.parametrize("text, ai_text, expected", [
    ("Bob 改寫的說法", "AI 的說法", True),
    ("AI 的說法", "AI 的說法", False),
    ("AI 的說法", None, False),
])
def test_claim_human_edited(text, ai_text, expected):
    claim = Claim(id="m:a:purpose", kind="purpose", module_id="a", text=text,
                  source_ids=[], valid=True, ai_text=ai_text)
    assert claim.human_edited is expected

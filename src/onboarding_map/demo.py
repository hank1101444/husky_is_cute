"""Offline demo mode: a predefined sample snapshot and map, so the app can be tried without an API key.

Nothing here calls Claude or GitHub. The sample describes this repository; the source texts are short
excerpts from it, and the map claims were written by hand to look like a typical AI draft. The UI labels
it as sample data (``RepoSnapshot.demo``).
"""

from __future__ import annotations

from onboarding_map.models import (
    NO_REASON,
    DraftModule,
    DraftReadingItem,
    DraftRelation,
    OnboardingMapDraft,
    RepoSnapshot,
    SourceItem,
)

DEMO_REPO_URL = "https://github.com/hank1101444/husky_is_cute"

_TREE = [
    "README.md",
    "DECISIONS.md",
    "src/onboarding_map/app.py",
    "src/onboarding_map/config.py",
    "src/onboarding_map/github_fetcher.py",
    "src/onboarding_map/mapper.py",
    "src/onboarding_map/models.py",
    "src/onboarding_map/prompts.py",
    "src/onboarding_map/store.py",
]

_DECISION_STACK = "DECISION:2026-11-23 — MVP stack: Streamlit + SQLite"
_DECISION_LANGUAGE = "DECISION:2026-11-23 — Map language and review gate"


def demo_snapshot() -> RepoSnapshot:
    return RepoSnapshot(
        owner="hank1101444", repo="husky_is_cute", url=DEMO_REPO_URL, default_branch="main",
        tree=list(_TREE), demo=True,
        sources=[
            SourceItem(id="README", type="readme", title="README", url=f"{DEMO_REPO_URL}#readme",
                       text="The Onboarding Map reads a GitHub repository (README, file tree, pull requests "
                            "and their comments, issues, commit messages, DECISIONS.md) and asks Claude to "
                            "draft a map. Every statement cites its source."),
            SourceItem(id=_DECISION_STACK, type="decision", title=_DECISION_STACK.removeprefix("DECISION:"),
                       url=f"{DEMO_REPO_URL}/blob/main/DECISIONS.md",
                       text="The MVP is a single Python Streamlit app with a local SQLite database. "
                            "Why: Python only and the fastest path to a working two-person demo before CP2."),
            SourceItem(id=_DECISION_LANGUAGE, type="decision", title=_DECISION_LANGUAGE.removeprefix("DECISION:"),
                       url=f"{DEMO_REPO_URL}/blob/main/DECISIONS.md",
                       text="When no source explains something the map says exactly 「無紀錄的理由」. "
                            "Flagged claims are hidden from the new member."),
            SourceItem(id="PR#10", type="pr", title="feat: fetch PR review bodies as sources",
                       url=f"{DEMO_REPO_URL}/pull/10",
                       text="The GitHub fetcher now also reads PR reviews, so code steward review text "
                            "becomes a citable source."),
            SourceItem(id="PR#11", type="pr", title="fix: accept decorated NO_REASON in claim validation",
                       url=f"{DEMO_REPO_URL}/pull/11",
                       text="validate now recognises 「無紀錄的理由」 even when the model adds whitespace, "
                            "「」 quotes or final punctuation."),
        ],
    )


def demo_draft() -> OnboardingMapDraft:
    return OnboardingMapDraft(
        modules=[
            DraftModule(
                id="fetcher", name="GitHub 讀取",
                purpose="從 GitHub API 讀取 README、檔案清單、PR 與留言、issue、commit 和 DECISIONS.md，整理成來源清單。",
                purpose_source_ids=["README", "PR#10"],
                key_files=["src/onboarding_map/github_fetcher.py"],
                relations=[DraftRelation(target_module_id="mapper", reason="讀到的來源清單交給 mapper 產生地圖。",
                                         source_ids=["README"])],
            ),
            DraftModule(
                id="mapper", name="地圖產生與驗證",
                purpose="把來源送給 Claude 產生地圖草稿，再用程式檢查每條說法引用的來源是否存在。",
                purpose_source_ids=["README", "PR#11"],
                key_files=["src/onboarding_map/mapper.py", "src/onboarding_map/prompts.py"],
                relations=[DraftRelation(target_module_id="store", reason=NO_REASON, source_ids=[])],
            ),
            DraftModule(
                id="store", name="資料儲存",
                purpose="用 SQLite 保存地圖、每條說法的檢查狀態，以及新成員的提問與回答。",
                purpose_source_ids=[_DECISION_STACK],
                key_files=["src/onboarding_map/store.py"],
                relations=[],
            ),
            DraftModule(
                id="app", name="網頁介面",
                purpose="Streamlit 網頁，既有成員檢查地圖並回答問題，新成員閱讀地圖並提問。",
                purpose_source_ids=[_DECISION_STACK, _DECISION_LANGUAGE],
                key_files=["src/onboarding_map/app.py"],
                relations=[DraftRelation(target_module_id="store", reason="畫面上的確認、修改、標記和問答都寫進資料庫。",
                                         source_ids=[_DECISION_STACK])],
            ),
        ],
        reading_order=[
            DraftReadingItem(target="README.md", reason="先了解這個工具要解決的問題和兩個角色。", source_ids=["README"]),
            DraftReadingItem(target="DECISIONS.md", reason="記錄了技術選擇和地圖語言等重要決定的理由。",
                             source_ids=[_DECISION_STACK, _DECISION_LANGUAGE]),
            DraftReadingItem(target="src/onboarding_map/mapper.py", reason=NO_REASON, source_ids=[]),
        ],
    )

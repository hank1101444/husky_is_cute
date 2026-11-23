import pytest

from onboarding_map.models import (
    DraftModule,
    DraftReadingItem,
    DraftRelation,
    OnboardingMapDraft,
    RepoSnapshot,
    SourceItem,
)


@pytest.fixture
def snap() -> RepoSnapshot:
    return RepoSnapshot(
        owner="o", repo="r", url="https://github.com/o/r", default_branch="main",
        tree=["src/a.py", "src/b.py"], truncation={},
        sources=[
            SourceItem(id="README", type="readme", title="README", url="https://github.com/o/r#readme",
                       text="# Demo\nA calls B."),
            SourceItem(id="PR#1", type="pr", title="Split a and b", url="https://github.com/o/r/pull/1",
                       text="Split so b can be tested alone."),
        ],
    )


@pytest.fixture
def good_draft() -> OnboardingMapDraft:
    return OnboardingMapDraft(
        modules=[
            DraftModule(
                id="a", name="入口模組", purpose="負責接收輸入並呼叫 b。", purpose_source_ids=["README"],
                key_files=["src/a.py"],
                relations=[DraftRelation(target_module_id="b", reason="a 呼叫 b 處理資料。", source_ids=["PR#1"])],
            ),
            DraftModule(
                id="b", name="處理模組", purpose="處理資料。", purpose_source_ids=["file:src/b.py"],
                key_files=["src/b.py"], relations=[],
            ),
        ],
        reading_order=[DraftReadingItem(target="src/a.py", reason="程式入口。", source_ids=["README"])],
    )

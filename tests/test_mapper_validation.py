import pytest

from onboarding_map.mapper import validate
from onboarding_map.models import NO_REASON, ValidationResult
from onboarding_map.prompts import SYSTEM_PROMPT, build_user_prompt


def claim(result: ValidationResult, claim_id: str):
    return next(c for c in result.claims if c.id == claim_id)


def test_valid_draft_has_no_problems(snap, good_draft):
    res = validate(good_draft, snap)
    assert all(c.valid for c in res.claims)
    assert res.invalid_key_files == {}
    assert {c.id for c in res.claims} == {"m:a:purpose", "m:b:purpose", "m:a:rel:b", "r:0"}


def test_claim_texts_and_kinds(snap, good_draft):
    res = validate(good_draft, snap)
    assert claim(res, "m:a:purpose").kind == "purpose"
    assert claim(res, "m:a:purpose").text == "負責接收輸入並呼叫 b。"
    assert claim(res, "m:a:rel:b").text == "入口模組 ↔ 處理模組：a 呼叫 b 處理資料。"
    assert claim(res, "m:a:rel:b").module_id == "a"
    assert claim(res, "r:0").text == "src/a.py：程式入口。"
    assert claim(res, "r:0").module_id is None


def test_purpose_without_source_is_invalid(snap, good_draft):
    good_draft.modules[0].purpose_source_ids = []
    c = claim(validate(good_draft, snap), "m:a:purpose")
    assert not c.valid and c.problems


def test_unknown_source_id_is_invalid(snap, good_draft):
    good_draft.modules[0].relations[0].source_ids = ["PR#999"]
    c = claim(validate(good_draft, snap), "m:a:rel:b")
    assert not c.valid and any("PR#999" in p for p in c.problems)


def test_no_reason_with_empty_sources_is_valid(snap, good_draft):
    rel = good_draft.modules[0].relations[0]
    rel.reason, rel.source_ids = NO_REASON, []
    assert claim(validate(good_draft, snap), "m:a:rel:b").valid


def test_no_reason_with_sources_is_invalid(snap, good_draft):
    rel = good_draft.modules[0].relations[0]
    rel.reason, rel.source_ids = NO_REASON, ["PR#1"]
    assert not claim(validate(good_draft, snap), "m:a:rel:b").valid


def test_reason_without_sources_is_invalid(snap, good_draft):
    good_draft.reading_order[0].source_ids = []
    assert not claim(validate(good_draft, snap), "r:0").valid


def test_invented_key_file_reported(snap, good_draft):
    good_draft.modules[0].key_files.append("src/ghost.py")
    assert validate(good_draft, snap).invalid_key_files == {"a": ["src/ghost.py"]}


def test_relation_to_unknown_module_is_invalid(snap, good_draft):
    good_draft.modules[0].relations[0].target_module_id = "zzz"
    assert not claim(validate(good_draft, snap), "m:a:rel:zzz").valid


def test_user_prompt_contains_ids_and_tree(snap):
    p = build_user_prompt(snap)
    assert "[PR#1]" in p and "src/a.py" in p and "Split so b can be tested alone." in p


def test_user_prompt_lists_truncation(snap):
    snap.truncation = {"pulls": "只顯示最新 30 筆"}
    assert "只顯示最新 30 筆" in build_user_prompt(snap)


def test_system_prompt_rules():
    assert NO_REASON in SYSTEM_PROMPT
    assert "繁體中文" in SYSTEM_PROMPT


def test_duplicate_relation_ids_are_unique(snap, good_draft):
    dup = good_draft.modules[0].relations[0].model_copy()
    dup.reason = "另一個原因。"
    good_draft.modules[0].relations.append(dup)
    ids = [c.id for c in validate(good_draft, snap).claims]
    assert len(ids) == len(set(ids))
    assert {"m:a:rel:b", "m:a:rel:b:2"} <= set(ids)


def test_reading_target_must_exist(snap, good_draft):
    good_draft.reading_order[0].target = "src/ghost.py"
    c = claim(validate(good_draft, snap), "r:0")
    assert not c.valid and any("src/ghost.py" in p for p in c.problems)


def test_reading_target_may_be_source_id(snap, good_draft):
    good_draft.reading_order[0].target = "PR#1"
    assert claim(validate(good_draft, snap), "r:0").valid


NO_REASON_VARIANTS = ["無紀錄的理由。", "「無紀錄的理由」", "  無紀錄的理由  ", "無紀錄的理由."]
GUESSED_REASONS = ["這裡無紀錄的理由是效能", "無紀錄的理由，但可能是為了效能"]


def _set_reason(draft, kind, reason, source_ids):
    """Set the reason of the relation (m:a:rel:b) or reading (r:0) claim; return its claim id."""
    item = draft.modules[0].relations[0] if kind == "relation" else draft.reading_order[0]
    item.reason, item.source_ids = reason, source_ids
    return "m:a:rel:b" if kind == "relation" else "r:0"


@pytest.mark.parametrize("kind", ["relation", "reading"])
@pytest.mark.parametrize("reason", NO_REASON_VARIANTS)
def test_no_reason_variant_with_empty_sources_is_valid(snap, good_draft, kind, reason):
    claim_id = _set_reason(good_draft, kind, reason, [])
    c = claim(validate(good_draft, snap), claim_id)
    assert c.valid, c.problems


@pytest.mark.parametrize("kind", ["relation", "reading"])
@pytest.mark.parametrize("reason", NO_REASON_VARIANTS)
def test_no_reason_variant_with_sources_is_invalid(snap, good_draft, kind, reason):
    claim_id = _set_reason(good_draft, kind, reason, ["PR#1"])
    c = claim(validate(good_draft, snap), claim_id)
    assert c.problems == ["標示「無紀錄的理由」時不應附上來源"]


@pytest.mark.parametrize("kind", ["relation", "reading"])
@pytest.mark.parametrize("reason", GUESSED_REASONS)
def test_guessed_reason_is_not_treated_as_no_reason(snap, good_draft, kind, reason):
    claim_id = _set_reason(good_draft, kind, reason, [])
    c = claim(validate(good_draft, snap), claim_id)
    assert c.problems == ["理由沒有附上來源"]

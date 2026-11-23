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

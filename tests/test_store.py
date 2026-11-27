import pytest

from onboarding_map.mapper import validate
from onboarding_map.store import Store


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "nested" / "t.db")


@pytest.fixture
def saved(store, snap, good_draft):
    return store.save_map(snap, good_draft, validate(good_draft, snap))


def get_claim(store, map_id, claim_id):
    return next(c for c in store.load_map(map_id).claims if c.id == claim_id)


def test_save_and_load_roundtrip(store, saved, snap, good_draft):
    m = store.load_map(saved)
    assert m.repo_url == "https://github.com/o/r"
    assert m.snapshot == snap
    assert m.draft == good_draft
    assert m.invalid_key_files == {}
    assert len(m.claims) == 4
    assert all(c.status == "inferred" for c in m.claims)


def test_claims_keep_draft_order(store, saved):
    assert [c.id for c in store.load_map(saved).claims] == ["m:a:purpose", "m:a:rel:b", "m:b:purpose", "r:0"]


def test_confirm_marks_verified(store, saved):
    store.review_claim(saved, "m:a:purpose", "confirm")
    assert get_claim(store, saved, "m:a:purpose").status == "verified"


def test_edit_keeps_ai_text(store, saved):
    store.review_claim(saved, "m:a:purpose", "edit", "新的說明")
    c = get_claim(store, saved, "m:a:purpose")
    assert (c.status, c.text) == ("verified", "新的說明")
    assert c.ai_text == "負責接收輸入並呼叫 b。"


def test_edit_requires_text(store, saved):
    with pytest.raises(ValueError):
        store.review_claim(saved, "m:a:purpose", "edit", "  ")


def test_last_review_wins_and_stats_count_once(store, saved):
    store.review_claim(saved, "m:a:purpose", "confirm")
    store.review_claim(saved, "m:a:purpose", "flag")
    store.review_claim(saved, "r:0", "edit", "x")
    store.review_claim(saved, "r:0", "confirm")
    store.review_claim(saved, "m:b:purpose", "confirm")
    s = store.stats(saved)
    assert (s.total, s.flagged, s.edited, s.accepted_without_edit) == (4, 1, 1, 1)
    assert s.review_minutes is not None and s.review_minutes >= 0


def test_stats_without_reviews(store, saved):
    s = store.stats(saved)
    assert (s.accepted_without_edit, s.edited, s.flagged, s.review_minutes, s.questions) == (0, 0, 0, None, 0)


def test_second_map_same_repo_is_separate(store, saved, snap, good_draft):
    store.review_claim(saved, "m:a:purpose", "flag")
    qid = store.ask(saved, "a", "舊地圖的問題")
    new_id = store.save_map(snap, good_draft, validate(good_draft, snap))
    assert new_id != saved
    maps = store.list_maps()
    assert [m[0] for m in maps] == [new_id, saved]
    assert get_claim(store, saved, "m:a:purpose").status == "flagged"
    assert get_claim(store, new_id, "m:a:purpose").status == "inferred"
    assert [q.id for q in store.questions(saved)] == [qid]
    assert store.questions(new_id) == []


def test_questions_flow(store, saved):
    qid = store.ask(saved, "a", "為什麼要這樣分？")
    assert store.questions(saved, "a")[0].answer is None
    store.answer(qid, "因為 PR#1")
    q = store.questions(saved, "a")[0]
    assert q.answer == "因為 PR#1" and q.answered_at is not None
    assert store.questions(saved, "b") == []
    assert store.stats(saved).questions == 1


def test_blank_question_rejected(store, saved):
    with pytest.raises(ValueError):
        store.ask(saved, "a", "   ")


def test_blank_answer_rejected(store, saved):
    qid = store.ask(saved, "a", "問題")
    with pytest.raises(ValueError):
        store.answer(qid, "")


def test_persists_across_instances(store, saved, tmp_path):
    store.review_claim(saved, "m:a:purpose", "confirm")
    again = Store(tmp_path / "nested" / "t.db")
    assert get_claim(again, saved, "m:a:purpose").status == "verified"


def test_duplicate_relations_can_be_saved(store, snap, good_draft):
    good_draft.modules[0].relations.append(good_draft.modules[0].relations[0].model_copy())
    map_id = store.save_map(snap, good_draft, validate(good_draft, snap))
    assert len(store.load_map(map_id).claims) == 5


# Regression: stats reflect each claim's *current* status. "edited" counts claims that are
# currently verified and whose text differs from the AI's; an edited-then-flagged claim is only flagged.
def counts(s):
    inferred = s.total - s.accepted_without_edit - s.edited - s.flagged
    return {"accepted": s.accepted_without_edit, "edited": s.edited, "flagged": s.flagged, "inferred": inferred}


def test_stats_edited_then_flagged_counts_only_as_flagged(store, saved):
    store.review_claim(saved, "r:0", "edit", "x")
    store.review_claim(saved, "r:0", "flag")
    assert counts(store.stats(saved)) == {"accepted": 0, "edited": 0, "flagged": 1, "inferred": 3}


def test_stats_edited_and_still_verified_counts_as_edited(store, saved):
    store.review_claim(saved, "r:0", "edit", "x")
    assert counts(store.stats(saved)) == {"accepted": 0, "edited": 1, "flagged": 0, "inferred": 3}


def test_stats_confirm_without_edit_counts_as_accepted(store, saved):
    store.review_claim(saved, "r:0", "confirm")
    assert counts(store.stats(saved)) == {"accepted": 1, "edited": 0, "flagged": 0, "inferred": 3}


def test_stats_repeated_edits_count_once(store, saved):
    for text in ("x", "y", "z"):
        store.review_claim(saved, "r:0", "edit", text)
    assert counts(store.stats(saved)) == {"accepted": 0, "edited": 1, "flagged": 0, "inferred": 3}


def test_stats_edit_flag_confirm_sequence_is_consistent(store, saved):
    store.review_claim(saved, "r:0", "edit", "x")
    store.review_claim(saved, "r:0", "flag")
    assert counts(store.stats(saved)) == {"accepted": 0, "edited": 0, "flagged": 1, "inferred": 3}
    store.review_claim(saved, "r:0", "confirm")
    assert counts(store.stats(saved)) == {"accepted": 0, "edited": 1, "flagged": 0, "inferred": 3}


@pytest.mark.parametrize("rewrites", [
    ["Bob 改寫"],  # edited, then changed back to the AI's exact words
    [],            # saved an edit without changing anything
])
def test_stats_edit_back_to_ai_text_counts_as_accepted(store, saved, rewrites):
    # Same definition as the 「人工修改」 label (Claim.human_edited): compare text, not button presses.
    ai_text = get_claim(store, saved, "r:0").ai_text
    for text in [*rewrites, ai_text]:
        store.review_claim(saved, "r:0", "edit", text)
    assert not get_claim(store, saved, "r:0").human_edited
    assert counts(store.stats(saved)) == {"accepted": 1, "edited": 0, "flagged": 0, "inferred": 3}


def test_stats_keep_review_history(store, saved):
    store.review_claim(saved, "r:0", "edit", "x")
    store.review_claim(saved, "r:0", "flag")
    store.stats(saved)
    with store._conn() as conn:
        actions = [r["action"] for r in conn.execute("SELECT action FROM events WHERE map_id = ? ORDER BY id",
                                                     (saved,))]
    assert actions == ["edit", "flag"]

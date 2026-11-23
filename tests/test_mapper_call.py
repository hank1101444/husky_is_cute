from types import SimpleNamespace

import anthropic
import httpx2
import pydantic
import pytest

from onboarding_map.mapper import MapperError, draft_map
from onboarding_map.models import DraftRelation, OnboardingMapDraft
from onboarding_map.prompts import SYSTEM_PROMPT


class _Messages:
    def __init__(self, result=None, raises=None):
        self.result, self.raises, self.kwargs = result, raises, None

    def parse(self, **kwargs):
        self.kwargs = kwargs
        if self.raises:
            raise self.raises
        return self.result


class FakeClient:
    def __init__(self, result=None, raises=None):
        self.beta = SimpleNamespace(messages=_Messages(result, raises))

    @property
    def kwargs(self):
        return self.beta.messages.kwargs


def http_response(status: int) -> httpx2.Response:
    return httpx2.Response(status, request=httpx2.Request("POST", "https://api.anthropic.com/v1/messages"))


def test_draft_map_returns_parsed(snap, good_draft):
    fc = FakeClient(result=SimpleNamespace(stop_reason="end_turn", parsed_output=good_draft))
    assert draft_map(snap, client=fc, model="claude-sonnet-5-5") == good_draft
    assert fc.kwargs["model"] == "claude-sonnet-5-5"
    assert fc.kwargs["output_format"] is OnboardingMapDraft
    assert fc.kwargs["system"] == SYSTEM_PROMPT
    assert "[PR#1]" in fc.kwargs["messages"][0]["content"]
    assert fc.kwargs["fallbacks"] == "default"
    assert fc.kwargs["betas"] == ["server-side-fallback-2026-07-01"]


def test_default_model_from_settings(snap, good_draft, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-haiku-5-5")
    fc = FakeClient(result=SimpleNamespace(stop_reason="end_turn", parsed_output=good_draft))
    draft_map(snap, client=fc)
    assert fc.kwargs["model"] == "claude-haiku-5-5"


@pytest.mark.parametrize("stop,msg", [("refusal", "拒絕"), ("max_tokens", "截斷")])
def test_bad_stop_reasons(snap, stop, msg):
    fc = FakeClient(result=SimpleNamespace(stop_reason=stop, parsed_output=None))
    with pytest.raises(MapperError, match=msg):
        draft_map(snap, client=fc, model="m")


def test_missing_parsed_output(snap):
    fc = FakeClient(result=SimpleNamespace(stop_reason="end_turn", parsed_output=None))
    with pytest.raises(MapperError, match="格式"):
        draft_map(snap, client=fc, model="m")


@pytest.mark.parametrize("exc,msg", [
    (anthropic.AuthenticationError("bad", response=http_response(401), body=None), "ANTHROPIC_API_KEY"),
    (anthropic.RateLimitError("slow", response=http_response(429), body=None), "上限"),
    (anthropic.InternalServerError("boom", response=http_response(500), body=None), "500"),
    (anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com")), "連線"),
])
def test_api_errors_are_friendly(snap, exc, msg):
    with pytest.raises(MapperError, match=msg):
        draft_map(snap, client=FakeClient(raises=exc), model="m")


def _truncated_json_error():
    try:
        OnboardingMapDraft.model_validate_json('{"modules": [{"id": "a", "na')
    except pydantic.ValidationError as exc:
        return exc
    raise AssertionError("expected a ValidationError")


def test_unparseable_output_is_friendly(snap):
    # The real SDK validates JSON inside parse(); a max_tokens cut-off raises ValidationError there.
    with pytest.raises(MapperError, match="截斷"):
        draft_map(snap, client=FakeClient(raises=_truncated_json_error()), model="m")


def test_duplicate_module_ids_are_renamed(snap, good_draft):
    good_draft.modules[1].id = "a"
    fc = FakeClient(result=SimpleNamespace(stop_reason="end_turn", parsed_output=good_draft))
    out = draft_map(snap, client=fc, model="m")
    assert [m.id for m in out.modules] == ["a", "a-2"]


def _draft_with_ids(good_draft, ids):
    base = good_draft.modules[1]
    modules = [base.model_copy(update={"id": mid, "name": f"module {i}"}) for i, mid in enumerate(ids)]
    return good_draft.model_copy(update={"modules": modules})


# Regression: a generated suffix must not collide with an id the model already returned (e.g. "a-2"),
# whichever comes first; already unique ids stay as they are.
@pytest.mark.parametrize("ids,expected", [
    (["a", "a", "a-2"], ["a", "a-3", "a-2"]),
    (["a", "a-2", "a"], ["a", "a-2", "a-3"]),
    (["a", "a-2", "b"], ["a", "a-2", "b"]),
])
def test_dedupe_suffix_does_not_collide_with_original_ids(snap, good_draft, ids, expected):
    fc = FakeClient(result=SimpleNamespace(stop_reason="end_turn", parsed_output=_draft_with_ids(good_draft, ids)))
    out = draft_map(snap, client=fc, model="fake-model")
    assert [m.id for m in out.modules] == expected
    assert len({m.id for m in out.modules}) == len(out.modules)
    assert [m.name for m in out.modules] == [f"module {i}" for i in range(len(ids))]  # order and fields kept


def test_dedupe_keeps_relation_targets_on_original_ids(snap, good_draft):
    draft = _draft_with_ids(good_draft, ["a", "a", "a-2"])
    draft.modules[0].relations = [DraftRelation(target_module_id="a-2", reason="r", source_ids=["PR#1"])]
    fc = FakeClient(result=SimpleNamespace(stop_reason="end_turn", parsed_output=draft))
    out = draft_map(snap, client=fc, model="fake-model")
    assert out.modules[0].relations[0].target_module_id == "a-2"
    # "a-2" still names exactly one module: the one the model originally called "a-2".
    assert [m.name for m in out.modules if m.id == "a-2"] == ["module 2"]

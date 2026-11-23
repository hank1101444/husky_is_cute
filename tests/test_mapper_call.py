from types import SimpleNamespace

import anthropic
import httpx2
import pydantic
import pytest

from onboarding_map.mapper import MapperError, draft_map
from onboarding_map.models import OnboardingMapDraft
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

"""Offline demo mode (issue #14): load a predefined sample map without an API key or network calls."""

import importlib
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from onboarding_map.mapper import validate
from onboarding_map.store import Store

APP = str(Path(__file__).resolve().parents[1] / "src" / "onboarding_map" / "app.py")
ALICE = "新成員 (Alice)"
DEMO_LABEL = "示範資料"


def demo():
    # Imported lazily so each test fails on its own (not as one collection error) before demo.py exists.
    return importlib.import_module("onboarding_map.demo")


def run_app() -> AppTest:
    return AppTest.from_file(APP, default_timeout=60).run()


def load_demo(at: AppTest) -> AppTest:
    return at.button(key="load-demo").click().run()


def warnings(at: AppTest) -> str:
    return " ".join(w.value for w in at.warning)


@pytest.fixture
def app_env(tmp_path, monkeypatch):
    db = tmp_path / "app.db"
    monkeypatch.setenv("ONBOARDING_DB_PATH", str(db))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr("onboarding_map.config.load_dotenv", lambda *a, **k: None)
    return db


@pytest.fixture
def no_network(monkeypatch):
    """Fail the test if demo mode reaches Claude or GitHub."""

    def boom(*a, **k):
        raise AssertionError("demo mode must not call Claude or GitHub")

    monkeypatch.setattr("anthropic.Anthropic", boom)
    monkeypatch.setattr("onboarding_map.mapper.draft_map", boom)
    monkeypatch.setattr("onboarding_map.github_fetcher.fetch_snapshot", boom)


def test_demo_data_is_marked_and_passes_validation():
    snapshot, draft = demo().demo_snapshot(), demo().demo_draft()
    assert snapshot.demo is True
    result = validate(draft, snapshot)
    assert result.claims
    assert [c.id for c in result.claims if not c.valid] == []
    assert result.invalid_key_files == {}


def test_live_snapshot_is_not_demo(snap):
    assert snap.demo is False


def test_bob_loads_demo_without_api_key(app_env, no_network):
    at = load_demo(run_app())
    assert not at.exception
    maps = Store(app_env).list_maps()
    assert len(maps) == 1
    assert at.sidebar.selectbox[0].value == maps[0][0]
    assert DEMO_LABEL in warnings(at)


def test_alice_sees_demo_label(app_env, no_network):
    at = load_demo(run_app())
    at.sidebar.radio[0].set_value(ALICE).run()
    assert not at.exception
    assert DEMO_LABEL in warnings(at)


def test_live_map_has_no_demo_label(app_env, snap, good_draft):
    Store(app_env).save_map(snap, good_draft, validate(good_draft, snap))
    at = run_app()
    assert not at.exception
    assert DEMO_LABEL not in warnings(at)


def test_bob_confirms_edits_and_flags_demo_claims(app_env, no_network):
    at = load_demo(run_app())
    at.button(key="confirm-m:fetcher:purpose").click().run()
    at.button(key="flag-m:store:purpose").click().run()
    at.button(key="edit-m:mapper:purpose").click().run()
    at.text_area(key="edit-text-m:mapper:purpose").input("改寫後的用途").run()
    at.button(key="save-m:mapper:purpose").click().run()
    assert not at.exception
    store = Store(app_env)
    claims = {c.id: c for c in store.load_map(store.list_maps()[0][0]).claims}
    assert claims["m:fetcher:purpose"].status == "verified"
    assert claims["m:store:purpose"].status == "flagged"
    assert (claims["m:mapper:purpose"].status, claims["m:mapper:purpose"].text) == ("verified", "改寫後的用途")


def test_alice_asks_and_bob_answer_is_saved_on_demo(app_env, no_network):
    at = load_demo(run_app())
    at.sidebar.radio[0].set_value(ALICE).run()
    at.text_area(key="ask-store").input("為什麼用 SQLite？").run()
    at.button(key="ask-btn-store").click().run()
    assert not at.exception
    store = Store(app_env)
    map_id = store.list_maps()[0][0]
    question = store.questions(map_id, "store")[0]

    bob = run_app()
    bob.text_area(key=f"ans-{question.id}").input("MVP 要最快能跑起來。").run()
    bob.button(key=f"ans-btn-{question.id}").click().run()
    assert not bob.exception
    assert store.questions(map_id, "store")[0].answer == "MVP 要最快能跑起來。"

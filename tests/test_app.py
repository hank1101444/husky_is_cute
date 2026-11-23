from pathlib import Path
from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest

from onboarding_map.mapper import MapperError, validate
from onboarding_map.store import Store

APP = str(Path(__file__).resolve().parents[1] / "src" / "onboarding_map" / "app.py")
FLAGGED_TEXT = "負責接收輸入並呼叫 b。"


def run_app() -> AppTest:
    return AppTest.from_file(APP, default_timeout=60).run()


def page_text(at: AppTest) -> str:
    return " ".join(m.value for m in at.markdown)


@pytest.fixture
def app_env(tmp_path, monkeypatch):
    db = tmp_path / "app.db"
    monkeypatch.setenv("ONBOARDING_DB_PATH", str(db))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr("onboarding_map.config.load_dotenv", lambda *a, **k: None)
    return db


@pytest.fixture
def seeded_flagged(app_env, snap, good_draft):
    store = Store(app_env)
    map_id = store.save_map(snap, good_draft, validate(good_draft, snap))
    store.review_claim(map_id, "m:a:purpose", "flag")
    return SimpleNamespace(store=store, map_id=map_id, flagged_text=FLAGGED_TEXT)


def test_empty_state(app_env):
    at = run_app()
    assert not at.exception
    assert any("尚無地圖" in m.value for m in at.sidebar.markdown)


def test_alice_hides_flagged_claim(seeded_flagged):
    at = run_app()
    at.sidebar.radio[0].set_value("新成員 (Alice)").run()
    assert not at.exception
    text = page_text(at)
    assert any("從這裡開始" in h.value for h in at.subheader)
    assert "處理資料。" in text
    assert seeded_flagged.flagged_text not in text


def test_bob_sees_flagged_claim(seeded_flagged):
    at = run_app()
    assert not at.exception
    text = page_text(at)
    assert seeded_flagged.flagged_text in text and "已標記錯誤" in text


def test_bob_confirm_updates_store(seeded_flagged):
    at = run_app()
    at.button(key="confirm-m:b:purpose").click().run()
    assert not at.exception
    claims = seeded_flagged.store.load_map(seeded_flagged.map_id).claims
    assert next(c for c in claims if c.id == "m:b:purpose").status == "verified"


def test_alice_question_reaches_store_and_bob(seeded_flagged):
    at = run_app()
    at.sidebar.radio[0].set_value("新成員 (Alice)").run()
    at.text_area(key="ask-b").input("為什麼要拆成兩個模組？").run()
    at.button(key="ask-btn-b").click().run()
    assert not at.exception
    assert [q.text for q in seeded_flagged.store.questions(seeded_flagged.map_id, "b")] == ["為什麼要拆成兩個模組？"]
    bob = run_app()
    assert "為什麼要拆成兩個模組？" in page_text(bob)


def test_missing_api_key_shows_error(app_env):
    at = run_app()
    at.text_input(key="repo_url").input("https://github.com/o/r")
    at.button(key="generate").click().run()
    assert not at.exception
    assert "ANTHROPIC_API_KEY" in at.error[0].value


def test_mapper_error_shown_not_raised(app_env, monkeypatch, snap):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.setattr("onboarding_map.github_fetcher.fetch_snapshot", lambda *a, **k: snap)

    def boom(*a, **k):
        raise MapperError("AI 拒絕產生這份地圖")

    monkeypatch.setattr("onboarding_map.mapper.draft_map", boom)
    at = run_app()
    at.text_input(key="repo_url").input("https://github.com/o/r")
    at.button(key="generate").click().run()
    assert not at.exception
    assert "拒絕" in at.error[0].value


def test_generate_second_map_selects_it(seeded_flagged, monkeypatch, snap, good_draft):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.setattr("onboarding_map.github_fetcher.fetch_snapshot", lambda *a, **k: snap)
    monkeypatch.setattr("onboarding_map.mapper.draft_map", lambda *a, **k: good_draft)
    at = run_app()
    at.text_input(key="repo_url").input("https://github.com/o/r")
    at.button(key="generate").click().run()
    assert not at.exception
    maps = seeded_flagged.store.list_maps()
    assert len(maps) == 2
    assert at.sidebar.selectbox[0].value == maps[0][0] != seeded_flagged.map_id


def test_alice_question_shows_and_box_clears(seeded_flagged):
    at = run_app()
    at.sidebar.radio[0].set_value("新成員 (Alice)").run()
    at.text_area(key="ask-b").input("模組 b 做什麼？").run()
    at.button(key="ask-btn-b").click().run()
    assert not at.exception
    assert "模組 b 做什麼？" in page_text(at)
    assert at.text_area(key="ask-b").value == ""
    at.button(key="ask-btn-b").click().run()
    assert len(seeded_flagged.store.questions(seeded_flagged.map_id, "b")) == 1


def test_bob_sees_role_guide(app_env):
    at = run_app()
    guide = " ".join(i.value for i in at.info)
    assert "你是既有成員" in guide and "標記錯誤" in guide and "無紀錄的理由" in guide


def test_alice_sees_role_guide(app_env):
    at = run_app()
    at.sidebar.radio[0].set_value("新成員 (Alice)").run()
    guide = " ".join(i.value for i in at.info)
    assert "你是新成員" in guide and "從這裡開始" in guide and "提問" in guide
    assert "你是既有成員" not in guide

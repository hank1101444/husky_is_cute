"""Issue #13: validate the GitHub URL before checking ANTHROPIC_API_KEY."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "src" / "onboarding_map" / "app.py")
EMPTY_URL_ERROR = "請先輸入 GitHub repo 網址"
INVALID_URL_ERROR = "請輸入 GitHub repo 網址，例如 https://github.com/owner/repo"


@pytest.fixture
def app_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ONBOARDING_DB_PATH", str(tmp_path / "app.db"))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr("onboarding_map.config.load_dotenv", lambda *a, **k: None)


@pytest.fixture
def no_fetch(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("an invalid URL must not reach GitHub")

    monkeypatch.setattr("onboarding_map.github_fetcher.fetch_snapshot", boom)


def generate(url: str) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.text_input(key="repo_url").input(url)
    return at.button(key="generate").click().run()


def errors(at: AppTest) -> list[str]:
    return [e.value for e in at.error]


@pytest.mark.parametrize("url", ["", "   "])
def test_empty_url_shows_url_error_not_api_key_error(app_env, url):
    at = generate(url)
    assert not at.exception
    assert errors(at) == [EMPTY_URL_ERROR]


@pytest.mark.parametrize("url", ["https://gitlab.com/a/b", "not a url", "https://github.com/onlyowner"])
def test_invalid_url_shows_url_error_not_api_key_error(app_env, url):
    at = generate(url)
    assert not at.exception
    assert errors(at) == [INVALID_URL_ERROR]


@pytest.mark.parametrize("url", ["", "https://gitlab.com/a/b"])
def test_bad_url_with_api_key_does_not_fetch(app_env, no_fetch, monkeypatch, url):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    at = generate(url)
    assert not at.exception
    assert errors(at) == [EMPTY_URL_ERROR if not url else INVALID_URL_ERROR]


def test_valid_url_without_api_key_still_shows_api_key_error(app_env):
    at = generate("https://github.com/o/r")
    assert not at.exception
    assert len(errors(at)) == 1
    assert "ANTHROPIC_API_KEY" in errors(at)[0]

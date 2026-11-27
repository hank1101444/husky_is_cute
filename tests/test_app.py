import re
from html.parser import HTMLParser
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


# Regression: file:<path> source links must percent-encode the path (spaces, parentheses, '#',
# non-ASCII) so the GitHub URL points at the right file and the Markdown link is not broken.
SPECIAL_PATHS = {
    "src/b.py": "src/b.py",
    "docs/My Notes.md": "docs/My%20Notes.md",
    "src/utils (old)/a.py": "src/utils%20%28old%29/a.py",
    "notes/#1.md": "notes/%231.md",
    "文件/說明.md": "%E6%96%87%E4%BB%B6/%E8%AA%AA%E6%98%8E.md",
}


@pytest.fixture
def seeded_special_paths(app_env, snap, good_draft):
    snap = snap.model_copy(update={"tree": [*snap.tree, *SPECIAL_PATHS]})
    module_b = good_draft.modules[1].model_copy(
        update={"purpose_source_ids": [f"file:{p}" for p in SPECIAL_PATHS]}
    )
    draft = good_draft.model_copy(update={"modules": [good_draft.modules[0], module_b]})
    store = Store(app_env)
    store.save_map(snap, draft, validate(draft, snap))


def _source_caption(at: AppTest) -> str:
    return next(c.value for c in at.caption if "file:src/b.py" in c.value)


@pytest.mark.parametrize("path,encoded", SPECIAL_PATHS.items())
def test_file_source_link_is_url_encoded(seeded_special_paths, path, encoded):
    at = run_app()
    assert not at.exception
    expected = f"[file:{path}](https://github.com/o/r/blob/main/{encoded})"
    assert expected in _source_caption(at)


def test_file_source_links_form_valid_markdown(seeded_special_paths):
    at = run_app()
    caption = _source_caption(at)
    urls = [part.split(")")[0] for part in caption.split("](")[1:]]
    assert len(urls) == len(SPECIAL_PATHS)
    for url in urls:
        assert url.startswith("https://github.com/o/r/blob/main/")
        assert not any(ch in url for ch in " ()#") and url.isascii()


# Sidebar page index: a two-level native <details> panel below the role / map selectors whose
# links jump to targets that are actually rendered on the main page.
SAFE_ANCHOR = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


class _Node:
    def __init__(self, tag: str, attrs: dict, parent: "_Node | None"):
        self.tag, self.attrs, self.parent, self.children, self.text = tag, attrs, parent, [], ""

    def walk(self):
        for child in self.children:
            yield child
            yield from child.walk()

    def find_all(self, tag: str) -> list["_Node"]:
        return [n for n in self.walk() if n.tag == tag]

    def full_text(self) -> str:
        return self.text + "".join(c.full_text() for c in self.children)


class _TreeBuilder(HTMLParser):
    VOID = {"br", "hr", "img", "input", "meta", "link"}

    def __init__(self):
        super().__init__()
        self.root = self.cur = _Node("root", {}, None)

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, dict(attrs), self.cur)
        self.cur.children.append(node)
        if tag not in self.VOID:
            self.cur = node

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.cur = node.parent

    def handle_data(self, data):
        if self.cur.tag != "style":
            self.cur.text += data


def _parse(body: str) -> _Node:
    builder = _TreeBuilder()
    builder.feed(body)
    return builder.root


def _index_html(at: AppTest) -> str | None:
    bodies = [h.value for h in at.sidebar.html if "onboarding-page-index" in h.value]
    assert len(bodies) <= 1
    return bodies[0] if bodies else None


def _index_links(at: AppTest) -> list[tuple[str, str]]:
    return [(a.attrs["href"], a.full_text().strip()) for a in _parse(_index_html(at)).find_all("a")]


def _main_targets(at: AppTest) -> set[str]:
    """Every id the main page renders: subheader anchors and module marker elements."""
    ids = {h.proto.anchor for h in at.main.subheader if h.proto.anchor}
    for h in at.main.html:
        ids |= {n.attrs["id"] for n in _parse(h.value).walk() if n.attrs.get("id")}
    return ids


def _marker_then_expander(at: AppTest) -> list[tuple[str, str]]:
    """(marker id, label of the expander rendered right after it) for each main-page marker."""
    nodes = list(at.main.children.values())
    pairs = []
    for node, nxt in zip(nodes, nodes[1:]):
        if node.type == "html":
            ids = [n.attrs["id"] for n in _parse(node.value).walk() if n.attrs.get("id")]
            if ids:
                pairs.append((ids[0], nxt.label if nxt.type == "expander" else f"<{nxt.type}>"))
    return pairs


def test_page_index_sits_below_selectors_with_overview_and_module_links(seeded_flagged):
    at = run_app()
    assert not at.exception
    types = [n.type for n in at.sidebar.children.values()]
    assert types.index("radio") < types.index("selectbox") < types.index("html")
    assert at.sidebar.radio[0].label == "角色" and at.sidebar.selectbox[0].label == "地圖"
    links = _index_links(at)
    assert [text for _, text in links] == ["從這裡開始", "模組", "入口模組", "處理模組"]
    hrefs = [href for href, _ in links]
    assert all(h.startswith("#") and SAFE_ANCHOR.match(h[1:]) for h in hrefs)
    assert len(set(hrefs)) == len(hrefs)
    # Every link points at something the main page actually renders.
    assert {h[1:] for h in hrefs} <= _main_targets(at)
    assert [i for i, _ in _marker_then_expander(at)] == [h[1:] for h in hrefs[2:]]
    assert [label for _, label in _marker_then_expander(at)] == ["入口模組（a）", "處理模組（b）"]


def test_page_index_has_two_independent_open_disclosures(seeded_flagged):
    root = _parse(_index_html(run_app()))
    outer = [d for d in root.find_all("details") if not any(p.tag == "details" for p in _ancestors(d))]
    assert len(outer) == 1
    outer = outer[0]
    assert "open" in outer.attrs
    assert outer.children[0].tag == "summary" and "頁面索引" in outer.children[0].full_text()
    inner = outer.find_all("details")
    assert len(inner) == 1 and "open" in inner[0].attrs
    summary = inner[0].children[0]
    assert summary.tag == "summary" and "模組清單" in summary.full_text()
    assert _module_badge(summary) == "2"
    # Summaries only toggle; navigation links live outside them.
    assert not any(s.find_all("a") for s in root.find_all("summary"))
    overview = [a.full_text().strip() for a in outer.find_all("a") if inner[0] not in _ancestors(a)]
    assert overview == ["從這裡開始", "模組"]
    assert [a.full_text().strip() for a in inner[0].find_all("a")] == ["入口模組", "處理模組"]
    # Only one "頁面索引" title, inside the panel.
    assert sum("頁面索引" in m.value for m in run_app().sidebar.markdown) == 0


def _module_badge(summary: _Node) -> str:
    return summary.full_text().replace("模組清單", "").strip()


def _ancestors(node: _Node) -> list[_Node]:
    out = []
    while node.parent is not None:
        node = node.parent
        out.append(node)
    return out


def test_page_index_same_links_for_alice_without_flagged_text(seeded_flagged):
    bob = run_app()
    alice = run_app()
    alice.sidebar.radio[0].set_value("新成員 (Alice)").run()
    assert not alice.exception
    assert _index_links(alice) == _index_links(bob)
    assert {h[1:] for h, _ in _index_links(alice)} <= _main_targets(alice)
    assert seeded_flagged.flagged_text not in _index_html(alice)
    assert seeded_flagged.flagged_text not in _index_html(bob)


TRICKY_MODULES = [
    ("x", "資料處理"),
    ("x-2", "資料處理"),
    ("a b/<c>", ""),
    ("Ω", "<script>alert(1)</script> **粗體** [連結](http://e.com)"),
    ("9", "一個非常非常長的中文模組名稱用來測試換行是否會被截斷或與圖示重疊的情況"),
]


@pytest.fixture
def seeded_tricky(app_env, snap, good_draft):
    module = good_draft.modules[1]
    modules = [module.model_copy(update={"id": mid, "name": name}) for mid, name in TRICKY_MODULES]
    draft = good_draft.model_copy(update={"modules": modules})
    Store(app_env).save_map(snap, draft, validate(draft, snap))


def test_page_index_anchors_unique_and_safe_for_tricky_modules(seeded_tricky):
    at = run_app()
    assert not at.exception
    body = _index_html(at)
    assert "<script" not in body and "&lt;script&gt;" in body
    links = _index_links(at)[2:]
    hrefs = [h for h, _ in links]
    assert len(set(hrefs)) == len(TRICKY_MODULES)
    assert all(SAFE_ANCHOR.match(h[1:]) for h in hrefs)
    labels = [text for _, text in links]
    # Duplicate names are told apart by their ids; a blank name falls back to the id.
    assert labels[0] != labels[1] and "x" in labels[0] and "x-2" in labels[1]
    assert labels[2] == "a b/<c>"
    assert labels[3].startswith("<script>alert(1)</script> **粗體**")  # kept as plain text
    assert labels[4] == TRICKY_MODULES[4][1]
    assert [i for i, _ in _marker_then_expander(at)] == [h[1:] for h in hrefs]
    assert _module_badge(_parse(body).find_all("details")[1].children[0]) == str(len(TRICKY_MODULES))


def test_page_index_follows_selected_map(seeded_flagged, snap, good_draft):
    module = good_draft.modules[0].model_copy(update={"id": "z", "name": "另一張圖的模組"})
    draft = good_draft.model_copy(update={"modules": [module]})
    other = snap.model_copy(update={"repo": "other", "url": "https://github.com/o/other"})
    second = seeded_flagged.store.save_map(other, draft, validate(draft, other))
    at = run_app()
    at.sidebar.selectbox[0].set_value(seeded_flagged.map_id).run()
    first_links = _index_links(at)
    at.sidebar.selectbox[0].set_value(second).run()
    assert not at.exception
    links = _index_links(at)
    assert [t for _, t in links] == ["從這裡開始", "模組", "另一張圖的模組"]
    assert not {h for h, _ in first_links[2:]} & {h for h, _ in links}
    assert {h[1:] for h, _ in links} <= _main_targets(at)
    assert _module_badge(_parse(_index_html(at)).find_all("details")[1].children[0]) == "1"


def test_page_index_absent_without_map(app_env):
    at = run_app()
    assert not at.exception
    assert _index_html(at) is None
    assert not any("href" in h.value for h in at.sidebar.html)


def test_page_index_without_modules_has_no_module_group(app_env, snap, good_draft):
    draft = good_draft.model_copy(update={"modules": []})
    Store(app_env).save_map(snap, draft, validate(draft, snap))
    at = run_app()
    assert not at.exception
    root = _parse(_index_html(at))
    assert len(root.find_all("details")) == 1
    assert "沒有模組" in root.full_text()
    hrefs = [a.attrs["href"][1:] for a in root.find_all("a")]
    assert len(hrefs) == 2 and set(hrefs) <= _main_targets(at)
    assert "（沒有模組）" in page_text(at)


# Walking skeleton slice (issue #23): mark claims a person has rewritten.
EDITED_TEXT = "Bob 改寫：a 是程式的入口，負責把輸入交給 b。"
ORIGINAL_NOTE = "原本 AI 寫的：負責接收輸入並呼叫 b。"


def all_text(at: AppTest) -> str:
    return " ".join([m.value for m in at.markdown] + [c.value for c in at.caption])


@pytest.fixture
def seeded_edited(app_env, snap, good_draft):
    store = Store(app_env)
    map_id = store.save_map(snap, good_draft, validate(good_draft, snap))
    store.review_claim(map_id, "m:a:purpose", "edit", EDITED_TEXT)
    store.review_claim(map_id, "m:b:purpose", "confirm")
    return store


def test_alice_sees_human_edited_label_only_on_edited_claim(seeded_edited):
    at = run_app()
    at.sidebar.radio[0].set_value("新成員 (Alice)").run()
    assert not at.exception
    lines = [m.value for m in at.markdown]
    edited = next(v for v in lines if v.endswith(EDITED_TEXT))
    confirmed_only = next(v for v in lines if v.endswith("· 處理資料。"))
    assert "人工修改" in edited
    assert "人工修改" not in confirmed_only


def test_only_bob_sees_original_ai_text(seeded_edited):
    bob = run_app()
    assert not bob.exception
    assert ORIGINAL_NOTE in all_text(bob)

    alice = run_app()
    alice.sidebar.radio[0].set_value("新成員 (Alice)").run()
    assert not alice.exception
    assert "原本 AI 寫的" not in all_text(alice)

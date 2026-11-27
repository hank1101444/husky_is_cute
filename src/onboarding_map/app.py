"""Streamlit UI. Run: streamlit run src/onboarding_map/app.py

Two roles share one running app and one SQLite DB:
- Bob (existing member): generates a map, reviews each claim, answers questions.
- Alice (new member): reads the map in the suggested order, asks questions on a module.
"""

from __future__ import annotations

import html
import os
import re
from urllib.parse import quote

import streamlit as st

from onboarding_map import demo, github_fetcher, mapper
from onboarding_map.config import load_settings
from onboarding_map.models import Claim, DraftModule
from onboarding_map.store import LoadedMap, Store

ROLE_BOB = "既有成員 (Bob)"
ROLE_ALICE = "新成員 (Alice)"
STATUS_LABEL = {"inferred": "推論", "verified": "已確認", "flagged": "已標記錯誤"}
STATUS_ICON = {"inferred": "🟡", "verified": "✅", "flagged": "⛔"}
ROLE_GUIDE = {
    ROLE_BOB: (
        "**你是既有成員**：AI 先畫好了這份地圖，請逐條檢查。點「來源」看 AI 的根據 → 對的按 **確認**、"
        "不準確的按 **修改** 改寫、錯的按 **標記錯誤**（新成員就看不到這條）。"
        "「無紀錄的理由」表示 repo 裡沒有寫原因；如果你知道，按修改把原因寫進去。"
        "新成員的提問會出現在「待回答的問題」。"
    ),
    ROLE_ALICE: (
        "**你是新成員**：這是這個專案的導覽地圖，先照「從這裡開始」的順序讀。"
        "🟡 推論＝AI 推測、還沒人確認；✅ 已確認＝既有成員檢查過。每條都可以點「來源」看原始資料。"
        "看不懂的地方，在該模組底下的問答框提問，既有成員回答後會留在地圖上。"
    ),
}
READING_ANCHOR = "onboarding-reading-order"
MODULES_ANCHOR = "onboarding-modules"
# Styles only the sidebar page index (.onboarding-page-index) and its scroll targets.
PAGE_INDEX_CSS = """
.onboarding-page-index { font-size: 0.9rem; line-height: 1.4; }
.onboarding-page-index .opi-panel {
  border: 1px solid rgba(128, 128, 128, 0.3); border-radius: 12px; padding: 0.4rem;
}
.onboarding-page-index summary {
  list-style: none; display: flex; align-items: center; gap: 0.5rem; cursor: pointer;
  padding: 0.45rem 0.55rem; border-radius: 8px; font-weight: 600; color: inherit;
}
.onboarding-page-index summary::-webkit-details-marker { display: none; }
.onboarding-page-index summary::marker { content: ""; }
.onboarding-page-index .opi-chevron {
  flex: none; width: 0.42rem; height: 0.42rem; margin: 0 0.15rem;
  border-right: 2px solid currentColor; border-bottom: 2px solid currentColor;
  opacity: 0.65; transform: rotate(-45deg); transition: transform 0.15s ease;
}
.onboarding-page-index details[open] > summary > .opi-chevron { transform: rotate(45deg); }
.onboarding-page-index .opi-title { flex: 1 1 auto; min-width: 0; }
.onboarding-page-index .opi-badge {
  flex: none; min-width: 1.4rem; padding: 0.15rem 0.45rem; border-radius: 999px; text-align: center;
  font-size: 0.75rem; font-weight: 600; background: rgba(128, 128, 128, 0.18);
}
.onboarding-page-index .opi-body { display: flex; flex-direction: column; gap: 2px; padding-top: 0.15rem; }
.onboarding-page-index a.opi-link,
.onboarding-page-index a.opi-link:visited {
  display: block; padding: 0.5rem 0.6rem 0.5rem 1.65rem; border-radius: 8px;
  color: inherit; text-decoration: none; overflow-wrap: anywhere;
}
.onboarding-page-index summary:hover,
.onboarding-page-index a.opi-link:hover { background: rgba(28, 131, 225, 0.1); color: inherit; }
.onboarding-page-index a.opi-link:focus-visible,
.onboarding-page-index summary:focus-visible { outline: 2px solid #1c83e1; outline-offset: 1px; }
.onboarding-page-index .opi-modules {
  list-style: none; margin: 0.1rem 0 0 1.2rem; padding: 0 0 0 0.35rem; font-size: inherit; line-height: inherit;
  border-left: 1px solid rgba(128, 128, 128, 0.3);
}
.onboarding-page-index .opi-modules li { margin: 0; padding: 0; font-size: inherit; line-height: inherit; }
.onboarding-page-index .opi-modules a.opi-link { padding-left: 0.6rem; }
.onboarding-page-index .opi-note { margin: 0; padding: 0.4rem 0.6rem 0.4rem 1.65rem; opacity: 0.75; }
.onboarding-page-index-target, #onboarding-reading-order, #onboarding-modules { scroll-margin-top: 4.5rem; }
"""


def source_links(m: LoadedMap, source_ids: list[str]) -> str:
    links = []
    for sid in source_ids:
        if sid.startswith("file:"):
            # Percent-encode the path (spaces, parentheses, '#', non-ASCII) but keep '/' separators.
            path = quote(sid[5:], safe="/")
            links.append(f"[{sid}]({m.snapshot.url}/blob/{m.snapshot.default_branch}/{path})")
        elif (src := m.snapshot.source(sid)) is not None:
            links.append(f"[{sid}]({src.url})")
        else:
            links.append(f"`{sid}`")
    return "來源：" + ("、".join(links) if links else "（無）")


def original_text_note(claim: Claim) -> str | None:
    """Issue #23: the AI's original wording, shown to the existing member only."""
    edited = claim.ai_text is not None and claim.text != claim.ai_text  # TODO: use claim.human_edited
    return f"原本 AI 寫的：{claim.ai_text}" if edited else None


def render_claim(store: Store, m: LoadedMap, claim: Claim, role: str) -> None:
    st.markdown(f"{STATUS_ICON[claim.status]} **{STATUS_LABEL[claim.status]}** · {claim.text}")
    st.caption(source_links(m, claim.source_ids))
    if not claim.valid:
        st.warning("⚠ 來源有問題：" + "；".join(claim.problems))
    if role != ROLE_BOB:
        return
    note = original_text_note(claim)
    if note:
        st.caption(note)
    edit_key = f"editing-{m.map_id}-{claim.id}"
    cols = st.columns([1, 1, 1, 6])
    if cols[0].button("確認", key=f"confirm-{claim.id}"):
        store.review_claim(m.map_id, claim.id, "confirm")
        st.rerun()
    if cols[1].button("修改", key=f"edit-{claim.id}"):
        st.session_state[edit_key] = True
    if cols[2].button("標記錯誤", key=f"flag-{claim.id}"):
        store.review_claim(m.map_id, claim.id, "flag")
        st.rerun()
    if st.session_state.get(edit_key):
        new_text = st.text_area("修改內容", value=claim.text, key=f"edit-text-{claim.id}")
        if st.button("儲存", key=f"save-{claim.id}"):
            if new_text.strip():
                store.review_claim(m.map_id, claim.id, "edit", new_text)
                st.session_state[edit_key] = False
                st.rerun()
            else:
                st.error("修改內容不能是空的")


def visible(claims: list[Claim], role: str) -> list[Claim]:
    return claims if role == ROLE_BOB else [c for c in claims if c.status != "flagged"]


def module_anchors(m: LoadedMap) -> list[str]:
    """Deterministic, unique HTML ids for the module targets of this map.

    The position makes each id unique; the ASCII part of the module id only helps readability.
    """
    anchors = []
    for i, module in enumerate(m.draft.modules, start=1):
        safe = re.sub(r"[^A-Za-z0-9]+", "-", module.id).strip("-")[:40]
        anchors.append(f"onboarding-map{m.map_id}-module{i}" + (f"-{safe}" if safe else ""))
    return anchors


def module_index_labels(modules: list[DraftModule]) -> list[str]:
    """Index labels: the module name, plus its id when the name repeats; the id when the name is blank."""
    names = [mod.name.strip() for mod in modules]
    labels = []
    for mod, name in zip(modules, names):
        if not name:
            labels.append(mod.id)
        elif names.count(name) > 1:
            labels.append(f"{name}（{mod.id}）")
        else:
            labels.append(name)
    return labels


def page_index_html(m: LoadedMap) -> str:
    """Sidebar page index: two native <details> levels; summaries only toggle, links only navigate."""
    def link(anchor: str, label: str) -> str:
        return f'<a class="opi-link" href="#{anchor}">{html.escape(label)}</a>'

    modules = m.draft.modules
    if modules:
        items = "".join(
            f"<li>{link(anchor, label)}</li>"
            for anchor, label in zip(module_anchors(m), module_index_labels(modules))
        )
        group = (
            '<details class="opi-group" open><summary><span class="opi-chevron" aria-hidden="true"></span>'
            f'<span class="opi-title">模組清單</span><span class="opi-badge">{len(modules)}</span></summary>'
            f'<ul class="opi-modules">{items}</ul></details>'
        )
    else:
        group = '<p class="opi-note">（沒有模組）</p>'
    return (
        f"<style>{PAGE_INDEX_CSS}</style>"
        '<nav class="onboarding-page-index" aria-label="頁面索引">'
        '<details class="opi-panel" open><summary><span class="opi-chevron" aria-hidden="true"></span>'
        '<span class="opi-title">頁面索引</span></summary>'
        f'<div class="opi-body">{link(READING_ANCHOR, "從這裡開始")}{link(MODULES_ANCHOR, "模組")}{group}</div>'
        "</details></nav>"
    )


def render_reading_order(store: Store, m: LoadedMap, role: str) -> None:
    st.subheader("從這裡開始", anchor=READING_ANCHOR)
    reading = visible([c for c in m.claims if c.kind == "reading"], role)
    if not reading:
        st.markdown("（沒有建議的閱讀順序）")
    for claim in reading:
        render_claim(store, m, claim, role)


def render_module(store: Store, m: LoadedMap, module: DraftModule, role: str, anchor: str) -> None:
    # Index target sits before the expander header, so a collapsed module can still be located.
    st.html(f'<div id="{anchor}" class="onboarding-page-index-target"></div>')
    with st.expander(f"{module.name}（{module.id}）", expanded=True):
        bad = set(m.invalid_key_files.get(module.id, []))
        files = [f"`{f}`" + (" ⚠ 不在檔案清單中" if f in bad else "") for f in module.key_files]
        st.markdown("關鍵檔案：" + ("、".join(files) if files else "（無）"))
        for claim in visible([c for c in m.claims if c.module_id == module.id], role):
            render_claim(store, m, claim, role)

        st.markdown("**問答**")
        for q in store.questions(m.map_id, module.id):
            st.markdown(f"❓ {q.text}")
            st.markdown(f"💬 {q.answer}" if q.answer else "（等待既有成員回答）")
        if role == ROLE_ALICE:
            box = f"ask-{module.id}"
            st.text_area("你的問題", key=box)
            st.button("在這個模組提問", key=f"ask-btn-{module.id}", on_click=_submit_question,
                      args=(store, m.map_id, module.id, box))
            note = st.session_state.pop(f"{box}-note", None)
            if note == "sent":
                st.success("已送出，既有成員回答後會顯示在這裡")
            elif note == "empty":
                st.error("問題不能是空的")


def _submit_question(store: Store, map_id: int, module_id: str, box: str) -> None:
    """Button callback: runs before the rerun, so the question shows and the box can be cleared."""
    text = st.session_state.get(box, "")
    if text.strip():
        store.ask(map_id, module_id, text)
        st.session_state[box] = ""
        st.session_state[f"{box}-note"] = "sent"
    else:
        st.session_state[f"{box}-note"] = "empty"


def render_generator(store: Store, settings) -> None:
    st.subheader("產生新地圖")
    url = st.text_input("GitHub repo 網址", key="repo_url", placeholder="https://github.com/owner/repo")
    cols = st.columns([1, 2, 5])
    if cols[1].button("載入示範地圖（不需 API key）", key="load-demo"):
        _load_demo(store)
    if not cols[0].button("產生地圖", key="generate"):
        return
    # Check the URL first: a missing API key should not hide a URL the user can fix right away.
    if not url.strip():
        st.error("請先輸入 GitHub repo 網址")
        return
    try:
        github_fetcher.parse_repo_url(url)
    except github_fetcher.InvalidRepoUrl as exc:
        st.error(str(exc))
        return
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error("尚未設定 ANTHROPIC_API_KEY，請在 .env 填入金鑰後重新啟動，或按「載入示範地圖」先試用")
        return
    status = st.status("步驟 1/3：讀取 GitHub 資料…", expanded=True)
    try:
        with status:
            snapshot = github_fetcher.fetch_snapshot(url, token=settings.github_token, progress=st.write)
            st.write(f"讀到 {len(snapshot.tree)} 個檔案、{len(snapshot.sources)} 筆來源")
            status.update(label="步驟 2/3：Claude 產生地圖中（小 repo 約 20 秒，大 repo 可能 1–2 分鐘）…")
            st.write(f"送出給 {settings.anthropic_model}，等待回應…")
            draft = mapper.draft_map(snapshot, model=settings.anthropic_model)
            status.update(label="步驟 3/3：驗證來源並儲存…")
            result = mapper.validate(draft, snapshot)
            map_id = store.save_map(snapshot, draft, result)
            status.update(label="完成", state="complete")
    except (github_fetcher.GitHubError, mapper.MapperError) as exc:
        status.update(label="失敗", state="error")
        st.error(str(exc))
        return
    # The sidebar selectbox (key "map_id") already exists in this run; hand the id over via another key.
    st.session_state["select_map_id"] = map_id
    st.rerun()


def _load_demo(store: Store) -> None:
    """Save the predefined sample map and select it. No Claude or GitHub call; validation runs locally."""
    snapshot, draft = demo.demo_snapshot(), demo.demo_draft()
    st.session_state["select_map_id"] = store.save_map(snapshot, draft, mapper.validate(draft, snapshot))
    st.rerun()


def render_bob_extras(store: Store, m: LoadedMap) -> None:
    s = store.stats(m.map_id)
    cols = st.columns(3)
    cols[0].metric("未修改即接受", f"{s.accepted_without_edit} / {s.total}")
    cols[1].metric("檢查時間（分鐘）", "—" if s.review_minutes is None else f"{s.review_minutes:.1f}")
    cols[2].metric("提問數", s.questions)

    st.subheader("待回答的問題")
    open_qs = [q for q in store.questions(m.map_id) if not q.answer]
    if not open_qs:
        st.markdown("（目前沒有待回答的問題）")
    names = {mod.id: mod.name for mod in m.draft.modules}
    for q in open_qs:
        st.markdown(f"❓ **{names.get(q.module_id, q.module_id)}**：{q.text}")
        answer = st.text_area("回答", key=f"ans-{q.id}")
        if st.button("送出回答", key=f"ans-btn-{q.id}"):
            if answer.strip():
                store.answer(q.id, answer)
                st.rerun()
            else:
                st.error("回答不能是空的")


def main() -> None:
    st.set_page_config(page_title="Onboarding Map", page_icon="🗺️", layout="wide")
    settings = load_settings()
    store = Store(settings.db_path)

    role = st.sidebar.radio("角色", [ROLE_BOB, ROLE_ALICE], key="role")
    maps = store.list_maps()
    map_id = None
    if "select_map_id" in st.session_state:
        st.session_state["map_id"] = st.session_state.pop("select_map_id")
    if maps:
        labels = {mid: f"{url} · {created[:16].replace('T', ' ')}" for mid, url, created in maps}
        if st.session_state.get("map_id") not in labels:
            st.session_state["map_id"] = maps[0][0]
        map_id = st.sidebar.selectbox("地圖", list(labels), format_func=labels.get, key="map_id")
    else:
        st.sidebar.markdown("尚無地圖")
    m = store.load_map(map_id) if map_id is not None else None
    if m is not None:
        st.sidebar.html(page_index_html(m))

    st.title("新成員 Onboarding Map")
    st.info(ROLE_GUIDE[role])
    if role == ROLE_BOB:
        render_generator(store, settings)
    if m is None:
        if role == ROLE_ALICE:
            st.info("還沒有地圖，請既有成員先產生一份。")
        return

    st.markdown(f"### {m.repo_url}")
    if m.snapshot.demo:
        st.warning("這是示範資料：地圖內容是預先寫好的範例，不是 Claude 即時產生的。你的確認、修改和問答仍會照常儲存。")
    for kind, note in m.snapshot.truncation.items():
        st.info(f"資料不完整（{kind}）：{note}")
    st.caption("每條說法都由 AI 推論並附上來源；🟡 推論、✅ 已確認、⛔ 已標記錯誤。")
    if role == ROLE_BOB:
        render_bob_extras(store, m)
    render_reading_order(store, m, role)
    st.subheader("模組", anchor=MODULES_ANCHOR)
    if not m.draft.modules:
        st.markdown("（沒有模組）")
    for module, anchor in zip(m.draft.modules, module_anchors(m)):
        render_module(store, m, module, role, anchor)


main()

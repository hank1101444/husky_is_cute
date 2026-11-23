"""Streamlit UI. Run: streamlit run src/onboarding_map/app.py

Two roles share one running app and one SQLite DB:
- Bob (existing member): generates a map, reviews each claim, answers questions.
- Alice (new member): reads the map in the suggested order, asks questions on a module.
"""

from __future__ import annotations

import os

import streamlit as st

from onboarding_map import github_fetcher, mapper
from onboarding_map.config import load_settings
from onboarding_map.models import Claim, DraftModule
from onboarding_map.store import LoadedMap, Store

ROLE_BOB = "既有成員 (Bob)"
ROLE_ALICE = "新成員 (Alice)"
STATUS_LABEL = {"inferred": "推論", "verified": "已確認", "flagged": "已標記錯誤"}
STATUS_ICON = {"inferred": "🟡", "verified": "✅", "flagged": "⛔"}


def source_links(m: LoadedMap, source_ids: list[str]) -> str:
    links = []
    for sid in source_ids:
        if sid.startswith("file:"):
            links.append(f"[{sid}]({m.snapshot.url}/blob/{m.snapshot.default_branch}/{sid[5:]})")
        elif (src := m.snapshot.source(sid)) is not None:
            links.append(f"[{sid}]({src.url})")
        else:
            links.append(f"`{sid}`")
    return "來源：" + ("、".join(links) if links else "（無）")


def render_claim(store: Store, m: LoadedMap, claim: Claim, role: str) -> None:
    st.markdown(f"{STATUS_ICON[claim.status]} **{STATUS_LABEL[claim.status]}** · {claim.text}")
    st.caption(source_links(m, claim.source_ids))
    if not claim.valid:
        st.warning("⚠ 來源有問題：" + "；".join(claim.problems))
    if role != ROLE_BOB:
        return
    edit_key = f"editing-{m.map_id}-{claim.id}"
    cols = st.columns(3)
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


def render_reading_order(store: Store, m: LoadedMap, role: str) -> None:
    st.subheader("從這裡開始")
    reading = visible([c for c in m.claims if c.kind == "reading"], role)
    if not reading:
        st.markdown("（沒有建議的閱讀順序）")
    for claim in reading:
        render_claim(store, m, claim, role)


def render_module(store: Store, m: LoadedMap, module: DraftModule, role: str) -> None:
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
    if not st.button("產生地圖", key="generate"):
        return
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error("尚未設定 ANTHROPIC_API_KEY，請在 .env 填入金鑰後重新啟動")
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

    st.title("新成員 Onboarding Map")
    if role == ROLE_BOB:
        render_generator(store, settings)
    if map_id is None:
        if role == ROLE_ALICE:
            st.info("還沒有地圖，請既有成員先產生一份。")
        return

    m = store.load_map(map_id)
    st.markdown(f"### {m.repo_url}")
    for kind, note in m.snapshot.truncation.items():
        st.info(f"資料不完整（{kind}）：{note}")
    st.caption("每條說法都由 AI 推論並附上來源；🟡 推論、✅ 已確認、⛔ 已標記錯誤。")
    if role == ROLE_BOB:
        render_bob_extras(store, m)
    render_reading_order(store, m, role)
    st.subheader("模組")
    for module in m.draft.modules:
        render_module(store, m, module, role)


main()

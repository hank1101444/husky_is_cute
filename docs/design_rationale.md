# Design Rationale — Onboarding Map (CP2)

Key interaction design decisions in the MVP, and what shaped each one. Evidence sources:
CP1 interviews (2026-10-24, two first-year master's students who took over existing codebases),
the CP1 design sketch, our own pilot, and two user-testing sessions with students outside the team (§3).
Decisions that changed scope or architecture are also in [`DECISIONS.md`](../DECISIONS.md).

## 1. Decisions and what shaped them

| # | Decision | What shaped it |
|---|---|---|
| D1 | **Every AI claim shows its source links**: README, `file:` path, PR, PR comment, issue, commit or DECISIONS entry. | Both CP1 interviewees found the *reason* behind strange code only in history: a commit message (A, the 0.3 loss scaling) or an 8-month-old PR (B, the 50 ms sleep). Interviewee B found ChatGPT least useful because it explains *what* but guesses *why*. A link lets the reader check the claim instead of trusting it. |
| D2 | **When nothing explains a reason, the map says 「無紀錄的理由」 instead of guessing.** Citations are checked in code. | Same evidence as D1: a confident guess is the failure mode we are replacing. In our prompt test suite, the `decoy_obvious_reason` case checks that the AI does not invent an "obvious" reason (see `docs/prompt_card.md`). |
| D3 | **Three claim states: 🟡 inferred → ✅ verified / ⛔ flagged.** The existing member reviews claim by claim (confirm / edit / flag). | CP1 §3.3: the existing member checks the AI draft. Claim-level review (not "approve the whole map") lets Bob fix one wrong sentence without redoing the rest. It also gives us the CP1 §4.4 metric "share of claims accepted without edits". |
| D4 | **The new member sees the map before Bob finishes reviewing.** Flagged claims are hidden from her. | CP1 left this open: will existing members spend 10–15 minutes checking up front? We chose CP1's fallback, "verification optional, rely on the inferred label plus source links", so Alice is never blocked waiting for Bob. The 🟡 label tells her what is unchecked. |
| D5 | **Questions are attached to a module, and answers stay on the map.** | CP1 problem statement: answers to new members "stay in private chat, where the next new member cannot find them". Interviewee B's questions were specific ("I see A exists to solve B, but now C happens…"), which fits a per-module thread better than a general chat. |
| D6 | **Map and UI in Traditional Chinese.** | Our test users are Taiwanese students. Both CP1 interviews were conducted in Chinese. |
| D7 | **A "start here" reading order of 5–8 items.** | CP1 problem statement: new members "spend days reading code in no particular order". |
| D8 | **One shared app, a role switch in the sidebar, no login.** | CP2 asks for a prototype two people can use together, built in one week. Accounts add no evidence about the onboarding interaction itself. |
| D9 | **Step-by-step progress while a map is generated** (reading GitHub → Claude drafting → validating). | Pilot finding P1 (§2). |
| D10 | **An in-page guide for each role, and the three review buttons grouped together.** | Pilot finding P2 (§2). |
| D11 | **A sidebar page index** below the role and map selectors: 「從這裡開始」, 「模組」 and one link per module, in a panel with two collapsible levels (「頁面索引」, 「模組清單」 with the module count). Links scroll the same full page. | TiffanyChen-tc's navigation and design request (2026-11-23), recorded in `DECISIONS.md`. Not a pilot or user-testing finding; we have no measurements of its effect yet. |

## 2. Internal pilot (team member, not counted as user testing)

These come from a team member using the app for the first time. **They are not user-testing
sessions**: CP2 requires sessions with real users outside the team (§3).

| # | Date | Who | What happened | Change made |
|---|---|---|---|---|
| P1 | 2026-11-23 | Hank (team) | Generated a map of a mid-sized repo (`Cloud-Native-Development-Project`). The page showed only a spinner, 「正在讀取 repo 並產生地圖…」. He asked how long it takes and what step it is on. | D9: a status box shows each step, e.g. 「讀取 PR 留言 12/30」, and how long Claude usually takes. |
| P2 | 2026-11-23 | Hank (team) | Looking at the finished map (27 claims), he asked 「這什麼東西 我怎麼看？」 and then 「我要怎麼解讀這些按鈕… 不同成員能幹嘛」. The page never explains the roles, the 🟡/✅/⛔ states, 「無紀錄的理由」, or what the buttons do, and the buttons were spread across the full width. | D10: a short guide at the top for each role; buttons grouped on the left. |

**What P2 suggests we test with real users:** whether new users understand, *without help*, what
the buttons do and what 「無紀錄的理由」 means. If they still don't, the guide is not enough.

## 3. User-testing sessions (real users outside the team)

**Method as run** (differs from the CP1 §4 plan; see "Limits" below). Two 15-minute online
sessions on Google Meet. A teammate shared their screen with the demo map of this repository
(Bob: 「載入示範地圖（不需 API key）」, then switched to 「新成員 (Alice)」); the participant answered
aloud and asked the facilitator to scroll or open things. The facilitator did not explain buttons or
give hints. Script, tasks and answer key: T1–T4 required, T5–T6 if time allowed, then Q1–Q4.

| # | Task | Counts as correct (decided before the sessions) |
|---|---|---|
| T1 | Name the main modules | At least 3 of 4: GitHub 讀取, 地圖產生與驗證, 資料儲存, 網頁介面 |
| T2 | Which file reads GitHub data? | `github_fetcher.py` |
| T3 | How do 「GitHub 讀取」 and 「地圖產生」 relate? | Data flows from the first to the second |
| T4 | Why Streamlit + SQLite, and where did you see it? | One reason (Python only / fastest two-person version) **and** the source (`DECISIONS.md`) |
| T5 | How do you run the project? (optional) | README: `conda env create` → `conda activate husky` → `streamlit run …` |
| T6 | Which file would you edit to change 「✍️ 人工修改」? (optional) | `app.py` |

Correct / partial below was scored by us from the written answers against this key.
Quotes are the participants' words, lightly condensed by the note-taker.

### Session 1

- **Date / duration:** *not recorded* (15-minute format)
- **Participant:** computer-science student with GitHub project experience; not a team member
- **Repository used:** this repository, through the hand-written demo map (no Claude call)
- **Tasks** (time not recorded; no help from the facilitator recorded):

  | Task | Result | What they said |
  |---|---|---|
  | T1 | Correct (4/4) | 「GitHub 資料讀取、地圖產生、資料儲存，還有網頁介面」 |
  | T2 | Correct | 「應該是 github_fetcher.py，我看檔名就滿明顯的」 |
  | T3 | Correct | 「先取得專案資訊，然後把資料傳給地圖產生模組」 |
  | T4 | Correct | Reason (Python, fastest version two people can use, no complex front/back-end split) and source (`DECISIONS.md`) |
  | T5 | Partial | README → install the environment → set the API key → start with Streamlit; no commands named, and 「可能要真的照著指令跑一次才會確定」. (The demo map needs no API key.) |
  | T6 | Correct | `app.py`, 「因為這應該是畫面顯示的部分」 |

- **Q1 🟡 / ✅:** 🟡 = AI-generated and not yet checked; ✅ = checked by a person, more trustworthy. Correct.
- **Q2 「無紀錄的理由」:** 「GitHub 裡沒有找到相關的設計原因，不代表真的沒有原因，只是目前沒有資料可以證明」. Correct.
- **Q3 rating:** **4 / 5.** Helped because they did not have to read code first to know the modules and what each does; some relations were only clear after opening the source.
- **Q4 stuck / suggestion:** 「有些來源連結比較多，我一開始不知道要點哪個」; suggests marking the most important source.
- **Did they understand the labels and 「無紀錄的理由」 without help?** Yes, both.
- **Changes we made because of this session:** none yet; see the "User testing findings" draft in `DECISIONS.md`.

### Session 2

- **Date / duration:** *not recorded* (15-minute format)
- **Participant:** student who has used GitHub but did not know this project; not a team member
- **Repository used:** this repository, through the demo map
- **Tasks** (time not recorded; no help from the facilitator recorded):

  | Task | Result | What they said |
  |---|---|---|
  | T1 | Correct (4/4) | 「讀 GitHub 資料的，然後有 AI 整理地圖，還有存資料跟顯示畫面的部分。大概是這幾個吧」 |
  | T2 | Correct, after self-correction | First guessed `app.py`, then corrected to `github_fetcher.py` from the module description |
  | T3 | Correct | 「沒有前面的資料，後面應該也沒辦法產生」 |
  | T4 | Partial | Guessed 「比較簡單、比較快開發吧？」; 「我一開始沒看到這個原因寫在哪裡，找了一下才發現可以點來源」. Did not name `DECISIONS.md` |
  | T5 | Partial | Knows to read the README; would copy the setup commands and try them |
  | T6 | Correct, unsure | `app.py`, guessed from 「跟畫面有關的程式」 |

- **Q1 🟡 / ✅:** 「我一開始以為黃色是有問題的意思，後來看說明才知道是 AI 推論、還沒確認」. Correct after reading the in-page guide.
- **Q2 「無紀錄的理由」:** Unsure: 「不知道是 AI 不知道原因，還是原本開發者沒有寫」; one more sentence of explanation would help.
- **Q3 rating:** **3 / 5.** Easier than the GitHub file list and gave a sense of what the project does, but module names are still technical and needed time with the descriptions.
- **Q4 stuck / suggestion:** explain 「推論」 vs 「已確認」 more clearly; a simple arrow diagram of how data moves from one module to the next.
- **Did they understand the labels and 「無紀錄的理由」 without help?** Labels: only after reading the guide. 「無紀錄的理由」: no.
- **Changes we made because of this session:** none yet; see the "User testing findings" draft in `DECISIONS.md`.

### What the two sessions show

| Finding | Session 1 | Session 2 | Ties to |
|---|---|---|---|
| The module list answers "what is in this repo": T1–T3 all correct | ✓ | ✓ (T2 after self-correction from the map) | D7, module list |
| **Reasons are hard to locate.** The reason was on the map only behind a source link | Some relations needed the source; too many links, which one first? | Did not see where the reason was written; found the source link after searching | D1 |
| **🟡 can read as a warning** before the guide is read | — | Read 🟡 as "something is wrong" | D3, D10 |
| **「無紀錄的理由」 is ambiguous for a new member.** Alice's in-page guide explains 🟡 / ✅ but not this phrase (only Bob's guide does) | Understood | Did not know whether the AI or the developers lacked the reason | D2, D10 |
| Requests | Mark the most important source | Arrow diagram of data flow; plainer module names | — |

On P2's open question (§2: do new users understand the buttons and 「無紀錄的理由」 without help?):
one participant did; the other needed the guide for the labels and still did not understand
「無紀錄的理由」. The in-page guide helps but is not sufficient on its own.

**Limits.** Two participants; no timings were recorded, so nothing here speaks to speed. The
participant watched the facilitator's screen instead of using the app, so we did not see what they
would click first, and the existing-member side (Bob's review) was not tested. The demo map was
written by the team, so these sessions test the map's presentation, not Claude's drafting. The
repository is our own project, which participants may have heard about.

## 4. Open questions

- Will existing members actually review claims, or skip straight to answering questions? (D4 is
  our bet; the stats box will show this.)
- Is the module level the right place for questions, or do people want to ask about a single file?
- Does the reading order help more than the module list? Watch which one participants use first.

# Design Rationale — Onboarding Map (CP2)

Key interaction design decisions in the MVP, and what shaped each one. Evidence sources:
CP1 interviews (2026-10-24, two first-year master's students who took over existing codebases),
the CP1 design sketch, our own pilot, and user-testing sessions (§3, to be filled in).
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

## 3. User-testing sessions (real users outside the team) — TO BE FILLED IN

CP2 requires at least two. Method from CP1 §4: the participant does the six onboarding tasks on an
unfamiliar repo with the map, while a teammate plays the existing member. Leave a field empty
rather than guessing.

### Session 1

- **Date / place / duration:**
- **Participant:** (role, e.g. "first-year master's student, has joined an existing lab codebase"; no names)
- **Repository used:**
- **Six tasks** (time · correct? · questions asked to the "existing member"):
  1. Name the main modules:
  2. Find the file where a given feature is implemented:
  3. Find how to run the project:
  4. Explain how two modules relate:
  5. Find the reason behind one recorded design decision:
  6. Say which file they would edit first for a given small change:
- **Existing-member side** (if tested): minutes to review; claims confirmed / edited / flagged (from the stats box).
- **What they said / where they got stuck** (quotes, translated):
- **Did they understand the buttons and 「無紀錄的理由」 without help?**
- **Changes we made because of this session** (and the PR / DECISIONS entry):

### Session 2

(same fields)

## 4. Open questions

- Will existing members actually review claims, or skip straight to answering questions? (D4 is
  our bet; the stats box will show this.)
- Is the module level the right place for questions, or do people want to ask about a single file?
- Does the reading order help more than the module list? Watch which one participants use first.

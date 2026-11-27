# Decisions Log

## 2026-09-21 — Initial code steward
**What:** Hank is the initial code steward for the team.
**Why:** Hank volunteered and has the most Git experience so far.

## 2026-10-25 — Problem and target users (Phase 1, recorded 2026-11-28)
> The four Phase 1 entries below were decided while writing our CP1 report (submitted 2026-10-25) but were not logged here at the time. They were recorded on 2026-11-28 from that report.

**What:** We build a New Member Onboarding Map for university students who join a software project whose repository already has weeks or months of history (joining a course team mid-semester, taking over a graduated senior's lab code, inheriting a service as an intern). It turns the repository's own records (README, file tree, PRs and comments, issues, commits, `DECISIONS.md`) into a map of the main modules, how they relate and why key choices were made, each claim linked to its source.
**Why:** Two interviews (2026-10-24, first-year master's students who took over existing codebases) showed that both could work out the structure on their own, but the reason behind unusual code (a 0.3 loss scaling, a 50 ms sleep) was only in a commit message or an 8-month-old PR, found after digging. Answers from existing members stay in private chat where the next new member cannot find them.
**Alternative rejected:** Relying on what new members already use: the README (describes what, rarely why), PR search and `git log` / `git blame` (only help once you know which line is strange), and ChatGPT or DeepWiki-style summaries (explain what, guess why, and nobody who knows the project checks the guess).
**Led by:** all four (decided together while writing CP1)

## 2026-10-25 — Team charter: disagreements, definition of done, communication (Phase 1, recorded 2026-11-28)
**What:** Disagreements: whoever raises one writes the options and the evidence in the PR or team channel; everyone replies within 24 hours; without agreement the current code steward decides within the next 24 hours (if the steward is one of the two sides, the next steward in the rotation decides); decisions that change architecture, data model, scope or evaluation method get a `DECISIONS.md` entry. Done means: merged into `main` through a PR (branch protection, one approving review), PR template filled in including AI involvement, approved by a teammate, runs from a fresh clone with the README steps and tests pass, a `DECISIONS.md` entry for significant choices, the prompt logged if AI output stayed in the repository, and the related issue closed. Communication: LINE for day-to-day messages and GitHub for anything about code; a 15-minute sync after Monday class; replies within 24 hours on weekdays and 48 on weekends; PR reviews within 48 hours.
**Why:** "I prefer X" is not evidence; we wanted decisions made on evidence and kept next to the work, and a definition of done that can be checked on GitHub.
**Alternative rejected:** Breaking ties by a vote.
**Led by:** all four (decided together while writing CP1)

## 2026-10-25 — Interaction design: AI drafts, the existing member checks, the new member asks (Phase 1, recorded 2026-11-28)
**What:** The existing member (Bob) gives a GitHub URL; the AI drafts a map of about 5–10 modules (purpose, key files, related modules, linked PRs and decisions) and a "start here" reading order of 5–8 items. Every claim is labelled inferred and cites a repository source, or says "no recorded reason" instead of guessing. Bob confirms, edits or flags each claim; the new member (Alice) reads in the suggested order and asks questions on a module; Bob's answers are saved on the map. A drafted `DECISIONS.md` entry may only be opened as a PR, never committed directly. AI component: Gemini API (replaced by the Claude API, see 2026-11-23).
**Why:** The interviews found the reasons in repository history, and AI tools answer "why" with confident guesses (as seen in our Week 6 lab), so a person who knows the project checks each claim and every claim shows where it came from. Answers kept on the map reach the next new member.
**Alternative rejected:** An AI summary used without a human check; questions answered in private chat. Left open: if existing members will not review up front, make the review optional and rely on the inferred label and source links (decided 2026-11-23, "Map language and review gate").
**Led by:** all four (decided together while writing CP1)

## 2026-10-25 — Evaluation method: each participant with and without the map (Phase 1, recorded 2026-11-28)
**What:** 6–8 students from outside the team do six onboarding tasks (name the modules, find a feature's file, find how to run it, explain how two modules relate, find a recorded design reason, say which file to edit first) on two comparable repositories, one with the map and one with GitHub only, order swapped for half. We measure time, tasks correct and questions to the "existing member" (a teammate), plus the share of AI claims accepted without edits and the minutes the check takes. Supported only if all hold: at least 6 participants complete both conditions; at least 4 of 6 are faster and the median time drops by at least 25 %; accuracy with the map is at least 70 % and not lower than without; fewer questions with the map in at least 4 of 6; at least 80 % of AI claims accepted without edits and the check takes 15 minutes or less.
**Why:** Each person is their own comparison, so a result cannot come from one repository being easier; faster but wrong does not count.
**Alternative rejected:** Testing each participant on one repository only. CP2 ran two sessions with the map only; see `docs/evaluation_report.md` §2 and §4.
**Led by:** all four (decided together while writing CP1)

## 2026-11-23 — MVP scope: map + review + questions
**What:** The CP2 MVP covers the full two-person loop at its smallest: the existing member generates an AI-drafted onboarding map and confirms / edits / flags each claim; the new member asks questions on a module; the existing member's answers are saved on the map.
**Why:** CP2 requires a prototype that two people can use together; the map alone would be a one-person tool.
**Alternative rejected:** (A) AI map only — not a two-person tool. (C) Also auto-drafting DECISIONS.md PRs from answers — does not fit the CP2 timeline; kept as a later feature.
**Led by:** Hank

## 2026-11-23 — AI component: Gemini → Claude API
**What:** The product's AI component is the Claude API (official `anthropic` Python SDK), default model `claude-sonnet-5-5`, configurable via `ANTHROPIC_MODEL`. Claude Code / Codex remain development tools only.
**Why:** The course provides Claude API access.
**Alternative rejected:** Gemini API (our CP1 plan).
**Led by:** Hank

## 2026-11-23 — MVP stack: Streamlit + SQLite
**What:** The MVP is a single Python Streamlit app with a local SQLite database; both roles open the same running app in separate browser windows.
**Why:** Python only and the fastest path to a working two-person demo before CP2 (2026-11-29).
**Alternative rejected:** FastAPI backend + HTML/JS frontend — cleaner split but roughly twice the code and needs JS.
**Led by:** Hank. Proposed by Claude Code during design and accepted by Hank (an AI suggestion that changed the approach, so it is recorded here per our AI usage guidelines).

## 2026-11-23 — Map language and review gate
**What:** The generated map and the UI are in Traditional Chinese; when no source explains something the map says exactly 「無紀錄的理由」. The new member can see the map before the existing member has reviewed it; every claim shows its status and flagged claims are hidden from the new member.
**Why:** Our test users are Taiwanese students. Showing the map before review resolves the CP1 open question (§3.3) with its fallback: rely on the "inferred" label plus source links instead of blocking on the existing member.
**Alternative rejected:** English output; a "publish" step before the new member can see the map.
**Led by:** Hank

## 2026-11-23 — Code steward handoff: Hank → Tiffany
**What:** TiffanyChen-tc is the code steward from today, taking over from Hank. Her first action as steward is reviewing the MVP pull requests (this PR, then the MVP code and the UI guide).
**Why:** Hank wrote the MVP pull requests and cannot approve his own work. CP2 also requires every member to serve as steward at least once and to approve two PRs as steward with a real comment, so we rotate now instead of at the end.
**Alternative rejected:** Hank staying steward until merge day. That would leave him reviewing nothing of his own and the others with no steward record.

## 2026-11-23 — In-page role guide and progress steps (pilot finding)
**What:** The page shows a short guide for each role (what the buttons and 🟡/✅/⛔ mean, what 「無紀錄的理由」 means, where questions go), the three review buttons are grouped together, and map generation shows step-by-step progress.
**Why:** In our first internal pilot (Hank, 2026-11-23) the page was not self-explanatory ("我怎麼看？", "不同成員能幹嘛？") and the spinner gave no sense of progress. Details in `docs/design_rationale.md` §2. This is a team-member pilot, not one of the CP2 user-testing sessions.
**Alternative rejected:** A separate help page (one more click; first-time users would not find it).
**Led by:** Hank

## 2026-11-23 — Code steward handoff: Tiffany → ChingChingKao
**What:** ChingChingKao is the code steward from today, taking over from Tiffany after PR #5 was merged. Her first action as steward is reviewing the MVP code PR (this PR) and then the UI guide PR.
**Why:** We rotate the steward role so every member serves as steward and approves at least two PRs as steward before CP2 (individual minimum).
**Alternative rejected:** Keeping one steward for all MVP PRs, which would leave the other members without a steward record.
**Led by:** Hank

## 2026-11-23 — Code steward handoff: ChingChingKao → ShenChiaoHsuan
**What:** ShenChiaoHsuan is the code steward from today, taking over from ChingChingKao. As steward, ShenChiaoHsuan reviewed and approved ChingChingKao's PR #8 (percent-encode `file:` source links) and PR #9 (count edited claims by current status).
**Why:** ChingChingKao wrote PR #8 and PR #9 and cannot approve her own work. We rotate the steward role so every member serves as steward and approves at least two PRs as steward before CP2 (individual minimum).
**Alternative rejected:** ChingChingKao staying steward, which would leave ShenChiaoHsuan without a steward record.
**Led by:** ShenChiaoHsuan

## 2026-11-23 — Code steward handoff: ShenChiaoHsuan → TiffanyChen-tc
**What:** TiffanyChen-tc is the code steward from today, taking over from ShenChiaoHsuan.
**Why:** We rotate the steward role so every member serves as steward and approves at least two PRs as steward before CP2 (individual minimum).
**Alternative rejected:** ShenChiaoHsuan staying steward.
**Led by:** TiffanyChen-tc

## 2026-11-23 — Sidebar in-page index
**What:** The sidebar shows a page index below the role and map selectors: links to 「從這裡開始」, 「模組」 and every module of the selected map, in module order, inside a compact rounded panel with two native collapsible levels (「頁面索引」 for the whole panel, 「模組清單」 with the module count). Links scroll the same page; the full page stays as it is (no tabs, separate pages or module filtering).
**Why:** TiffanyChen-tc asked for a faster way to reach the reading order, the module list and a specific module on a long map, and for the index to look like a tidy navigation panel rather than a plain underlined link list.
**Alternative rejected:** Keeping manual scrolling as the only way to locate sections.
**Led by:** TiffanyChen-tc

## 2026-11-24 — Collision-safe module ID deduplication
**What:** Reserve all original module IDs before renaming duplicates. Keep the first occurrence of each original ID and assign duplicates the smallest available numeric suffix, avoiding both original and newly assigned IDs. Preserve module order, non-ID fields and relation targets.
**Why:** A generated suffix can otherwise collide with an original ID such as a-2, leaving duplicate IDs. Reserving originals keeps distinct modules identifiable without redirecting references to an existing original ID.
**Alternative rejected:** Renaming duplicates using only per-ID occurrence counts without reserving the original IDs.
**Led by:** TiffanyChen-tc

## 2026-11-24 — Code steward handoff: TiffanyChen-tc → hank1101444
**What:** hank1101444 is the code steward from today, taking over from TiffanyChen-tc.
**Why:** We rotate the steward role so every member serves as steward and approves at least two PRs as steward before CP2 (individual minimum).
**Alternative rejected:** TiffanyChen-tc staying steward.
**Led by:** TiffanyChen-tc

## 2026-11-27 — Walking skeleton slice: mark human-edited claims (issue #23)
**What:** In the walking skeleton session (2026-11-27, online, all four present) we chose one thin slice: a claim that a person has rewritten shows 「✍️ 人工修改」 to both roles, and only the existing member also sees 「原本 AI 寫的：…」. "Edited" is derived from the stored `Claim.ai_text` versus `Claim.text`; no new database column. Split: hank1101444 writes the failing AppTests first (`skeleton/tests`), ChingChingKao adds `Claim.human_edited` (`skeleton/model`), TiffanyChen-tc adds the label (`skeleton/label`), ShenChiaoXiuan adds the original-text note (`skeleton/original`); each builds on their own branch and the pieces are connected into `walking-skeleton` one at a time. Worksheet: `docs/walking_skeleton.md`.
**Why:** Group 10's review (A3) found that an edited claim looked the same as an AI claim that was only confirmed. The original text is already stored, so the slice fits one session without touching the schema, review or stats.
**Alternative rejected:** A provenance column in the database; showing the AI's original text to the new member as well; issue #22 (needs a prompt change and the live suite) or issue #24 as the session's slice.
**Led by:** hank1101444 (proposal); agreed by all four in the session.

## 2026-11-28 — "Edited" means the text changed, in the stats too
**What:** `store.stats()` counts a claim as edited only when its current text differs from the AI's original (`text != ai_text`), the same rule as the 「✍️ 人工修改」 label. A claim that was edited back to the AI's exact words, or saved without changing a character, counts as accepted without edit. This updates the walking skeleton entry above, which had planned to leave the stats untouched.
**Why:** In the review of PR #25, hank1101444 (steward) pointed out that the label compared text while the stats counted any press of 「修改」, so the page and the stats box could disagree about the same claim. "Accepted without edit" is a CP1 evaluation metric, so it needs one definition.
**Alternative rejected:** Keeping the event-based count and opening an issue for later; counting both "pressed edit" and "changed text" separately.
**Led by:** ChingChingKao (commit `283bbcc` in PR #25, in reply to hank1101444's review)

## 2026-11-28 — Merge day plan
**What:** Merge plan for the CP2 merge day, written by the code steward before the session (worksheet: `docs/merge_day.md`). State on 2026-11-28: `main` at `324edd1`, `pytest` 161 passed; no open pull requests; open issues #22 and #24 stay open for Phase 3.
- Open branches and PRs: (1) `docs/team-sessions`: the two team-session worksheets, the evaluation report, this plan and the stats decision above; ready except for user-testing results; opened by a member other than the steward. (2) `docs/user-testing`: results of the two user-testing sessions in `docs/design_rationale.md` §3 and the evaluation report; ready once both sessions are written up. (3) Already merged branches (`skeleton/*`, `walking-skeleton` and 16 older ones): delete.
- Merge order: (1) first, because it carries this plan and the evaluation report that (2) builds on; then (2); then delete merged branches and run the fresh-clone test on `main`. Anything else opened on the day goes after these, or becomes an issue if it puts the fresh-clone test at risk.
- Expected conflicts: `DECISIONS.md` and `docs/prompt_log.md` (both append; keep both sides in date order), possibly `docs/evaluation_report.md` (keep the user-testing numbers from (2)).
- Close without merging: none.
- Done today means: `pytest` passes and the app starts on `main`; a member other than the steward clones into a new folder, follows only the README and completes the main task (Bob generates or loads the demo map and reviews claims, Alice asks on a module, Bob answers, Alice sees the answer); no open pull requests.
**Why:** CP2 asks for a clean `main` that runs end to end on a fresh copy, with every open PR merged or closed together.
**Alternative rejected:** Merging the user-testing results first; it is branched from `docs/team-sessions`, so it would bring that branch in without its own review.
**Led by:** hank1101444 (code steward)
**Outcome (2026-11-28):** Merged #26 (`docs/team-sessions`, approved by hank1101444 as steward after he asked for the PR's test checkboxes to be corrected) and #27 (`docs/user-testing`, approved and merged by TiffanyChen-tc), at 00:57 and 01:07 on 2026-11-28, one day before the planned merge day and not step by step on a shared screen; closed none. No conflicts on GitHub; one conflict in `docs/prompt_log.md` when `docs/user-testing` took in `docs/team-sessions` (both sides changed the end of the table), resolved by keeping both rows (`c442220`). #27 merged the "User testing findings" entry as a draft; all four then agreed to it as written, confirmed in #28 (merge-day records, merged by ShenChiaoXiuan). Deleted the 23 remote branches already merged into `main`. Fresh clone test by ShenChiaoXiuan (not the steward), following only the README: succeeded with no missing steps reported. `main` is green: `pytest` 161 passed, 13 deselected, and the app starts (`bdf91d1`). Left for after CP2: issues #22 and #24, and the three changes in "User testing findings". Worksheet: `docs/merge_day.md`.

## 2026-11-28 — User testing findings
**What:** Record what the two CP2 user-testing sessions found (`docs/design_rationale.md` §3, `docs/evaluation_report.md` E5) and change nothing in the app before CP2 (the merge day plan adds nothing new). After CP2, in this order:
1. Alice's in-page guide explains 「無紀錄的理由」 in one sentence: the repository has no written reason, which is not the same as the AI not knowing; a person who knows can add it. It also says that 🟡 is not a warning.
2. A simple arrow diagram of how data moves between modules, drawn from the module relations the map already has.
3. Mark one main source per claim. This needs a prompt change, so it goes through the live suite and `docs/prompt_card.md`.
Not changing: module names. Claude takes them from the repository and each module already has a plain description; revisit if later sessions show the same problem.
**Why:** Both participants found the modules, a file and a module relation from the map (T1–T3), but locating a design reason took longer (Session 2 did not see where it was written; Session 1 did not know which of several source links to open). Session 2 first read 🟡 as "something is wrong" and could not tell whether 「無紀錄的理由」 meant the AI or the developers lacked the reason; Alice's guide explains 🟡 / ✅ but not that phrase (only Bob's guide does). Ratings 4/5 and 3/5.
**Alternative rejected:** Changing the guide text before CP2: small, but the merge day plan adds nothing new on the day, and one participant was affected.
**Led by:** all four (hank1101444, ChingChingKao, ShenChiaoXiuan, TiffanyChen-tc) agreed to the proposal as written. Drafted by Claude Code from the session records; merged as a draft in PR #27 and confirmed afterwards.

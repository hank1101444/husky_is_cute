# Decisions Log

## 2026-09-21 — Initial code steward
**What:** Hank is the initial code steward for the team.
**Why:** Hank volunteered and has the most Git experience so far.

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

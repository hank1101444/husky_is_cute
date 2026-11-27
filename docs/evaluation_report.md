# Evaluation Report — Onboarding Map (CP2, interim)

**Status (2026-11-28):** interim. The prototype works end to end and its AI component is tested, but
our main claim, that new members understand a repository faster and more accurately with the map,
is **not yet shown**. The two CP2 user-testing sessions are recorded in
[`design_rationale.md`](design_rationale.md) §3 and summarised in E5 and §4 below: both participants
could find the modules, a file and a module relation from the map, but finding *why* something was
built a certain way took longer, and one participant did not understand 「無紀錄的理由」.
Where we have no evidence, this report says so.

## 1. What we set out to show (from CP1)

CP1 defined success as: new members understand an unfamiliar course project **faster and more
accurately** with the map than with the team's usual onboarding (asking people, reading the README,
code, PRs and issues). We planned to measure, on onboarding tasks:

- time to complete the tasks;
- accuracy on project-comprehension questions;
- number of clarification questions asked to an existing member;
- whether participants say the map made the project easier to understand.

**AI–human boundary (unchanged in spirit, now with Claude):** Claude drafts the map from the
repository's own records and must cite a source for every claim, or say 「無紀錄的理由」. It decides
nothing authoritative. The existing member confirms, edits or flags each claim; the new member decides
what to trust, with the source links and the 🟡/✅/⛔ status in front of them.

## 2. Changes to the plan since CP1

| CP1 plan | What changed | Why | Record |
|---|---|---|---|
| Gemini API | Claude API (`claude-sonnet-5-5`) | The course provides Claude API access | `DECISIONS.md` 2026-11-23 |
| ≥ 5 participants before judging success | 2 sessions by CP2 (the course minimum); 5 is now the Phase 3 target | One week between MVP and CP2 | this report |
| Compare with the existing onboarding process | No "without the map" condition has been run yet, so no speed comparison is possible | Two sessions are too few to split into two conditions | this report, §5 |
| "Share of claims accepted without edits" | Defined: a claim counts as edited only if its text differs from the AI's original | The label and the stats box used different rules (found in review of PR #25) | `DECISIONS.md` 2026-11-28 |

## 3. Evidence so far

| # | Source | Who | What it shows | What it does **not** show |
|---|---|---|---|---|
| E1 | Prompt test suite, 13 cases (`pytest -m live`), [`prompt_card.md`](prompt_card.md) | Team, real Claude API | Output follows our rules on typical repos, edge cases (no README, no PRs, huge tree, Chinese README, conflicting sources) and an invented-reason decoy. One revision cycle: round 2 failed 8/13 on half-width commas in Chinese text; after a prompt change round 3 passed 13/13 | That cited sources actually support the claims (we check that IDs exist, not what they say); behaviour on repos unlike our cases; stability across runs |
| E2 | Offline tests (`pytest`), 161 passing on `main` at `324edd1` | Team | Fetching, validation, storage, both roles' pages, review flow, demo mode and the human-edited label work as specified | Anything about users |
| E3 | Internal pilot P1–P2, [`design_rationale.md`](design_rationale.md) §2 | Hank (team member) | The first version was not self-explanatory (「我怎麼看？」) and gave no sense of progress; led to the role guide and step-by-step progress | Anything about outside users; the pilot user wrote the app |
| E4 | Group 10's Week 12 review (Track A), issues [#22](https://github.com/hank1101444/husky_is_cute/issues/22), [#23](https://github.com/hank1101444/husky_is_cute/issues/23), [#24](https://github.com/hank1101444/husky_is_cute/issues/24) | Classmates outside the team, reviewing the prototype | An edit made in Bob's view shows up in Alice's view (A1). Of **8 AI claims inspected, 7 were supported** by their sources; 1 said 「無紀錄的理由」 although `DECISIONS.md` held the reason (A2, #22, open). Edited claims looked like AI claims (A3, #23, **fixed in PR #25**). Demo maps are not marked in the selector (#24, open) | Onboarding tasks, timing or comprehension; reviewers were checking the prototype, not learning a repo |
| E5 | User-testing sessions 1–2 (15 min each, online), [`design_rationale.md`](design_rationale.md) §3 | Two students outside the team: one CS student with GitHub project experience, one GitHub user new to this project | With the demo map, both named the modules (T1), found `github_fetcher.py` (T2) and explained the data flow between two modules (T3). Finding a design reason and its source (T4) was correct for one and partial for the other, who did not see where the reason was until finding the source link. Ratings 4/5 and 3/5. One participant read 🟡 as "something is wrong" until reading the guide and did not understand 「無紀錄的理由」; Alice's guide does not explain that phrase | Speed (no timings recorded); anything without the map; Claude's own drafting (the demo map is hand-written); what participants would click themselves (they watched the facilitator's screen); the existing member's side |

## 4. Results against the CP1 thresholds

| CP1 criterion | Threshold | Status | Evidence |
|---|---|---|---|
| Participants | ≥ 5 target users | **Not met.** 2 sessions held (the CP2 minimum) | E5 |
| Faster with the map than without | ≥ 4 of 5 faster | **Untested.** No "without the map" condition | — |
| Comprehension accuracy | ≥ 80 % correct with the map | **Met on paper, too few to judge.** Required tasks T1–T4: 7 of 8 correct (88 %), 1 partial. All six tasks: 9 of 12 correct (75 %), 3 partial (T4 once, T5 twice). Scored by us from the notes against an answer key written before the sessions | E5 |
| Perceived help | ≥ 4 of 5 say it helped | **Mixed.** Ratings 4/5 and 3/5; both said it was easier than starting from the code or the file list | E5 |
| AI claims are trustworthy enough to help | (no CP1 number) | **Partial.** 7 of 8 claims supported in one outside review; suite 13/13 | E1, E4 |
| Existing member's review effort | (CP1 §3.3 open question) | **Untested with real users.** The stats box records review minutes and accepted / edited / flagged counts, but no existing member outside the team has reviewed a map | — |

## 5. What is untested, and why it matters

- **The core claim (faster, more accurate onboarding).** We have no comparison against onboarding
  without the map, and the two sessions recorded no timings. They show that people can use the map
  and where they get stuck (finding reasons, 🟡, 「無紀錄的理由」), not that it is faster.
- **Whether citations support the claims.** The validator only checks that a cited source exists. One
  outside review found 7 of 8 supported; that is one map of one repository.
- **Missed reasons.** #22 shows the AI can say 「無紀錄的理由」 when a reason does exist. We do not
  know how often this happens.
- **The existing member's side.** Will a real existing member spend time reviewing claims, or skip to
  answering questions? (CP1 §3.3; `design_rationale.md` §4.)
- **Repositories unlike ours.** Large repositories (only the latest 30 PRs / 30 issues / 50 commits are
  read), private repositories, and projects whose reasons live outside GitHub (chat, wandb, meetings).
- **Run-to-run variation** of Claude's output: each suite case was run once per round.

## 6. Threats to validity

- Participants may be classmates who have seen our project or this repository.
- A team member plays the existing member, so answers are faster and better informed than in a real team.
- The team wrote the demo map by hand; sessions that use it test the interface, not Claude's drafting.
- In both sessions the participant watched a teammate's shared screen and asked them to scroll or
  click, so we did not observe what participants would open first on their own.
- We scored correct / partial ourselves from notes; T5 and T6 had no written pass criterion.
- Small numbers: two sessions cannot support any percentage claim.

## 7. Next steps (Phase 3)

1. Reach the CP1 threshold of 5 participants, with a "without the map" condition (README and GitHub
   only) on a matched repository, so speed and accuracy can be compared.
2. Measure citation support on more claims: for each map, an outside reader checks every claim against
   its source (extends E4).
3. Fix #22 with a regression case in the prompt suite, and record before/after results in
   `prompt_card.md`.
4. Ask a real existing member (outside our team) to review a map of their own repository, and read
   review minutes and accepted / edited / flagged counts from the stats box.
5. Act on the user-testing findings (E5) after a team decision (`DECISIONS.md`, "User testing
   findings"), then check them in the next sessions: does a new member understand 🟡 and
   「無紀錄的理由」 without help, and find a design reason without searching?

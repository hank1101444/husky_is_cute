# AI Usage Guidelines — Group 21

Refined from our Week 3 / CP1 draft. **Change on 2026-11-23:** the product's AI component moved
from the Gemini API to the Claude API (see `DECISIONS.md`, "AI component: Gemini → Claude API").
**Change on 2026-11-24 (Week 12):** three rules were rewritten as checkable rules, based on our
merged PRs. The evidence is in §4.

## 1. Tools and what we use them for

### Claude API (in the product)

The Claude API (`claude-sonnet-5-5` by default, set by `ANTHROPIC_MODEL`) is the AI component of the
Onboarding Map. It is used to:

- group the repository's files into 5–10 modules and summarise each module's purpose;
- suggest how modules relate and which PRs, issues, commits and `DECISIONS.md` entries explain them;
- suggest a "start here" reading order for a new member.

It is **not** an authoritative source. Every claim it makes must cite a source from the repository;
when there is no source it must say 「無紀錄的理由」 instead of guessing. Claims start as *inferred*;
the existing member decides whether each one is correct. The product prompt lives only in
`src/onboarding_map/prompts.py` and is documented in `docs/prompt_card.md`.

### Claude Code and Codex (during development)

Used for implementation help, debugging, explaining code, refactoring suggestions, boilerplate and
first-draft tests. **Not** used as a substitute for human code review or for final engineering
decisions. AI-generated code is reviewed and tested by a team member before it is merged into
`main`. Architecture and design decisions are made by the team. Rules for these tools in this repo
are in `CLAUDE.md`.

## 2. How we document AI interactions

- **Prompt engineering log (`docs/prompt_log.md`):** every prompt that produced code, documentation,
  analysis or other content that ends up in the repository — tool/model, prompt or task, output,
  what was kept / changed / rejected. One-off syntax, debugging or Git lookups need no entry unless
  their output ends up in the repo.
- **Pull request descriptions (Rule 1, revised 2026-11-24):** every PR fills in all four lines of
  the **AI assistance** section of `.github/pull_request_template.md`: tool and model, what it
  generated (file or function names), the instruction given, and what the author changed afterwards
  ("nothing" is a valid answer). A PR without AI help writes "Tool and model: none". When AI helped,
  `docs/prompt_log.md` has at least one row whose PR column is the real PR number (`#<n>`, not `TBD`)
  before the PR is merged. Whoever resolves a merge conflict in `docs/prompt_log.md` keeps the rows
  from both sides.
  *Check:* the reviewer reads the four lines and runs `git grep -n "#<n>" -- docs/prompt_log.md` on
  the PR branch; after the merge, the same command on `main` still finds the row.
- **`DECISIONS.md`:** only when an AI suggestion meaningfully changes an important decision
  (architecture, data model, map structure, the evidence used to infer relationships, evaluation or
  implementation approach). We record what was chosen and why — the decision stays the team's.

## 3. Disagreements about AI output quality

- The **code steward** has the final say — not the person who wrote the prompt, and not a vote.
- **Test evidence for AI-generated code (Rule 2, revised 2026-11-24):** a PR that changes files
  under `src/` lists in **How I checked it**: the exact test command; the tests it adds or changes
  and how many of them failed before the change; and the full offline result as
  `N passed, M deselected`. If `src/onboarding_map/prompts.py` changed, it also gives the
  `pytest -m live` result before and after the change; otherwise it says
  "N/A: prompts.py unchanged". A PR that changes no code says "Docs-only, no tests run" and does not
  claim that tests passed. A PR is not merged while any offline test fails.
  *Check:* the reviewer finds each of these items in the PR description.
- **Human review by the code steward (Rule 3, revised 2026-11-24):** before a PR is merged, a member
  other than the author (normally the current code steward, see `DECISIONS.md`) approves it with a
  review comment that (a) names at least one specific function, test or file in the change and
  says what they checked there, and (b) says whether they re-ran `pytest -q` on the branch (with
  the result) or only read the diff. An empty approval, or praise without a specific reference,
  does not count as a review. The author ticks "I read every line of this change myself and can
  explain it without the AI" before the merge.
  *Check:* the PR's review list on GitHub.
- Style, formatting and naming disagreements follow our formatter / linter settings.
- If it is still unresolved, the steward decides and, when the decision is significant, writes the
  reasoning in `DECISIONS.md`.

## 4. Evidence for the 2026-11-24 revision

**Sources:** the descriptions, reviews and comments of every PR merged between 2026-11-10 and
2026-11-24 (12 PRs: #5–#12 and #16–#19, read through the GitHub REST API on 2026-11-24),
`docs/prompt_log.md`, and the git history. Each "Old rule" is quoted from this file as first
committed in
[`1428c56`](https://github.com/hank1101444/husky_is_cute/commit/1428c56d63dae9fd217aab5e3d9c6112b4621ea6)
(PR #5). That version says it was refined from our Week 3 / CP1 draft. The Week 3 text itself is
not in the repository, so it is not quoted here.

### Numbers (12 merged PRs)

| Measure | Count | How it was counted |
|---|---|---|
| PRs mainly generated by AI | 12 / 12 | Each PR's own AI section says that an AI tool wrote the main diff (code, tests or docs); humans gave the instructions and decided the scope. This is self-reported. The records do not show what share of each diff was AI-written. |
| PRs with evidence that another member understood the change | 11 / 12 | A non-author's review or comment names a specific function, test, behaviour or file in the change: #5, #6, #8–#12, #16–#19. #7 got only general praise. #6 and #9 have one-sentence reviews. This is evidence from written reviews only. The records cannot confirm that the reviewer could explain the change without AI, and no review clearly says that the tests were re-run. |
| PRs with AI involvement clearly recorded | 8 / 12 | The PR description names the tool, the model and what was generated, and `docs/prompt_log.md` on `main` has a row with that PR number: #5, #8–#11, #17–#19. Partly recorded: #6 and #7 (their log rows say "PR 2" and "PR 3"), #12 (its log row was lost in a merge, see Rule 1) and #16 (the ChatGPT model is "not reported"). Only #17–#19 fill in all four lines of the current template, which was added in #17. |

### Rule 1: the AI assistance section of the PR

- **Old rule:** "every PR fills in the **AI involvement** line of the template (e.g. 'Claude Code
  drafted the initial implementation; see prompt log 2026-11-23'). It is a pointer for reviewers,
  not a copy of the conversation." (#17 renamed "AI involvement line" to "AI assistance section".)
- **New rule:** §2, "Pull request descriptions".
- **Evidence:**
  - [PR #12](https://github.com/hank1101444/husky_is_cute/pull/12) says "Logged in
    `docs/prompt_log.md`". The row was added in
    [`b8b9a5d`](https://github.com/hank1101444/husky_is_cute/commit/b8b9a5d5cea9d536dc9900dc0d39f015d8b0a0f6)
    and dropped when `main` was merged into the branch in
    [`02a00d1`](https://github.com/hank1101444/husky_is_cute/commit/02a00d129463d73ea797c8f11fd294b7893f769f),
    so it is not on `main`. Nobody noticed, because no one checked the log after the merge.
  - [PR #7](https://github.com/hank1101444/husky_is_cute/pull/7) points to "the #7 row", but the
    row in [`docs/prompt_log.md`](prompt_log.md) says "PR 3". The rows for
    [PR #6](https://github.com/hank1101444/husky_is_cute/pull/6) say "PR 2".
  - [PR #16](https://github.com/hank1101444/husky_is_cute/pull/16) and its log row name ChatGPT
    with "model not reported".
  - [PR #8](https://github.com/hank1101444/husky_is_cute/pull/8) and
    [PR #9](https://github.com/hank1101444/husky_is_cute/pull/9) do not say which instruction was
    given or what the author changed afterwards.
  - The check works when someone does it: on
    [PR #17](https://github.com/hank1101444/husky_is_cute/pull/17) the reviewer asked for the `TBD`
    in the log to be replaced with the PR number before approving.
    [PR #18](https://github.com/hank1101444/husky_is_cute/pull/18) and
    [PR #19](https://github.com/hank1101444/husky_is_cute/pull/19) fill in all four lines.

### Rule 2: test evidence for AI-generated code

- **Old rule:** "Before AI-generated code is merged it must: pass the test suite (`pytest`, and
  `pytest -m live` for prompt changes), pass PR review, and be explainable by a team member other
  than the one who generated it." (Its review part is Rule 3.)
- **New rule:** §3, "Test evidence for AI-generated code".
- **Evidence:**
  - Most code PRs already report this: [#8](https://github.com/hank1101444/husky_is_cute/pull/8),
    [#9](https://github.com/hank1101444/husky_is_cute/pull/9),
    [#10](https://github.com/hank1101444/husky_is_cute/pull/10),
    [#11](https://github.com/hank1101444/husky_is_cute/pull/11),
    [#18](https://github.com/hank1101444/husky_is_cute/pull/18) and
    [#19](https://github.com/hank1101444/husky_is_cute/pull/19) give how many new tests failed
    before the change and the full offline result after it. The new rule makes this required.
  - [PR #7](https://github.com/hank1101444/husky_is_cute/pull/7) reports only "93 passed" for a
    code change, with no before-change result for its 2 new tests.
  - [PR #6](https://github.com/hank1101444/husky_is_cute/pull/6) changed the product prompt and
    reports the live suite, including the failed round (8/13), which is what the rule asks for.
  - [PR #12](https://github.com/hank1101444/husky_is_cute/pull/12) and
    [PR #17](https://github.com/hank1101444/husky_is_cute/pull/17) say that they are docs-only
    instead of claiming that tests passed.
  - We have no CI (`.github/` contains only the PR template), so every test result is a local run
    reported by the author. That is why the rule asks for the exact command and counts.

### Rule 3: a real human review by the code steward

- **Old rule:** "Before AI-generated code is merged it must: ... pass PR review, and be explainable
  by a team member other than the one who generated it."
- **New rule:** §3, "Human review by the code steward".
- **Evidence:**
  - Every one of the 12 PRs was approved by a member other than its author.
  - [PR #7](https://github.com/hank1101444/husky_is_cute/pull/7) was approved with general praise
    only ("The role guides make the app easier for new users to understand ...").
  - [PR #16](https://github.com/hank1101444/husky_is_cute/pull/16) was approved with an empty
    review. The reviewer's question was in a separate comment.
  - Specific reviews that show what the new rule asks for:
    [PR #8](https://github.com/hank1101444/husky_is_cute/pull/8) (`safe="/"` and the 5/6
    failing tests), [PR #11](https://github.com/hank1101444/husky_is_cute/pull/11) (the trimmed
    exact comparison and its counter-example) and
    [PR #19](https://github.com/hank1101444/husky_is_cute/pull/19) (the check order in
    `render_generator()`, the `no_fetch` fixture and a question about `parse_repo_url`).
  - No review clearly says that the reviewer re-ran the tests. The closest is
    [PR #18](https://github.com/hank1101444/husky_is_cute/pull/18): "Tried the demo button path in
    the tests", which does not say whether the tests were run or only read.
  - [PR #17](https://github.com/hank1101444/husky_is_cute/pull/17) was merged with "I read every
    line of this change myself" unticked.

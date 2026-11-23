# AI Usage Guidelines — Group 21

Refined from our Week 3 / CP1 draft. **Change on 2026-11-23:** the product's AI component moved
from the Gemini API to the Claude API (see `DECISIONS.md`, "AI component: Gemini → Claude API").

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
- **Pull request descriptions:** every PR fills in the **AI involvement** line of the template
  (e.g. "Claude Code drafted the initial implementation; see prompt log 2026-11-23"). It is a
  pointer for reviewers, not a copy of the conversation.
- **`DECISIONS.md`:** only when an AI suggestion meaningfully changes an important decision
  (architecture, data model, map structure, the evidence used to infer relationships, evaluation or
  implementation approach). We record what was chosen and why — the decision stays the team's.

## 3. Disagreements about AI output quality

- The **code steward** has the final say — not the person who wrote the prompt, and not a vote.
- Before AI-generated code is merged it must: pass the test suite (`pytest`, and `pytest -m live`
  for prompt changes), pass PR review, and be explainable by a team member other than the one who
  generated it.
- Style, formatting and naming disagreements follow our formatter / linter settings.
- If it is still unresolved, the steward decides and, when the decision is significant, writes the
  reasoning in `DECISIONS.md`.

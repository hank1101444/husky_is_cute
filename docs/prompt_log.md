# Prompt Engineering Log

Record every prompt whose output (code, docs, analysis) ends up in this repository.
See `docs/ai_usage_guidelines.md` §2. Newest entries at the bottom.

| Date | Tool / model | Prompt or task | Output | Kept / changed / rejected | PR |
|---|---|---|---|---|---|
| 2026-11-23 | Claude Code (Claude Opus 5.5) | Hank: read CP1 + course pages, brainstorm a simple CP2 MVP, update README, set up conda env + requirements, follow good AI-collaboration practice | Design spec and implementation plan (kept locally in `docs/superpowers/`, not committed), env files, `DECISIONS.md` entries, `CLAUDE.md`, these guidelines | Kept. Scope, model (Sonnet 5.5), map language and review gate were decided by Hank; stack proposal accepted by Hank; Claude's own smaller calls (fetch limits, claim/source rules, two-PR split) were reviewed by Hank with the spec | PR 1 |
| 2026-11-23 | Claude Code (Claude Opus 5.5) | Implement the MVP from the approved plan (fetcher, mapper, store, Streamlit UI, tests) | `src/onboarding_map/*`, `tests/*` | Kept; all offline tests pass; Hank to review in PR 2 | PR 2 |
| 2026-11-23 | Claude Code (Claude Opus 5.5) wrote the product prompt; tested on Claude Sonnet 5.5 | Draft the product system prompt (`prompts.py`): zh-TW output, cite source IDs, 「無紀錄的理由」 when no source | Initial `SYSTEM_PROMPT` | Kept; 12/12 suite cases passed on the first run | PR 2 |
| 2026-11-23 | Claude Code (Claude Opus 5.5); tested on Claude Sonnet 5.5 | Suite round 2 found half-width commas in Chinese text (8/13 failed); revise the prompt | Added the full-width punctuation rule + example to `SYSTEM_PROMPT` | Kept; 13/13 passed (see `docs/prompt_card.md` revision history) | PR 2 |
| 2026-11-23 | Claude Code (Claude Opus 5.5); review by a fresh Claude Fable 5.2 reviewer | Whole-branch code review of the MVP, then fix Critical/Important findings with regression tests; add step-by-step progress (Hank's request) | Fixes in `app.py`, `github_fetcher.py`, `mapper.py` + 12 tests | Kept; 91 offline tests pass; real 2-map run OK; minor findings deferred (listed in PR 2) | PR 2 |

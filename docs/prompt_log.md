# Prompt Engineering Log

Record every prompt whose output (code, docs, analysis) ends up in this repository.
See `docs/ai_usage_guidelines.md` §2. Newest entries at the bottom.

| Date | Tool / model | Prompt or task | Output | Kept / changed / rejected | PR |
|---|---|---|---|---|---|
| 2026-11-23 | Claude Code (Claude Opus 5.5) | Plan a simple CP2 MVP; set up the conda env and requirements; write AI-collaboration docs | `environment.yml`, `requirements.txt`, `pyproject.toml`, `.env.example`, `DECISIONS.md` entries (incl. steward handoff), `CLAUDE.md`, `docs/ai_usage_guidelines.md`, this log. Design spec and plan kept locally, not committed | Kept. Hank decided scope, model, map language, review gate and the steward handoff; he accepted the Streamlit + SQLite proposal | #5 |
| 2026-11-23 | Claude Code (Claude Opus 5.5) | Implement the MVP from the approved plan (fetcher, mapper, store, Streamlit UI, tests) | `src/onboarding_map/*`, `tests/*` | Kept; all offline tests pass; Hank to review in PR 2 | PR 2 |
| 2026-11-23 | Claude Code (Claude Opus 5.5) wrote the product prompt; tested on Claude Sonnet 5.5 | Draft the product system prompt (`prompts.py`): zh-TW output, cite source IDs, 「無紀錄的理由」 when no source | Initial `SYSTEM_PROMPT` | Kept; 12/12 suite cases passed on the first run | PR 2 |
| 2026-11-23 | Claude Code (Claude Opus 5.5); tested on Claude Sonnet 5.5 | Suite round 2 found half-width commas in Chinese text (8/13 failed); revise the prompt | Added the full-width punctuation rule + example to `SYSTEM_PROMPT` | Kept; 13/13 passed (see `docs/prompt_card.md` revision history) | PR 2 |
| 2026-11-23 | Claude Code (Claude Opus 5.5); review by a fresh Claude Fable 5.2 reviewer | Whole-branch code review of the MVP, then fix Critical/Important findings with regression tests; add step-by-step progress (Hank's request) | Fixes in `app.py`, `github_fetcher.py`, `mapper.py` + 12 tests | Kept; 91 offline tests pass; real 2-map run OK; minor findings deferred (listed in PR 2) | PR 2 |

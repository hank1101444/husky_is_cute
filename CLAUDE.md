# CLAUDE.md

Guidance for Claude Code (and other AI coding tools) working in this repository. Humans: this is
also the shortest summary of how we work.

## Project

**New Member Onboarding Map** (CSIC30216 Fall 2026, Group 21). A Streamlit app that turns a GitHub
repository (README, file tree, PRs + comments, issues, commits, `DECISIONS.md`) into an
AI-drafted onboarding map. The existing member confirms / edits / flags each claim; the new member
reads it and asks questions on a module; answers are saved on the map. Every AI claim must cite a
source from the repository or say 「無紀錄的理由」.

Key design decisions and their reasons: `DECISIONS.md`.

## Setup and commands

```bash
conda env create -f environment.yml   # once; env name: husky
conda activate husky
copy .env.example .env                # then fill in ANTHROPIC_API_KEY (Windows; use cp elsewhere)
streamlit run src/onboarding_map/app.py
pytest                                # offline tests
pytest -m live                        # prompt test suite, calls the real Claude API (costs money)
```

## Layout

- `src/onboarding_map/config.py` — settings from `.env`, fetch limits
- `src/onboarding_map/models.py` — Pydantic models shared by all modules
- `src/onboarding_map/github_fetcher.py` — GitHub API → `RepoSnapshot`
- `src/onboarding_map/prompts.py` — **the product's system prompt (single source of truth)**
- `src/onboarding_map/mapper.py` — Claude call (structured output) + source validation
- `src/onboarding_map/store.py` — SQLite: maps, claim reviews, questions, stats
- `src/onboarding_map/app.py` — Streamlit UI (Bob = existing member, Alice = new member)
- `tests/` — offline tests; `tests/prompt_suite/` — live prompt test cases

## Rules for AI coding tools

1. Work on a feature branch and open a PR; never push to `main` (it is protected anyway).
2. Never read, print, log or commit `.env` or any API key / token.
3. Do not add or change decisions in `DECISIONS.md` on your own. Draft an entry and let a human
   decide; record who led it.
4. If your output (code, docs, prompts) stays in the repo, add an entry to `docs/prompt_log.md` and
   fill in the PR template's **AI assistance** section.
5. Write the failing test first; run `pytest` and read the result before saying something works.
6. The product prompt lives only in `src/onboarding_map/prompts.py`. Any change to it must be run
   against the prompt suite (`pytest -m live`) and recorded in `docs/prompt_card.md`.
7. Map text and UI labels are Traditional Chinese; code, identifiers, comments and repo docs are
   English.
8. Keep each module's responsibility as listed above; teammates improve modules in separate PRs.

## Product system prompt

See `src/onboarding_map/prompts.py` (source of truth) and `docs/prompt_card.md` (what the AI
decides vs. what humans decide, known failure modes, revision history).

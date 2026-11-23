# husky_is_cute — New Member Onboarding Map

CSIC30216 Fall 2026 · Group 21

Students who join a project after its repository already has history cannot tell which parts
matter or why key choices were made. The **Onboarding Map** reads a GitHub repository (README, file
tree, pull requests and their comments, issues, commit messages, `DECISIONS.md`) and asks Claude to
draft a map: the main modules, what each is for, how they relate, and what to read first. Every
statement cites its source. When nothing in the repository explains a reason, the map says
「無紀錄的理由」 instead of guessing.

Two people use it together:

1. **Existing member (Bob)** pastes a repo URL and generates the map, then confirms ✅, edits or
   flags ⛔ each AI claim (every claim starts as 🟡 inferred).
2. **New member (Alice)** reads the map in the suggested order and asks a question on any module.
   Flagged claims are hidden from her.
3. Bob answers. The answer is saved on that module, so the next new member sees it.

The map and the UI are in Traditional Chinese.

## Setup

Requirements: [Miniconda/Anaconda](https://docs.conda.io/) and Git.

```bash
git clone https://github.com/hank1101444/husky_is_cute.git
cd husky_is_cute
conda env create -f environment.yml      # creates the "husky" env (Python 3.11) and installs this package
conda activate husky
copy .env.example .env                   # Windows; on macOS/Linux: cp .env.example .env
```

Then open `.env` and fill in:

| Variable | Required | What it is |
|---|---|---|
| `ANTHROPIC_API_KEY` | yes | Claude API key (from the course). Never commit or share it. |
| `ANTHROPIC_MODEL` | no | Defaults to `claude-sonnet-5-5`. |
| `GITHUB_TOKEN` | recommended | A read-only GitHub token. Without it GitHub allows 60 requests/hour, and each map uses about two requests per PR (one for PR comments, one for PR reviews), so you can hit the limit after a single map. Needed for private repos. |
| `ONBOARDING_DB_PATH` | no | SQLite file, defaults to `data/onboarding.db`. |

`.env` and `data/` are git-ignored.

## Run

```bash
streamlit run src/onboarding_map/app.py
```

Streamlit opens `http://localhost:8501`. To use it as two people, open the page in **two browser
windows** and pick a different role in the sidebar of each (`既有成員 (Bob)` / `新成員 (Alice)`).
Someone on the same network can also open the "Network URL" Streamlit prints. There is no login.
Anyone who can reach that URL can use the app, so only run it on networks you trust.

Generating a map takes about 20 seconds for a small repository.

When a map is selected, the sidebar shows a **頁面索引** panel below the role and map selectors. Its
links jump within the same page to 「從這裡開始」, 「模組」 and each module (a collapsed module is
scrolled to but not opened). Click 「頁面索引」 to fold the whole panel, or 「模組清單」 (the badge is
the number of modules) to fold only the module links.

**No API key?** As the existing member, press **載入示範地圖（不需 API key）** to load a predefined
sample map of this repository. It makes no Claude or GitHub calls, and both roles see a banner saying it
is sample data, not a live Claude result. Reviewing, asking and answering work as usual.

## Test

```bash
pytest              # offline tests (no network, no cost)
pytest -m live      # prompt test suite: 13 cases against the real Claude API (~3.5 min, roughly US$1)
```

Run `pytest -m live` after any change to `src/onboarding_map/prompts.py`, and record the result in
`docs/prompt_card.md`.

## Project layout

Each module has one job, which makes it a good unit for an improvement PR:

| Path | Responsibility |
|---|---|
| `src/onboarding_map/github_fetcher.py` | GitHub REST API → `RepoSnapshot` (limits: 30 PRs + comments, 30 issues, 50 commits) |
| `src/onboarding_map/prompts.py` | The product's system prompt and user-message builder |
| `src/onboarding_map/mapper.py` | Claude call (structured output) and the source validator |
| `src/onboarding_map/store.py` | SQLite: maps, claim reviews, questions and answers, review stats |
| `src/onboarding_map/app.py` | Streamlit UI for both roles |
| `src/onboarding_map/models.py` | Pydantic models shared by all modules |
| `src/onboarding_map/config.py` | Settings from `.env` |
| `tests/` | Offline tests; `tests/prompt_suite/` holds the live prompt cases |

## How we work

- Branch → pull request into `main` (protected, one approval). Fill in
  `.github/pull_request_template.md`, including the **AI assistance** section.
- Significant choices go in [`DECISIONS.md`](DECISIONS.md): what was chosen, why, what was rejected,
  who led it.
- AI tools: see [`docs/ai_usage_guidelines.md`](docs/ai_usage_guidelines.md). Prompts whose output
  stays in the repo are logged in [`docs/prompt_log.md`](docs/prompt_log.md). Rules for AI coding
  tools are in [`CLAUDE.md`](CLAUDE.md).
- What the product's AI does, its prompt, test suite and known failure modes:
  [`docs/prompt_card.md`](docs/prompt_card.md).
- Interaction design decisions, pilot findings and user-testing notes:
  [`docs/design_rationale.md`](docs/design_rationale.md).

## Known limitations (MVP)

- No login or permissions. The role is chosen in the sidebar.
- It runs locally. There is no cloud deployment.
- It reads only GitHub. Reasons kept in chat, wandb or meeting notes are invisible.
- It reads file names, not file contents.
- Answers are not yet turned into `DECISIONS.md` pull requests (planned).
- A map is not updated when the repository changes. Generate a new one instead (old maps stay
  selectable).
- The page index's folded / unfolded state lives only in the browser. Clicking index links keeps it;
  in our browser check it also survived Streamlit reruns after typing or switching role. A page
  reload starts with both levels open again, and other reruns (such as a map switch) may reset it.

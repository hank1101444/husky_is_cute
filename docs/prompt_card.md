# Prompt Card — Onboarding Map drafter

For a new engineer: what the AI in this product does, what it was told to do, how we test it, and
where it is known to fail. Source of truth for the prompt: `src/onboarding_map/prompts.py`.

## What the AI does (and does not do)

| The AI (Claude API) decides | Humans decide |
|---|---|
| How to group files into 5–10 modules for the draft | **Existing member:** whether each claim is correct — confirm, edit or flag — and the answer to every question |
| A one- or two-sentence purpose for each module, from repository content only | **New member:** what to trust and what to ask about |
| Which modules are related and why, citing PRs / issues / commits / DECISIONS entries | **Code steward:** anything that becomes a `DECISIONS.md` entry |
| A 5–8 item "start here" reading order | |

Every claim starts as **inferred** and must cite source IDs from the input. When no source explains a
reason the AI must write exactly 「無紀錄的理由」 instead of guessing. Citations are checked in code
(`mapper.validate`), not trusted: a claim with a missing / unknown source, or 「無紀錄的理由」 with sources
attached, is shown with ⚠ to both roles.

## Model and call

- Model: `ANTHROPIC_MODEL`, default `claude-sonnet-5-5` (decision 2026-11-23 in `DECISIONS.md`).
- One call per map: `client.beta.messages.parse(...)` with `output_format=OnboardingMapDraft`
  (structured output, Pydantic schema in `src/onboarding_map/models.py`), `max_tokens=16000`.
- Server-side refusal fallback on (`fallbacks="default"`, beta `server-side-fallback-2026-07-01`):
  if the model declines, the API retries on a fallback model inside the same call.
- Errors (bad key, rate limit, refusal, truncated output) become zh-TW messages in the UI
  (`mapper.MapperError`).

## Input format (user message)

Built by `build_user_prompt(snapshot)`:

```
Repository: https://github.com/<owner>/<repo> (default branch: main)

## File tree
<one path per line>

## Sources
[README] README
<url>
<text>

[PR#12] <title>
<url>
<body>
...            (also [PR#12/comment:<id>], [PR#12/review:<id>], [ISSUE#n], [commit:<sha7>], [DECISION:<heading>])

## Notes: incomplete data
- pulls: 只顯示最新 30 筆
```

Limits: 30 most recently updated PRs (with conversation comments), 30 issues, 50 commits, the full
file tree (GitHub may truncate very large trees; this is noted in the input and the UI).

## Output schema

`OnboardingMapDraft { modules: [DraftModule], reading_order: [DraftReadingItem] }`

- `DraftModule { id, name, purpose, purpose_source_ids[], key_files[], relations: [DraftRelation] }`
- `DraftRelation { target_module_id, reason, source_ids[] }`
- `DraftReadingItem { target, reason, source_ids[] }`

## System prompt (current version, copied from `prompts.py`)

```
You help a student who has just joined an existing software project. From the repository material you are given, draft an onboarding map: the main modules, what each is for, how they relate, and what to read first. An existing team member will check every statement you make, so only state what the material supports.

Language: write every name, purpose and reason in 繁體中文 (Traditional Chinese). Keep file paths, PR / issue titles and quoted identifiers exactly as they appear. Use full-width Chinese punctuation in Chinese sentences (，。、：；「」), e.g. 「負責讀取設定，並啟動伺服器。」. Never use a half-width comma "," inside Chinese text.

Sources: every item in the material has an ID in square brackets, e.g. [README], [PR#12], [PR#12/comment:345], [ISSUE#3], [commit:ab12cd3], [DECISION:<heading>]. Every file in the file tree can be cited as file:<path>. Cite sources only by these exact IDs. Never invent an ID.

Modules:
- Group the files into 5-10 modules (fewer only if the repository has very few files). Give each a short lowercase id (letters, digits, hyphens), a short Chinese name, and a purpose of one or two sentences.
- purpose_source_ids must list at least one ID that supports the purpose (a file:<path> of the module's own files is acceptable).
- key_files: 1-5 paths copied exactly from the file tree.
- relations: links to other modules (use their module id). Each relation has a reason.

Reading order: 5-8 items a new member should read first, in order. Each target is a file path from the tree or a source ID; each has a reason.

Reasons (relations and reading order):
- If a source explains the reason, write it and list those source IDs in source_ids.
- If no source explains it, the reason must be exactly 「無紀錄的理由」 and source_ids must be empty. Never guess why something was done. A "why" that is not written in the material is unknown, even if it seems obvious.
- Design reasons are often only in PR descriptions, PR comments, commit messages or DECISIONS entries; look there before concluding there is no recorded reason.
```

## Prompt test suite

`tests/prompt_suite/cases/*.json` — 13 fixed repository snapshots. Run with `pytest -m live`
(about 13 calls to `claude-sonnet-5-5`, ~3.5 minutes, roughly US$1). `pytest` alone only checks that
the case files are well-formed.

| Case | What it targets |
|---|---|
| `typical_python_app` | Typical layered Flask app with a clear PR reason |
| `typical_js_app` | Typical React + Express app |
| `husky_is_cute` | Our own tiny repo (real GitHub data) |
| `no_readme` | No README: must work from file names and commits |
| `empty_decisions` | `DECISIONS.md` exists but is empty |
| `no_prs` | README + commits only |
| `huge_tree_truncated` | ~2,000 files, truncated tree: must not invent paths |
| `chinese_readme` | README written in Chinese |
| `readme_vs_pr_conflict` | README is outdated; the PR holds the real reason → must cite `PR#12` |
| `reason_only_in_commit` | Strange 0.3 loss scaling explained only in a commit → must cite it |
| `reason_only_in_pr_comment` | Deliberate 50 ms sleep explained only in a PR comment → must cite it |
| `no_reason_anywhere` | Nothing explains anything → must say 「無紀錄的理由」 |
| `decoy_obvious_reason` | A cache whose "why" looks obvious (speed) but is written nowhere → must not invent 效能 / 加速 / … |

Checks on every case: module count within the case's range; every claim passes `validate`; no
invented key files; required citations present; 「無紀錄的理由」 where required; purposes contain
Chinese; no forbidden "invented reason" words; no half-width comma inside Chinese text.

## Known failure modes and limits

- **Only file names, not code.** The AI never reads file contents, so module purposes for files that
  no README / PR / commit mentions are guesses from the name ("依檔名判斷…"). The AI usually says so,
  but the existing member should check these first.
- **A real citation does not prove the reason.** `validate` checks that a cited source exists, not that
  it says what the claim says. The `decoy_obvious_reason` case probes this; reviewers still need to
  open the source link.
- **Nothing outside GitHub.** Reasons that live in wandb logs, chat, or meeting notes are invisible
  (CP1 interviewee A's case).
- **Truncated history.** Only the latest 30 PRs / 30 issues / 50 commits are read; an old PR that holds
  a reason can be missed. The UI says when data was cut.
- **Reading-order reasons** sometimes come out as 「無紀錄的理由」 for files like `README.md`, which is
  correct by our rule but reads oddly; a later prompt change could let reading-order reasons be the
  AI's own suggestion, labelled as such.
- **Run-to-run variation.** Outputs differ between runs; one green suite run is evidence, not proof.

## Revision history

| Date | Round | What happened | Prompt change | Result |
|---|---|---|---|---|
| 2026-11-23 | 1 | First run of the 12 original cases | — (initial prompt) | 12/12 passed |
| 2026-11-23 | 1b | Added `decoy_obvious_reason` (invented "performance" reason probe), ran it 3× | — | 3/3 passed: the model wrote 「無紀錄的理由」 / file-name based purposes instead of inventing a reason |
| 2026-11-23 | 2 | Added a check found by reading outputs: Chinese text used half-width commas (e.g. 「說明首頁,目前只有標題」) | — | **8/13 failed**, all on half-width commas |
| 2026-11-23 | 3 | — | Added: use full-width Chinese punctuation (，。、：；「」) with an example; never a half-width comma inside Chinese text | 13/13 passed |

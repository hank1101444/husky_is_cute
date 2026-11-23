"""Prompt test suite: runs the real prompt against fixed repository snapshots.

Offline check (always runs): every case file is well-formed.
Live check (`pytest -m live`, needs ANTHROPIC_API_KEY, costs money): the model's output passes
the checks below. See docs/prompt_card.md for what each case targets and the revision history.
"""

import json
import os
import re
from pathlib import Path

import pytest
from dotenv import load_dotenv

from onboarding_map.mapper import draft_map, validate
from onboarding_map.models import NO_REASON, RepoSnapshot

CASES_DIR = Path(__file__).parent / "cases"
CASE_FILES = sorted(CASES_DIR.glob("*.json"))
CJK = re.compile(r"[一-鿿]")
HALF_WIDTH_COMMA = re.compile(r"[一-鿿],|,[一-鿿]")


def load_case(path: Path) -> tuple[dict, RepoSnapshot]:
    case = json.loads(path.read_text(encoding="utf-8"))
    return case, RepoSnapshot.model_validate(case["snapshot"])


def test_at_least_ten_cases():
    assert len(CASE_FILES) >= 10


@pytest.mark.parametrize("path", CASE_FILES, ids=lambda p: p.stem)
def test_case_file_is_well_formed(path):
    case, snap = load_case(path)
    assert case["name"] == path.stem
    expect = case["expect"]
    assert set(expect) == {"min_modules", "max_modules", "must_cite", "requires_no_reason", "must_not_contain"}
    assert 1 <= expect["min_modules"] <= expect["max_modules"] <= 10
    assert set(expect["must_cite"]) <= snap.source_ids()


@pytest.mark.live
@pytest.mark.parametrize("path", CASE_FILES, ids=lambda p: p.stem)
def test_prompt_case(path):
    load_dotenv()
    if not os.getenv("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY not set")
    case, snap = load_case(path)
    expect = case["expect"]

    draft = draft_map(snap)
    result = validate(draft, snap)
    all_cited = {sid for c in result.claims for sid in c.source_ids}
    failures = []

    if not expect["min_modules"] <= len(draft.modules) <= expect["max_modules"]:
        failures.append(f"module count {len(draft.modules)} not in "
                        f"[{expect['min_modules']}, {expect['max_modules']}]")
    failures += [f"invalid claim {c.id}: {c.problems} | {c.text}" for c in result.claims if not c.valid]
    if result.invalid_key_files:
        failures.append(f"invented key files: {result.invalid_key_files}")
    failures += [f"must cite {sid}" for sid in expect["must_cite"] if sid not in all_cited]
    if expect["requires_no_reason"] and not any(NO_REASON in c.text for c in result.claims):
        failures.append(f"expected at least one 「{NO_REASON}」")
    failures += [f"purpose not in Chinese: {m.id}: {m.purpose}" for m in draft.modules if not CJK.search(m.purpose)]
    texts = [c.text for c in result.claims]
    failures += [f"half-width comma in Chinese text: {t}" for t in texts if HALF_WIDTH_COMMA.search(t)]
    failures += [f"invented reason containing 「{w}」: {t}" for w in expect["must_not_contain"] for t in texts if w in t]

    assert not failures, "\n".join(failures)

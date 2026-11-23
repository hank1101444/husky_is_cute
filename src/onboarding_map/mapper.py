"""Turn a RepoSnapshot into an onboarding map with Claude, and validate every claim in code."""

from __future__ import annotations

from onboarding_map.models import NO_REASON, Claim, OnboardingMapDraft, RepoSnapshot, ValidationResult


def _check_sources(source_ids: list[str], known: set[str]) -> list[str]:
    return [f"來源 {sid} 不存在於 repo 資料中" for sid in source_ids if sid not in known]


def _check_reason(reason: str, source_ids: list[str], known: set[str]) -> list[str]:
    if reason.strip() == NO_REASON:
        return ["標示「無紀錄的理由」時不應附上來源"] if source_ids else []
    if not source_ids:
        return ["理由沒有附上來源"]
    return _check_sources(source_ids, known)


def _claim(claim_id: str, kind, module_id: str | None, text: str, source_ids: list[str],
           problems: list[str]) -> Claim:
    return Claim(id=claim_id, kind=kind, module_id=module_id, text=text, source_ids=source_ids,
                 valid=not problems, problems=problems, ai_text=text)


def validate(draft: OnboardingMapDraft, snapshot: RepoSnapshot) -> ValidationResult:
    known = snapshot.source_ids()
    tree = set(snapshot.tree)
    names = {m.id: m.name for m in draft.modules}
    claims: list[Claim] = []
    invalid_key_files: dict[str, list[str]] = {}

    for m in draft.modules:
        problems = ["用途沒有附上來源"] if not m.purpose_source_ids else _check_sources(m.purpose_source_ids, known)
        claims.append(_claim(f"m:{m.id}:purpose", "purpose", m.id, m.purpose, m.purpose_source_ids, problems))

        bad_files = [f for f in m.key_files if f not in tree]
        if bad_files:
            invalid_key_files[m.id] = bad_files

        for rel in m.relations:
            problems = _check_reason(rel.reason, rel.source_ids, known)
            if rel.target_module_id not in names or rel.target_module_id == m.id:
                problems.insert(0, f"關聯的模組 {rel.target_module_id} 不存在")
            target_name = names.get(rel.target_module_id, rel.target_module_id)
            claims.append(_claim(f"m:{m.id}:rel:{rel.target_module_id}", "relation", m.id,
                                 f"{m.name} ↔ {target_name}：{rel.reason}", rel.source_ids, problems))

    for i, item in enumerate(draft.reading_order):
        problems = _check_reason(item.reason, item.source_ids, known)
        claims.append(_claim(f"r:{i}", "reading", None, f"{item.target}：{item.reason}", item.source_ids, problems))

    return ValidationResult(claims=claims, invalid_key_files=invalid_key_files)

"""Pydantic models shared by every module (the contract between fetcher, mapper, store and UI)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

NO_REASON = "無紀錄的理由"
"""Exact text the AI must use when no source explains a reason."""

SourceType = Literal["readme", "file", "pr", "pr_comment", "issue", "commit", "decision"]


class SourceItem(BaseModel):
    """One piece of repository evidence the AI may cite.

    ID scheme: ``README``, ``file:<path>``, ``PR#<n>``, ``PR#<n>/comment:<id>``,
    ``ISSUE#<n>``, ``commit:<sha7>``, ``DECISION:<heading>``.
    """

    id: str
    type: SourceType
    title: str
    url: str
    text: str


class RepoSnapshot(BaseModel):
    owner: str
    repo: str
    url: str
    default_branch: str
    tree: list[str] = Field(default_factory=list)
    sources: list[SourceItem] = Field(default_factory=list)
    truncation: dict[str, str] = Field(default_factory=dict)

    def source_ids(self) -> set[str]:
        return {f"file:{p}" for p in self.tree} | {s.id for s in self.sources}

    def source(self, source_id: str) -> SourceItem | None:
        return next((s for s in self.sources if s.id == source_id), None)


# --- LLM output (kept free of length/regex constraints for structured outputs) ---


class DraftRelation(BaseModel):
    target_module_id: str
    reason: str
    source_ids: list[str]


class DraftModule(BaseModel):
    id: str
    name: str
    purpose: str
    purpose_source_ids: list[str]
    key_files: list[str]
    relations: list[DraftRelation]


class DraftReadingItem(BaseModel):
    target: str
    reason: str
    source_ids: list[str]


class OnboardingMapDraft(BaseModel):
    modules: list[DraftModule]
    reading_order: list[DraftReadingItem]


# --- Validated / stored data ---

ClaimKind = Literal["purpose", "relation", "reading"]
ClaimStatus = Literal["inferred", "verified", "flagged"]


class Claim(BaseModel):
    """One checkable statement. IDs: ``m:<module>:purpose``, ``m:<module>:rel:<target>``, ``r:<index>``."""

    id: str
    kind: ClaimKind
    module_id: str | None
    text: str
    source_ids: list[str]
    valid: bool
    problems: list[str] = Field(default_factory=list)
    status: ClaimStatus = "inferred"
    ai_text: str | None = None


class ValidationResult(BaseModel):
    claims: list[Claim]
    invalid_key_files: dict[str, list[str]] = Field(default_factory=dict)


class Question(BaseModel):
    id: int
    map_id: int
    module_id: str
    text: str
    asked_at: str
    answer: str | None = None
    answered_at: str | None = None


class ReviewStats(BaseModel):
    total: int
    accepted_without_edit: int
    edited: int
    flagged: int
    review_minutes: float | None
    questions: int

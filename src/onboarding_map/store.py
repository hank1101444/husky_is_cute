"""SQLite persistence for maps, claim reviews, questions and evaluation stats."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Literal

from onboarding_map.models import (
    Claim,
    OnboardingMapDraft,
    Question,
    RepoSnapshot,
    ReviewStats,
    ValidationResult,
)

ReviewAction = Literal["confirm", "edit", "flag"]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS maps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_url TEXT NOT NULL,
    created_at TEXT NOT NULL,
    snapshot_json TEXT NOT NULL,
    draft_json TEXT NOT NULL,
    invalid_key_files_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS claims (
    map_id INTEGER NOT NULL REFERENCES maps(id),
    claim_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    module_id TEXT,
    ai_text TEXT NOT NULL,
    text TEXT NOT NULL,
    source_ids_json TEXT NOT NULL,
    valid INTEGER NOT NULL,
    problems_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'inferred',
    PRIMARY KEY (map_id, claim_id)
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    map_id INTEGER NOT NULL,
    claim_id TEXT NOT NULL,
    action TEXT NOT NULL,
    at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    map_id INTEGER NOT NULL,
    module_id TEXT NOT NULL,
    text TEXT NOT NULL,
    asked_at TEXT NOT NULL,
    answer TEXT,
    answered_at TEXT
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class LoadedMap:
    map_id: int
    repo_url: str
    created_at: str
    snapshot: RepoSnapshot
    draft: OnboardingMapDraft
    invalid_key_files: dict[str, list[str]]
    claims: list[Claim]


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as conn:
            conn.executescript(_SCHEMA)

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        # A new connection per call: Streamlit reruns the script on different threads.
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def save_map(self, snapshot: RepoSnapshot, draft: OnboardingMapDraft, result: ValidationResult) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO maps (repo_url, created_at, snapshot_json, draft_json, invalid_key_files_json)"
                " VALUES (?, ?, ?, ?, ?)",
                (snapshot.url, _now(), snapshot.model_dump_json(), draft.model_dump_json(),
                 json.dumps(result.invalid_key_files, ensure_ascii=False)),
            )
            map_id = cur.lastrowid
            conn.executemany(
                "INSERT INTO claims (map_id, claim_id, kind, module_id, ai_text, text, source_ids_json, valid,"
                " problems_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [(map_id, c.id, c.kind, c.module_id, c.ai_text or c.text, c.text,
                  json.dumps(c.source_ids, ensure_ascii=False), int(c.valid),
                  json.dumps(c.problems, ensure_ascii=False)) for c in result.claims],
            )
        return map_id

    def list_maps(self) -> list[tuple[int, str, str]]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, repo_url, created_at FROM maps ORDER BY id DESC").fetchall()
        return [(r["id"], r["repo_url"], r["created_at"]) for r in rows]

    def load_map(self, map_id: int) -> LoadedMap:
        with self._conn() as conn:
            m = conn.execute("SELECT * FROM maps WHERE id = ?", (map_id,)).fetchone()
            if m is None:
                raise KeyError(map_id)
            rows = conn.execute("SELECT * FROM claims WHERE map_id = ? ORDER BY rowid", (map_id,)).fetchall()
        claims = [
            Claim(id=r["claim_id"], kind=r["kind"], module_id=r["module_id"], text=r["text"],
                  source_ids=json.loads(r["source_ids_json"]), valid=bool(r["valid"]),
                  problems=json.loads(r["problems_json"]), status=r["status"], ai_text=r["ai_text"])
            for r in rows
        ]
        return LoadedMap(
            map_id=m["id"], repo_url=m["repo_url"], created_at=m["created_at"],
            snapshot=RepoSnapshot.model_validate_json(m["snapshot_json"]),
            draft=OnboardingMapDraft.model_validate_json(m["draft_json"]),
            invalid_key_files=json.loads(m["invalid_key_files_json"]),
            claims=claims,
        )

    def review_claim(self, map_id: int, claim_id: str, action: ReviewAction, new_text: str | None = None) -> None:
        if action == "edit" and not (new_text and new_text.strip()):
            raise ValueError("修改內容不能是空的")
        status = "flagged" if action == "flag" else "verified"
        with self._conn() as conn:
            if action == "edit":
                cur = conn.execute("UPDATE claims SET status = ?, text = ? WHERE map_id = ? AND claim_id = ?",
                                   (status, new_text.strip(), map_id, claim_id))
            else:
                cur = conn.execute("UPDATE claims SET status = ? WHERE map_id = ? AND claim_id = ?",
                                   (status, map_id, claim_id))
            if cur.rowcount == 0:
                raise KeyError(claim_id)
            conn.execute("INSERT INTO events (map_id, claim_id, action, at) VALUES (?, ?, ?, ?)",
                         (map_id, claim_id, action, _now()))

    def ask(self, map_id: int, module_id: str, text: str) -> int:
        if not text.strip():
            raise ValueError("問題不能是空的")
        with self._conn() as conn:
            cur = conn.execute("INSERT INTO questions (map_id, module_id, text, asked_at) VALUES (?, ?, ?, ?)",
                               (map_id, module_id, text.strip(), _now()))
        return cur.lastrowid

    def answer(self, question_id: int, text: str) -> None:
        if not text.strip():
            raise ValueError("回答不能是空的")
        with self._conn() as conn:
            conn.execute("UPDATE questions SET answer = ?, answered_at = ? WHERE id = ?",
                         (text.strip(), _now(), question_id))

    def questions(self, map_id: int, module_id: str | None = None) -> list[Question]:
        sql, params = "SELECT * FROM questions WHERE map_id = ?", [map_id]
        if module_id is not None:
            sql += " AND module_id = ?"
            params.append(module_id)
        with self._conn() as conn:
            rows = conn.execute(sql + " ORDER BY id", params).fetchall()
        return [Question(**dict(r)) for r in rows]

    def stats(self, map_id: int) -> ReviewStats:
        with self._conn() as conn:
            claims = conn.execute("SELECT claim_id, status FROM claims WHERE map_id = ?", (map_id,)).fetchall()
            events = conn.execute("SELECT claim_id, action, at FROM events WHERE map_id = ? ORDER BY id",
                                  (map_id,)).fetchall()
            n_questions = conn.execute("SELECT COUNT(*) FROM questions WHERE map_id = ?", (map_id,)).fetchone()[0]
        edited_ids = {e["claim_id"] for e in events if e["action"] == "edit"}
        minutes = None
        if events:
            first, last = (datetime.fromisoformat(events[i]["at"]) for i in (0, -1))
            minutes = (last - first).total_seconds() / 60
        return ReviewStats(
            total=len(claims),
            accepted_without_edit=sum(1 for c in claims if c["status"] == "verified" and c["claim_id"] not in edited_ids),
            edited=len(edited_ids),
            flagged=sum(1 for c in claims if c["status"] == "flagged"),
            review_minutes=minutes,
            questions=n_questions,
        )

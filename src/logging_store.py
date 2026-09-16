"""Decision log (FR-11, A8, B-10): every automated decision, reconstructable months later.

One row per stage per ticket (classification, routing, generation, validation) with the Governance
Framework section 1 minimum record. Append-only: this module has no update or delete path.
SQLite in WAL mode with synchronous=FULL, one commit per row, so a crash loses at most the row
being written and never a committed decision. reconcile() is the A8 check: every processed
ticket must have a routing and a validation row.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

REQUIRED_FIELDS = [
    "ticket_id", "stage", "input_summary", "model_name", "model_version", "prediction_value",
    "prediction_confidence", "alternatives", "sources_used", "threshold_applied", "action_taken", "reason",
    "guardrail_results", "prompt_version", "requirement_ids", "latency_ms", "error",
]
STAGES = ("classification", "routing", "generation", "validation")
_JSON_FIELDS = ("alternatives", "sources_used", "guardrail_results", "requirement_ids")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS decisions (
    decision_id           TEXT PRIMARY KEY,
    timestamp             TEXT NOT NULL,
    run_id                TEXT,
    ticket_id             TEXT NOT NULL,
    stage                 TEXT NOT NULL,
    input_summary         TEXT,
    model_name            TEXT,
    model_version         TEXT,
    prediction_value      TEXT,
    prediction_confidence REAL,
    alternatives          TEXT,
    sources_used          TEXT,
    threshold_applied     REAL,
    action_taken          TEXT NOT NULL,
    reason                TEXT NOT NULL,
    guardrail_results     TEXT,
    prompt_version        TEXT,
    requirement_ids       TEXT,
    latency_ms            REAL,
    error                 TEXT
);
CREATE INDEX IF NOT EXISTS ix_decisions_ticket ON decisions (ticket_id, stage);
"""


class DecisionLog:
    def __init__(self, path: str | Path, run_id: Optional[str] = None):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id or datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ")
        self._con = sqlite3.connect(self.path, isolation_level=None)  # autocommit; explicit BEGIN per row
        self._con.execute("PRAGMA journal_mode=WAL")
        self._con.execute("PRAGMA synchronous=FULL")
        self._con.executescript(_SCHEMA)

    # ---- write -------------------------------------------------------------------------------
    def record(self, ticket_id: str, stage: str, action_taken: str, reason: str, input_summary: str = "",
               model_name: Optional[str] = None, model_version: Optional[str] = None,
               prediction_value: Optional[str] = None, prediction_confidence: Optional[float] = None,
               alternatives: Optional[List[Dict[str, Any]]] = None, sources_used: Optional[List[Dict[str, Any]]] = None,
               threshold_applied: Optional[float] = None, guardrail_results: Optional[Dict[str, Any]] = None,
               prompt_version: Optional[str] = None, requirement_ids: Optional[List[str]] = None,
               latency_ms: Optional[float] = None, error: Optional[str] = None) -> str:
        if stage not in STAGES:
            raise ValueError(f"unknown stage {stage!r}")
        decision_id = uuid.uuid4().hex
        row = (
            decision_id, datetime.now(timezone.utc).isoformat(), self.run_id, ticket_id, stage,
            (input_summary or "")[:300], model_name, model_version, prediction_value, prediction_confidence,
            json.dumps(alternatives or [], ensure_ascii=False), json.dumps(sources_used or [], ensure_ascii=False),
            threshold_applied, action_taken, reason, json.dumps(guardrail_results or {}, ensure_ascii=False),
            prompt_version, json.dumps(requirement_ids or []), latency_ms, error,
        )
        self._con.execute("BEGIN")
        self._con.execute("INSERT INTO decisions VALUES (" + ",".join("?" * len(row)) + ")", row)
        self._con.execute("COMMIT")
        return decision_id

    # ---- read --------------------------------------------------------------------------------
    @staticmethod
    def _decode(cursor, row) -> Dict[str, Any]:
        d = {col[0]: val for col, val in zip(cursor.description, row)}
        for f in _JSON_FIELDS:
            try:
                d[f] = json.loads(d[f]) if d.get(f) else ([] if f != "guardrail_results" else {})
            except (TypeError, ValueError):
                pass
        return d

    def rows_for(self, ticket_id: str) -> List[Dict[str, Any]]:
        cur = self._con.execute("SELECT * FROM decisions WHERE ticket_id = ? ORDER BY timestamp", (ticket_id,))
        return [self._decode(cur, r) for r in cur.fetchall()]

    def count(self, run_id: Optional[str] = None) -> int:
        if run_id:
            return self._con.execute("SELECT COUNT(*) FROM decisions WHERE run_id = ?", (run_id,)).fetchone()[0]
        return self._con.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]

    def reconcile(self, ticket_ids: Iterable[str], run_id: Optional[str] = None) -> Dict[str, Any]:
        """A8: decisions counted against tickets processed must reconcile exactly."""
        ids = list(ticket_ids)
        q = "SELECT ticket_id, stage, COUNT(*) FROM decisions" + (" WHERE run_id = ?" if run_id else "") + " GROUP BY ticket_id, stage"
        cur = self._con.execute(q, (run_id,) if run_id else ())
        have: Dict[str, Dict[str, int]] = {}
        for tid, stage, n in cur.fetchall():
            have.setdefault(tid, {})[stage] = n
        rows_by_stage = {s: sum(v.get(s, 0) for v in have.values()) for s in STAGES}
        missing_routing = [t for t in ids if "routing" not in have.get(t, {})]
        missing_validation = [t for t in ids if "validation" not in have.get(t, {})]
        return {
            "tickets": len(ids),
            "tickets_with_rows": sum(1 for t in ids if t in have),
            "tickets_with_routing": len(ids) - len(missing_routing),
            "tickets_with_validation": len(ids) - len(missing_validation),
            "rows_by_stage": rows_by_stage,
            "rows_total": sum(rows_by_stage.values()),
            "missing_routing": missing_routing,
            "missing_validation": missing_validation,
            "complete": not missing_routing and not missing_validation,
        }

    def export_jsonl(self, path: str | Path, run_id: Optional[str] = None) -> int:
        q = "SELECT * FROM decisions" + (" WHERE run_id = ?" if run_id else "") + " ORDER BY timestamp"
        cur = self._con.execute(q, (run_id,) if run_id else ())
        n = 0
        with open(path, "w", encoding="utf-8") as fh:
            for r in cur.fetchall():
                fh.write(json.dumps(self._decode(cur, r), ensure_ascii=False) + "\n")
                n += 1
        return n

    def close(self) -> None:
        self._con.close()

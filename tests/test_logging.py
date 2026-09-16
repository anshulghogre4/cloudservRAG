"""B-10 / FR-11, A8: the decision log.

T-18  test_reconciles   rows per stage reconcile exactly with tickets processed; a missing stage is reported
plus  every Governance section 1 field is a column; the store is append-only (no update/delete API);
      values are JSON-serialised and read back; the key never appears.
"""
import json
import sqlite3

import pytest

from src.logging_store import DecisionLog, REQUIRED_FIELDS


@pytest.fixture
def log(tmp_path):
    return DecisionLog(tmp_path / "decisions.db", run_id="run-test")


def _row(ticket_id, stage, action="proceed", **kw):
    base = dict(ticket_id=ticket_id, stage=stage, input_summary="subject: x body: y", model_name="fake-model",
                model_version="v0", prediction_value="rate_limit", prediction_confidence=0.9,
                alternatives=[{"intent": "quota_or_overage", "confidence": 0.1}],
                sources_used=[{"doc_id": "DOC-API-001", "score": 0.7}], threshold_applied=0.8,
                action_taken=action, reason="because", guardrail_results={"pii": "pass"},
                prompt_version="PR-02 v1.0", requirement_ids=["FR-02"], latency_ms=12.5, error=None)
    base.update(kw)
    return base


def test_schema_has_every_required_field(log):
    cols = {r[1] for r in sqlite3.connect(log.path).execute("PRAGMA table_info(decisions)")}
    missing = [f for f in REQUIRED_FIELDS if f not in cols]
    assert not missing, missing
    assert {"decision_id", "timestamp", "run_id"} <= cols


def test_record_and_read_back(log):
    did = log.record(**_row("T1", "classification"))
    assert did and len(did) >= 8
    rows = log.rows_for("T1")
    assert len(rows) == 1
    r = rows[0]
    assert r["stage"] == "classification" and r["alternatives"][0]["intent"] == "quota_or_overage"
    assert r["sources_used"][0]["doc_id"] == "DOC-API-001" and r["requirement_ids"] == ["FR-02"]
    assert r["guardrail_results"] == {"pii": "pass"} and r["run_id"] == "run-test"


def test_append_only_api(log):
    assert not any(name.startswith(("update", "delete", "remove", "clear")) for name in dir(log))


def test_reconciles(log):
    for t in ("T1", "T2", "T3"):
        log.record(**_row(t, "classification"))
        log.record(**_row(t, "routing", action="auto_respond"))
        log.record(**_row(t, "validation", action="auto_respond"))
    log.record(**_row("T4", "classification"))               # T4 crashed before routing
    rec = log.reconcile(["T1", "T2", "T3", "T4"])
    assert rec["tickets"] == 4 and rec["tickets_with_routing"] == 3 and rec["tickets_with_validation"] == 3
    assert rec["missing_routing"] == ["T4"] and rec["complete"] is False
    assert rec["rows_by_stage"]["classification"] == 4
    log.record(**_row("T4", "routing", action="escalate"))
    log.record(**_row("T4", "validation", action="escalate"))
    assert log.reconcile(["T1", "T2", "T3", "T4"])["complete"] is True


def test_count_and_export(log, tmp_path):
    log.record(**_row("T1", "classification"))
    log.record(**_row("T1", "routing", action="escalate"))
    assert log.count() == 2
    out = tmp_path / "export.jsonl"
    n = log.export_jsonl(out)
    assert n == 2 and len(out.read_text(encoding="utf-8").splitlines()) == 2


def test_durability_pragmas(log):
    con = sqlite3.connect(log.path)
    assert con.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"


def test_rows_written_from_worker_threads_reconcile(tmp_path):
    """The API handles requests on a thread pool (B-16); the log must accept rows from any thread."""
    import threading
    log = DecisionLog(tmp_path / "t.db", run_id="threads")

    def work(i):
        for stage in ("classification", "routing", "generation", "validation"):
            log.record(ticket_id=f"T-{i}", stage=stage, action_taken="escalate", reason="r",
                       input_summary="s", model_name="m")

    threads = [threading.Thread(target=work, args=(i,)) for i in range(8)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    rec = log.reconcile([f"T-{i}" for i in range(8)], run_id="threads")
    assert rec["complete"] and rec["rows_total"] == 32
    assert len(log.rows_for("T-3")) == 4


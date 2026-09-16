"""B-05 / FR-13, A9, A10: the evaluation harness.

T-20  test_input_output_paths     any input file path, any output dir; one JSONL row per ticket; metrics.json with the four groups
T-25  test_urgency_flag           every record carries the predicted urgency (FR-16)
plus  failure isolation (a ticket that raises is still recorded as an escalation), resume, CLI entry point,
      metric shapes (per-class report, hit rate, routing accuracy, governance counts, calibration bins, Wilson CI).
"""
import json
from pathlib import Path

import pytest

from src.ingest import Ticket
from src.models import TicketResult
from evaluation import harness
from evaluation.metrics_report import compute_metrics, wilson_interval


class OracleStub:
    """Deterministic pipeline that follows the labels: auto-respond when expected, cite the expected docs.
    It stands in for classify/retrieve/generate so the harness can be tested end to end offline."""

    def __init__(self, fail_on=()):
        self.fail_on = set(fail_on)

    def process(self, ticket: Ticket) -> TicketResult:
        if ticket.ticket_id in self.fail_on:
            raise RuntimeError("simulated component crash")
        labels = ticket.raw.get("labels", {})
        intent = labels.get("intent", "unclear_request")
        auto = labels.get("expected_route") == "auto_respond" and not labels.get("must_not_auto_respond", False)
        docs = list(labels.get("expected_doc_ids", []))
        return TicketResult(
            ticket_id=ticket.ticket_id, channel=ticket.channel, tier=ticket.customer.tier,
            region=ticket.customer.region, fluency=ticket.customer.fluency, text_len=len(ticket.text),
            intent=intent, urgency=labels.get("urgency", "medium"), confidence=0.9 if auto else 0.3,
            raw_confidence=0.9 if auto else 0.3, alternatives=[], instruction_like=False,
            retrieved=[{"doc_id": d, "section": "Resolution", "score": 0.7} for d in docs],
            action="auto_respond" if auto else "escalate",
            route_reason="oracle stub", answer="Thanks. [%s]" % ",".join(docs) if auto else None,
            citations=docs if auto else [], escalation=None if auto else {"summary": "s", "uncertainty": "u"},
            guardrails={"pii": "pass", "grounding": "pass", "tone": "pass", "injection": "pass"},
            latency_ms=12.0, error=None, stage_reached="validation",
            labels=labels or None, history=ticket.raw.get("history"),
            prompt_versions={"PR-02": "1.0", "PR-03": "1.0"},
        )


@pytest.fixture
def input_file(tmp_path, sample_tickets, documentation):
    # sample tickets have full labels; add two more crafted from real ids so metrics have a spread
    p = tmp_path / "some_random_name.json"
    p.write_text(json.dumps(sample_tickets), encoding="utf-8")
    return p


def test_input_output_paths(input_file, tmp_path, sample_tickets):
    out = tmp_path / "out_dir_that_does_not_exist_yet"
    metrics = harness.run(input_path=input_file, output_dir=out, pipeline=OracleStub())
    rows = [json.loads(l) for l in (out / "results.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [r["ticket_id"] for r in rows] == [t["ticket_id"] for t in sample_tickets]
    m = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    for group in ("volume", "business", "technical", "governance"):
        assert group in m, group
    assert m["volume"]["processed"] == len(sample_tickets)
    assert m["volume"]["processed"] == m["volume"]["auto_responded"] + m["volume"]["escalated"] + m["volume"]["blocked"]
    meta = json.loads((out / "run_meta.json").read_text(encoding="utf-8"))
    assert meta["input"].endswith("some_random_name.json") and meta["tickets"] == len(sample_tickets)
    assert (out / "run_summary.md").exists()
    assert metrics == m


def test_urgency_flag(input_file, tmp_path):
    out = tmp_path / "o"
    harness.run(input_path=input_file, output_dir=out, pipeline=OracleStub())
    for line in (out / "results.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        assert r["urgency"] in ("high", "medium", "low")


def test_failing_ticket_is_recorded_not_dropped(input_file, tmp_path, sample_tickets):
    victim = sample_tickets[1]["ticket_id"]
    out = tmp_path / "o"
    m = harness.run(input_path=input_file, output_dir=out, pipeline=OracleStub(fail_on=[victim]))
    rows = {json.loads(l)["ticket_id"]: json.loads(l) for l in (out / "results.jsonl").read_text(encoding="utf-8").splitlines()}
    assert len(rows) == len(sample_tickets)                 # nothing silently dropped (A9)
    r = rows[victim]
    assert r["action"] == "escalate" and r["error"] and "crash" in r["error"]
    assert m["governance"]["failed_tickets"] == 1
    assert m["volume"]["processed"] == len(sample_tickets)


def test_resume_skips_completed_rows(input_file, tmp_path):
    out = tmp_path / "o"
    harness.run(input_path=input_file, output_dir=out, pipeline=OracleStub())
    first = (out / "results.jsonl").read_text(encoding="utf-8")
    harness.run(input_path=input_file, output_dir=out, pipeline=OracleStub(), resume=True)
    second = (out / "results.jsonl").read_text(encoding="utf-8")
    assert first == second                                  # no duplicates
    m = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    assert m["volume"]["processed"] == len(first.splitlines())


def test_limit(input_file, tmp_path):
    out = tmp_path / "o"
    m = harness.run(input_path=input_file, output_dir=out, pipeline=OracleStub(), limit=2)
    assert m["volume"]["processed"] == 2


def test_cli_entry_point(input_file, tmp_path, monkeypatch):
    monkeypatch.setattr(harness, "build_pipeline", lambda settings: OracleStub())
    out = tmp_path / "cli_out"
    rc = harness.main(["--input", str(input_file), "--output", str(out)])
    assert rc == 0 and (out / "metrics.json").exists()


def test_metric_shapes(input_file, tmp_path):
    out = tmp_path / "o"
    m = harness.run(input_path=input_file, output_dir=out, pipeline=OracleStub())
    b, t, g = m["business"], m["technical"], m["governance"]
    assert set(b) >= {"first_contact_resolution", "escalation_rate", "response_time_ms_mean", "response_time_ms_median"}
    assert "ci95" in b["first_contact_resolution"]        # Wilson interval on a small sample
    assert t["classification"]["per_class"] and "macro_precision" in t["classification"]
    assert 0.0 <= t["retrieval_hit_rate"] <= 1.0
    assert "routing_accuracy" in t and "latency_ms_p95" in t
    assert g["must_not_auto_respond_violations"] == 0      # the oracle never auto-answers those
    assert g["decisions_logged"] == m["volume"]["processed"]
    assert isinstance(g["calibration"]["bins"], list)
    assert "segments" in m and "tier" in m["segments"]


def test_wilson_interval_bounds():
    lo, hi = wilson_interval(42, 100)
    assert 0.32 < lo < 0.42 < hi < 0.53
    assert wilson_interval(0, 0) == (0.0, 0.0)


def test_compute_metrics_handles_unlabelled_records():
    recs = [{"ticket_id": "X", "channel": "email", "tier": "standard", "region": "europe", "fluency": "fluent",
             "text_len": 10, "intent": "rate_limit", "urgency": "low", "confidence": 0.8, "retrieved": [],
             "action": "escalate", "citations": [], "guardrails": {}, "latency_ms": 5.0, "error": None,
             "labels": None, "history": None}]
    m = compute_metrics(recs)
    assert m["volume"]["processed"] == 1
    assert m["technical"]["classification"]["labelled"] == 0   # no labels -> no precision claimed


class LoggingStub(OracleStub):
    """OracleStub that also writes the decision-log rows the real pipeline writes, so reconciliation is testable."""

    def __init__(self, db_path, fail_on=()):
        super().__init__(fail_on)
        from src.logging_store import DecisionLog
        self.log = DecisionLog(db_path, run_id="stub-run")

    def process(self, ticket):
        r = super().process(ticket)
        for stage in ("classification", "routing", "generation", "validation"):
            self.log.record(ticket_id=ticket.ticket_id, stage=stage, action_taken=r.action, reason="stub",
                            input_summary=ticket.text[:50], model_name="stub")
        return r


def test_log_reconciles_including_harness_level_failures(input_file, tmp_path, sample_tickets):
    victim = sample_tickets[1]["ticket_id"]
    out = tmp_path / "o"
    m = harness.run(input_path=input_file, output_dir=out, pipeline=LoggingStub(tmp_path / "d.db", fail_on=[victim]))
    rec = m["governance"]["decision_log"]
    assert rec["complete"] and rec["tickets"] == len(sample_tickets) and rec["missing_validation"] == []
    assert m["governance"]["decisions_logged"] == rec["rows_total"]
    assert "reconcil" in (out / "run_summary.md").read_text(encoding="utf-8").lower()


def test_calibration_small_bins_are_reported_not_judged():
    from evaluation.metrics_report import calibration_table
    pairs = [(0.99, True)] * 100 + [(0.70, True), (0.70, True)]      # two tickets in the 0.6-0.8 band
    t = calibration_table(pairs)
    assert t["all_bins_within_5_points"] is True                     # judged on bins with n >= min_n only
    small = [b for b in t["bins"] if b["n"] == 2][0]
    assert small["evaluable"] is False and t["min_n"] == 20

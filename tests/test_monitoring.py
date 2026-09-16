"""B-12: Prometheus metrics. observe() counts outcomes, latency, guardrail blocks, confidence and
failures; the API serves /metrics; the harness leaves a metrics.prom snapshot after a run."""
import json

from fastapi.testclient import TestClient

from evaluation import harness
from src import monitoring
from src.api import create_app
from src.config import Settings
from src.ingest import normalise_ticket
from tests.test_harness import OracleStub


def test_observe_counts_every_view(sample_tickets):
    raw = sample_tickets[1]                                       # DEV-0001, chat, auto-respond by label
    r = OracleStub().process(normalise_ticket(raw))
    key = {"channel": r.channel, "outcome": r.action}
    before_t = monitoring.sample("tickets_processed_total", key)
    before_l = monitoring.sample("response_seconds_count")
    before_c = monitoring.sample("classification_confidence_count")
    monitoring.observe(r)
    assert monitoring.sample("tickets_processed_total", key) == before_t + 1
    assert monitoring.sample("response_seconds_count") == before_l + 1
    assert monitoring.sample("classification_confidence_count") == before_c + 1

    r.guardrails = {**r.guardrails, "grounding": "block"}
    r.error = "generation failed: provider unavailable: timeout"
    before_g = monitoring.sample("guardrail_blocks_total", {"guardrail": "grounding"})
    before_f = monitoring.sample("pipeline_failures_total", {"stage": "generation"})
    monitoring.observe(r)
    assert monitoring.sample("guardrail_blocks_total", {"guardrail": "grounding"}) == before_g + 1
    assert monitoring.sample("pipeline_failures_total", {"stage": "generation"}) == before_f + 1


def test_observe_never_raises():
    monitoring.observe(object())                                  # nothing usable on it


def test_api_serves_metrics(tmp_path, sample_tickets):
    s = Settings(database_url=f"sqlite:///{(tmp_path / 'd.db').as_posix()}")
    c = TestClient(create_app(pipeline=OracleStub(), settings=s))
    assert c.post("/tickets", json=sample_tickets[0]).status_code == 200
    r = c.get("/metrics")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/plain")
    body = r.text
    for name in ("tickets_processed_total", "response_seconds", "guardrail_blocks_total", "classification_confidence"):
        assert name in body


def test_harness_writes_metrics_snapshot(tmp_path, sample_tickets):
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps(sample_tickets), encoding="utf-8")
    out = tmp_path / "out"
    harness.run(input_path=inp, output_dir=out, pipeline=OracleStub())
    snap = (out / "metrics.prom").read_text(encoding="utf-8")
    assert "tickets_processed_total" in snap and "response_seconds_bucket" in snap

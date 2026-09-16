"""Monitoring (B-12): Prometheus metrics for the five views the Setup Guide asks a dashboard to show
(section 06): tickets per hour by channel and outcome, auto-answered against escalated, latency at
the median and 95th percentile, guardrail activations by guardrail, and the distribution of
confidence scores (where drift shows first). One extra counter records pipeline failures by stage.

`observe()` is called once per ticket from `safe_process()`, so the harness and the API feed the
same metrics. The API serves them at GET /metrics and, via `python -m src.api`, on METRICS_PORT
for Prometheus to scrape (monitoring/prometheus.yml). The harness writes a snapshot to
metrics.prom at the end of a run, so a batch run leaves the same evidence as a live process.
"""
from __future__ import annotations

from typing import Dict, Optional

from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, Counter, Histogram, generate_latest

TICKETS = Counter("tickets_processed_total", "Tickets processed", ["channel", "outcome"])
LATENCY = Histogram("response_seconds", "End-to-end response time per ticket, seconds",
                    buckets=(0.25, 0.5, 1, 2, 3, 5, 10, 20, 30, 60))
GUARDRAIL = Counter("guardrail_blocks_total", "Responses blocked, by guardrail", ["guardrail"])
CONFIDENCE = Histogram("classification_confidence", "Calibrated classification confidence per ticket",
                       buckets=tuple(round(i / 10, 1) for i in range(1, 11)))
FAILURES = Counter("pipeline_failures_total", "Tickets whose processing recorded an error, by stage", ["stage"])

_STAGES = ("classification", "retrieval", "routing", "generation", "validation", "escalation")


def _failure_stage(error: str, stage_reached: Optional[str]) -> str:
    head = (error or "").split(":", 1)[0].lower()          # "classification failed: ..." -> classification
    for s in _STAGES:
        if head.startswith(s):
            return s
    return stage_reached or "pipeline"


def observe(result) -> None:
    """Record one TicketResult. Never raises: monitoring must not break processing."""
    try:
        TICKETS.labels(channel=result.channel or "unknown", outcome=result.action or "unknown").inc()
        LATENCY.observe(max(float(result.latency_ms or 0.0), 0.0) / 1000.0)
        CONFIDENCE.observe(min(max(float(result.confidence or 0.0), 0.0), 1.0))
        for name, verdict in (result.guardrails or {}).items():
            if verdict == "block":
                GUARDRAIL.labels(guardrail=name).inc()
        if result.error:
            FAILURES.labels(stage=_failure_stage(result.error, result.stage_reached)).inc()
    except Exception:  # noqa: BLE001
        pass


def export() -> bytes:
    """The Prometheus text exposition of every metric (what /metrics serves)."""
    return generate_latest(REGISTRY)


def sample(name: str, labels: Optional[Dict[str, str]] = None) -> float:
    """Current value of one sample, 0.0 when it has never been set (tests and reports)."""
    v = REGISTRY.get_sample_value(name, labels or {})
    return float(v) if v is not None else 0.0


CONTENT_TYPE = CONTENT_TYPE_LATEST

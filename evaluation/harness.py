"""Evaluation harness (FR-13, A9, A10): one command, any input path, unattended, never drops a ticket.

    python -m evaluation.harness --input <tickets.json> --output <dir> [--limit N] [--resume] [--sort-urgency]

Writes into <dir>:
    results.jsonl    one row per ticket, appended as each ticket finishes (crash-safe, resumable)
    metrics.json     the four metric groups + segments (Build Spec section 04)
    run_summary.md   human-readable summary
    metrics.prom     Prometheus text snapshot of the run's counters and histograms
    run_meta.json    input path, ticket count, timestamps, system version, thresholds, run count

Every ticket is wrapped: a component failure produces an escalation row with the error, and the
run continues (A11). Never points at a hard-coded file.
"""
from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional

from src.config import Settings, load_settings
from src.ingest import Ticket, load_tickets
from src.models import Pipeline
from src.monitoring import export as export_metrics
from src.pipeline import safe_process
from evaluation.metrics_report import compute_metrics, render_summary

log = logging.getLogger("harness")
URGENCY_ORDER = {"high": 0, "medium": 1, "low": 2}


def build_pipeline(settings: Settings) -> Pipeline:
    """Real pipeline; imported lazily so the harness (and its tests) never need the model."""
    from src.pipeline import SupportPipeline
    return SupportPipeline(settings)


def _version() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL,
            cwd=Path(__file__).resolve().parents[1]).decode().strip()
    except Exception:
        return "unknown"


def _done_ids(results_path: Path) -> set:
    if not results_path.exists():
        return set()
    ids = set()
    for line in results_path.read_text(encoding="utf-8").splitlines():
        try:
            ids.add(json.loads(line)["ticket_id"])
        except Exception:
            continue
    return ids


def _reconcile(pipeline, ticket_ids: List[str], resume: bool) -> Optional[dict]:
    """A8: logged decisions must reconcile with tickets processed. Scoped to this run id unless resuming
    (a resumed run has rows under earlier run ids)."""
    store = getattr(pipeline, "log", None)
    if store is None or not hasattr(store, "reconcile"):
        return None
    try:
        return store.reconcile(ticket_ids, run_id=None if resume else getattr(store, "run_id", None))
    except Exception:  # noqa: BLE001
        log.exception("reconciliation failed")
        return None


def run(input_path, output_dir, pipeline: Optional[Pipeline] = None, settings: Optional[Settings] = None,
        limit: Optional[int] = None, resume: bool = False, sort_urgency: bool = False,
        progress_every: int = 25) -> dict:
    settings = settings or load_settings()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    results_path = out / "results.jsonl"
    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()

    tickets: List[Ticket] = load_tickets(input_path)
    if limit is not None:
        tickets = tickets[:limit]
    done = _done_ids(results_path) if resume else set()
    if not resume and results_path.exists():
        results_path.unlink()
    todo = [t for t in tickets if t.ticket_id not in done]
    pipeline = pipeline or build_pipeline(settings)
    log.info("run: %d tickets (%d already done), input=%s", len(tickets), len(done), input_path)

    processed = 0
    with results_path.open("a", encoding="utf-8") as fh:
        for i, ticket in enumerate(todo, 1):
            t_start = time.perf_counter()
            result = safe_process(pipeline, ticket, settings)   # a failing component must not stop the run (A9, A11)
            fh.write(json.dumps(result.to_record(), ensure_ascii=False) + "\n")
            fh.flush()
            processed += 1
            if progress_every and i % progress_every == 0:
                log.info("progress %d/%d", i, len(todo))

    records = [json.loads(l) for l in results_path.read_text(encoding="utf-8").splitlines()]
    if sort_urgency:
        ordered = sorted(records, key=lambda r: URGENCY_ORDER.get(r.get("urgency"), 9))
        (out / "results_by_urgency.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in ordered), encoding="utf-8")
    metrics = compute_metrics(records)
    rec = _reconcile(pipeline, [t.ticket_id for t in tickets], resume)
    if rec is not None:
        metrics["governance"]["decision_log"] = rec
        metrics["governance"]["decisions_logged"] = rec["rows_total"]
        (log.info if rec["complete"] else log.error)("decision log reconciliation: %s (%d rows, %d tickets)",
                                                     "complete" if rec["complete"] else "INCOMPLETE", rec["rows_total"], rec["tickets"])

    meta_path = out / "run_meta.json"
    prior = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    meta = {
        "input": str(input_path), "output": str(out), "tickets": len(tickets), "processed_this_run": processed,
        "started_at": started.isoformat(), "finished_at": datetime.now(timezone.utc).isoformat(),
        "duration_s": time.perf_counter() - t0, "version": _version(), "model": settings.model_name,
        "confidence_threshold": settings.confidence_threshold, "retrieval_threshold": settings.retrieval_threshold,
        "kill_switch": settings.kill_switch,
        "run_count_on_this_input": prior.get("run_count_on_this_input", 0) + 1,
    }
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (out / "run_summary.md").write_text(render_summary(metrics, meta), encoding="utf-8")
    (out / "metrics.prom").write_bytes(export_metrics())          # Prometheus snapshot of the run (B-12)
    log.info("done: %d records, metrics at %s", len(records), out / "metrics.json")
    return metrics


def main(argv: Optional[Iterable[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Process a ticket file unattended and write a metrics report.")
    ap.add_argument("--input", required=True, help="path to a JSON list of tickets (any file with the schema)")
    ap.add_argument("--output", required=True, help="directory for results.jsonl, metrics.json, run_summary.md")
    ap.add_argument("--limit", type=int, default=None, help="process only the first N tickets (development use)")
    ap.add_argument("--resume", action="store_true", help="skip tickets already present in results.jsonl")
    ap.add_argument("--sort-urgency", action="store_true", help="also write results ordered by predicted urgency (FR-16)")
    ap.add_argument("--log-level", default=None)
    a = ap.parse_args(list(argv) if argv is not None else None)
    settings = load_settings()
    logging.basicConfig(level=a.log_level or settings.log_level,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    run(a.input, a.output, settings=settings, limit=a.limit, resume=a.resume, sort_urgency=a.sort_urgency)
    return 0


if __name__ == "__main__":
    sys.exit(main())

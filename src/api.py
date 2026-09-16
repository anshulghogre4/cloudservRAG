"""FastAPI application (FR-18, B-16): one ticket in, one decision out.

The graders submit one ticket per channel and a guardrail-trigger ticket by hand before the batch
run (Build Specification section 06, steps 5 to 7). The endpoint runs the same SupportPipeline as
the harness, so the two cannot drift apart, and returns the same record the harness writes.

    POST /tickets                 body: one ticket object (dataset schema; labels optional)
                                  200: the TicketResult record (action, intent, confidence, answer or
                                  escalation package, guardrail verdicts, citations, latency, error)
    GET  /decisions/{ticket_id}   the decision-log rows for that ticket (A8)
    GET  /health                  liveness, kill-switch state, model, version
    GET  /metrics                 Prometheus exposition (also served on METRICS_PORT by python -m src.api)

Malformed input never fails the request: normalise_ticket() accepts anything object-shaped, and a
component failure returns an escalation with the reason (A11). Only a body that is not a JSON
object is rejected (422). Run with `python -m src.api`; Prometheus metrics are served on
METRICS_PORT when the prometheus_client package is installed (B-12).
"""
from __future__ import annotations

import logging
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response

from src.config import Settings, load_settings
from src.ingest import normalise_ticket
from src.models import Pipeline
from src.monitoring import CONTENT_TYPE, export
from src.pipeline import SupportPipeline, safe_process

log = logging.getLogger("api")
ROOT = Path(__file__).resolve().parents[1]


def _version() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def create_app(pipeline: Optional[Pipeline] = None, settings: Optional[Settings] = None) -> FastAPI:
    """Build the app. A pipeline can be injected (tests); otherwise the production one is built at
    startup, once, because the embedder, the NLI model and the vector store take seconds to load."""
    settings = settings or load_settings()
    state: Dict[str, Any] = {"pipeline": pipeline, "version": _version()}

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if state["pipeline"] is None:
            log.info("building pipeline (model %s)", settings.model_name)
            state["pipeline"] = SupportPipeline(settings)
        yield

    app = FastAPI(title="CloudServe support pipeline", version=state["version"], lifespan=lifespan)

    def _pipeline() -> Pipeline:
        if state["pipeline"] is None:           # a request before startup finished (TestClient without context)
            state["pipeline"] = SupportPipeline(settings)
        return state["pipeline"]

    @app.post("/tickets")
    def submit_ticket(ticket: Dict[str, Any]):
        t = normalise_ticket(ticket)
        result = safe_process(_pipeline(), t, settings)
        return JSONResponse(result.to_record())

    @app.get("/decisions/{ticket_id}")
    def decisions(ticket_id: str):
        store = getattr(_pipeline(), "log", None)
        rows = store.rows_for(ticket_id) if store is not None and hasattr(store, "rows_for") else []
        return {"ticket_id": ticket_id, "decisions": rows}

    @app.get("/metrics")
    def metrics():
        return Response(export(), headers={"Content-Type": CONTENT_TYPE})

    @app.get("/health")
    def health():
        return {"status": "ok", "kill_switch": settings.kill_switch_active(), "model": settings.model_name,
                "pipeline_ready": state["pipeline"] is not None, "version": state["version"]}

    return app


def main() -> None:
    import uvicorn

    settings = load_settings()
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        from prometheus_client import start_http_server
        start_http_server(settings.metrics_port)
        log.info("metrics on http://localhost:%d/metrics", settings.metrics_port)
    except Exception as exc:  # noqa: BLE001 - metrics are optional, the API is not
        log.warning("metrics server not started: %s", exc)
    uvicorn.run(create_app(settings=settings), host=settings.api_host, port=settings.api_port, log_level="info")


if __name__ == "__main__":
    main()

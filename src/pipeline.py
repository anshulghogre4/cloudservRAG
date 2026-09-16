"""The pipeline: one ticket through ingest -> classify -> retrieve -> route -> generate -> validate (B-10).

Used by both the harness (batch) and the API (single ticket) so they cannot drift apart. Every
stage writes a decision-log row; the four rows per ticket reconcile in the harness (A8). Any
component failure turns into an escalation with the reason, never a crash (A11).

Components are injectable for tests; production ones are built lazily from Settings:
embedder (all-MiniLM-L6-v2), retriever (Chroma at CHROMA_PATH, built from documentation.json),
neighbour classifier (fitted on the labelled development tickets), calibrator
(evaluation/results/calibration.json), grounder (embedder + NLI cross-encoder), decision log (SQLite).
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.calibration import load_calibrator
from src.classify import KNNClassifier, classify, PROMPT_VERSION as PR02
from src.config import Settings
from src.escalation import build_escalation, PROMPT_VERSION as PR04
from src.generate import Draft, add_disclosure, generate, PROMPT_VERSION as PR03
from src.guardrails import Grounder, NLIScorer, run_guardrails
from src.ingest import Ticket, load_tickets
from src.llm import LLMClient
from src.logging_store import DecisionLog
from src.models import TicketResult, failure_result
from src.monitoring import observe
from src.retrieve import Passage, Retriever, SentenceTransformerEmbedder
from src.route import Route, route

log = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DOCS_PATH = ROOT / "Docs" / "Capstone_Project" / "05_Datasets" / "documentation.json"
MEMORY_PATH = ROOT / "Docs" / "Capstone_Project" / "05_Datasets" / "development_tickets.json"


def _summary(ticket: Ticket) -> str:
    """What the log records as input: the text, never the customer fields."""
    return (ticket.text or "")[:300]


class SupportPipeline:
    def __init__(self, settings: Settings, *, llm=None, embedder=None, retriever: Optional[Retriever] = None,
                 knn: Optional[KNNClassifier] = None, calibrator=None, grounder: Optional[Grounder] = None,
                 log_store: Optional[DecisionLog] = None, log=None, run_id: Optional[str] = None,
                 docs_path: Optional[Path] = None, memory_path: Optional[Path] = None):
        self.settings = settings
        self.llm = llm or LLMClient(settings)
        self.embedder = embedder or SentenceTransformerEmbedder(settings.embedding_model)
        self.docs_path = Path(docs_path or DOCS_PATH)
        self.memory_path = Path(memory_path or MEMORY_PATH)
        self.retriever = retriever or self._build_retriever()
        self.knn = knn if knn is not None else self._build_knn()
        self.calibrator = calibrator if calibrator is not None else load_calibrator()
        self.grounder = grounder or Grounder(self.embedder, nli=NLIScorer() if settings.grounding_nli else None,
                                             cos_threshold=settings.grounding_cos, lex_threshold=settings.grounding_lex,
                                             contradiction_threshold=settings.grounding_contradiction)
        self.log = log or log_store or DecisionLog(settings.sqlite_path, run_id=run_id)
        self.model_name = getattr(getattr(self.llm, "settings", None), "model_name", settings.model_name)

    # ---- production component builders -----------------------------------------------------
    def _build_retriever(self) -> Retriever:
        r = Retriever(self.embedder, self.settings.chroma_path)
        docs = json.loads(self.docs_path.read_text(encoding="utf-8"))
        n = r.ensure_built(docs)
        log.info("retriever ready: %d chunks at %s", n, self.settings.chroma_path)
        return r

    def _build_knn(self) -> KNNClassifier:
        tickets = load_tickets(self.memory_path) if self.memory_path.exists() else []
        knn = KNNClassifier(self.embedder, k=7).fit(tickets)
        log.info("neighbour memory: %d labelled tickets from %s", len(knn), self.memory_path)
        return knn

    # ---- the chain ---------------------------------------------------------------------------
    def process(self, ticket: Ticket) -> TicketResult:
        t0 = time.perf_counter()
        s = self.settings
        stage = "classification"
        prompt_versions: Dict[str, str] = {}
        summary = _summary(ticket)

        # 1. classify
        cls = classify(ticket, self.llm, calibrator=self.calibrator, knn=self.knn)
        prompt_versions["PR-02"] = cls.prompt_version
        self.log.record(
            ticket_id=ticket.ticket_id, stage="classification", action_taken="proceed", reason=cls.reason,
            input_summary=summary, model_name=self.model_name, model_version=cls.prompt_version,
            prediction_value=f"{cls.intent}|{cls.urgency}", prediction_confidence=cls.confidence,
            alternatives=cls.alternatives, prompt_version=cls.prompt_version,
            requirement_ids=["FR-02", "FR-15", "FR-16"], error=cls.error)

        # 2. retrieve
        stage = "retrieval"
        passages: List[Passage] = []
        try:
            passages = self.retriever.search(ticket.text, k=s.retrieval_top_k, threshold=s.retrieval_threshold)
        except Exception as exc:  # noqa: BLE001 - retrieval failure is handled as "no grounded source"
            log.exception("retrieval failed for %s", ticket.ticket_id)
        sources = [{"doc_id": p.doc_id, "section": p.section, "score": round(p.score, 4)} for p in passages]

        # 3. route
        stage = "routing"
        rt: Route = route(cls, passages, ticket.customer.tier, s)
        self.log.record(
            ticket_id=ticket.ticket_id, stage="routing", action_taken=rt.action, reason=rt.reason,
            input_summary=summary, model_name=self.model_name, prediction_value=rt.rule,
            prediction_confidence=cls.confidence, sources_used=sources, threshold_applied=rt.threshold_applied,
            requirement_ids=["FR-04", "FR-05", "FR-06"])

        draft: Optional[Draft] = None
        guard_verdicts = {"pii": "skipped", "grounding": "skipped", "tone": "skipped", "injection": "skipped"}
        guard_details: Dict[str, Any] = {}
        answer: Optional[str] = None
        citations: List[str] = []
        escalation: Optional[Dict[str, Any]] = None
        final_action = rt.action
        final_reason = rt.reason
        error = cls.error

        if rt.action == "auto_respond":
            # 4. generate
            stage = "generation"
            draft = generate(ticket, passages, self.llm)
            prompt_versions["PR-03"] = draft.prompt_version
            self.log.record(
                ticket_id=ticket.ticket_id, stage="generation", action_taken="proceed" if not draft.unknown else "escalate",
                reason="draft produced" if not draft.unknown else (draft.error or "model could not answer from the passages"),
                input_summary=summary, model_name=self.model_name, prediction_value="draft" if not draft.unknown else "unknown",
                sources_used=[{"doc_id": c} for c in draft.citations], prompt_version=draft.prompt_version,
                requirement_ids=["FR-07", "FR-12"], error=draft.error)
            if draft.unknown:
                final_action = "escalate"
                final_reason = f"Escalated: {draft.error or 'the model could not answer from the retrieved passages'}."
                error = error or draft.error
            else:
                # 5. validate
                stage = "validation"
                rep = run_guardrails(draft, ticket, passages, self.grounder)
                guard_verdicts, guard_details = rep.verdicts, rep.details
                if rep.blocked:
                    final_action = "block"
                    blocked_by = [k for k, v in rep.verdicts.items() if v == "block"]
                    final_reason = (f"Blocked by guardrail ({', '.join(blocked_by)}) and escalated: "
                                    + self._guardrail_reason(rep.details, blocked_by))
                elif s.kill_switch_active():                  # switched on while this ticket was in flight
                    final_action = "escalate"
                    final_reason = "Escalated: the kill switch was switched on while the answer was being prepared."
                else:
                    answer = add_disclosure(rep.answer)
                    citations = draft.citations

        if final_action != "auto_respond":
            # escalation package, for any escalate or block
            esc = build_escalation(ticket, cls, passages, draft, Route(final_action if final_action == "escalate" else "escalate",
                                                                     rt.rule if final_action == "escalate" else "guardrail_block",
                                                                     final_reason, rt.threshold_applied), self.llm)
            prompt_versions["PR-04"] = esc.prompt_version
            escalation = esc.to_dict()
            self.log.record(
                ticket_id=ticket.ticket_id, stage="generation", action_taken="escalate",
                reason=f"escalation summary ({esc.summary_source})", input_summary=summary, model_name=self.model_name,
                prediction_value="escalation_summary", sources_used=sources, prompt_version=esc.prompt_version,
                requirement_ids=["FR-08"], error=esc.error)

        # validation row for every ticket (records what was checked, even when skipped)
        self.log.record(
            ticket_id=ticket.ticket_id, stage="validation", action_taken=final_action, reason=final_reason,
            input_summary=summary, model_name=self.model_name, prediction_value=final_action,
            prediction_confidence=cls.confidence, sources_used=[{"doc_id": c} for c in citations] or sources,
            threshold_applied=rt.threshold_applied, guardrail_results=guard_verdicts,
            prompt_version=prompt_versions.get("PR-03"), requirement_ids=["FR-09", "FR-10", "FR-11", "FR-15"],
            error=error)

        latency = (time.perf_counter() - t0) * 1000
        raw = ticket.raw if isinstance(ticket.raw, dict) else {}
        return TicketResult(
            ticket_id=ticket.ticket_id, channel=ticket.channel, tier=ticket.customer.tier, region=ticket.customer.region,
            fluency=ticket.customer.fluency, text_len=len(ticket.text), intent=cls.intent, urgency=cls.urgency,
            confidence=cls.confidence, raw_confidence=cls.raw_confidence, alternatives=cls.alternatives,
            instruction_like=cls.instruction_like or guard_verdicts.get("injection") == "block",
            retrieved=sources, action=final_action, route_reason=final_reason, answer=answer, citations=citations,
            escalation=escalation, guardrails=guard_verdicts, latency_ms=latency, error=error,
            stage_reached="validation", labels=raw.get("labels"), history=raw.get("history"),
            prompt_versions=prompt_versions,
        )

    @staticmethod
    def _guardrail_reason(details: Dict[str, Any], blocked_by: List[str]) -> str:
        parts = []
        for k in blocked_by:
            d = details.get(k, {})
            if k == "pii":
                parts.append("the draft contained " + ", ".join(m["type"].replace("_", " ") for m in d.get("matches", [])))
            elif k == "tone":
                parts.append("the draft made a commitment (" + ", ".join(h["type"].replace("_", " ") for h in d.get("hits", [])) + ")")
            elif k == "grounding":
                u = d.get("unsupported", [])
                parts.append(f"{len(u)} sentence(s) not supported by the documentation" + (f': "{u[0]["sentence"][:80]}"' if u else ""))
            elif k == "injection":
                parts.append("the ticket text contained instructions aimed at the system")
        return "; ".join(parts) + "."


def safe_process(pipeline, ticket: Ticket, settings: Settings) -> TicketResult:
    """process() that cannot raise: a component failure becomes an escalation with the reason (A11),
    and the routing and validation rows are written so the failure still reconciles (A8). Used by
    the harness and the API so both degrade the same way."""
    t0 = time.perf_counter()
    try:
        result = pipeline.process(ticket)
        observe(result)                                  # B-12: one observation per ticket
        return result
    except Exception as exc:  # noqa: BLE001
        error = f"{type(exc).__name__}: {exc}"
        log.exception("ticket %s failed; escalating", ticket.ticket_id)
        result = failure_result(ticket, error, stage="pipeline", latency_ms=(time.perf_counter() - t0) * 1000)
        store = getattr(pipeline, "log", None)
        if store is not None and hasattr(store, "record"):
            for stage in ("routing", "validation"):
                try:
                    store.record(ticket_id=ticket.ticket_id, stage=stage, action_taken="escalate",
                                 reason=f"Escalated: pipeline failure ({error})", input_summary=(ticket.text or "")[:300],
                                 model_name=settings.model_name, prediction_value="escalate",
                                 requirement_ids=["FR-14"], error=error)
                except Exception:  # noqa: BLE001
                    log.exception("could not log failure row for %s", ticket.ticket_id)
        observe(result)
        return result


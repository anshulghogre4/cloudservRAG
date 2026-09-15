"""Shared result model: one record per ticket, written to results.jsonl by the harness.

Every stage fills its part; the harness never needs to know which components exist yet, so
it can run with stubs from day one (Stage 4 rule: harness before classifier).
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Protocol

ACTIONS = ("auto_respond", "escalate", "block")


@dataclass
class TicketResult:
    ticket_id: str
    channel: str
    tier: str
    region: str
    fluency: str
    text_len: int
    intent: str
    urgency: str
    confidence: float
    raw_confidence: float
    alternatives: List[Dict[str, Any]]
    instruction_like: bool
    retrieved: List[Dict[str, Any]]          # [{doc_id, section, score}]
    action: str                              # auto_respond | escalate | block
    route_reason: str
    answer: Optional[str]
    citations: List[str]
    escalation: Optional[Dict[str, str]]     # {summary, uncertainty}
    guardrails: Dict[str, str]               # {pii, grounding, tone, injection}: pass | block | skipped
    latency_ms: float
    error: Optional[str]
    stage_reached: str                       # ingest | classification | retrieval | routing | generation | validation
    labels: Optional[Dict[str, Any]] = None  # copied from the input when present (evaluation only)
    history: Optional[Dict[str, Any]] = None
    prompt_versions: Dict[str, str] = field(default_factory=dict)

    def to_record(self) -> Dict[str, Any]:
        d = asdict(self)
        assert d["action"] in ACTIONS, d["action"]
        return d


class Pipeline(Protocol):
    def process(self, ticket) -> TicketResult: ...


def failure_result(ticket, error: str, stage: str, latency_ms: float) -> TicketResult:
    """The record written when a component raises: the ticket escalates with the reason (A9, A11)."""
    raw = ticket.raw if isinstance(ticket.raw, dict) else {}
    return TicketResult(
        ticket_id=ticket.ticket_id, channel=ticket.channel, tier=ticket.customer.tier,
        region=ticket.customer.region, fluency=ticket.customer.fluency, text_len=len(ticket.text),
        intent="unclear_request", urgency="medium", confidence=0.0, raw_confidence=0.0, alternatives=[],
        instruction_like=False, retrieved=[], action="escalate",
        route_reason=f"escalated: processing failed at {stage} ({error})", answer=None, citations=[],
        escalation={"summary": "Automated processing failed; ticket forwarded unchanged.",
                    "uncertainty": f"Failure at {stage}: {error}"},
        guardrails={"pii": "skipped", "grounding": "skipped", "tone": "skipped", "injection": "skipped"},
        latency_ms=latency_ms, error=error, stage_reached=stage,
        labels=raw.get("labels"), history=raw.get("history"),
    )

"""Escalation package (FR-08, B-10): what a tier-two engineer receives instead of a raw ticket.

Daniel's four items: what the ticket is about, the documentation that seemed relevant, the draft if
there is one, and what the system was unsure about. The summary comes from PR-04; if the provider
is unavailable or returns something unparseable, a deterministic template built from the
classification and the route reason is used instead, so an escalation never leaves without its
context (FR-14). Customer name and id are never placed in the prompt.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from src.classify import Classification
from src.generate import Draft
from src.ingest import Ticket
from src.llm import ProviderUnavailable
from src.retrieve import Passage
from src.route import Route

PROMPT_VERSION = "PR-04 v1.0"
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "build" / "PR-04_escalation_summary_v1.0.txt"
_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.S)
_OBJ = re.compile(r"\{.*\}", re.S)


@dataclass
class Escalation:
    summary: str
    uncertainty: str
    intent: str
    confidence: float
    doc_ids: List[str]
    draft: Optional[str]
    route_reason: str
    rule: str
    summary_source: str = "model"      # model | template
    prompt_version: str = PROMPT_VERSION
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def build_prompt(ticket: Ticket, cls: Classification, doc_ids: Sequence[str], route: Route,
                 draft: Optional[Draft], template: Optional[str] = None) -> str:
    t = template or load_prompt()
    return (t.replace("{INTENT}", cls.intent).replace("{CONFIDENCE}", f"{cls.confidence:.2f}")
             .replace("{REASON}", route.reason).replace("{DOC_IDS}", ", ".join(doc_ids) or "none")
             .replace("{DRAFT_OR_NONE}", (draft.answer if draft and not draft.unknown else "none"))
             .replace("{TICKET_TEXT}", ticket.text or ""))


def _extract(text: str) -> Optional[dict]:
    for c in ([m.group(1) for m in [_FENCE.search(text or "")] if m] + [text or ""] +
              [m.group(0) for m in [_OBJ.search(text or "")] if m]):
        try:
            obj = json.loads(c)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    return None


def template_summary(ticket: Ticket, cls: Classification, doc_ids: Sequence[str], route: Route,
                     draft: Optional[Draft]) -> Dict[str, str]:
    words = cls.intent.replace("_", " ")
    head = (ticket.subject or ticket.body or "")[:120].strip()
    docs = ", ".join(doc_ids) if doc_ids else "no documentation passage was relevant"
    summary = (f"Customer ticket about {words} (confidence {cls.confidence:.2f}): \"{head}\". "
               f"Relevant documentation: {docs}. "
               + ("A draft answer is attached." if draft and not draft.unknown else "No draft was produced."))
    return {"summary": summary, "uncertainty": route.reason}


def build_escalation(ticket: Ticket, cls: Classification, passages: Sequence[Passage], draft: Optional[Draft],
                     route: Route, llm, template: Optional[str] = None) -> Escalation:
    doc_ids = list(dict.fromkeys(p.doc_id for p in passages))
    draft_text = draft.answer if (draft and not draft.unknown) else None
    base = dict(intent=cls.intent, confidence=cls.confidence, doc_ids=doc_ids, draft=draft_text,
                route_reason=route.reason, rule=route.rule)
    error = None
    try:
        raw = llm.complete(build_prompt(ticket, cls, doc_ids, route, draft, template), json_mode=True, max_tokens=300)
        obj = _extract(raw)
        if obj and isinstance(obj.get("summary"), str) and obj["summary"].strip():
            return Escalation(summary=obj["summary"].strip(), uncertainty=str(obj.get("uncertainty") or route.reason).strip(),
                              summary_source="model", **base)
        error = "escalation summary: could not parse model output"
    except ProviderUnavailable as exc:
        error = f"escalation summary: {exc}"
    except Exception as exc:  # noqa: BLE001
        error = f"escalation summary: {type(exc).__name__}: {exc}"
    t = template_summary(ticket, cls, doc_ids, route, draft)
    return Escalation(summary=t["summary"], uncertainty=t["uncertainty"], summary_source="template", error=error, **base)

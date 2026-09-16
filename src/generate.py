"""Generate (FR-07, FR-12, FR-15, B-08): draft a reply grounded in the retrieved passages, with citations.

- Prompt PR-03 (prompts/build/PR-03_drafter_v1.0.txt). Passages are listed as
  [doc_id | section | applies_to] blocks inside <passages>; the ticket text inside <ticket>.
  Customer fields (name, id) are never placed in the prompt (FR-09).
- Inline [DOC-ID] markers are the citation format: standard for grounded generation, easy for a
  small model to follow, and mechanically checkable.
- Every citation is validated against the passages actually retrieved for this ticket (A6);
  anything else is dropped and reported in invalid_citations.
- No passages -> unknown draft, no model call. Provider or parse failure -> unknown draft with the
  error, so the router escalates (A11). The disclosure line (FR-12) is added by code, not by the model.
- citation_map() splits the draft into sentences with their citations for the grounding guardrail (B-09).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from src.ingest import Ticket
from src.llm import ProviderUnavailable
from src.retrieve import Passage

PROMPT_VERSION = "PR-03 v1.2"
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "build" / "PR-03_drafter_v1.2.txt"

DISCLOSURE = ("This reply was drafted automatically from CloudServe's support documentation. "
              "A support engineer will confirm it if you reply.")
UNKNOWN_ANSWER = ("Thank you for getting in touch. I could not find documentation that answers this, "
                  "so a support engineer will look at your ticket and reply directly.")

_CITE = re.compile(r"\[(DOC-[A-Z]+-\d{3})\]")
# the model sometimes copies the whole passage header: [DOC-X | Section | Plan]; normalise to [DOC-X]
_CITE_LONG = re.compile(r"\[(DOC-[A-Z]+-\d{3})\s*\|[^\]]*\]")


def normalise_markers(text: str) -> str:
    return _CITE_LONG.sub(lambda m: f"[{m.group(1)}]", text or "")
_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.S)
_OBJ = re.compile(r"\{.*\}", re.S)
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\[])")


@dataclass
class Draft:
    answer: str
    citations: List[str]
    unknown: bool
    invalid_citations: List[str] = field(default_factory=list)
    error: Optional[str] = None
    raw: Optional[str] = None
    prompt_version: str = PROMPT_VERSION


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def format_passages(passages: Sequence[Passage]) -> str:
    blocks = []
    for p in passages:
        blocks.append(f"[{p.doc_id} | {p.section} | {p.applies_to}]\n{p.text.strip()}")
    return "\n\n".join(blocks)


def build_prompt(ticket: Ticket, passages: Sequence[Passage], tier: str, template: Optional[str] = None) -> str:
    template = template or load_prompt()
    return (template.replace("{PASSAGES}", format_passages(passages))
                    .replace("{TICKET_TEXT}", ticket.text or "")
                    .replace("{TIER}", tier or "unknown"))


def _extract_json(text: str) -> Optional[dict]:
    if not text:
        return None
    candidates = [text.strip()]
    m = _FENCE.search(text)
    if m:
        candidates.insert(0, m.group(1))
    m = _OBJ.search(text)
    if m:
        candidates.append(m.group(0))
    for c in candidates:
        try:
            obj = json.loads(c)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    return None


def split_sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", (text or "").strip())
    return [s for s in _SENT_SPLIT.split(text) if s.strip()] if text else []


def citation_map(text: str) -> List[Dict[str, object]]:
    """[{sentence (markers stripped), citations [...]}] in order, for the grounding check."""
    out = []
    for s in split_sentences(normalise_markers(text)):
        cites = _CITE.findall(s)
        clean = _CITE.sub("", s).replace("  ", " ").strip()
        out.append({"sentence": clean, "citations": list(dict.fromkeys(cites))})
    return out


def add_disclosure(answer: str) -> str:
    answer = (answer or "").rstrip()
    if answer.endswith(DISCLOSURE):
        return answer
    return f"{answer}\n\n{DISCLOSURE}" if answer else DISCLOSURE


def _unknown(error: Optional[str] = None, raw: Optional[str] = None) -> Draft:
    return Draft(answer=UNKNOWN_ANSWER, citations=[], unknown=True, error=error, raw=raw)


def generate(ticket: Ticket, passages: Sequence[Passage], llm, tier: Optional[str] = None,
             template: Optional[str] = None) -> Draft:
    """Draft a reply. Never raises; an unknown draft with `error` set means the router must escalate."""
    if not passages:
        return _unknown()
    tier = tier or ticket.customer.tier
    try:
        raw = llm.complete(build_prompt(ticket, passages, tier, template), json_mode=True, max_tokens=500)
    except ProviderUnavailable as exc:
        return _unknown(error=f"generation failed: {exc}")
    except Exception as exc:  # noqa: BLE001
        return _unknown(error=f"generation failed: {type(exc).__name__}: {exc}")

    obj = _extract_json(raw)
    if obj is None or not isinstance(obj.get("answer"), str):
        return _unknown(error="generation failed: could not parse model output as JSON", raw=raw)

    answer = normalise_markers(obj["answer"].strip())
    unknown = bool(obj.get("unknown", False)) or not answer
    retrieved = [p.doc_id for p in passages]
    listed = [str(c) for c in (obj.get("citations") or []) if isinstance(c, str)]
    inline = _CITE.findall(answer)
    wanted = list(dict.fromkeys(listed + inline))
    valid = [c for c in wanted if c in retrieved]
    invalid = [c for c in wanted if c not in retrieved]
    for bad in invalid:                          # never leave a citation that cannot be verified (A6)
        answer = answer.replace(f"[{bad}]", "").replace("  ", " ")
    if unknown:
        return Draft(answer=UNKNOWN_ANSWER, citations=[], unknown=True, invalid_citations=invalid, raw=raw)
    return Draft(answer=answer, citations=valid, unknown=False, invalid_citations=invalid, raw=raw)

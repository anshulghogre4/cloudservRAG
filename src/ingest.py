"""Ingest: normalise a raw ticket from any channel into one Ticket object (FR-01, B-02).

Rules from the Build Specification, Ingest section:
- accepts email, chat, docs_comment and forum;
- one internal representation regardless of channel;
- preserves the original text and the channel;
- handles missing fields, unusual characters and empty bodies without failing.

Nothing here calls a model. Every later stage reads Ticket.text, never the raw JSON,
so customer fields (name, id, tier) are not passed to the model by accident (FR-09).
"""
from __future__ import annotations

import json
import re
import unicodedata
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, List, Optional

CHANNELS = ("email", "chat", "docs_comment", "forum")
TIERS = ("enterprise", "business", "standard")
REGIONS = ("north_america", "europe", "asia_pacific", "latin_america")
FLUENCY = ("fluent", "non_fluent")

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


@dataclass(frozen=True)
class Customer:
    customer_id: str
    tier: str        # enterprise | business | standard | unknown
    region: str      # north_america | europe | asia_pacific | latin_america | unknown
    fluency: str     # fluent | non_fluent | unknown


@dataclass
class Ticket:
    ticket_id: str
    channel: str                 # one of CHANNELS, or "unknown"
    subject: str                 # original, "" when absent (all chat tickets)
    body: str                    # original
    text: str                    # cleaned subject + body; what classify and retrieve read
    customer: Customer
    received_at: Optional[str]
    raw: dict                    # the untouched input record
    warnings: List[str] = field(default_factory=list)


def _clean(value: Any) -> str:
    """Return a printable string: None -> "", strip control chars, normalise unicode."""
    if value is None:
        return ""
    s = str(value)
    s = unicodedata.normalize("NFC", s)
    s = _CONTROL.sub("", s)
    return s.strip()


def _enum(value: Any, allowed: Iterable[str], name: str, warnings: List[str]) -> str:
    v = _clean(value).lower()
    if v in allowed:
        return v
    warnings.append(f"{name} missing or unrecognised ({value!r}); set to 'unknown'")
    return "unknown"


def normalise_ticket(raw: dict) -> Ticket:
    """Build a Ticket from a raw record. Never raises on bad input; records warnings."""
    warnings: List[str] = []
    if not isinstance(raw, dict):
        warnings.append(f"record is not an object ({type(raw).__name__}); wrapped as empty ticket")
        raw = {"body": _clean(raw)}

    ticket_id = _clean(raw.get("ticket_id"))
    if not ticket_id:
        ticket_id = f"UNKNOWN-{uuid.uuid4().hex[:8]}"
        warnings.append(f"ticket_id missing; generated {ticket_id}")

    channel = _enum(raw.get("channel"), CHANNELS, "channel", warnings)
    subject = _clean(raw.get("subject"))
    body = _clean(raw.get("body"))
    if not body:
        warnings.append("body is empty")

    text = f"{subject}\n{body}".strip() if subject else body

    customer = Customer(
        customer_id=_clean(raw.get("customer_id")) or "unknown",
        tier=_enum(raw.get("customer_tier"), TIERS, "customer_tier", warnings),
        region=_enum(raw.get("customer_region"), REGIONS, "customer_region", warnings),
        fluency=_enum(raw.get("language_fluency"), FLUENCY, "language_fluency", warnings),
    )
    received_at = _clean(raw.get("received_at")) or None

    return Ticket(
        ticket_id=ticket_id,
        channel=channel,
        subject=subject,
        body=body,
        text=text,
        customer=customer,
        received_at=received_at,
        raw=raw,
        warnings=warnings,
    )


def load_tickets(path: str | Path) -> List[Ticket]:
    """Read a JSON list of tickets from any path (A9: never a hard-coded filename)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON list of tickets, got {type(data).__name__}")
    return [normalise_ticket(r) for r in data]

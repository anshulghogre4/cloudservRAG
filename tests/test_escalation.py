"""B-10 / FR-08: every escalation carries summary, intent, retrieved doc ids, draft and uncertainty.

T-14  test_escalation_package   all five fields present; provider outage still yields a complete package
"""
import json

import pytest

from src.classify import Classification
from src.escalation import Escalation, build_escalation
from src.generate import Draft
from src.ingest import normalise_ticket
from src.llm import ProviderUnavailable
from src.retrieve import Passage
from src.route import Route


class FakeLLM:
    def __init__(self, reply=None, error=None):
        self.reply, self.error, self.prompts = reply, error, []

    def complete(self, prompt, **kw):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return self.reply


@pytest.fixture
def ticket():
    return normalise_ticket({"ticket_id": "T1", "channel": "email", "subject": "Data location",
                             "body": "Our auditor needs to know where backups are stored.",
                             "customer_name": "Priya Sharma", "customer_id": "CUST-1042",
                             "customer_tier": "business", "customer_region": "europe", "language_fluency": "fluent"})


@pytest.fixture
def cls():
    return Classification(intent="compliance_request", urgency="medium", confidence=0.99, raw_confidence=0.9,
                          alternatives=[{"intent": "data_residency", "confidence": 0.3}], instruction_like=False,
                          reason="auditor asks for records")


@pytest.fixture
def passages():
    return [Passage(doc_id="DOC-SEC-003", section="Resolution", title="Audit logging", applies_to="Business and Enterprise plans",
                    text="Export the relevant period to object storage.", score=0.7, chunk_id="DOC-SEC-003#resolution")]


ROUTE = Route(action="escalate", rule="never_auto_intent",
              reason="Escalated: compliance request tickets are always handled by a person, whatever the confidence (policy rule).",
              threshold_applied=0.8)


def test_escalation_package(ticket, cls, passages):
    llm = FakeLLM(reply=json.dumps({"summary": "Auditor asks where backups are stored; DOC-SEC-003 covers export.",
                                    "uncertainty": "Compliance tickets always go to a person."}))
    e = build_escalation(ticket, cls, passages, None, ROUTE, llm)
    assert isinstance(e, Escalation)
    assert e.summary and e.uncertainty and e.intent == "compliance_request"
    assert e.doc_ids == ["DOC-SEC-003"] and e.draft is None
    assert e.prompt_version.startswith("PR-04")
    p = llm.prompts[0]
    assert "<ticket>" in p and "compliance_request" in p and "DOC-SEC-003" in p and "Priya" not in p
    d = e.to_dict()
    assert set(d) >= {"summary", "uncertainty", "intent", "confidence", "doc_ids", "draft", "route_reason", "rule"}


def test_escalation_survives_provider_outage(ticket, cls, passages):
    llm = FakeLLM(error=ProviderUnavailable("provider unavailable: timeout"))
    draft = Draft(answer="Draft text [DOC-SEC-003].", citations=["DOC-SEC-003"], unknown=False)
    e = build_escalation(ticket, cls, passages, draft, ROUTE, llm)
    assert e.summary and "compliance request" in e.summary.lower()
    assert "DOC-SEC-003" in e.summary and e.draft == "Draft text [DOC-SEC-003]."
    assert "person" in e.uncertainty.lower() or "policy" in e.uncertainty.lower()
    assert e.summary_source == "template" and e.error


def test_escalation_with_bad_json_falls_back(ticket, cls, passages):
    e = build_escalation(ticket, cls, passages, None, ROUTE, FakeLLM(reply="not json"))
    assert e.summary_source == "template" and e.summary

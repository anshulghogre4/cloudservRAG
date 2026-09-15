"""B-06 / FR-02: intent + urgency + confidence, fallback on failure, alternatives recorded.

T-03  test_schema_and_range      every field present, confidence in [0,1], alternatives list
T-04  test_fallback_on_failure   provider down / bad JSON -> unclear_request, confidence 0, reason names the cause
"""
import json

import pytest

from src.classify import classify, Classification, INTENTS, URGENCIES, PROMPT_VERSION
from src.ingest import normalise_ticket
from src.llm import ProviderUnavailable


class FakeLLM:
    def __init__(self, reply=None, error=None):
        self.reply, self.error, self.prompts = reply, error, []

    def complete(self, prompt, **kw):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return self.reply


GOOD = json.dumps({
    "intent": "rate_limit", "urgency": "medium", "confidence": 0.91,
    "alternatives": [{"intent": "quota_or_overage", "confidence": 0.07}],
    "instruction_like": False, "reason": "The customer reports 429 responses.",
})


@pytest.fixture
def ticket(sample_tickets):
    return normalise_ticket(sample_tickets[0])


def test_schema_and_range(ticket):
    llm = FakeLLM(reply=GOOD)
    c = classify(ticket, llm)
    assert isinstance(c, Classification)
    assert c.intent in INTENTS and c.urgency in URGENCIES
    assert 0.0 <= c.confidence <= 1.0
    assert c.alternatives and c.alternatives[0]["intent"] == "quota_or_overage"
    assert c.instruction_like is False
    assert c.reason
    assert c.fallback is False and c.error is None
    assert c.prompt_version == PROMPT_VERSION
    # the prompt carried the body inside <ticket> tags and the fixed intent list (FR-15)
    p = llm.prompts[0]
    assert "<ticket>" in p and ticket.body in p and "unclear_request" in p


def test_confidence_is_clamped_and_alternatives_capped():
    t = normalise_ticket({"ticket_id": "X", "channel": "email", "subject": "s", "body": "b"})
    reply = json.dumps({"intent": "billing_query", "urgency": "low", "confidence": 1.7,
                        "alternatives": [{"intent": "quota_or_overage", "confidence": 0.5},
                                         {"intent": "rate_limit", "confidence": 0.2},
                                         {"intent": "onboarding", "confidence": 0.1}],
                        "instruction_like": True, "reason": "r"})
    c = classify(t, FakeLLM(reply=reply))
    assert c.confidence == 1.0
    assert len(c.alternatives) == 2
    assert c.instruction_like is True


def test_fallback_on_provider_failure(ticket):
    c = classify(ticket, FakeLLM(error=ProviderUnavailable("provider unavailable: timeout")))
    assert c.intent == "unclear_request" and c.confidence == 0.0
    assert c.fallback is True
    assert "provider unavailable" in c.reason.lower()


def test_fallback_on_bad_json(ticket):
    c = classify(ticket, FakeLLM(reply="Sure! Here is the classification: rate_limit"))
    assert c.intent == "unclear_request" and c.confidence == 0.0 and c.fallback is True
    assert "parse" in c.reason.lower()


def test_fallback_on_unknown_intent(ticket):
    c = classify(ticket, FakeLLM(reply=json.dumps({"intent": "made_up", "urgency": "high", "confidence": 0.9})))
    assert c.intent == "unclear_request" and c.fallback is True


def test_json_inside_code_fence_is_accepted(ticket):
    c = classify(ticket, FakeLLM(reply="```json\n" + GOOD + "\n```"))
    assert c.intent == "rate_limit" and c.fallback is False


def test_calibrator_is_applied(ticket):
    c = classify(ticket, FakeLLM(reply=GOOD), calibrator=lambda x: x * 0.5)
    assert c.raw_confidence == pytest.approx(0.91)
    assert c.confidence == pytest.approx(0.455)

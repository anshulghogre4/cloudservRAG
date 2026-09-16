"""B-06: the nearest-neighbour signal used alongside PR-02 (offline embedder, no network)."""
import pytest

from src.classify import KNNClassifier, combine, classify
from src.ingest import normalise_ticket
from src.llm import ProviderUnavailable
from tests.test_retrieve import BagOfWordsEmbedder


def _t(i, body, intent, urgency="medium"):
    return normalise_ticket({"ticket_id": f"K-{i}", "channel": "email", "subject": "", "body": body,
                             "labels": {"intent": intent, "urgency": urgency}})


@pytest.fixture
def knn():
    tickets = [
        _t(1, "requests return 429 too many requests rate limit", "rate_limit", "high"),
        _t(2, "we are being rate limited with 429 errors", "rate_limit", "high"),
        _t(3, "invoice is higher than expected this month billing", "billing_query"),
        _t(4, "why is my invoice higher billing period", "billing_query"),
        _t(5, "cannot log in invalid credentials locked", "authentication_failure"),
    ]
    return KNNClassifier(BagOfWordsEmbedder(), k=3).fit(tickets)


def test_fit_and_predict_distribution(knn):
    assert len(knn) == 5
    probs = knn.predict_proba("getting 429 too many requests")
    assert abs(sum(probs.values()) - 1.0) < 1e-6
    best, p = knn.predict("getting 429 too many requests")
    assert best == "rate_limit" and 0 < p <= 1


def test_exclude_identical_body_for_leave_one_out(knn):
    body = "requests return 429 too many requests rate limit"
    probs_in = knn.predict_proba(body)
    probs_out = knn.predict_proba(body, exclude_text=body)
    assert probs_in.get("rate_limit", 0) >= probs_out.get("rate_limit", 0)


def test_empty_index_is_harmless():
    k = KNNClassifier(BagOfWordsEmbedder()).fit([])
    assert len(k) == 0 and k.predict_proba("x") == {} and k.predict("x") == (None, 0.0)


def test_combine_rewards_agreement_and_caps_disagreement():
    assert combine(0.9, None, None) == 0.9
    assert combine(0.9, 0.8, True) == pytest.approx(0.9)
    assert combine(0.9, 0.8, False) == pytest.approx(0.4)
    assert combine(0.2, 1.0, True) == pytest.approx(1.0)


def test_neighbours_override_llm_intent_on_disagreement(knn):
    t = _t(9, "we keep getting 429 too many requests", "rate_limit")
    reply = ('{"intent": "billing_query", "urgency": "low", "confidence": 0.95, "alternatives": [], '
             '"instruction_like": false, "reason": "r"}')
    c = classify(t, FakeLLM(reply=reply), knn=knn)
    assert c.intent == "rate_limit" and c.llm_intent == "billing_query" and c.agreement is False
    assert c.alternatives and c.alternatives[0]["intent"] == "billing_query"   # the LLM view is kept as an alternative
    assert c.confidence < 0.6                                                  # disagreement lowers confidence


class FakeLLM:
    def __init__(self, reply=None, error=None):
        self.reply, self.error = reply, error

    def complete(self, prompt, **kw):
        if self.error:
            raise self.error
        return self.reply


def test_classify_uses_knn_signal(knn):
    t = _t(9, "we keep getting 429 too many requests", "rate_limit")
    reply = '{"intent": "rate_limit", "urgency": "medium", "confidence": 0.9, "alternatives": [], "instruction_like": false, "reason": "r"}'
    c = classify(t, FakeLLM(reply=reply), knn=knn)
    assert c.knn_intent == "rate_limit" and c.agreement is True and c.intent == "rate_limit"
    assert c.combined_score is not None and c.confidence == c.combined_score
    assert c.raw_confidence == pytest.approx(0.9) and c.llm_intent == "rate_limit"


def test_provider_down_still_reports_knn_intent(knn):
    t = _t(9, "we keep getting 429 too many requests", "rate_limit")
    c = classify(t, FakeLLM(error=ProviderUnavailable("provider unavailable: timeout")), knn=knn)
    assert c.fallback is True and c.intent == "unclear_request" and c.confidence == 0.0
    assert c.knn_intent == "rate_limit"      # the escalation package can still say what it looks like


def test_knn_votes_on_urgency(knn):
    u, share = knn.predict_urgency("getting 429 too many requests")
    assert u == "high" and 0 < share <= 1


def test_classify_takes_urgency_from_neighbours(knn):
    t = _t(9, "we keep getting 429 too many requests", "rate_limit")
    reply = ('{"intent": "rate_limit", "urgency": "low", "confidence": 0.9, "alternatives": [], '
             '"instruction_like": false, "reason": "r"}')
    c = classify(t, FakeLLM(reply=reply), knn=knn)
    assert c.urgency == "high" and c.urgency_source == "knn"
    c2 = classify(t, FakeLLM(reply=reply))
    assert c2.urgency == "low" and c2.urgency_source == "llm"


def test_contains_and_self_exclusion_for_memorised_tickets(knn):
    body = knn._texts[0]
    assert knn.contains(body) and not knn.contains("something never seen before")
    with_self = knn._neighbours(body)
    without = knn._neighbours(body, exclude_text=body)
    assert with_self[0][1] > 0.999 and all(sim < 0.999 for _, sim in without)

"""B-07 / FR-05, FR-06, FR-15: the routing decision table.

T-09  test_deterministic        same inputs -> same decision, every time
T-10  test_reason_present       every route has a plain-English reason and the threshold applied
T-11  test_never_auto_intents   compliance, security, feature, unclear always escalate, whatever the confidence
plus  kill switch, provider fallback, instruction-like, no passages, plan restriction, happy path.
"""
import pytest

from src.classify import Classification
from src.config import Settings
from src.retrieve import Passage
from src.route import NEVER_AUTO, Route, plan_allows, route


def cls(intent="rate_limit", confidence=0.95, fallback=False, instruction_like=False, knn_answerable=None):
    return Classification(intent=intent, urgency="medium", confidence=confidence, raw_confidence=0.9,
                          alternatives=[], instruction_like=instruction_like,
                          reason="classification failed: provider unavailable: timeout" if fallback else "r",
                          fallback=fallback, error="provider unavailable" if fallback else None,
                          knn_answerable=knn_answerable)


def passage(doc_id="DOC-API-001", applies_to="All plans", score=0.7):
    return Passage(doc_id=doc_id, section="Resolution", title="t", applies_to=applies_to, text="x",
                   score=score, chunk_id=f"{doc_id}#resolution")


@pytest.fixture
def settings():
    return Settings(confidence_threshold=0.80, retrieval_threshold=0.40, kill_switch=False)


def test_happy_path_auto_responds(settings):
    r = route(cls(), [passage()], "standard", settings)
    assert isinstance(r, Route) and r.action == "auto_respond"
    assert r.rule == "confident_and_grounded"


def test_deterministic(settings):
    args = (cls(confidence=0.83), [passage(), passage("DOC-API-002")], "business", settings)
    first = route(*args)
    for _ in range(20):
        assert route(*args) == first


def test_reason_present(settings):
    cases = [
        (cls(), [passage()], "standard"),
        (cls(confidence=0.5), [passage()], "standard"),
        (cls(intent="security_incident"), [passage()], "standard"),
        (cls(), [], "standard"),
    ]
    for c, p, tier in cases:
        r = route(c, p, tier, settings)
        assert r.reason and r.reason[0].isupper() and len(r.reason) > 20
        assert r.threshold_applied == pytest.approx(0.80)
        assert r.action in ("auto_respond", "escalate")


def test_never_auto_intents(settings):
    assert NEVER_AUTO == {"compliance_request", "security_incident", "feature_request", "unclear_request"}
    for intent in NEVER_AUTO:
        r = route(cls(intent=intent, confidence=1.0), [passage(score=0.99)], "enterprise", settings)
        assert r.action == "escalate" and r.rule == "never_auto_intent"
        assert intent.replace("_", " ") in r.reason


def test_below_threshold_escalates(settings):
    r = route(cls(confidence=0.79), [passage()], "standard", settings)
    assert r.action == "escalate" and r.rule == "low_confidence"
    assert "0.79" in r.reason and "0.80" in r.reason
    assert route(cls(confidence=0.80), [passage()], "standard", settings).action == "auto_respond"


def test_no_passages_escalates(settings):
    r = route(cls(), [], "standard", settings)
    assert r.action == "escalate" and r.rule == "no_grounded_source"


def test_provider_fallback_escalates(settings):
    r = route(cls(intent="rate_limit", confidence=0.0, fallback=True), [passage()], "standard", settings)
    assert r.action == "escalate" and r.rule == "classification_failed"
    assert "provider" in r.reason.lower()


def test_instruction_like_escalates(settings):
    r = route(cls(instruction_like=True), [passage()], "standard", settings)
    assert r.action == "escalate" and r.rule == "instruction_like_input"


def test_kill_switch_escalates_everything():
    s = Settings(confidence_threshold=0.80, kill_switch=True)
    r = route(cls(confidence=1.0), [passage()], "enterprise", s)
    assert r.action == "escalate" and r.rule == "kill_switch"


def test_plan_restriction():
    assert plan_allows("All plans", "standard")
    assert plan_allows("Container Service, Functions", "standard")
    assert plan_allows("Business and Enterprise plans", "business")
    assert plan_allows("Business and Enterprise plans", "enterprise")
    assert not plan_allows("Business and Enterprise plans", "standard")
    assert not plan_allows("Business and Enterprise plans", "unknown")   # unknown tier: be conservative


def test_restricted_article_for_standard_tier_escalates_only_when_rule_enabled():
    p = passage("DOC-AUTH-003", applies_to="Business and Enterprise plans")
    on = Settings(confidence_threshold=0.80, plan_rule=True)
    r = route(cls(intent="sso_configuration"), [p], "standard", on)
    assert r.action == "escalate" and r.rule == "plan_restriction"
    assert "standard" in r.reason and "Business and Enterprise" in r.reason
    assert route(cls(intent="sso_configuration"), [p], "business", on).action == "auto_respond"
    off = Settings(confidence_threshold=0.80, plan_rule=False)
    assert route(cls(intent="sso_configuration"), [p], "standard", off).action == "auto_respond"


def test_learned_answerability_floor():
    s = Settings(confidence_threshold=0.80, answerable_floor=0.5)
    r = route(cls(knn_answerable=0.2), [passage()], "standard", s)
    assert r.action == "escalate" and r.rule == "learned_not_answerable" and "historically" in r.reason
    assert route(cls(knn_answerable=0.8), [passage()], "standard", s).action == "auto_respond"
    assert route(cls(knn_answerable=None), [passage()], "standard", s).action == "auto_respond"
    disabled = Settings(confidence_threshold=0.80, answerable_floor=0.0)
    assert route(cls(knn_answerable=0.2), [passage()], "standard", disabled).action == "auto_respond"


def test_rule_order_never_auto_beats_threshold(settings):
    # never-auto is checked before confidence so the reason names the governance rule, not the number
    r = route(cls(intent="feature_request", confidence=0.1), [], "standard", settings)
    assert r.rule == "never_auto_intent"


def test_kill_switch_flag_file_takes_effect_without_restart(tmp_path):
    """Governance section 5: the flag file stops automatic answers for the next ticket, no restart."""
    from src.classify import Classification
    from src.retrieve import Passage
    s = Settings(confidence_threshold=0.80, retrieval_threshold=0.40, kill_switch=False, kill_switch_file=tmp_path / "KILL")
    cls = Classification(intent="rate_limit", urgency="medium", confidence=0.99, raw_confidence=0.9, alternatives=[],
                         instruction_like=False, reason="r")
    p = [Passage(doc_id="DOC-API-001", section="Resolution", title="t", applies_to="All plans", text="x", score=0.8, chunk_id="c")]
    assert route(cls, p, "business", s).action == "auto_respond"
    (tmp_path / "KILL").write_text("set by test", encoding="utf-8")
    r = route(cls, p, "business", s)
    assert r.action == "escalate" and r.rule == "kill_switch"
    (tmp_path / "KILL").unlink()
    assert route(cls, p, "business", s).action == "auto_respond"


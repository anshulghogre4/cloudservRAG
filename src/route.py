"""Route (FR-05, FR-06, FR-15, B-07): auto-respond or escalate, deterministically, with a reason.

Decision table, checked in this order; the first rule that fires decides:

  1. kill_switch            operator has stopped automatic answers (Governance §5)
  2. classification_failed  provider was unavailable or output unparseable (FR-02 fallback)
  3. instruction_like_input the ticket tried to instruct the system (FR-15)
  4. never_auto_intent      compliance, security, feature, unclear (FR-06, Dataset Guide)
  5. low_confidence         calibrated P(intent correct) below the threshold (FR-05)
  6. learned_not_answerable neighbours in the labelled history say tickets like this were not
                            resolvable from the documentation (ANSWERABLE_FLOOR; 0 disables)
  7. no_grounded_source     retrieval returned nothing above its threshold (FR-04)
  8. plan_restriction       the article to be cited applies to other plans (PLAN_RULE; off by
                            default: measured on the development set it costs 28 expected
                            auto-answers and PR-03 already words plan limits into the draft)
  9. confident_and_grounded auto-respond; guardrails may still block later (FR-09, FR-10)

No model call, no randomness: the same inputs always give the same decision (A5).
The threshold is CONFIDENCE_THRESHOLD, chosen from development data (evaluation/route_check.py).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from src.classify import Classification
from src.config import Settings
from src.retrieve import Passage

NEVER_AUTO = {"compliance_request", "security_incident", "feature_request", "unclear_request"}

_TIERS = ("enterprise", "business", "standard")


@dataclass(frozen=True)
class Route:
    action: str              # auto_respond | escalate
    rule: str                # which row of the decision table fired
    reason: str              # plain English, for the log and the escalation package
    threshold_applied: float


def plan_allows(applies_to: str, tier: str) -> bool:
    """True unless the article names specific plans and the customer's plan is not among them.
    Corpus values are 'All plans', 'Business and Enterprise plans' or product names."""
    text = (applies_to or "").lower()
    if "plan" not in text or "all plans" in text:
        return True
    named = {t for t in _TIERS if t in text}
    if not named:
        return True
    return (tier or "").lower() in named


def route(classification: Classification, passages: Sequence[Passage], customer_tier: str,
          settings: Settings) -> Route:
    thr = float(settings.confidence_threshold)
    intent_words = classification.intent.replace("_", " ")

    if settings.kill_switch:
        return Route("escalate", "kill_switch",
                     "Escalated: the kill switch is on, so no ticket is answered automatically.", thr)
    if classification.fallback:
        return Route("escalate", "classification_failed",
                     f"Escalated: the ticket could not be classified ({classification.reason}), "
                     f"so no automatic answer is attempted.", thr)
    if classification.instruction_like:
        return Route("escalate", "instruction_like_input",
                     "Escalated: the ticket text contains instructions aimed at the system; "
                     "it is passed to a person and the input is kept for review.", thr)
    if classification.intent in NEVER_AUTO:
        return Route("escalate", "never_auto_intent",
                     f"Escalated: {intent_words} tickets are always handled by a person, "
                     f"whatever the confidence (policy rule).", thr)
    if classification.confidence < thr:
        return Route("escalate", "low_confidence",
                     f"Escalated: confidence that this is a {intent_words} ticket is "
                     f"{classification.confidence:.2f}, below the {thr:.2f} threshold.", thr)
    ka = classification.knn_answerable
    if settings.answerable_floor > 0 and ka is not None and ka < settings.answerable_floor:
        return Route("escalate", "learned_not_answerable",
                     f"Escalated: historically, tickets like this {intent_words} one were not resolved from "
                     f"the documentation (estimated {ka:.2f} chance it can be), so a person should answer.", thr)
    if not passages:
        return Route("escalate", "no_grounded_source",
                     f"Escalated: no documentation passage was relevant enough to ground an answer "
                     f"for this {intent_words} ticket.", thr)
    top = passages[0]
    if settings.plan_rule and not plan_allows(top.applies_to, customer_tier):
        return Route("escalate", "plan_restriction",
                     f"Escalated: the relevant article {top.doc_id} applies to {top.applies_to}, "
                     f"but the customer is on the {customer_tier or 'unknown'} plan.", thr)
    return Route("auto_respond", "confident_and_grounded",
                 f"Answered automatically: confidence {classification.confidence:.2f} is at or above "
                 f"{thr:.2f} and {len(passages)} passage(s) from {top.doc_id} support an answer.", thr)

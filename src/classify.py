"""Classify (FR-02, FR-15, FR-16, B-06): intent, urgency, confidence, alternatives.

Two signals, one calibrated confidence:

1. LLM (prompt PR-02): intent, urgency, a verbalized confidence, alternatives and an
   instruction_like flag. Instruction-tuned models are overconfident, so this number is
   treated as a feature, not as the probability of being right.
2. Nearest neighbours over the labelled development tickets, using the same sentence
   embedding as retrieval: a vote distribution over intents. Local, deterministic, no rate limit,
   and it still works when the provider is down (FR-14).

intent         = the neighbour intent when neighbours are available (99.2% leave-one-body-out on
                 the development set, against 71% for the LLM alone); llm_intent keeps what PR-02 said.
raw_confidence = the LLM's verbalized number (kept for the calibration table).
confidence     = calibrator(score), score = half the neighbour share plus half an agreement bonus;
                 the calibrator is Platt scaling fitted on the development set
                 (evaluation/classify_check.py). Without a fitted calibrator the score is used as is.

Fallback on any failure: unclear_request at confidence 0 with a reason naming the cause, so the
harness reports outages separately from genuine unclear tickets.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

from src.ingest import Ticket
from src.llm import ProviderUnavailable

PROMPT_VERSION = "PR-02 v1.0"
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "build" / "PR-02_classifier_v1.0.txt"

INTENTS = (
    "account_access", "api_key_issue", "api_usage_question", "authentication_failure", "billing_query",
    "compliance_request", "configuration_help", "data_export", "data_residency", "database_issue",
    "deployment_failure", "feature_request", "integration_help", "onboarding", "performance_degradation",
    "quota_or_overage", "rate_limit", "rollback_request", "security_incident", "sso_configuration",
    "unclear_request", "webhook_issue",
)
URGENCIES = ("high", "medium", "low")
FALLBACK_INTENT = "unclear_request"

_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.S)
_OBJ = re.compile(r"\{.*\}", re.S)


@dataclass
class Classification:
    intent: str
    urgency: str
    confidence: float                  # calibrated, in [0, 1]; what the router uses
    raw_confidence: float              # the model's verbalized number
    alternatives: List[Dict[str, Any]]
    instruction_like: bool
    reason: str
    fallback: bool = False
    error: Optional[str] = None
    prompt_version: str = PROMPT_VERSION
    knn_intent: Optional[str] = None
    knn_prob: Optional[float] = None   # neighbour vote share for the chosen intent
    agreement: Optional[bool] = None
    combined_score: Optional[float] = None
    urgency_source: str = "llm"
    llm_intent: Optional[str] = None   # what PR-02 said, kept for the per-class report
    knn_answerable: Optional[float] = None   # neighbours' estimate that the docs can resolve this ticket
    model: Optional[str] = None


# ---------------------------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------------------------
def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def build_prompt(ticket: Ticket, template: Optional[str] = None) -> str:
    template = template or load_prompt()
    return template.replace("{SUBJECT}", ticket.subject or "").replace("{BODY}", ticket.body or "")


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


def _clamp(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, v))


def _fallback(reason: str, error: str) -> Classification:
    return Classification(intent=FALLBACK_INTENT, urgency="medium", confidence=0.0, raw_confidence=0.0,
                          alternatives=[], instruction_like=False, reason=reason, fallback=True, error=error)


# ---------------------------------------------------------------------------------------------
# Nearest-neighbour signal
# ---------------------------------------------------------------------------------------------
class KNNClassifier:
    """Cosine nearest neighbours over labelled tickets; returns a vote distribution over intents.

    fit() takes Ticket objects that carry labels. Vectors are normalised by the embedder, so the
    dot product is the cosine similarity. `exclude_text` lets evaluation drop neighbours with an
    identical body (the development set repeats bodies), which is a leave-one-group-out check.
    """

    def __init__(self, embedder, k: int = 7):
        self.embedder = embedder
        self.k = k
        self._vecs: List[List[float]] = []
        self._labels: List[str] = []
        self._urgencies: List[str] = []
        self._answerable: List[Optional[bool]] = []
        self._texts: List[str] = []

    def fit(self, tickets: Sequence[Ticket]) -> "KNNClassifier":
        labelled = [t for t in tickets if isinstance(t.raw, dict) and t.raw.get("labels", {}).get("intent")]
        self._texts = [t.text for t in labelled]
        self._labels = [t.raw["labels"]["intent"] for t in labelled]
        self._urgencies = [str(t.raw["labels"].get("urgency") or "medium") for t in labelled]
        self._answerable = [t.raw["labels"].get("answerable_from_docs") for t in labelled]
        self._vecs = self.embedder.embed_documents(self._texts) if labelled else []
        return self

    def __len__(self) -> int:
        return len(self._labels)

    def contains(self, text: str) -> bool:
        """True when a ticket with exactly this text is in the memory (a development-set run)."""
        ex = (text or "").strip().lower()
        return any(t.strip().lower() == ex for t in self._texts)

    def _neighbours(self, text: str, exclude_text: Optional[str] = None,
                    exclude_sim_above: Optional[float] = None):
        if not self._vecs:
            return []
        q = self.embedder.embed_query(text)
        sims = [sum(a * b for a, b in zip(q, v)) for v in self._vecs]
        order = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)
        if exclude_text is not None:
            ex = exclude_text.strip().lower()
            order = [i for i in order if self._texts[i].strip().lower() != ex]
        if exclude_sim_above is not None:      # evaluation only: drop near-duplicates too
            order = [i for i in order if sims[i] < exclude_sim_above]
        return [(i, max(sims[i], 1e-6)) for i in order[: self.k]]

    @staticmethod
    def _vote(pairs) -> Dict[str, float]:
        weights: Dict[str, float] = {}
        total = 0.0
        for label, w in pairs:
            weights[label] = weights.get(label, 0.0) + w
            total += w
        return {k: v / total for k, v in weights.items()} if total else {}

    def predict_proba(self, text: str, exclude_text: Optional[str] = None,
                      exclude_sim_above: Optional[float] = None) -> Dict[str, float]:
        return self._vote([(self._labels[i], w) for i, w in self._neighbours(text, exclude_text, exclude_sim_above)])

    def predict_answerable(self, text: str, exclude_text: Optional[str] = None,
                           exclude_sim_above: Optional[float] = None) -> Optional[float]:
        """Weighted neighbour estimate of P(answerable from the documentation); None if unknown."""
        pairs = [(self._answerable[i], w) for i, w in self._neighbours(text, exclude_text, exclude_sim_above)
                 if self._answerable[i] is not None]
        if not pairs:
            return None
        total = sum(w for _, w in pairs)
        return sum(w for a, w in pairs if a) / total if total else None

    def predict_urgency(self, text: str, exclude_text: Optional[str] = None):
        """Weighted neighbour vote on urgency; (label, share) or (None, 0.0)."""
        probs = self._vote([(self._urgencies[i], w) for i, w in self._neighbours(text, exclude_text)])
        if not probs:
            return None, 0.0
        best = max(probs, key=probs.get)
        return best, probs[best]

    def predict(self, text: str, exclude_text: Optional[str] = None, exclude_sim_above: Optional[float] = None):
        probs = self.predict_proba(text, exclude_text, exclude_sim_above)
        if not probs:
            return None, 0.0
        best = max(probs, key=probs.get)
        return best, probs[best]


def combine(llm_conf: float, knn_share: Optional[float], agree: Optional[bool]) -> float:
    """Raw score in [0, 1] that the calibrator maps to P(intent correct).

    Decided from the full development run (16 Sep 2026): the neighbour vote is right 99.2% of the
    time and the LLM 71%; when they disagree the LLM is right 2% of the time. So the final intent
    is the neighbour intent, and the score is half the neighbour share plus half an agreement
    bonus. Without a neighbour signal the LLM's verbalized number is all there is."""
    if knn_share is None or agree is None:
        return llm_conf
    return 0.5 * knn_share + 0.5 * (1.0 if agree else 0.0)


# ---------------------------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------------------------
def classify(ticket: Ticket, llm, calibrator: Optional[Callable[[float], float]] = None,
             knn: Optional[KNNClassifier] = None, template: Optional[str] = None,
             exclude_self: bool = True) -> Classification:
    """Classify one ticket. Never raises; returns a fallback Classification on any failure.
    exclude_self: when the ticket itself is in the neighbour memory (a development-set run), it does
    not vote for itself, so development figures are leave-one-out rather than memorised. The hidden
    and validation sets are never in the memory, so production behaviour is unchanged."""
    knn_intent, knn_probs, knn_answerable = None, {}, None
    ex = None
    if knn is not None and len(knn):
        try:
            ex = ticket.text if (exclude_self and knn.contains(ticket.text)) else None
            knn_probs = knn.predict_proba(ticket.text, exclude_text=ex)
            knn_intent = max(knn_probs, key=knn_probs.get) if knn_probs else None
            knn_answerable = knn.predict_answerable(ticket.text, exclude_text=ex)
        except Exception:  # the local signal must never break classification
            knn_intent, knn_probs, knn_answerable = None, {}, None

    try:
        text = llm.complete(build_prompt(ticket, template), json_mode=True)
    except ProviderUnavailable as exc:
        c = _fallback(f"classification failed: {exc}", str(exc))
        _attach_knn(c, knn_intent, knn_probs, calibrator)
        return c
    except Exception as exc:
        c = _fallback(f"classification failed: {type(exc).__name__}: {exc}", str(exc))
        _attach_knn(c, knn_intent, knn_probs, calibrator)
        return c

    obj = _extract_json(text)
    if obj is None:
        c = _fallback("classification failed: could not parse model output as JSON", "parse error")
        _attach_knn(c, knn_intent, knn_probs, calibrator)
        return c

    intent = str(obj.get("intent", "")).strip().lower()
    if intent not in INTENTS:
        c = _fallback(f"classification failed: unknown intent {intent!r} from model", "unknown intent")
        _attach_knn(c, knn_intent, knn_probs, calibrator)
        return c
    urgency = str(obj.get("urgency", "")).strip().lower()
    if urgency not in URGENCIES:
        urgency = "medium"
    urgency_source = "llm"
    if knn is not None and len(knn):
        try:
            u, _share = knn.predict_urgency(ticket.text, exclude_text=ex)
            if u in URGENCIES:
                urgency, urgency_source = u, "knn"   # neighbours beat the model on urgency (classify_check)
        except Exception:
            pass

    raw_conf = _clamp(obj.get("confidence"))
    alts = []
    for a in (obj.get("alternatives") or [])[:2]:
        if isinstance(a, dict) and str(a.get("intent", "")).lower() in INTENTS:
            alts.append({"intent": str(a["intent"]).lower(), "confidence": _clamp(a.get("confidence"))})
    instruction_like = bool(obj.get("instruction_like", False))
    reason = str(obj.get("reason") or "").strip() or "no reason given by model"

    llm_intent = intent
    agree = (knn_intent == llm_intent) if knn_intent is not None else None
    if knn_intent is not None:
        intent = knn_intent                     # neighbours are the primary intent signal (see combine)
        if not agree:
            alts = [{"intent": llm_intent, "confidence": raw_conf}] + [a for a in alts if a["intent"] != llm_intent]
            alts = alts[:2]
    knn_share = knn_probs.get(intent) if knn_probs else None
    score = combine(raw_conf, knn_share, agree)
    confidence = _clamp(calibrator(score)) if calibrator else score

    return Classification(intent=intent, urgency=urgency, confidence=confidence, raw_confidence=raw_conf,
                          alternatives=alts, instruction_like=instruction_like, reason=reason,
                          knn_intent=knn_intent, knn_prob=knn_share, agreement=agree, combined_score=score,
                          urgency_source=urgency_source, llm_intent=llm_intent, knn_answerable=knn_answerable,
                          model=getattr(getattr(llm, "settings", None), "model_name", None))


def _attach_knn(c: Classification, knn_intent: Optional[str], knn_probs: Dict[str, float],
                calibrator: Optional[Callable[[float], float]] = None) -> None:
    """On a model failure the neighbour vote still stands (it needs no provider): the escalation
    package gets the neighbours' intent and a confidence scored as if the model had disagreed.
    The ticket still escalates because the router's classification_failed rule runs before the
    threshold; the confidence only tells the engineer how reliable the intent is (A11;
    disconnected-provider smoke run, 16 Sep 2026)."""
    c.knn_intent = knn_intent
    c.knn_prob = knn_probs.get(knn_intent) if knn_intent else None
    if knn_intent:
        c.intent = knn_intent
        c.combined_score = combine(0.0, c.knn_prob, False)
        c.confidence = _clamp(calibrator(c.combined_score)) if calibrator else c.combined_score
        c.alternatives = [{"intent": k, "confidence": round(v, 3)} for k, v in
                          sorted(knn_probs.items(), key=lambda kv: -kv[1]) if k != knn_intent][:2]
        c.reason = c.reason + "; intent taken from the labelled neighbours"

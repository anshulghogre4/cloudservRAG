"""Guardrails (FR-09, FR-10, FR-15, B-09): checks that run on every draft and can block it.

Governance Framework section 4, one function each:

  pii        private data in the outbound text: the customer's own name and id (exact, from the ticket
             fields), plus e-mail addresses, credential-like strings, phone and card numbers, IPs.
             Block and escalate; never redact and send.
  grounding  every factual sentence must be supported by a retrieved passage. Three local signals:
             sentence-embedding cosine, lexical containment, and an NLI contradiction score from a
             small cross-encoder. Supported but uncited sentences get their marker attached; an
             unsupported or contradicted sentence blocks the draft with the sentence flagged.
  tone       scope and commitments: refund issued, fixed on our side, a delivery date or timeline.
  injection  instruction-like customer text (patterns); the classifier's flag is a second signal.

Every check records its verdict (pass | block | skipped) whether or not it blocks (Build Spec,
Validate). None of this needs a model provider, so guardrails keep working during an outage.

Guardrails AI was evaluated (16 Sep 2026) and not adopted: its hub install needs an API key, the PII
and jailbreak validators download models at first use, and the core package requires openai >= 1.30
which cannot be installed with the pack's pinned stack (uv dry run). The provenance-embeddings
validator's mechanism (cosine to sources with a threshold) is what `Grounder` implements locally.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.generate import Draft, citation_map
from src.ingest import Ticket
from src.retrieve import Passage

# ---------------------------------------------------------------------------------------------
# Private data
# ---------------------------------------------------------------------------------------------
_PII_PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "credential": re.compile(r"\b(?:sk|pk|ak|api|key|tok|token|secret)[_-][A-Za-z0-9_-]{12,}\b|\b[A-Za-z0-9]{32,}\b"),
    "card": re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b"),
    "phone": re.compile(r"\+\d{1,3}[ -]?\d{3,}[ -]?\d{3,}"),
    "ipv4": re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"),
    "customer_ref": re.compile(r"\bCUST-\d{3,}\b"),
}


def _name_patterns(name: str) -> List[re.Pattern]:
    """Full name, and 'first last' order-insensitive; single common words are never matched alone."""
    parts = [p for p in re.split(r"\s+", (name or "").strip()) if p]
    if len(parts) < 2:
        return [re.compile(r"\b" + re.escape(name.strip()) + r"\b", re.I)] if len((name or "").strip()) >= 6 else []
    full = r"\b" + r"\s+".join(re.escape(p) for p in parts) + r"\b"
    return [re.compile(full, re.I)]


def check_private_data(answer: str, ticket: Ticket) -> Tuple[str, Dict[str, Any]]:
    matches: List[Dict[str, str]] = []
    text = answer or ""
    for pat in _name_patterns(getattr(ticket.raw, "get", lambda k, d=None: d)("customer_name", "")):
        if pat.search(text):
            matches.append({"type": "customer_name"})
    cid = (ticket.customer.customer_id or "").strip()
    if cid and cid != "unknown" and re.search(r"\b" + re.escape(cid) + r"\b", text):
        matches.append({"type": "customer_id"})
    for kind, pat in _PII_PATTERNS.items():
        if kind == "customer_ref" and any(m["type"] == "customer_id" for m in matches):
            continue
        if pat.search(text):
            matches.append({"type": kind})
    seen, uniq = set(), []
    for m in matches:
        if m["type"] not in seen:
            uniq.append(m); seen.add(m["type"])
    return ("block" if uniq else "pass"), {"matches": uniq}


# ---------------------------------------------------------------------------------------------
# Tone and scope: forbidden commitments
# ---------------------------------------------------------------------------------------------
_FORBIDDEN = [
    ("refund_issued", re.compile(r"\brefund\b[^.]{0,40}\b(has been|have been|was|were|is|are|will be)\s+(issued|processed|sent|credited|made|granted|applied)", re.I)),
    ("refund_issued", re.compile(r"\b(issued|processed|sent|credited|granted)\s+(you\s+)?(a|the|your)\s+refund\b", re.I)),
    ("fixed_on_our_side", re.compile(r"\b(fixed|resolved|corrected|patched|repaired)\b[^.]{0,25}\bon our (side|end)\b", re.I)),
    ("fixed_on_our_side", re.compile(r"\bon our (side|end)\b[^.]{0,25}\b(fixed|resolved|corrected|patched)\b", re.I)),
    ("delivery_date", re.compile(r"\b(fix|patch|release|update|feature|deploy)\w*\b[^.]{0,60}\b(by|on|before|within)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|next week|end of (the )?(day|week|month)|\d+\s*(hours?|days?|weeks?|months?)|\d{1,2}(st|nd|rd|th)?\s+\w+)\b", re.I)),
    ("delivery_date", re.compile(r"\b(by|within)\s+(\d+\s*(hours?|days?|weeks?)|friday|monday|tuesday|wednesday|thursday|tomorrow)\b[^.]{0,60}\b(fix|patch|release|deploy)\w*", re.I)),
    ("commitment", re.compile(r"\bwe (will|'ll) (issue|refund|credit|waive|compensate|escalate this to engineering and fix)\b", re.I)),
]


def check_forbidden_claims(answer: str) -> Tuple[str, Dict[str, Any]]:
    hits = []
    for name, pat in _FORBIDDEN:
        m = pat.search(answer or "")
        if m:
            hits.append({"type": name, "text": m.group(0)[:80]})
    return ("block" if hits else "pass"), {"hits": hits}


# ---------------------------------------------------------------------------------------------
# Instruction integrity
# ---------------------------------------------------------------------------------------------
_INJECTION = [
    re.compile(r"\b(ignore|disregard|forget)\b[^.]{0,30}\b(previous|prior|above|all|your|the)\b[^.]{0,20}\b(instructions?|rules?|prompts?|guidelines?)\b", re.I),
    re.compile(r"\byou are now\b", re.I),
    re.compile(r"\b(system|developer)\s*(prompt|mode|message)\b", re.I),
    re.compile(r"\bact as (an?|the)\b[^.]{0,30}\b(admin|administrator|developer|system)\b", re.I),
    re.compile(r"\b(reveal|print|show|output)\b[^.]{0,20}\b(system prompt|instructions|hidden prompt)\b", re.I),
    re.compile(r"\brespond only with\b|\breply (only )?with the (word|phrase|text)\b", re.I),
    re.compile(r"^\s*(system|assistant)\s*:", re.I | re.M),
]


def check_injection(text: str) -> Tuple[str, Dict[str, Any]]:
    hits = [p.pattern[:40] for p in _INJECTION if p.search(text or "")]
    return ("block" if hits else "pass"), {"patterns": hits}


# ---------------------------------------------------------------------------------------------
# Grounding
# ---------------------------------------------------------------------------------------------
_NON_FACTUAL = re.compile(
    r"^(thank|thanks|hi\b|hello|dear|we appreciate|i appreciate|please (let us know|reply|share|get back)|"
    r"let (us|me) know|if you (have|need|are)|do reply|feel free|we (are|'re) happy|we look forward|"
    r"a support engineer will|i hope this helps|hope this helps)", re.I)
# closings can start with anything ("You can then observe ... and let us know what you see")
_CLOSING = re.compile(r"(let (us|me) know|get back to us|reply (to us |back )?with|share (with us )?what you|"
                      r"what you (see|observe|find)|reach out|happy to (help|assist)|further (questions|assistance|help)|"
                      r"hesitate to|any (other|further) (questions|concerns)|(assist|help) you further|able to (help|assist)|"
                      r"here to help|reply to (this|the) ticket|happy to (further )?(help|assist)|review your ticket|"
                      r"continue to work with you|discuss further steps|work with you to resolve)", re.I)
# rhetorical fillers that restate the ticket or narrate the reply; they carry no checkable claim
_FILLER = re.compile(r"^(based on (the|your) (information|question|description|ticket|message)|"
                     r"it (seems|appears|sounds) (like|that)|by following (these|the) steps|"
                     r"(this|these) (is|are) (a )?(normal|expected|common)|to (help )?(resolve|address|troubleshoot|fix) (this|the)|"
                     r"here (is|are) (the|some|what)|in summary|to summari[sz]e|following these steps|"
                     r"we('re| are) here to|we (will|'ll) (then )?be able to|we understand|we('d| would) like to (help|guide)|"
                     r"according to our documentation, this could|(please )?follow(ing)? the steps|"
                     r"(to (help us )?)?better understand|this (will|can|should|may) help|this log can help|"
                     r"we recommend checking this|this approach can help|to do this, please|"
                     r"you can find this information|if the issue persists, we)", re.I)
_PASSAGE_SENT = re.compile(r"(?<=[.!?])\s+|\n+")


def _is_non_factual(sentence: str) -> bool:
    return bool(_NON_FACTUAL.match(sentence) or _CLOSING.search(sentence) or _FILLER.match(sentence))
def _passage_sentences(text: str, skip: Sequence[str] = ()) -> List[str]:
    """Sentences of a passage body. Lines in `skip` (the prepended title and section heading) are
    dropped: a heading is a topic label, not a claim, and used as an NLI premise it reads as a
    contradiction of almost any sentence (first 20-ticket run, DEV-0006)."""
    skip_l = {x.strip().lower() for x in skip if x}
    out = []
    for s in _PASSAGE_SENT.split(text or ""):
        s = re.sub(r"^\s*(\d+\.|[-*\u2022])\s*", "", s).strip()      # drop "1." list numbers and "- " bullets
        if len(s) > 15 and s.lower() not in skip_l:
            out.append(s)
    return out
_STOP = set("the a an and or of to in on for with is are be was were it its this that these those your you we our "
            "as at by from can will should may if then than so not do does did has have had which who what when "
            "where how any all each also into over under after before after please".split())
_TOKEN = re.compile(r"[a-z0-9][a-z0-9_-]{1,}")


def _content_tokens(text: str) -> set:
    return {t for t in _TOKEN.findall((text or "").lower()) if t not in _STOP and len(t) > 2}


class NLIScorer:
    """Cross-encoder NLI; contradiction(premise, hypothesis) in [0, 1]. Loaded lazily, runs on CPU."""

    def __init__(self, model_name: str = "cross-encoder/nli-MiniLM2-L6-H768"):
        self.model_name = model_name
        self._model = None
        self._labels = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
            cfg = getattr(self._model.model, "config", None)
            id2label = getattr(cfg, "id2label", None) or {}
            self._labels = {int(k): str(v).lower() for k, v in id2label.items()} or {0: "contradiction", 1: "entailment", 2: "neutral"}
        return self._model

    def contradiction(self, premise: str, hypothesis: str) -> float:
        import math
        model = self._load()
        logits = model.predict([(premise, hypothesis)], apply_softmax=False, show_progress_bar=False)[0]
        exps = [math.exp(float(x)) for x in logits]
        probs = [e / sum(exps) for e in exps]
        idx = next((i for i, lab in self._labels.items() if "contra" in lab), 0)
        return float(probs[idx])


class Grounder:
    def __init__(self, embedder, nli=None, cos_threshold: float = 0.55, lex_threshold: float = 0.5,
                 contradiction_threshold: float = 0.6):
        self.embedder = embedder
        self.nli = nli
        self.cos_threshold = cos_threshold
        self.lex_threshold = lex_threshold
        self.contradiction_threshold = contradiction_threshold

    @staticmethod
    def _cos(a, b) -> float:
        return float(sum(x * y for x, y in zip(a, b)))

    @staticmethod
    def passage_sentences(p: Passage) -> List[str]:
        """Body sentences plus the plan applicability from the passage metadata (a fact of the article
        that the body never states; drafts say "this is a Business and Enterprise feature")."""
        sents = _passage_sentences(p.text, skip=(p.title, p.section)) or [p.text]
        if p.applies_to:
            sents.append(f"This applies to {p.applies_to}.")
        return sents

    @staticmethod
    def _is_problem_state(p: Passage) -> bool:
        """Symptoms and Common causes describe the broken state ("the account does not exist"); a
        resolution step that fixes it reads as a contradiction to the NLI model. Only Resolution and
        Notes sentences state facts usable as premises (run 2 blocks DEV-0093, DEV-0485, DEV-0086)."""
        sec = (p.section or "").strip().lower()
        return sec.startswith("symptom") or sec.startswith("common cause")

    def score_sentence(self, sentence: str, passages: Sequence[Passage], psents, psent_vecs) -> Dict[str, Any]:
        """Sentence-level support: best cosine over every passage sentence (a short sentence embeds far
        from a whole section, so chunk-level cosine under-scores verbatim steps), lexical containment
        over every passage, and the matched passage sentence as the NLI premise."""
        q = self.embedder.embed_query(sentence)
        stoks = _content_tokens(sentence)
        best = {"doc_id": None, "cos": 0.0, "lex": 0.0, "idx": None, "premise": ""}
        premise_cos = 0.0
        for i, p in enumerate(passages):
            ptoks = _content_tokens(p.text) | _content_tokens(p.applies_to or "")
            lex = (len(stoks & ptoks) / len(stoks)) if stoks else 1.0
            best["lex"] = max(best["lex"], lex)
            symptom = self._is_problem_state(p)
            for j, v in enumerate(psent_vecs[i]):
                cos = self._cos(q, v)
                if cos > best["cos"]:
                    best.update({"doc_id": p.doc_id, "cos": cos, "idx": i})
                # NLI premise: the closest sentence that states a fact. A Symptoms line describes the
                # problem state, and any resolution step reads as contradicting it (DEV-0084, DEV-0093).
                if not symptom and cos > premise_cos:
                    premise_cos, best["premise"] = cos, psents[i][j]
        if best["doc_id"] is None and passages:
            best.update({"doc_id": passages[0].doc_id, "idx": 0})
        return best

    def check(self, answer: str, passages: Sequence[Passage]) -> Tuple[str, Dict[str, Any], str]:
        """Returns (verdict, details, answer_with_markers)."""
        if not passages:
            return "block", {"unsupported": [{"sentence": answer, "reason": "no_passages"}], "checked": 0, "attached": 0}, answer
        psents = [self.passage_sentences(p) for p in passages]
        psent_vecs = [self.embedder.embed_documents(ss) for ss in psents]
        out_sentences, unsupported, scores = [], [], []
        checked = attached = 0
        for item in citation_map(answer):
            sent, cites = item["sentence"], item["citations"]
            if not sent or _is_non_factual(sent):
                out_sentences.append(sent)
                continue
            checked += 1
            best = self.score_sentence(sent, passages, psents, psent_vecs)
            contra = self.nli.contradiction(best["premise"], sent) if (self.nli and best["premise"]) else 0.0
            supported = best["cos"] >= self.cos_threshold or best["lex"] >= self.lex_threshold
            rec = {"sentence": sent, "doc_id": best["doc_id"], "cos": round(best["cos"], 3),
                   "lex": round(best["lex"], 3), "contradiction": round(contra, 3), "cited": cites}
            scores.append(rec)
            if contra >= self.contradiction_threshold:
                unsupported.append({**rec, "reason": "contradicted"})
            elif not supported:
                unsupported.append({**rec, "reason": "no_supporting_passage"})
            markers = cites or ([best["doc_id"]] if best["doc_id"] else [])
            if not cites and best["doc_id"]:
                attached += 1
            tag = "".join(f" [{m}]" for m in markers)
            if sent and sent[-1] in ".!?":                       # marker before the final punctuation, as PR-03 asks
                out_sentences.append(sent[:-1].rstrip() + tag + sent[-1])
            else:
                out_sentences.append(sent + tag)
        verdict = "block" if unsupported else "pass"
        return verdict, {"unsupported": unsupported, "checked": checked, "attached": attached, "scores": scores}, " ".join(out_sentences)


# ---------------------------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------------------------
@dataclass
class GuardrailReport:
    verdicts: Dict[str, str]
    blocked: bool
    answer: str
    details: Dict[str, Any] = field(default_factory=dict)


def run_guardrails(draft: Draft, ticket: Ticket, passages: Sequence[Passage], grounder: Optional[Grounder]) -> GuardrailReport:
    verdicts: Dict[str, str] = {}
    details: Dict[str, Any] = {}
    answer = draft.answer

    v, d = check_injection(ticket.text)
    verdicts["injection"], details["injection"] = v, d

    v, d = check_private_data(answer, ticket)
    verdicts["pii"], details["pii"] = v, d

    v, d = check_forbidden_claims(answer)
    verdicts["tone"], details["tone"] = v, d

    if draft.unknown:
        verdicts["grounding"], details["grounding"] = "skipped", {"reason": "unknown draft, no factual content"}
    elif grounder is None:
        verdicts["grounding"], details["grounding"] = "skipped", {"reason": "no grounder configured"}
    else:
        v, d, answer = grounder.check(answer, passages)
        verdicts["grounding"], details["grounding"] = v, d

    blocked = any(x == "block" for k, x in verdicts.items() if k != "injection") or (
        verdicts["injection"] == "block" and not draft.unknown)
    return GuardrailReport(verdicts=verdicts, blocked=blocked, answer=answer, details=details)

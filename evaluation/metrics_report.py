"""Metrics report (A10): the four groups the Build Specification section 04 requires, computed by code.

Volume     processed, auto_responded, escalated, blocked
Business   first contact resolution, escalation rate, response time mean/median (+ Wilson 95% CI)
Technical  per-class precision/recall (sklearn), retrieval hit rate, routing accuracy, citation accuracy,
           latency median/p95
Governance decisions logged, guardrail activations by type, private data detections, failed tickets,
           must_not_auto_respond violations, calibration table (Evaluation Framework section 3)
Segments   auto-respond rate and routing accuracy by tier, region, fluency, ticket length (fairness audit)

Quality metrics use only rows that carry labels; completion is reported separately (failed_tickets).
"""
from __future__ import annotations

import math
import statistics as st
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Sequence, Tuple


def wilson_interval(successes: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """95% Wilson score interval for a proportion; (0, 0) when n == 0."""
    if n <= 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def _rate(successes: int, n: int) -> Dict[str, Any]:
    lo, hi = wilson_interval(successes, n)
    return {"value": (successes / n) if n else None, "n": n, "ci95": [lo, hi]}


def _pct(values: Sequence[float], q: float) -> Optional[float]:
    if not values:
        return None
    s = sorted(values)
    return s[min(len(s) - 1, max(0, int(math.ceil(q * len(s))) - 1))]


def calibration_table(pairs: Sequence[Tuple[float, bool]], bands: int = 5, min_n: int = 20) -> Dict[str, Any]:
    """Evaluation Framework section 3: bin by stated confidence, compare to observed accuracy; ECE weighted by size.
    The 5-point test is judged on bins with at least `min_n` tickets; a two-ticket bin cannot show a
    calibration gap (its Wilson interval spans most of [0, 1]) and is reported, not judged."""
    rows: List[Dict[str, Any]] = []
    ece, total = 0.0, len(pairs)
    for i in range(bands):
        low, high = i / bands, (i + 1) / bands
        group = [(c, ok) for c, ok in pairs if low <= c < high or (i == bands - 1 and c == 1.0)]
        if not group:
            continue
        stated = sum(c for c, _ in group) / len(group)
        observed = sum(1 for _, ok in group if ok) / len(group)
        rows.append({"band": [low, high], "n": len(group), "stated": stated, "observed": observed,
                     "gap": stated - observed, "evaluable": len(group) >= min_n})
        ece += abs(stated - observed) * len(group) / total
    judged = [r for r in rows if r["evaluable"]]
    within5 = all(abs(r["gap"]) <= 0.05 for r in judged) if judged else None
    return {"bins": rows, "ece": ece if total else None, "all_bins_within_5_points": within5, "n": total, "min_n": min_n}


def _route_of(r: Dict[str, Any]) -> str:
    return "auto_respond" if r["action"] == "auto_respond" else "escalate"


def _confusion(y_true, y_pred) -> Dict[str, Dict[str, int]]:
    m: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for t, p in zip(y_true, y_pred):
        m[t][p] += 1
    return {t: dict(v) for t, v in m.items()}


def _segment(records: List[Dict[str, Any]], key_fn) -> Dict[str, Any]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in records:
        groups[key_fn(r)].append(r)
    out = {}
    for k, rs in sorted(groups.items()):
        lab = [r for r in rs if r.get("labels")]
        out[k] = {
            "n": len(rs),
            "auto_respond_rate": sum(1 for r in rs if r["action"] == "auto_respond") / len(rs),
            "routing_accuracy": (sum(1 for r in lab if _route_of(r) == r["labels"].get("expected_route")) / len(lab)) if lab else None,
            "intent_accuracy": (sum(1 for r in lab if r["intent"] == r["labels"].get("intent")) / len(lab)) if lab else None,
        }
    return out


def compute_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    n = len(records)
    by_action = Counter(r["action"] for r in records)
    auto = by_action.get("auto_respond", 0)
    esc = by_action.get("escalate", 0)
    blocked = by_action.get("block", 0)
    lat = [float(r.get("latency_ms") or 0.0) for r in records]
    labelled = [r for r in records if r.get("labels")]

    # technical: classification
    cls: Dict[str, Any] = {"labelled": len(labelled), "per_class": {}, "macro_precision": None,
                           "macro_recall": None, "accuracy": None, "urgency_accuracy": None}
    if labelled:
        from sklearn.metrics import classification_report
        y_true = [r["labels"]["intent"] for r in labelled]
        y_pred = [r["intent"] for r in labelled]
        rep = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
        cls["per_class"] = {
            k: {"precision": v["precision"], "recall": v["recall"], "f1": v["f1-score"], "support": v["support"]}
            for k, v in rep.items() if isinstance(v, dict) and k not in ("macro avg", "weighted avg")
        }
        cls["macro_precision"] = rep["macro avg"]["precision"]
        cls["macro_recall"] = rep["macro avg"]["recall"]
        cls["accuracy"] = rep.get("accuracy")
        cls["urgency_accuracy"] = sum(1 for r in labelled if r["urgency"] == r["labels"].get("urgency")) / len(labelled)
        cls["confusion"] = _confusion(y_true, y_pred)

    # technical: retrieval, routing, citations
    answerable = [r for r in labelled if r["labels"].get("answerable_from_docs")]
    hits = sum(1 for r in answerable
               if set(d["doc_id"] for d in r.get("retrieved", [])) & set(r["labels"].get("expected_doc_ids", [])))
    routing_ok = sum(1 for r in labelled if _route_of(r) == r["labels"].get("expected_route"))
    cited = [r for r in records if r.get("citations")]
    cite_ok = sum(1 for r in cited if set(r["citations"]) <= set(d["doc_id"] for d in r.get("retrieved", [])))
    cite_expected = [r for r in cited if r.get("labels")]
    cite_hit = sum(1 for r in cite_expected if set(r["citations"]) & set(r["labels"].get("expected_doc_ids", [])))

    # governance
    guard_counts: Counter = Counter()
    for r in records:
        for name, verdict in (r.get("guardrails") or {}).items():
            if verdict == "block":
                guard_counts[name] += 1
    violations = sum(1 for r in labelled if r["labels"].get("must_not_auto_respond") and r["action"] == "auto_respond")
    pairs = [(float(r["confidence"]), r["intent"] == r["labels"].get("intent")) for r in labelled]

    # segments (fairness audit inputs)
    segments = {
        "tier": _segment(records, lambda r: r.get("tier") or "unknown"),
        "region": _segment(records, lambda r: r.get("region") or "unknown"),
        "fluency": _segment(records, lambda r: r.get("fluency") or "unknown"),
        "ticket_length": _segment(records, lambda r: "short" if (r.get("text_len") or 0) < 120 else "long"),
        "channel": _segment(records, lambda r: r.get("channel") or "unknown"),
    }
    seg_var = {}
    for name, groups in segments.items():
        vals = [g["routing_accuracy"] for g in groups.values() if g["routing_accuracy"] is not None]
        seg_var[name] = (max(vals) - min(vals)) if len(vals) > 1 else None

    return {
        "volume": {"processed": n, "auto_responded": auto, "escalated": esc, "blocked": blocked},
        "business": {
            "first_contact_resolution": _rate(auto, n),
            "escalation_rate": _rate(esc + blocked, n),
            "response_time_ms_mean": st.mean(lat) if lat else None,
            "response_time_ms_median": st.median(lat) if lat else None,
            "response_time_ms_p95": _pct(lat, 0.95),
            "note": "FCR = auto-responded and not blocked; repeat contacts are not observable in an offline run.",
        },
        "technical": {
            "classification": cls,
            "retrieval_hit_rate": (hits / len(answerable)) if answerable else None,
            "retrieval_hit_rate_n": len(answerable),
            "routing_accuracy": (routing_ok / len(labelled)) if labelled else None,
            "citation_resolves_to_retrieved": (cite_ok / len(cited)) if cited else None,
            "citation_hits_expected_doc": (cite_hit / len(cite_expected)) if cite_expected else None,
            "latency_ms_median": st.median(lat) if lat else None,
            "latency_ms_p95": _pct(lat, 0.95),
        },
        "governance": {
            "decisions_logged": n,
            "guardrail_activations": dict(guard_counts),
            "private_data_detections": guard_counts.get("pii", 0),
            "failed_tickets": sum(1 for r in records if r.get("error")),
            "instruction_like_flagged": sum(1 for r in records if r.get("instruction_like")),
            "must_not_auto_respond_violations": violations,
            "calibration": calibration_table(pairs) if pairs else {"bins": [], "ece": None, "n": 0},
        },
        "segments": segments,
        "segment_variation_routing_accuracy": seg_var,
    }


def _pc(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{100 * x:.1f}%"


def _ms(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{x:.0f} ms"


def _reconcile_line(rec: Optional[Dict[str, Any]]) -> str:
    if not rec:
        return "- Decision log reconciliation: not available (pipeline exposes no decision log)"
    state = "complete" if rec.get("complete") else "INCOMPLETE"
    return (f"- Decision log reconciliation: {state}; {rec.get('rows_total')} rows for {rec.get('tickets')} tickets; "
            f"routing rows {rec.get('tickets_with_routing')}/{rec.get('tickets')}, validation rows "
            f"{rec.get('tickets_with_validation')}/{rec.get('tickets')}")


def render_summary(m: Dict[str, Any], meta: Dict[str, Any]) -> str:
    fcr, esc = m["business"]["first_contact_resolution"], m["business"]["escalation_rate"]
    cls = m["technical"]["classification"]
    g = m["governance"]
    lines = [
        "# Run summary",
        "",
        f"- Input: `{meta['input']}`; tickets: {meta['tickets']}; started: {meta['started_at']}; duration: {meta.get('duration_s', 0):.1f}s",
        f"- System version: {meta.get('version', 'unknown')}; thresholds: confidence {meta.get('confidence_threshold')}, retrieval {meta.get('retrieval_threshold')}; run count on this input: {meta.get('run_count_on_this_input')}",
        "",
        "## Volume",
        f"processed {m['volume']['processed']}, auto-responded {m['volume']['auto_responded']}, escalated {m['volume']['escalated']}, blocked {m['volume']['blocked']}",
        "",
        "## Business",
        f"- First contact resolution: {_pc(fcr['value'])} (95% CI {_pc(fcr['ci95'][0])} to {_pc(fcr['ci95'][1])})",
        f"- Escalation rate: {_pc(esc['value'])} (95% CI {_pc(esc['ci95'][0])} to {_pc(esc['ci95'][1])})",
        f"- Response time: mean {_ms(m['business']['response_time_ms_mean'])}, median {_ms(m['business']['response_time_ms_median'])}",
        "",
        "## Technical",
        f"- Intent macro precision {_pc(cls['macro_precision'])}, macro recall {_pc(cls['macro_recall'])}, accuracy {_pc(cls['accuracy'])} over {cls['labelled']} labelled tickets",
        f"- Retrieval hit rate {_pc(m['technical']['retrieval_hit_rate'])} (n={m['technical']['retrieval_hit_rate_n']}); routing accuracy {_pc(m['technical']['routing_accuracy'])}",
        f"- Citations resolve to retrieved passages {_pc(m['technical']['citation_resolves_to_retrieved'])}; cite the expected article {_pc(m['technical']['citation_hits_expected_doc'])}",
        f"- Latency median {_ms(m['technical']['latency_ms_median'])}, p95 {_ms(m['technical']['latency_ms_p95'])}",
        "",
        "## Governance",
        f"- Decisions logged {g['decisions_logged']}, failed tickets {g['failed_tickets']}, guardrail blocks {g['guardrail_activations']}",
        f"- Private data detections {g['private_data_detections']}, must-not-auto-respond violations {g['must_not_auto_respond_violations']}",
        f"- Calibration ECE {g['calibration'].get('ece')}, all bins with n >= {g['calibration'].get('min_n')} within 5 points: {g['calibration'].get('all_bins_within_5_points')}",
        _reconcile_line(g.get("decision_log")),
        "",
        "## Segment variation in routing accuracy (percentage points)",
    ]
    for k, v in m["segment_variation_routing_accuracy"].items():
        lines.append(f"- {k}: {'n/a' if v is None else f'{100 * v:.1f}'}")
    return "\n".join(lines) + "\n"

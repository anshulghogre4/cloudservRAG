"""B-06 / T-05: classifier evaluation on the DEVELOPMENT set and calibration fitting.

Produces (in --output):
  classify_check.json    per-class precision/recall/F1 (sklearn), confusion, kNN leave-one-body-out accuracy,
                         LLM/kNN agreement, calibration tables for raw, kNN and combined scores
  calibration.json       Platt parameters fitted on the combined score (used by src/calibration.py)
  classify_rows.jsonl    one row per ticket with all signals (used by B-07 to choose the routing threshold)

Run:  python -m evaluation.classify_check --input Docs/Capstone_Project/05_Datasets/development_tickets.json
      add --limit 20 for a smoke test, --no-llm for the offline kNN part only, --rpm 20 to respect free-tier limits.
Refuses to run on the validation set.
"""
from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path

from src.calibration import (binned, cross_validated_binned_pairs, cross_validated_pairs, fit_binned,
                             fit_platt, platt)
from src.classify import KNNClassifier, classify, combine
from src.config import load_settings
from src.ingest import load_tickets
from src.llm import LLMClient
from src.retrieve import SentenceTransformerEmbedder
from evaluation.metrics_report import calibration_table

ROOT = Path(__file__).resolve().parents[1]
log = logging.getLogger("classify_check")


def _confusion(y_true, y_pred):
    """Nested dict {true: {predicted: count}} with every class present, for the report appendix."""
    from src.classify import INTENTS
    m = {t: {p: 0 for p in INTENTS} for t in INTENTS}
    for t, p in zip(y_true, y_pred):
        m.setdefault(t, {}).setdefault(p, 0)
        m[t][p] += 1
    return m


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", default=str(ROOT / "evaluation" / "results"))
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--rpm", type=float, default=20.0, help="max provider calls per minute (0 = unlimited)")
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--loo-sim", type=float, default=0.95, help="strict check also drops neighbours with cosine >= this")
    ap.add_argument("--C", type=float, default=1.0, help="Platt regularisation (smaller = smoother)")
    a = ap.parse_args(argv)
    if "validation" in Path(a.input).name.lower():
        raise SystemExit("refusing: the validation set is reserved for the gate run")
    logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(message)s")

    settings = load_settings()
    out = Path(a.output); out.mkdir(parents=True, exist_ok=True)
    tickets = load_tickets(a.input)
    labelled = [t for t in tickets if t.raw.get("labels", {}).get("intent")]
    sample = labelled[: a.limit] if a.limit else labelled
    emb = SentenceTransformerEmbedder(settings.embedding_model)

    # ---- kNN, leave-one-body-out over the whole labelled set (offline) -----------------------
    knn = KNNClassifier(emb, k=a.k).fit(labelled)
    knn_rows = []
    for t in labelled:
        best, p = knn.predict(t.text, exclude_text=t.text)
        u, _ = knn.predict_urgency(t.text, exclude_text=t.text)
        strict, sp = knn.predict(t.text, exclude_text=t.text, exclude_sim_above=a.loo_sim)
        knn_rows.append({"ticket_id": t.ticket_id, "true": t.raw["labels"]["intent"], "knn": best, "knn_p": p,
                         "knn_strict": strict, "knn_strict_p": sp,
                         "true_urgency": t.raw["labels"].get("urgency"), "knn_urgency": u})
    knn_acc = sum(1 for r in knn_rows if r["knn"] == r["true"]) / len(knn_rows)
    knn_strict_acc = sum(1 for r in knn_rows if r["knn_strict"] == r["true"]) / len(knn_rows)
    knn_urg_acc = sum(1 for r in knn_rows if r["knn_urgency"] == r["true_urgency"]) / len(knn_rows)
    knn_cal = calibration_table([(r["knn_p"], r["knn"] == r["true"]) for r in knn_rows])
    log.info("kNN accuracy: leave-one-body-out %.3f | also excluding near-duplicates (sim>=%.2f) %.3f | n=%d",
             knn_acc, a.loo_sim, knn_strict_acc, len(knn_rows))

    report = {"input": a.input, "n_labelled": len(labelled), "knn_k": a.k,
              "knn_loo_accuracy": knn_acc, "knn_loo_strict_accuracy": knn_strict_acc, "loo_sim": a.loo_sim,
              "knn_urgency_loo_accuracy": knn_urg_acc, "knn_calibration": knn_cal}

    # ---- LLM (PR-02) over the sample, with the kNN signal fitted on everything else -----------
    if not a.no_llm:
        llm = LLMClient(settings)
        min_gap = 60.0 / a.rpm if a.rpm > 0 else 0.0
        rows = []
        last_call = 0.0
        for i, t in enumerate(sample, 1):
            # leave-one-body-out for the kNN signal used inside classify()
            probs = knn.predict_proba(t.text, exclude_text=t.text)
            knn_intent = max(probs, key=probs.get) if probs else None
            before = llm.calls
            wait = min_gap - (time.time() - last_call)
            if wait > 0 and before == llm.calls:
                time.sleep(wait)
            c = classify(t, llm)          # LLM only; kNN combined below with the LOO probabilities
            if llm.calls != before:
                last_call = time.time()
            true = t.raw["labels"]["intent"]
            agree = (knn_intent == c.intent) if (knn_intent and not c.fallback) else None
            final = knn_intent or c.intent                      # same policy as classify() with a kNN
            knn_share = probs.get(final) if probs else None
            score = combine(c.raw_confidence, knn_share, agree) if not c.fallback else 0.0
            rows.append({"ticket_id": t.ticket_id, "true": true, "true_urgency": t.raw["labels"].get("urgency"),
                         "llm": c.intent, "final": final, "urgency": c.urgency, "raw_conf": c.raw_confidence,
                         "fallback": c.fallback, "error": c.error, "knn": knn_intent, "knn_p": knn_share,
                         "agree": agree, "combined": score, "instruction_like": c.instruction_like,
                         "expected_route": t.raw["labels"].get("expected_route"),
                         "must_not_auto": t.raw["labels"].get("must_not_auto_respond")})
            if i % 25 == 0:
                log.info("progress %d/%d (calls %d, cache hits %d)", i, len(sample), llm.calls, llm.cache_hits)
        (out / "classify_rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

        from sklearn.metrics import classification_report
        ok = [r for r in rows if not r["fallback"]]
        y_true = [r["true"] for r in rows]; y_pred = [r["llm"] for r in rows]
        rep = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
        rep_final = classification_report(y_true, [r["final"] for r in rows], output_dict=True, zero_division=0)
        correct = [r["final"] == r["true"] for r in rows]      # calibration targets the intent actually used
        cal_raw = calibration_table([(r["raw_conf"], c) for r, c in zip(rows, correct)])
        cal_comb = calibration_table([(r["combined"], c) for r, c in zip(rows, correct)])
        scores = [r["combined"] for r in rows]
        fit = fit_platt(scores, correct, C=a.C)
        cal_after = cal_cv = None
        if fit.get("method") == "platt":
            f = platt(fit["a"], fit["b"])
            cal_after = calibration_table([(f(s), c) for s, c in zip(scores, correct)])
            cal_cv = calibration_table(cross_validated_pairs(scores, correct, folds=5, C=a.C))
        fit_b = fit_binned(scores, correct)
        g = binned(fit_b["edges"], fit_b["values"])
        cal_b = calibration_table([(g(s), c) for s, c in zip(scores, correct)])
        cal_b_cv = calibration_table(cross_validated_binned_pairs(scores, correct, folds=5))
        chosen = {**fit_b, "fitted_on": a.input, "date": time.strftime("%Y-%m-%d"),
                  "score": "0.5*knn_share + 0.5*agree", "alternative_platt": fit}
        (out / "calibration.json").write_text(json.dumps(chosen, indent=2), encoding="utf-8")
        report.update({
            "n_llm": len(rows), "llm_fallbacks": sum(1 for r in rows if r["fallback"]),
            "llm_accuracy": sum(1 for r in rows if r["llm"] == r["true"]) / len(rows),
            "llm_macro_precision": rep["macro avg"]["precision"], "llm_macro_recall": rep["macro avg"]["recall"],
            "llm_macro_f1": rep["macro avg"]["f1-score"], "llm_weighted_f1": rep["weighted avg"]["f1-score"],
            "final_accuracy": sum(correct) / len(rows),
            "final_macro_precision": rep_final["macro avg"]["precision"],
            "final_macro_recall": rep_final["macro avg"]["recall"],
            "final_macro_f1": rep_final["macro avg"]["f1-score"],
            "final_weighted_f1": rep_final["weighted avg"]["f1-score"],
            "final_per_class": {k: v for k, v in rep_final.items() if isinstance(v, dict)},
            "final_confusion": _confusion(y_true, [r["final"] for r in rows]),
            "llm_confusion": _confusion(y_true, y_pred),
            "urgency_accuracy": sum(1 for r in rows if r["urgency"] == r["true_urgency"]) / len(rows),
            "per_class": {k: v for k, v in rep.items() if isinstance(v, dict)},
            "agreement_rate": sum(1 for r in ok if r["agree"]) / max(1, len(ok)),
            "accuracy_when_agree": (sum(1 for r in ok if r["agree"] and r["llm"] == r["true"]) / max(1, sum(1 for r in ok if r["agree"]))),
            "accuracy_when_disagree": (sum(1 for r in ok if r["agree"] is False and r["llm"] == r["true"]) / max(1, sum(1 for r in ok if r["agree"] is False))),
            "calibration_raw": cal_raw, "calibration_combined": cal_comb, "calibration_after_platt": cal_after,
            "calibration_cross_validated": cal_cv,
            "calibration_binned": cal_b, "calibration_binned_cross_validated": cal_b_cv, "binned": fit_b,
            "platt": fit, "provider_calls": llm.calls, "cache_hits": llm.cache_hits,
        })
        log.info("LLM accuracy %.3f | final accuracy %.3f macro-precision %.3f | agree %.2f | ECE raw %.3f combined %.3f after %.3f",
                 report["llm_accuracy"], report["final_accuracy"], report["final_macro_precision"], report["agreement_rate"],
                 cal_raw["ece"] or 0, cal_comb["ece"] or 0, (cal_after or {}).get("ece") or 0)

    (out / "classify_check.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if not isinstance(v, dict)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

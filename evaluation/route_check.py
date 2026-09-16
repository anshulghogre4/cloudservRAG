"""B-07: choose the routing threshold from DEVELOPMENT data and measure routing against its ceiling.

Inputs: evaluation/results/classify_rows.jsonl (from classify_check), the fitted calibrator, the
retrieval index. For every development ticket it replays the decision table at a sweep of
thresholds and reports auto rate, routing accuracy, unsafe auto-answers and expected cost.

Cost rule (selective classification): with calibrated P(correct), escalate when
P < 1 - c_escalate / c_wrong. Marcus: an escalation costs about 4x a resolved ticket; a wrong
answer is worse than waiting. The sweep over c_wrong / c_escalate shows how the threshold moves.

Label ceiling: 35 groups of identical ticket bodies carry both routes in the labels, so no
text-only router can be right on all of them. The ceiling is reported next to the accuracy.

Run:  python -m evaluation.route_check --input Docs/Capstone_Project/05_Datasets/development_tickets.json
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from src.calibration import load_calibrator
from src.classify import Classification
from src.config import load_settings
from src.ingest import load_tickets
from src.retrieve import Retriever, SentenceTransformerEmbedder
from src.route import route

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "Docs" / "Capstone_Project" / "05_Datasets" / "documentation.json"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--rows", default=str(ROOT / "evaluation" / "results" / "classify_rows.jsonl"))
    ap.add_argument("--output", default=str(ROOT / "evaluation" / "results" / "route_check.json"))
    a = ap.parse_args(argv)
    if "validation" in Path(a.input).name.lower():
        raise SystemExit("refusing: the validation set is reserved for the gate run")

    settings = load_settings()
    cal = load_calibrator() or (lambda s: s)
    tickets = {t.ticket_id: t for t in load_tickets(a.input)}
    rows = [json.loads(l) for l in Path(a.rows).read_text(encoding="utf-8").splitlines()]
    docs = json.loads(DOCS.read_text(encoding="utf-8"))
    retr = Retriever(SentenceTransformerEmbedder(settings.embedding_model), settings.chroma_path)
    retr.ensure_built(docs)

    # retrieval per ticket, once; neighbour answerability leave-one-body-out, once
    from src.classify import KNNClassifier
    knn = KNNClassifier(retr.embedder, k=7).fit(list(tickets.values()))
    passages, answerable = {}, {}
    for r in rows:
        t = tickets[r["ticket_id"]]
        passages[r["ticket_id"]] = retr.search(t.text, k=settings.retrieval_top_k, threshold=settings.retrieval_threshold)
        answerable[r["ticket_id"]] = knn.predict_answerable(t.text, exclude_text=t.text)

    # label ceiling from duplicate bodies
    groups = defaultdict(list)
    for r in rows:
        groups[tickets[r["ticket_id"]].text.strip().lower()].append(r["expected_route"])
    ceiling = sum(max(g.count("auto_respond"), g.count("escalate")) for g in groups.values()) / len(rows)

    def replay(thr, plan_rule=False, floor=0.5):
        s = load_settings(); s.confidence_threshold = thr; s.plan_rule = plan_rule; s.answerable_floor = floor
        out = []
        for r in rows:
            t = tickets[r["ticket_id"]]
            conf = cal(r["combined"]) if not r["fallback"] else 0.0
            c = Classification(intent=r["final"], urgency=r["urgency"], confidence=conf, raw_confidence=r["raw_conf"],
                               alternatives=[], instruction_like=bool(r["instruction_like"]), reason="replay",
                               fallback=bool(r["fallback"]), knn_answerable=answerable[r["ticket_id"]])
            rt = route(c, passages[r["ticket_id"]], t.customer.tier, s)
            labels = t.raw["labels"]
            out.append({"action": rt.action, "rule": rt.rule, "expected": r["expected_route"],
                        "must_not_auto": labels["must_not_auto_respond"], "answerable": labels["answerable_from_docs"],
                        "intent_ok": r["final"] == r["true"]})
        return out

    # four router variants at the chosen threshold
    variants = []
    for name, plan_rule, floor in (("base", False, 0.0), ("plan_rule", True, 0.0),
                                   ("answerable_floor", False, 0.5), ("both", True, 0.5)):
        d = replay(0.8, plan_rule, floor)
        n = len(d); auto = [x for x in d if x["action"] == "auto_respond"]
        variants.append({"variant": name, "auto_rate": len(auto) / n,
                         "routing_accuracy": sum(1 for x in d if x["action"] == x["expected"]) / n,
                         "auto_on_not_answerable": sum(1 for x in auto if not x["answerable"]),
                         "escalated_but_expected_auto": sum(1 for x in d if x["action"] == "escalate" and x["expected"] == "auto_respond"),
                         "rules": {k: sum(1 for x in d if x["rule"] == k) for k in sorted({x["rule"] for x in d})}})
        print("variant", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in variants[-1].items()})

    sweep = []
    for thr in [0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99]:
        d = replay(thr)
        n = len(d)
        auto = [x for x in d if x["action"] == "auto_respond"]
        sweep.append({
            "threshold": thr,
            "auto_rate": len(auto) / n,
            "routing_accuracy": sum(1 for x in d if x["action"] == x["expected"]) / n,
            "unsafe_auto_must_not": sum(1 for x in auto if x["must_not_auto"]),
            "auto_on_not_answerable": sum(1 for x in auto if not x["answerable"]),
            "auto_with_wrong_intent": sum(1 for x in auto if not x["intent_ok"]),
            "escalated_but_expected_auto": sum(1 for x in d if x["action"] == "escalate" and x["expected"] == "auto_respond"),
            "rules": {k: sum(1 for x in d if x["rule"] == k) for k in sorted({x["rule"] for x in d})},
        })
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in sweep[-1].items() if k != "rules"})
    print("rules at 0.80:", next(s["rules"] for s in sweep if s["threshold"] == 0.8))
    print(f"routing accuracy ceiling from duplicate-body label conflicts: {ceiling:.3f}")

    # cost rule: threshold = 1 - c_esc / c_wrong, with c_esc = 4 (Marcus) and c_wrong swept
    cost_table = []
    for ratio in (1.5, 2, 3, 4, 5, 8, 10):
        thr = 1 - 1 / ratio
        d = replay(thr)
        cost = sum(4 if x["action"] == "escalate" else (ratio * 4 if not x["intent_ok"] else 1) for x in d)
        cost_table.append({"c_wrong_over_c_escalate": ratio, "implied_threshold": round(thr, 3), "expected_cost": cost,
                           "auto_rate": sum(1 for x in d if x["action"] == "auto_respond") / len(d)})
        print(cost_table[-1])

    Path(a.output).write_text(json.dumps({"variants": variants, "sweep": sweep, "ceiling": ceiling,
                                          "cost_table": cost_table, "n": len(rows)}, indent=2), encoding="utf-8")
    print("written", a.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

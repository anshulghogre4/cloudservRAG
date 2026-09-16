"""Fairness audit (B-14, NFR-06, Governance Framework section 3).

Segments a run's results and compares outcomes across segments with confidence intervals, in the
shape of the Governance Framework table: tickets in segment, resolution rate, quality score,
variation from best. The Explanation column is left for the author; the script prints the facts
that explain a gap (share labelled escalate, share with no passage above the threshold, mean
length) rather than an interpretation.

Definitions (the same as evaluation/metrics_report.py, so the audit and the metrics report agree):
- resolution rate: auto-responded and not blocked, the report's first-contact-resolution proxy
- quality score: routing accuracy against the labels (decision matches expected_route)
- ticket length: short when the normalised text is under 120 characters
- variation from best: best segment's quality in the group minus this segment's, in points
- "CI overlaps best": whether this segment's 95% Wilson interval overlaps the best segment's;
  a gap whose intervals overlap is not evidence of unfair treatment at this sample size

Usage:
    python -m evaluation.fairness_audit --results evaluation/results/2026-09-16_validation/results.jsonl
        [--results evaluation/results/2026-09-16_dev_full/results.jsonl] --output evaluation/results/fairness_audit
"""
from __future__ import annotations

import argparse
import json
import statistics as st
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from evaluation.metrics_report import wilson_interval

ROOT = Path(__file__).resolve().parents[1]
SHORT_CHARS = 120

GROUPS = {
    "tier": lambda r: r.get("tier") or "unknown",
    "fluency": lambda r: r.get("fluency") or "unknown",
    "ticket_length": lambda r: "short" if (r.get("text_len") or 0) < SHORT_CHARS else "long",
    "region": lambda r: r.get("region") or "unknown",
    "channel": lambda r: r.get("channel") or "unknown",
}
LABELS = {  # Governance table wording
    ("tier", "enterprise"): "Enterprise customers", ("tier", "business"): "Business customers",
    ("tier", "standard"): "Standard customers", ("fluency", "fluent"): "Tickets in fluent English",
    ("fluency", "non_fluent"): "Tickets in non-fluent English", ("ticket_length", "short"): "Short tickets (< 120 chars)",
    ("ticket_length", "long"): "Long or complex tickets",
}


def _ci(k: int, n: int) -> Dict[str, Any]:
    lo, hi = wilson_interval(k, n)
    return {"rate": (k / n) if n else None, "n": n, "ci": [round(lo, 4), round(hi, 4)]}


def _segment(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    n = len(records)
    auto = sum(1 for r in records if r.get("action") == "auto_respond")
    labelled = [r for r in records if r.get("labels")]
    correct = sum(1 for r in labelled
                  if ("auto_respond" if r["action"] == "auto_respond" else "escalate") == r["labels"].get("expected_route"))
    answerable = [r for r in labelled if r["labels"].get("answerable_from_docs")]
    hits = sum(1 for r in answerable
               if set(d["doc_id"] for d in r.get("retrieved", [])) & set(r["labels"].get("expected_doc_ids", [])))
    return {
        "tickets": n,
        "resolution": _ci(auto, n),
        "quality": _ci(correct, len(labelled)),
        "retrieval_hit": _ci(hits, len(answerable)),
        "blocked": _ci(sum(1 for r in records if r.get("action") == "block"), n),
        "facts": {
            "share_labelled_escalate": round(sum(1 for r in labelled if r["labels"].get("expected_route") != "auto_respond") / len(labelled), 3) if labelled else None,
            "share_no_passage": round(sum(1 for r in records if not r.get("retrieved")) / n, 3) if n else None,
            "mean_text_len": round(st.mean(r.get("text_len") or 0 for r in records), 1) if n else None,
            "mean_confidence": round(st.mean(float(r.get("confidence") or 0.0) for r in records), 3) if n else None,
        },
    }


def audit(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"tickets": len(records), "groups": {}}
    for group, key in GROUPS.items():
        buckets: Dict[str, List[Dict[str, Any]]] = {}
        for r in records:
            buckets.setdefault(key(r), []).append(r)
        segs = {name: _segment(rows) for name, rows in sorted(buckets.items())}
        scored = {k: v for k, v in segs.items() if v["quality"]["rate"] is not None}
        best_name = max(scored, key=lambda k: scored[k]["quality"]["rate"]) if scored else None
        best = scored[best_name] if best_name else None
        for name, seg in segs.items():
            q = seg["quality"]
            if best and q["rate"] is not None:
                seg["variation_from_best_pts"] = round((best["quality"]["rate"] - q["rate"]) * 100, 1)
                seg["ci_overlaps_best"] = q["ci"][1] >= best["quality"]["ci"][0]
            else:
                seg["variation_from_best_pts"], seg["ci_overlaps_best"] = None, None
            seg["label"] = LABELS.get((group, name), f"{group}: {name}")
        rates = [v["quality"]["rate"] for v in scored.values()]
        out["groups"][group] = {"best": best_name, "max_variation_pts": round((max(rates) - min(rates)) * 100, 1) if rates else None,
                                "within_5_points": (max(rates) - min(rates)) <= 0.05 if rates else None, "segments": segs}
    return out


def _pc(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{x * 100:.1f}%"


def render(name: str, a: Dict[str, Any]) -> str:
    lines = [f"## Fairness audit: {name} ({a['tickets']} tickets)", "",
             "Resolution rate = auto-responded and not blocked; quality score = routing accuracy against the labels; "
             "95% Wilson intervals; variation = best segment in the group minus this segment. "
             "The Explanation column is for the author.", ""]
    for group, g in a["groups"].items():
        flag = "within 5 points" if g["within_5_points"] else f"NOT within 5 points ({g['max_variation_pts']} pts)"
        lines += [f"### {group} ({flag})", "",
                  "| Segment | Tickets in segment | Resolution rate | Quality score | Variation from best | CI overlaps best | Explanation |",
                  "|---|---|---|---|---|---|---|"]
        for seg in g["segments"].values():
            r, q = seg["resolution"], seg["quality"]
            lines.append(f"| {seg['label']} | {seg['tickets']} | {_pc(r['rate'])} ({_pc(r['ci'][0])} to {_pc(r['ci'][1])}) | "
                         f"{_pc(q['rate'])} ({_pc(q['ci'][0])} to {_pc(q['ci'][1])}) | "
                         f"{'best' if seg['variation_from_best_pts'] == 0 else str(seg['variation_from_best_pts']) + ' pts'} | "
                         f"{'yes' if seg['ci_overlaps_best'] else 'no'} |  |")
        lines += ["", "Facts for the explanation: share labelled escalate / share with no passage above threshold / mean length / mean confidence / retrieval hit rate",
                  ""]
        for seg in g["segments"].values():
            f = seg["facts"]
            lines.append(f"- {seg['label']}: {_pc(f['share_labelled_escalate'])} / {_pc(f['share_no_passage'])} / {f['mean_text_len']} chars / "
                         f"{f['mean_confidence']} / {_pc(seg['retrieval_hit']['rate'])} (n={seg['retrieval_hit']['n']})")
        lines.append("")
    return "\n".join(lines)


def main(argv: Optional[Iterable[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--results", action="append", required=True, help="results.jsonl of a harness run (repeatable)")
    ap.add_argument("--output", required=True, help="directory for fairness_audit.json and fairness_audit.md")
    args = ap.parse_args(list(argv) if argv is not None else None)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    report: Dict[str, Any] = {}
    md = ["# Fairness audit (NFR-06, Governance Framework section 3)", ""]
    for path in args.results:
        p = Path(path)
        records = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        name = p.parent.name
        report[name] = audit(records)
        md.append(render(name, report[name]))
    (out / "fairness_audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (out / "fairness_audit.md").write_text("\n".join(md), encoding="utf-8")
    for name, a in report.items():
        print(name + ":", {g: (v["max_variation_pts"], "ok" if v["within_5_points"] else "OVER") for g, v in a["groups"].items()})
    print("written:", out / "fairness_audit.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

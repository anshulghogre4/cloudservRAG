"""B-09 check: tune and measure the guardrails on the DEVELOPMENT drafts already produced by generate_check.

Uses the real embedder and the real NLI cross-encoder (downloaded once, cached) on every sentence of
every draft in the given generate_check row files, plus the known bad sentence from DEV-0404 (v1.0),
and reports: per-sentence score distributions, how many drafts each guardrail would block at the
configured thresholds, and the verdict on the known contradiction.

Run:  python -m evaluation.guardrail_check
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import time
from pathlib import Path

from src.config import load_settings
from src.generate import Draft, citation_map
from src.guardrails import Grounder, NLIScorer, check_forbidden_claims, check_injection, check_private_data, run_guardrails
from src.ingest import load_tickets
from src.retrieve import Retriever, SentenceTransformerEmbedder

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Docs" / "Capstone_Project" / "05_Datasets"
KNOWN_BAD = {"ticket_id": "DEV-0404",
             "sentence": "This will ensure that running containers pick up the new values without a restart.",
             "doc_id": "DOC-DEPLOY-004"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", nargs="+", default=[str(ROOT / "evaluation" / "results" / d / "generate_rows.jsonl")
                                                  for d in ("generate_check", "generate_check_v1.1", "generate_check_v1.2")])
    ap.add_argument("--output", default=str(ROOT / "evaluation" / "results" / "guardrail_check.json"))
    ap.add_argument("--no-nli", action="store_true")
    a = ap.parse_args(argv)

    s = load_settings()
    tickets = {t.ticket_id: t for t in load_tickets(DATA / "development_tickets.json")}
    docs = json.loads((DATA / "documentation.json").read_text(encoding="utf-8"))
    emb = SentenceTransformerEmbedder(s.embedding_model)
    retr = Retriever(emb, s.chroma_path); retr.ensure_built(docs)
    nli = None if a.no_nli else NLIScorer()
    grounder = Grounder(emb, nli=nli, cos_threshold=s.grounding_cos, lex_threshold=s.grounding_lex,
                        contradiction_threshold=s.grounding_contradiction)

    drafts = []
    for f in a.rows:
        p = Path(f)
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r["unknown"] or r["error"]:
                continue
            drafts.append((p.parent.name, r))
    print(f"{len(drafts)} drafts loaded")

    sent_scores, per_draft = [], []
    t0 = time.perf_counter()
    for src, r in drafts:
        t = tickets[r["ticket_id"]]
        passages = retr.search(t.text, k=s.retrieval_top_k, threshold=s.retrieval_threshold)
        d = Draft(answer=r["answer"], citations=r["citations"], unknown=False)
        rep = run_guardrails(d, t, passages, grounder)
        g = rep.details["grounding"]
        for sc in g.get("scores", []):
            sent_scores.append({**sc, "ticket_id": r["ticket_id"], "source": src})
        per_draft.append({"source": src, "ticket_id": r["ticket_id"], "verdicts": rep.verdicts, "blocked": rep.blocked,
                          "unsupported": [(u["reason"], u["sentence"][:90], u["cos"], u["lex"], u["contradiction"]) for u in g.get("unsupported", [])],
                          "checked": g.get("checked"), "attached": g.get("attached")})
    elapsed = time.perf_counter() - t0

    # the known contradiction
    t = tickets[KNOWN_BAD["ticket_id"]]
    passages = retr.search(t.text, k=s.retrieval_top_k, threshold=s.retrieval_threshold)
    kb = grounder.check(KNOWN_BAD["sentence"], passages)
    known = {"verdict": kb[0], "scores": kb[1]["scores"], "unsupported": kb[1]["unsupported"]}

    cos = [x["cos"] for x in sent_scores]; lex = [x["lex"] for x in sent_scores]; con = [x["contradiction"] for x in sent_scores]
    def q(xs, p): xs = sorted(xs); return xs[min(len(xs) - 1, int(p * len(xs)))] if xs else None
    summary = {
        "drafts": len(drafts), "factual_sentences": len(sent_scores), "seconds": round(elapsed, 1),
        "thresholds": {"cos": s.grounding_cos, "lex": s.grounding_lex, "contradiction": s.grounding_contradiction},
        "cos_quantiles": {"p05": q(cos, .05), "p10": q(cos, .10), "p25": q(cos, .25), "p50": q(cos, .5), "min": min(cos) if cos else None},
        "lex_quantiles": {"p05": q(lex, .05), "p10": q(lex, .10), "p25": q(lex, .25), "p50": q(lex, .5), "min": min(lex) if lex else None},
        "contradiction_quantiles": {"p50": q(con, .5), "p90": q(con, .9), "p95": q(con, .95), "p99": q(con, .99), "max": max(con) if con else None},
        "blocked_drafts": sum(1 for d in per_draft if d["blocked"]),
        "blocked_by": {k: sum(1 for d in per_draft if d["verdicts"].get(k) == "block") for k in ("pii", "tone", "grounding", "injection")},
        "markers_attached_total": sum(d["attached"] or 0 for d in per_draft),
        "known_contradiction": known,
        "unsupported_examples": [u for d in per_draft for u in d["unsupported"]][:15],
    }
    Path(a.output).write_text(json.dumps({"summary": summary, "per_draft": per_draft, "sentences": sent_scores}, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

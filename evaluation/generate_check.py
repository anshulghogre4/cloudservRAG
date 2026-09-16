"""B-08 check: draft answers for a sample of DEVELOPMENT tickets and measure citation behaviour.

For each sampled answerable ticket: retrieve, draft with PR-03, then report
  parse rate, unknown rate, citations that resolve to retrieved passages, share of sentences
  carrying a citation, forbidden-claim hits, must_mention coverage where ground truth exists,
  answer length. Rows are saved for the grounding guardrail tuning (B-09).

Run:  python -m evaluation.generate_check --input Docs/.../development_tickets.json --limit 20
Refuses the validation set.
"""
from __future__ import annotations

import argparse
import json
import logging
import random
import re
import statistics as st
import time
from pathlib import Path

from src.config import load_settings
from src.generate import citation_map, generate
from src.ingest import load_tickets
from src.llm import LLMClient
from src.retrieve import Retriever, SentenceTransformerEmbedder

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Docs" / "Capstone_Project" / "05_Datasets"
FORBIDDEN = [r"refund (has been|was) (issued|processed)", r"(fixed|resolved) (it )?on our (side|end)",
             r"\b(by|on|within) (monday|tuesday|wednesday|thursday|friday|\d+ (days?|hours?|weeks?))\b.*\b(fix|release|deploy)"]
_GREETING = re.compile(r"^(thank|thanks|hi|hello|please reply|if you|let me know|do reply)", re.I)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--rpm", type=float, default=20.0)
    ap.add_argument("--output", default=str(ROOT / "evaluation" / "results" / "generate_check"))
    a = ap.parse_args(argv)
    if "validation" in Path(a.input).name.lower():
        raise SystemExit("refusing: the validation set is reserved for the gate run")
    logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(message)s")

    s = load_settings()
    out = Path(a.output); out.mkdir(parents=True, exist_ok=True)
    tickets = [t for t in load_tickets(a.input) if t.raw.get("labels", {}).get("answerable_from_docs")]
    random.Random(a.seed).shuffle(tickets)
    sample = tickets[: a.limit]
    docs = json.loads((DATA / "documentation.json").read_text(encoding="utf-8"))
    truth = {g["ticket_id"]: g for g in json.loads((DATA / "ground_truth_responses.json").read_text(encoding="utf-8"))}
    retr = Retriever(SentenceTransformerEmbedder(s.embedding_model), s.chroma_path); retr.ensure_built(docs)
    llm = LLMClient(s)

    rows, last = [], 0.0
    for i, t in enumerate(sample, 1):
        passages = retr.search(t.text, k=s.retrieval_top_k, threshold=s.retrieval_threshold)
        wait = 60.0 / a.rpm - (time.time() - last)
        before = llm.calls
        if wait > 0:
            time.sleep(wait)
        d = generate(t, passages, llm)
        if llm.calls != before:
            last = time.time()
        cm = citation_map(d.answer) if not d.unknown else []
        factual = [x for x in cm if not _GREETING.match(x["sentence"])]
        expected = set(t.raw["labels"].get("expected_doc_ids", []))
        g = truth.get(t.ticket_id)
        rows.append({
            "ticket_id": t.ticket_id, "intent": t.raw["labels"]["intent"], "tier": t.customer.tier,
            "retrieved": [p.doc_id for p in passages], "expected": sorted(expected),
            "unknown": d.unknown, "error": d.error, "citations": d.citations, "invalid_citations": d.invalid_citations,
            "cites_expected": bool(set(d.citations) & expected),
            "sentences": len(cm), "factual_sentences": len(factual),
            "factual_with_citation": sum(1 for x in factual if x["citations"]),
            "words": len(d.answer.split()),
            "forbidden_hits": [p for p in FORBIDDEN if re.search(p, d.answer, re.I)],
            "must_mention": g["must_mention"] if g else None,
            "must_mention_hit": (sum(1 for m in g["must_mention"] if m.lower() in d.answer.lower()) if g and g["must_mention"] else None),
            "answer": d.answer,
        })
        logging.info("%d/%d %s unknown=%s cites=%s err=%s", i, len(sample), t.ticket_id, d.unknown, d.citations, d.error)

    (out / "generate_rows.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    ok = [r for r in rows if not r["unknown"] and not r["error"]]
    summary = {
        "n": len(rows), "parsed_ok": len([r for r in rows if not r["error"]]), "unknown": sum(1 for r in rows if r["unknown"]),
        "with_invalid_citation": sum(1 for r in rows if r["invalid_citations"]),
        "cites_expected_doc": sum(1 for r in ok if r["cites_expected"]) / max(1, len(ok)),
        "factual_sentence_citation_rate": (sum(r["factual_with_citation"] for r in ok) / max(1, sum(r["factual_sentences"] for r in ok))),
        "answers_with_every_factual_sentence_cited": sum(1 for r in ok if r["factual_sentences"] and r["factual_with_citation"] == r["factual_sentences"]) / max(1, len(ok)),
        "forbidden_claim_hits": sum(1 for r in rows if r["forbidden_hits"]),
        "must_mention_coverage": (lambda xs: (sum(h for h, _ in xs) / sum(n for _, n in xs)) if xs else None)(
            [(r["must_mention_hit"], len(r["must_mention"])) for r in ok if r["must_mention"]]),
        "words_mean": st.mean(r["words"] for r in ok) if ok else None,
        "words_min_max": [min(r["words"] for r in ok), max(r["words"] for r in ok)] if ok else None,
        "provider_calls": llm.calls, "cache_hits": llm.cache_hits,
    }
    (out / "generate_check.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

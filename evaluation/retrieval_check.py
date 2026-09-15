"""T-07 / B-03 / B-04: measure retrieval on the DEVELOPMENT set and pick the configuration from data.

Compares:
  chunking   : section (one chunk per H2 section)  vs  article (whole article as one chunk)
  retrieval  : dense (MiniLM cosine)  vs  hybrid (dense + BM25, reciprocal rank fusion)
Reports hit@1/3/5 and MRR at article level over answerable tickets, plus the score
distributions needed to choose the relevance threshold (FR-04).

Run:  python -m evaluation.retrieval_check --input Docs/Capstone_Project/05_Datasets/development_tickets.json
Never point this at validation_tickets.json before the gate run.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

from src.retrieve import Retriever, SentenceTransformerEmbedder, chunk_documents
from src.ingest import load_tickets

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "Docs" / "Capstone_Project" / "05_Datasets" / "documentation.json"
_TOK = re.compile(r"[a-z0-9_]+")


def tok(s): return _TOK.findall(s.lower())


class BM25:
    def __init__(self, texts, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.docs = [tok(t) for t in texts]
        self.avg = sum(len(d) for d in self.docs) / max(1, len(self.docs))
        self.df = Counter(w for d in self.docs for w in set(d))
        self.n = len(self.docs)
        self.tf = [Counter(d) for d in self.docs]

    def scores(self, query):
        q = tok(query); out = []
        for i, d in enumerate(self.docs):
            s = 0.0; L = len(d)
            for w in q:
                if w not in self.tf[i]: continue
                idf = math.log(1 + (self.n - self.df[w] + 0.5) / (self.df[w] + 0.5))
                f = self.tf[i][w]
                s += idf * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * L / self.avg))
            out.append(s)
        return out


def rrf(rankings, k=60):
    agg = defaultdict(float)
    for ranking in rankings:
        for r, key in enumerate(ranking):
            agg[key] += 1.0 / (k + r + 1)
    return sorted(agg, key=agg.get, reverse=True)


def article_chunks(docs):
    return [{"id": d["doc_id"], "doc_id": d["doc_id"], "text": d["content"]} for d in docs]


def section_chunks(docs):
    return [{"id": c.chunk_id, "doc_id": c.doc_id, "text": c.text} for c in chunk_documents(docs)]


def evaluate(name, chunks, embedder, tickets, hybrid, k_dense=10):
    ids = [c["id"] for c in chunks]; doc_of = {c["id"]: c["doc_id"] for c in chunks}
    embs = embedder.embed_documents([c["text"] for c in chunks])
    bm25 = BM25([c["text"] for c in chunks]) if hybrid else None
    hits = {1: 0, 3: 0, 5: 0}; rr = []; best_correct = []; best_any = []
    for t in tickets:
        q = embedder.embed_query(t.text)
        dense = [sum(a * b for a, b in zip(q, e)) for e in embs]           # cosine, vectors normalised
        order = sorted(range(len(ids)), key=lambda i: dense[i], reverse=True)
        if hybrid:
            bs = bm25.scores(t.text)
            b_order = sorted(range(len(ids)), key=lambda i: bs[i], reverse=True)
            order = rrf([order[:k_dense], b_order[:k_dense]])
        # collapse chunks to articles, keep first appearance
        docs_ranked = []
        for i in order:
            d = doc_of[ids[i]]
            if d not in docs_ranked: docs_ranked.append(d)
        expected = set(t.raw["labels"]["expected_doc_ids"])
        pos = next((j for j, d in enumerate(docs_ranked) if d in expected), None)
        for k in hits:
            if pos is not None and pos < k: hits[k] += 1
        rr.append(1.0 / (pos + 1) if pos is not None else 0.0)
        top_dense = max(dense)
        best_any.append(top_dense)
        if pos is not None:
            best_correct.append(max(dense[i] for i in range(len(ids)) if doc_of[ids[i]] in expected))
    n = len(tickets)
    return {"config": name, "n": n, "hit@1": hits[1] / n, "hit@3": hits[3] / n, "hit@5": hits[5] / n,
            "mrr": sum(rr) / n, "median_top_dense_score": st.median(best_any),
            "median_correct_doc_score": st.median(best_correct) if best_correct else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", default=str(ROOT / "evaluation" / "results" / "retrieval_check.json"))
    a = ap.parse_args()
    if "validation" in Path(a.input).name.lower():
        raise SystemExit("refusing: the validation set is reserved for the gate run")
    docs = json.loads(DOCS.read_text(encoding="utf-8"))
    tickets = load_tickets(a.input)
    answerable = [t for t in tickets if t.raw.get("labels", {}).get("answerable_from_docs")]
    not_answerable = [t for t in tickets if not t.raw.get("labels", {}).get("answerable_from_docs")]
    emb = SentenceTransformerEmbedder()
    results = []
    for cname, chunks in (("section", section_chunks(docs)), ("article", article_chunks(docs))):
        for hybrid in (False, True):
            r = evaluate(f"{cname}+{'hybrid' if hybrid else 'dense'}", chunks, emb, answerable, hybrid)
            results.append(r); print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    # threshold evidence: dense top score for non-answerable tickets (should fall below threshold)
    sec = section_chunks(docs); embs = emb.embed_documents([c["text"] for c in sec])
    def top(t):
        q = emb.embed_query(t.text); return max(sum(a * b for a, b in zip(q, e)) for e in embs)
    na = sorted(top(t) for t in not_answerable); an = sorted(top(t) for t in answerable)
    def pct(xs, p): return xs[min(len(xs) - 1, int(p * len(xs)))]
    thr = {"non_answerable_top_score": {"n": len(na), "p50": pct(na, .5), "p75": pct(na, .75), "p90": pct(na, .9), "max": na[-1]},
           "answerable_top_score": {"n": len(an), "p10": pct(an, .1), "p25": pct(an, .25), "p50": pct(an, .5), "min": an[0]}}
    print("threshold evidence:", json.dumps(thr, indent=1))
    out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"results": results, "threshold_evidence": thr, "chunks_section": len(sec),
                               "chunks_article": len(docs)}, indent=2), encoding="utf-8")
    print("written", out)


if __name__ == "__main__":
    main()

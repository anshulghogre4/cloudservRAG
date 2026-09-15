"""B-03 / B-04, FR-03 / FR-04: chunking, indexing and retrieval.

T-06  test_ids_resolve            every returned passage names a real doc_id and section
T-08  test_empty_on_irrelevant    below the relevance threshold, retrieval returns []
plus  chunking shape checks: one chunk per article section, metadata carried.

A deterministic bag-of-words embedder is injected so tests run without the model or network.
T-07 (hit rate >= 85% on development tickets) is measured by evaluation/retrieval_check.py.
"""
import math
import re
from collections import Counter

import pytest

from src.retrieve import chunk_documents, Retriever, SECTIONS


class BagOfWordsEmbedder:
    """Cosine-comparable sparse vectors over a fixed vocabulary; deterministic and offline."""

    def __init__(self, vocab_size: int = 512):
        self.n = vocab_size

    def _vec(self, text: str):
        v = [0.0] * self.n
        for tok in re.findall(r"[a-z0-9]+", text.lower()):
            v[hash(tok) % self.n] += 1.0
        norm = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / norm for x in v]

    def embed_documents(self, texts):
        return [self._vec(t) for t in texts]

    def embed_query(self, text):
        return self._vec(text)


@pytest.fixture(scope="module")
def chunks(documentation):
    return chunk_documents(documentation)


@pytest.fixture(scope="module")
def retriever(documentation, tmp_path_factory):
    r = Retriever(embedder=BagOfWordsEmbedder(), persist_dir=tmp_path_factory.mktemp("chroma"))
    r.build(documentation)
    return r


def test_chunking_one_chunk_per_section(chunks, documentation):
    per_doc = Counter(c.doc_id for c in chunks)
    assert set(per_doc) == {d["doc_id"] for d in documentation}
    for c in chunks:
        assert c.section in SECTIONS
        assert c.text.strip()
        assert c.title and c.applies_to
    # every article has all four sections in the corpus (Dataset Guide §2)
    for d in documentation:
        assert per_doc[d["doc_id"]] == len(SECTIONS)


def test_ids_resolve(retriever, documentation):
    valid = {d["doc_id"] for d in documentation}
    hits = retriever.search("429 too many requests rate limit backoff", k=5, threshold=0.0)
    assert hits, "top-k with threshold 0 must return something"
    for h in hits:
        assert h.doc_id in valid
        assert h.section in SECTIONS
        assert 0.0 <= h.score <= 1.0 + 1e-9
        assert h.text.strip()
    assert hits == sorted(hits, key=lambda h: h.score, reverse=True)


def test_search_finds_the_right_article(retriever):
    hits = retriever.search("requests return 429 too many requests, limit lower than documented", k=3, threshold=0.0)
    assert hits[0].doc_id == "DOC-API-001"


def test_empty_on_irrelevant(retriever):
    # A feature request has no article; a high threshold must return nothing (FR-04, never invent a citation)
    hits = retriever.search("please add per-project spend caps as a new feature", k=5, threshold=0.99)
    assert hits == []


def test_k_and_threshold_are_respected(retriever):
    hits = retriever.search("webhook signature verification failing", k=2, threshold=0.0)
    assert len(hits) <= 2

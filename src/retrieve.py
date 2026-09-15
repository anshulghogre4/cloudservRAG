"""Retrieve: chunk the 29 articles by section, embed, store in Chroma, search (FR-03, FR-04).

Design decisions (recorded in docs/architecture.md):
- Chunk per article section (Symptoms, Common causes, Resolution, Notes), never inside a
  resolution sequence (Dataset Guide §2). Each chunk keeps doc_id, title, applies_to as metadata
  so a citation can be verified and plan restrictions checked by the router.
- The embedder is injectable. Production uses all-MiniLM-L6-v2 through sentence-transformers;
  tests inject a deterministic offline embedder so CI needs no model download.
- Cosine similarity; score = 1 - distance in [0, 1]. Below `threshold` nothing is returned:
  returning nothing is a valid answer (Build Spec §08).
"""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Protocol, Sequence

SECTIONS = ("Symptoms", "Common causes", "Resolution", "Notes")
_HEADING = re.compile(r"^##\s+(.+?)\s*$", re.M)
COLLECTION = "cloudserve_docs"


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    category: str
    applies_to: str
    section: str
    text: str


@dataclass(frozen=True)
class Passage:
    doc_id: str
    section: str
    title: str
    applies_to: str
    text: str
    score: float
    chunk_id: str


class Embedder(Protocol):
    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]: ...
    def embed_query(self, text: str) -> List[float]: ...


class SentenceTransformerEmbedder:
    """all-MiniLM-L6-v2 (Project Brief §09). Loaded lazily; cached by sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_documents(self, texts):
        return self._load().encode(list(texts), normalize_embeddings=True, show_progress_bar=False).tolist()

    def embed_query(self, text):
        return self._load().encode([text], normalize_embeddings=True, show_progress_bar=False)[0].tolist()


def chunk_documents(docs: Sequence[dict]) -> List[Chunk]:
    """One chunk per section of each article; the title and section name are prepended so the
    passage reads as a complete unit and embeds with its context."""
    chunks: List[Chunk] = []
    for d in docs:
        content = d.get("content", "") or ""
        positions = [(m.start(), m.end(), m.group(1).strip()) for m in _HEADING.finditer(content)]
        for i, (start, end, heading) in enumerate(positions):
            stop = positions[i + 1][0] if i + 1 < len(positions) else len(content)
            body = content[end:stop].strip()
            if not body:
                continue
            section = heading if heading in SECTIONS else heading
            chunks.append(Chunk(
                chunk_id=f"{d['doc_id']}#{section.lower().replace(' ', '_')}",
                doc_id=d["doc_id"],
                title=d.get("title", ""),
                category=d.get("category", ""),
                applies_to=d.get("applies_to", ""),
                section=section,
                text=f"{d.get('title', '')}\n{section}\n{body}",
            ))
    return chunks


class Retriever:
    def __init__(self, embedder: Optional[Embedder] = None, persist_dir: Optional[str | Path] = None,
                 collection: str = COLLECTION):
        self.embedder = embedder or SentenceTransformerEmbedder()
        self.persist_dir = Path(persist_dir) if persist_dir else None
        self.collection_name = collection
        self._client = None
        self._collection = None

    # ---- storage -----------------------------------------------------------------
    def _connect(self):
        import chromadb
        if self._client is None:
            if self.persist_dir:
                self.persist_dir.mkdir(parents=True, exist_ok=True)
                self._client = chromadb.PersistentClient(path=str(self.persist_dir))
            else:
                self._client = chromadb.Client()
        if self._collection is None:
            self._collection = self._client.get_or_create_collection(
                self.collection_name, metadata={"hnsw:space": "cosine"})
        return self._collection

    def count(self) -> int:
        return self._connect().count()

    def build(self, docs: Sequence[dict]) -> int:
        """(Re)build the index from the corpus. Returns the number of chunks stored."""
        col = self._connect()
        if col.count():
            self._client.delete_collection(self.collection_name)
            self._collection = None
            col = self._connect()
        chunks = chunk_documents(docs)
        if not chunks:
            return 0
        col.add(
            ids=[c.chunk_id for c in chunks],
            documents=[c.text for c in chunks],
            embeddings=self.embedder.embed_documents([c.text for c in chunks]),
            metadatas=[{"doc_id": c.doc_id, "title": c.title, "category": c.category,
                        "applies_to": c.applies_to, "section": c.section} for c in chunks],
        )
        return len(chunks)

    def ensure_built(self, docs: Sequence[dict]) -> int:
        n = self.count()
        return n if n else self.build(docs)

    # ---- search ------------------------------------------------------------------
    def search(self, text: str, k: int = 5, threshold: float = 0.0) -> List[Passage]:
        """Top-k passages with cosine score >= threshold, best first. [] when nothing qualifies."""
        text = (text or "").strip()
        col = self._connect()
        if not text or col.count() == 0:
            return []
        res = col.query(query_embeddings=[self.embedder.embed_query(text)],
                        n_results=min(k, col.count()),
                        include=["documents", "metadatas", "distances"])
        out: List[Passage] = []
        for cid, doc, meta, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]):
            score = max(0.0, min(1.0, 1.0 - float(dist)))
            if score < threshold:
                continue
            out.append(Passage(doc_id=meta["doc_id"], section=meta["section"], title=meta["title"],
                               applies_to=meta["applies_to"], text=doc, score=score, chunk_id=cid))
        out.sort(key=lambda p: p.score, reverse=True)
        return out

# Architecture notes

Design decisions taken during the build, with the evidence behind each. Referenced from the
PRD (FR-03, FR-04, FR-05) and the Stage 5 revision log.

## Dependency pins (B-01, 16 Sep 2026)

The pack's `requirements.txt` does not resolve as shipped. Three pins were changed, each to
the nearest version that satisfies the neighbouring pins; nothing else was altered.

| Package | Pack pin | Used | Why |
|---|---|---|---|
| openai | 1.0.0 | 1.12.0 | `langchain-openai==0.0.7` requires `openai>=1.10,<2` |
| pydantic | 2.0.0 | 2.5.3 | `fastapi==0.104.0` explicitly excludes 2.0.0, 2.0.1 and 2.1.0 |
| langchain | 0.1.0 | 0.1.9 | `langchain-openai==0.0.7` needs `langchain-core>=0.1.26`, which `langchain==0.1.0` cannot use |
| langchain-community | 0.0.10 | 0.0.24 | same langchain-core / langsmith range as above |
| chromadb | 0.3.21 | 0.4.24 | 0.3.21 depends on `hnswlib`, which has no Windows wheel and needs a C++ toolchain; 0.4.x ships `chroma-hnswlib` wheels |
| huggingface-hub | (unpinned) | 0.20.3 | `sentence-transformers==2.2.2` imports `cached_download`, removed from huggingface_hub 0.26+ |

Environment: Python 3.11 (the version the pack's CI workflow uses), created with `uv`.
Python 3.13 cannot build `pandas==2.0.0`; a 3.10 venv would also work.

## Chunking (B-03)
_To be filled after the retrieval hit-rate comparison._

## Retrieval threshold (B-04)
_To be filled from development-set score distributions._

## Routing threshold and calibration (B-07)
_To be filled from the calibration table._

## Decision log schema (B-10)
_Governance Framework §1 record; see `src/logging_store.py`._

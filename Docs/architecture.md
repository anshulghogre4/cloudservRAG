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
| posthog | (unpinned) | 3.5.0 | chromadb 0.4.24 calls the pre-7.x posthog API; newer posthog prints a telemetry error on every client start |

Environment: Python 3.11 (the version the pack's CI workflow uses), created with `uv`.
Python 3.13 cannot build `pandas==2.0.0`; a 3.10 venv would also work.

## Chunking (B-03, decided 16 Sep 2026)

One chunk per article section (Symptoms, Common causes, Resolution, Notes), with the article
title and section name prepended; 29 articles x 4 = 116 chunks. Measured on the 357 answerable
development tickets, article-level hit rate against `expected_doc_ids`
(`evaluation/results/retrieval_check.json`):

| Config | hit@1 | hit@3 | hit@5 | MRR |
|---|---|---|---|---|
| section + dense (chosen) | 0.905 | 0.952 | 0.989 | 0.937 |
| section + hybrid (BM25 RRF) | 0.894 | 0.955 | 0.972 | 0.930 |
| article + dense | 0.874 | 0.958 | 0.972 | 0.921 |
| article + hybrid | 0.894 | 0.961 | 0.972 | 0.930 |

Why sections: the Dataset Guide warns against splitting inside a resolution sequence, and
all-MiniLM-L6-v2 truncates at 256 tokens, so a whole article (about 250 to 300 tokens) loses its
Notes; a section is 30 to 100 tokens, inside the model's best range. Hybrid BM25 fusion was
measured and not adopted: it lowered hit@1 and hit@5 on section chunks. Embeddings:
all-MiniLM-L6-v2, cosine space, vectors normalised.

## Retrieval threshold (B-04, decided 16 Sep 2026)

RETRIEVAL_THRESHOLD = 0.40 (cosine). On the development set: keeps 97.8% of answerable
tickets (99.4% at 0.35, 91.9% at 0.50) and returns nothing for 100% of `unclear_request`
tickets (median top score 0.265). Top-k = 5.

Finding that changes the design: the threshold cannot detect "no article exists". Non-answerable
tickets score almost as high as answerable ones (median top score 0.635 vs 0.644, p90 0.740),
because a feature request about spend caps resembles the spend-caps article. So FR-04's
"return nothing when nothing is relevant" holds only for off-topic text; deciding that a
compliance, security or feature request must not be auto-answered is the router's job (FR-06)
and the classifier's, not retrieval's. Recorded for the Stage 5 revision log.

## Routing threshold and calibration (B-07)
_To be filled from the calibration table._

## Decision log schema (B-10)
_Governance Framework §1 record; see `src/logging_store.py`._

## Evaluation harness (B-05, 16 Sep 2026)

`python -m evaluation.harness --input <file> --output <dir>`. One JSONL row per ticket, appended
as each ticket finishes, so a crash loses nothing and `--resume` continues from the last row.
A component failure becomes an escalation row carrying the error; the run never stops (A9, A11).
Quality metrics are computed only over labelled rows; completion (`failed_tickets`) is a separate
axis, following current batch-evaluation practice. Headline rates carry Wilson 95% intervals
because the graded set is small (80 to 120 tickets). Calibration uses the Evaluation Framework's
equal-width five-band table plus ECE. Segment tables (tier, region, fluency, ticket length,
channel) feed the fairness audit directly.

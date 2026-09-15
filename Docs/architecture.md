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
| onnxruntime | (unpinned) | 1.17.1 | pulled in by chromadb 0.4.24; the current 1.30 build segfaults on Windows when scipy is imported first (access violation in the full test run) |
| scipy | (unpinned) | 1.12.0 | scipy 1.15 with numpy 1.24 is an ABI mismatch; 1.12.0 is the February 2024 release matching the rest |
| numpy | 1.24.0 | 1.24.4 | onnxruntime 1.17.1 requires numpy >= 1.24.2; same 1.24 series, patch release only |

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

## Classifier and calibration (B-06, 16 Sep 2026)

Two signals, one calibrated confidence. PR-02 (Llama 3.1 8B, temperature 0, JSON mode) gives
intent, a verbalized confidence, alternatives and an instruction_like flag. A cosine
nearest-neighbour vote (k=7) over the labelled development tickets, using the same
all-MiniLM-L6-v2 embedding as retrieval, gives a second intent and an urgency. The routing
confidence is Platt-calibrated from a combined score: the mean of the two when they agree,
half their product when they disagree. Rationale: research shows instruction-tuned models are
overconfident, so the verbalized number is treated as a feature rather than a probability; the
neighbour signal is free, deterministic, rate-limit-proof and keeps working during a provider
outage (FR-14).

20-ticket smoke test (16 Sep): LLM intent accuracy 0.80; neighbours 0.992 leave-one-body-out
over 500; agreement 80% of tickets, accuracy 100% when they agree and 0% when they disagree;
ECE raw 0.145 -> combined 0.109 -> after Platt 0.045. LLM urgency accuracy 0.35, so urgency is
taken from the neighbour vote. Full development-set figures are in
`evaluation/results/classify_check.json`; the fitted parameters in `calibration.json`.

Caveat for the report: the development set repeats bodies (215 distinct among 500), so the
leave-one-body-out accuracy excludes exact duplicates but not near-duplicates; the hidden set is
drawn from the same population, so the figure is indicative rather than a guarantee.

### B-06 full development-set results (16 Sep 2026, 500 tickets, 323 paid calls, $0.007)

Supersedes the 20-ticket smoke figures above.

| Metric | LLM alone (PR-02) | Final: neighbour intent + LLM |
|---|---|---|
| Accuracy | 0.710 | 0.992 |
| Macro precision | 0.798 | 0.992 |
| Macro recall | 0.700 | 0.989 |
| Macro F1 | 0.678 | 0.990 |
| Weighted F1 | 0.682 | 0.992 |
| Urgency accuracy | 0.460 | 0.490 (neighbour vote) |

Agreement between the two signals on 70.4% of tickets; when they agree the intent is right 100%
of the time, when they disagree the LLM is right 2% of the time. Decision: the neighbour intent
is the final intent, the LLM intent is kept as the first alternative when they disagree, and the
LLM still supplies the instruction_like flag and the reason. The LLM alone would fail the 85%
target; this is recorded in the Stage 5 log as a failed PRD assumption.

Neighbour accuracy: 0.992 leave-one-body-out, 0.980 when near-duplicate neighbours
(cosine >= 0.95) are also excluded. The second figure is the better guide to the hidden set.
Only one class is below 0.85 on any measure: api_key_issue recall 0.83 (3 of 18 predicted as
account_access). Full per-class table in `evaluation/results/classify_check.json`, confusion
matrix in `evaluation/results/confusion_final.csv`.

Calibration: score = 0.5 x neighbour share + 0.5 x agreement. Histogram binning with Laplace
smoothing and enforced monotonicity (`evaluation/results/calibration.json`), chosen over Platt
because with four errors in 500 an unregularised Platt fit is a step function and a
regularised one is flat (every ticket 0.97 to 0.99). Five-fold cross-validated table: ECE 0.006,
every band within 5 points (0.6-0.8 band n=14 stated 0.686 observed 0.714; 0.8-1.0 band n=486
stated 0.995 observed 1.000). Urgency is barely predictable from text in this data (both
signals near the 45% majority baseline); reported as a limitation.

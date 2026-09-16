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
| httpx | (unpinned) | 0.27.2 | httpx 0.28 removed the app= argument starlette 0.27's TestClient uses; openai 1.12 accepts any httpx below 1.0 (B-16) |

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

## Routing threshold and decision table (B-07, 16 Sep 2026)

Decision table in `src/route.py`, checked in order: kill switch, classification failed,
instruction-like input, never-auto intent, low confidence, no grounded source, then auto-respond.
Deterministic, no model call, every branch logged with a plain-English reason and the threshold.

CONFIDENCE_THRESHOLD = 0.80. Derived with the selective-classification cost rule: with a
calibrated P(correct), escalate when P < 1 - c_escalate / c_wrong. Marcus put an escalation at
about 4x a resolved ticket and a wrong answer as worse than waiting. Sweeping c_wrong / c_escalate
over the development set (`evaluation/results/route_check.json`): ratios up to 3 imply a threshold
of 0.67 (expected cost 860); ratios of 4 and above imply 0.75 to 0.90 (cost 872), all of which
route identically because calibrated confidence is bimodal (0.686 for LLM/neighbour
disagreements, 0.99+ otherwise). 0.80 is the conservative reading of "rather say nothing than
something wrong"; the cost difference is 1.4%.

Measured and not adopted (kept behind settings, off by default):
- plan_restriction (escalate when the cited article applies to other plans): routing accuracy
  0.784 -> 0.756, 28 expected auto-answers lost; PR-03 rule 7 already words plan limits into
  the draft. Reverses the Stage 5 candidate change to FR-05.
- learned_not_answerable (neighbour vote on answerable_from_docs below 0.5): 0.784 -> 0.762;
  the labels are inconsistent on near-identical bodies, so neighbours cannot recover them.

Development-set routing at 0.80: auto-respond 78.6%, routing accuracy 0.784 against a
text-only ceiling of 0.938 (35 duplicate-body groups carry both routes), 0 auto-answers on
must_not_auto_respond tickets, 0 auto-answers with a wrong intent. The 81 auto-answers on
tickets labelled escalate are answerable-looking intents (rollback, database, performance) whose
labels the text does not distinguish; reported as the main limitation of routing.

## Answer generation and citations (B-08, 16 Sep 2026)

`src/generate.py` drafts with PR-03 in JSON mode from the retrieved passages only, listed as
[doc_id | section | applies_to] blocks. Inline [DOC-ID] markers are the citation format; every
marker is validated against the passages retrieved for that ticket and anything else is dropped
and reported (A6). No passages, provider failure or unparseable output all yield an "unknown" draft
that the router escalates. The disclosure line (FR-12) is appended by code.

PR-03 went through three versions on the same 20 development tickets (19 drafted, 1 unknown):

| Version | Markers resolve | Cites expected article | Factual sentences with a marker | must_mention coverage | Mean words |
|---|---|---|---|---|---|
| 1.0 | 100% | 100% | 22.6% | 100% | 99 |
| 1.1 (example + "uncited sentences removed") | 1 invalid | 94.7% | 64.9% | 50% | 66, min 13 |
| 1.2 (chosen) | 100% | 100% | 53.3% | 100% | 119 |

Two lessons recorded for the prompt register: a worked example was copied verbatim into an
unrelated answer by the 8B model (few-shot leakage), and a threat to remove uncited sentences made
it shorten answers instead of citing. v1.2 describes the marker form with a placeholder and asks for
full prose first. In v1.2, of 70 uncited sentences 32 are greetings or closings and 38 are steps
taken from the passage without a marker; one v1.0 draft inverted a fact (containers pick up new
values "without a restart", the passage says the opposite). Both facts define B-09: verify every
sentence against the retrieved passages, attach the marker mechanically when a sentence is
supported, block when it is not. Forbidden claims: 0 in all 57 drafts.

## Guardrails (B-09, 16 Sep 2026)

Four checks in `src/guardrails.py`, each returning pass, block or skipped on every draft, all local
(no provider call, so they keep working during an outage):

- pii: exact match on the customer's own name and id from the ticket fields, plus patterns for
  e-mail, credential-like strings, card and phone numbers, IPs. Block, never redact. Only the
  match type is logged, never the value. Exact matching beats NER here because the strings to
  catch are known and the corpus contains no other names.
- tone: forbidden commitments (refund issued, fixed on our side, a delivery date or timeline), the
  three universal must_not_claim items from the ground truth plus regex families around them.
  The articles' own wording about refunds ("an account owner should raise the request") passes.
- injection: instruction-like customer text by pattern; the classifier's instruction_like flag is
  the second signal; the router escalates on either.
- grounding: every factual sentence (greetings, closings and rhetorical fillers excluded) is
  compared with the retrieved passages at sentence level: best cosine over every passage sentence,
  lexical containment over every passage, and an NLI contradiction score from
  cross-encoder/nli-MiniLM2-L6-H768 against the matched passage sentence. Supported and uncited
  sentences get their marker attached; unsupported or contradicted sentences block the draft with
  the sentence flagged.

Tuning on the 57 development drafts (218 factual sentences, `evaluation/results/guardrail_check.json`):

| Stage | Blocked drafts | Known contradiction (DEV-0404) |
|---|---|---|
| chunk-level cosine, whole-passage NLI premise | 31 of 57 | passed (0.015) |
| sentence-level NLI premise | 21 | caught (0.965) |
| sentence-level cosine and lexical too | 7 | caught |
| contradiction threshold 0.85, filler filter | 3 | caught |

The three remaining blocks are all genuine: a v1.0 "we will investigate" filler, the inverted fact,
and a v1.1 draft that copied the prompt's example sentences into a billing answer. Zero false
blocks on the 19 v1.2 drafts. Thresholds at B-09: cosine 0.55 or lexical 0.50 for support (p05 of correct
sentences is 0.61 / 0.33), contradiction 0.85 (true positive 0.965; false positives at 0.61 and
0.73 on compound or conditional sentences). Cost: about 0.5 s per draft on CPU.

Guardrails AI (guardrailsai.com) was evaluated at the user's suggestion. Facts: hub validators are
pip-installable and, per the user, no hub key is now required; `provenance_embeddings` implements
the same cosine-to-sources check as the grounder; `detect_pii` depends on Presidio and a spaCy
model downloaded at first use; `detect_jailbreak` downloads a model. Installing guardrails-ai with
the pack's pinned stack fails on openai (needs >= 1.30.1); relaxing openai within the
langchain-openai range makes it resolve with 23 more packages (45 with detect_pii), replacing
openai, rich and typer. Decision: not adopted for the gate build, because it adds an install
surface to a clean-checkout test for mechanisms already implemented locally with models the
system already loads, and its PII validator is weaker than exact matching for this corpus. It is
recorded as the production-hardening option, and its provenance validator could be run as an
independent cross-check of the grounder in evaluation if time allows.

## Decision log, escalation package and pipeline (B-10, 16 Sep 2026)

`src/logging_store.py`: SQLite, WAL journal with synchronous=FULL, one committed row per decision,
no update or delete path in the code (append-only). Columns are the Governance Framework section 1
record plus run_id and latency. Four rows per ticket (classification, routing, generation,
validation); blocked tickets carry two generation rows (the draft and the escalation summary).
`reconcile()` is the A8 check the harness runs after every batch: every processed ticket must have
a routing and a validation row. The input summary is the ticket text only, never customer fields.

`src/escalation.py`: PR-04 summary plus intent, confidence, retrieved article ids, the draft if
one exists, the route reason and the rule; when the provider is unavailable or the output is
unparseable a deterministic template is used, so no escalation leaves without its context (FR-14).

`src/pipeline.py`: one `process()` used by the harness and the API. Component failures become
escalations with the reason. First real end-to-end run (20 development tickets, 16 Sep):
0 errors, 83 log rows reconciled, 12 auto-responses, 5 escalations, 3 grounding blocks.
Latency median 9.9 s, p95 20 s: two to three provider round trips per ticket at free-tier pacing
plus the NLI check; the 3 s p95 target (NFR-01) is not achievable with a remote free-tier model
and is reported as such.

### Checkpoint fixes after the first 20-ticket run (B-10, 16 Sep 2026)

The three grounding blocks in that run were re-scored sentence by sentence and all three were
false positives, with three distinct causes:

| Ticket | Sentence | Scores | Cause |
|---|---|---|---|
| DEV-0006 | "we recommend storing them as secrets rather than environment variables" | cos 0.79, lex 0.50, contradiction 0.96 | NLI premise was the chunk's prepended title line "Configuring environment variables and secrets" (best cosine, but a heading, not a claim) |
| DEV-0008 | "We will then be able to assist you further." | cos 0.20, lex 0.00 | closing filler not in the filter |
| DEV-0010 | "We're here to help you resolve the issue with ..." / "After making any changes, please redeploy ..." | cos 0.54 / cos 0.51, lex 0.38 | filler opener; a genuine paraphrase of the redeploy step just under the 0.55 line |

Changes (tests first, `tests/test_guardrails.py`, `tests/test_generate.py`): the title and section
heading lines are excluded from passage sentences, so a heading is never an NLI premise or the
best-cosine match; closing/filler patterns gained "assist you further", "able to help", "here to
help", "we're here to", "we will be able to"; a marker-only fragment left by repeated trailing
markers ("[DOC-X] [DOC-X].") is merged into the previous sentence instead of being scored as ".";
the cosine support threshold moved from 0.55 to 0.50. Evidence for the last: the 57-draft tuning
set has no factual sentence with cosine in [0.45, 0.55) (the threshold sits in a gap, so the
tuning data is silent), the run produced one correct paraphrase at 0.51, and the contradiction
check remains the second line against inverted facts. Re-run of the tuning set: still 3 of 57
blocked, the same three, known contradiction still caught at 0.965 with a body sentence as
premise. The three checkpoint drafts now pass. 106 tests pass.

## Full development-set run (B-11, 16 Sep 2026)

`python -m evaluation.harness --input Docs/Capstone_Project/05_Datasets/development_tickets.json --output evaluation/results/2026-09-16_dev_full`
was run three times on the same output directory (run count 3 in `run_meta.json`); run 1 is
archived as `2026-09-16_dev_full_run1`. Runs 2 and 3 reused the cached model replies, so their
latency figures measure the local pipeline only; run 1 is the honest end-to-end latency.

| | Run 1 (as built) | Run 3 (final) |
|---|---|---|
| auto / escalate / block | 356 / 101 / 43 | 387 / 107 / 6 |
| first-contact resolution | 71.2% | 77.4% (CI 73.5 to 80.8) |
| escalation rate | 28.8% | 22.6% |
| intent accuracy | 1.000 (memorised) | 0.992 (leave-one-out) |
| routing accuracy | 73.8% | 77.2% |
| retrieval hit rate (357 answerable) | 93.3% | 93.3% |
| citations resolve / cite expected article | 100% / 72.2% | 100% / 72.6% |
| must-not-auto violations / private data | 0 / 0 | 0 / 0 |
| calibration, bins with n >= 20 within 5 points | fails (a 2-ticket bin) | passes; ECE 0.005 |
| decision log | not reconciled by the harness | 2006 rows, 500/500 routing and validation rows |
| latency median / p95 | 2.4 s / 16.8 s (live provider) | 0.35 s / 0.53 s (cached) |
| errors | 0 | 0 |
| provider cost | about $0.03 | about $0.01 (escalation summaries) |

What run 1 exposed and what changed (tests first; 133 tests pass):

1. **Intent accuracy 1.000 was memorisation.** The neighbour memory is the development set, so
   every development ticket found itself. `classify()` now excludes a ticket with identical text
   from its own vote (`exclude_self`); development figures are leave-one-out (0.992, matching the
   B-06 estimate). The validation and hidden sets are never in the memory, so this changes nothing
   in production.
2. **The harness never called `reconcile()`**; A8 was asserted, not checked. The harness now
   reconciles the run's rows against every ticket id after the run, writes the result into
   `metrics.json` (governance.decision_log) and `run_summary.md`, and writes routing and
   validation rows itself when `process()` raises, so failures reconcile too.
3. **Calibration was judged on a 2-ticket bin.** The 5-point test is now judged on bins with at
   least 20 tickets; smaller bins are reported with `evaluable: false`. Run 3: bin 0.8-1.0 n=486
   stated 0.996 observed 1.000; bin 0.6-0.8 n=14 not judged.
4. **43 grounding blocks, 37 false.** Every unsupported sentence was re-scored
   (`2026-09-16_dev_full/block_review.json`). Causes and fixes: (a) NLI premise was a Symptoms or
   Common-causes line ("The invitation was never accepted and the account does not exist"), which
   any resolution step contradicts; premises now come only from Resolution and Notes sentences,
   and list bullets are stripped. (b) Plan applicability ("a feature of our Business and
   Enterprise plans") is stated in the passage metadata, not its body; `applies_to` is now a
   passage sentence. (c) Narration and courtesy sentences ("Please follow the steps outlined in
   our documentation", "To better understand the problem", "We understand that", "This will help",
   "We'd like to help you troubleshoot") were scored as claims; the filler and closing filters
   gained those patterns. Tuning set after the change: 5 of 57 blocked, the 3 genuine ones plus
   two superseded v1.1 drafts that copied a Common-causes line verbatim as a diagnosis; accepted as
   conservative rather than adding a verbatim bypass around the contradiction check (a negation
   flip would use the same path). Known inverted fact still caught at 0.965.
5. **The six remaining blocks** are genuine by the rule: "If the job is still in progress, please
   wait for it to complete" (4 tickets; the article says large jobs take several minutes, not to
   wait), "This is a known issue", "This approach is more secure and scalable".

Retrieval hit rate 93.3% versus the B-04 hit@5 of 0.989: the check counted the expected article
among the top five distinct articles over all chunks with no threshold; the pipeline passes at
most five chunks above 0.40, typically one or two articles, so the pipeline figure sits between
the check's hit@1 (0.905) and hit@3 (0.952). Of the 24 misses, 8 have no passage above the
threshold and 16 rank another article first. Capping chunks per article was measured (k=5 with at
most one or two per article, k=6, k=8): 0.933 to 0.938 at best, two tickets; not adopted.

Routing errors in run 3: 114 of 500; 95 are auto-responses on tickets labelled escalate (the label
ceiling problem from B-07: same text, different expected route), 19 are escalations on tickets
labelled auto (7 no passage above threshold, 6 grounding blocks, 6 low confidence).

Governance segment condition (under 5 points variation in routing accuracy) is **not met** on the
development set: ticket length 11.7 (short tickets n=49, 0.878 vs 0.761), region 7.5, tier 7.4,
channel 6.5, fluency 2.6. Short tickets are mostly chat and route better because they are more
often labelled escalate and get no passage; this is carried into the fairness audit (B-14) with
confidence intervals rather than tuned here.

Latency: the 3 s p95 target (NFR-01) fails with the live provider (run 1 p95 16.8 s, two or three
round trips per ticket at free-tier pacing); the local pipeline without the provider is 0.5 s p95.

### Validation run (B-11 gate, 16 Sep 2026, once)

`validation_tickets.json` was restored after the development run and run exactly once
(`evaluation/results/2026-09-16_validation`, run count 1, code version ab696a0, live provider,
460 s for 80 tickets, 0 errors). The file was not opened or analysed; only the harness output
was read. Nothing was tuned on it.

| Metric | Validation (n=80) | Development run 3 (n=500) |
|---|---|---|
| auto / escalate / block | 60 / 16 / 4 | 387 / 107 / 6 |
| first-contact resolution | 75.0% (CI 64.5 to 83.2) | 77.4% |
| escalation rate | 25.0% | 22.6% |
| intent accuracy / macro precision | 0.988 / 0.991 (one error, at confidence 0.69, escalated) | 0.992 / 0.992 |
| retrieval hit rate (answerable) | 96.2% (n=53) | 93.3% (n=357) |
| routing accuracy | 75.0% | 77.2% |
| citations resolve / cite expected article | 100% / 73.3% | 100% / 72.6% |
| must-not-auto violations / private data | 0 / 0 | 0 / 0 |
| calibration, bins n >= 20 | passes; ECE 0.013 | passes; ECE 0.005 |
| decision log | 324 rows, 80/80 reconciled | 2006 rows, 500/500 |
| latency median / p95 (live) | 6.0 s / 13.7 s | 2.4 s / 16.8 s (run 1) |
| segment variation in routing accuracy | tier 14.2, region 26.5, fluency 22.4, length 28.6, channel 8.7 points | 7.4 / 7.5 / 2.6 / 11.7 / 6.5 |

Reading: business and technical figures are within a few points of the development set, which is
what the Dataset Guide predicts for a system that was not tuned to a number. The one class under
85 percent precision is account_access (0.80 on 4 tickets). The segment variation figures are
large because the segments are tiny at n=80 (a single ticket moves a 4-ticket segment by 25
points); they must be reported with Wilson intervals in the fairness audit, not as point
estimates. Two of the four grounding blocks are again narration sentences ("To address your
concern, I'd like to walk you through the steps", "We will look at the ticket further"); the
filler filter is left unchanged, because adjusting it on the validation set would be tuning
toward the set. They are recorded as the expected false-block rate (about 2 to 3 percent of
tickets) for the report.

## Single-ticket API (B-16, FR-18, 16 Sep 2026)

`python -m src.api` serves the same `SupportPipeline` the harness uses, on API_HOST:API_PORT
(default 127.0.0.1:8000), with Prometheus metrics on METRICS_PORT (8001) when prometheus_client
is importable. Endpoints: `POST /tickets` (one ticket object in the dataset schema, labels
optional; returns the same record the harness writes), `GET /decisions/{ticket_id}` (the
decision-log rows, so a grader can reconcile a hand-submitted ticket), `GET /health` (kill-switch
state, model, git version). The pipeline is built once at startup (embedder, NLI model, vector
store, neighbour memory: about 20 s).

Design points: `safe_process()` in `src/pipeline.py` is now the single failure boundary for both
the harness and the API: a component exception becomes an escalation with the reason and the
routing and validation rows are still written (A8, A11). Only a body that is not a JSON object is
rejected (422); an empty object, unknown channel or control characters go through
`normalise_ticket()` and produce a decision. The decision log's SQLite connection is opened with
`check_same_thread=False` and every use is serialised by a lock, because FastAPI runs sync handlers
on a thread pool (found by the test client; the same would have failed under uvicorn).

Pins: httpx 0.27.2 added to requirements.txt. httpx 0.28 removed the `app=` argument that
starlette 0.27's TestClient passes, so the API tests could not run; openai 1.12 accepts any httpx
below 1.0.

Live check (graders' steps 5 to 7, real models and provider): one ticket per channel returned in
150 ms to 1.4 s (cached classifications), the four trigger tickets in 5.6 to 11 s. Outcomes:
DEV-0005 escalate (feature request), DEV-0001 auto (deployment_failure, DOC-DEPLOY-003), DEV-0003
escalate (compliance), DEV-0023 auto (account_access, DOC-ACCT-001); TRIG-PII-001 **blocked** by
the grounding check (the model did not echo the name, so the PII check passed and an unsupported
sentence blocked instead), TRIG-INJ-001 escalated as instruction-like, TRIG-TONE-001 escalated on
low confidence (0.50), TRIG-GRND-001 auto-answered (the model did not invert the fact this time).
Which guardrail fires on a live model cannot be forced from the ticket text; each check's blocking
behaviour is proven deterministically in `tests/test_guardrails.py` and `tests/test_pipeline.py`,
and the API response always shows the verdict of every check that ran. A malformed body
(`{"channel": "fax"}`) returned 200 with an escalation under a generated UNKNOWN- id; `[1]`
returned 422. 140 tests pass.

## Continuous integration (B-13, 16 Sep 2026)

`.github/workflows/ci.yml` follows the Setup Guide template (ubuntu, Python 3.11, no key) with
two jobs. `test` runs the 141 tests; every test uses fakes for the provider, the embedder and the
NLI model, so no key or network is involved. `smoke-no-key` runs the real pipeline over the four
sample tickets with the provider disconnected (empty key, empty reply cache) and asserts that all
four escalate with a reason and that the decision log reconciles: the A11 check the graders run,
performed on every push. torch is installed from the CPU wheel index first, because the pinned
sentence-transformers pulls the default CUDA build otherwise; the two local models are cached
between runs.

The disconnected smoke run, done locally first, found two things. With the reply cache present,
tickets whose model replies were cached still auto-answered without a key; that is intended
(cached replies make runs reproducible), so the smoke job uses an empty cache directory. With an
empty cache, every ticket escalated with "provider unavailable: no API key configured", but the
fallback intent was unclear_request even though the neighbour vote, which needs no provider, had
the right intent. `classify()` now keeps the neighbours' intent on a model failure, with a
confidence scored as if the model had disagreed (0.99 after calibration on development tickets:
when the model disagrees with a strong neighbour vote, the neighbours are right 99% of the time);
the ticket still escalates through the classification_failed rule. Second local run: 4 of 4
escalated, intents feature_request, deployment_failure, compliance_request, account_access, 16
rows reconciled, 0 crashes. The metrics report counts these as failed tickets, which is correct:
the provider failed.

## Monitoring (B-12, 16 Sep 2026)

`src/monitoring.py` defines the metrics for the five dashboard views the Setup Guide names
(section 06): `tickets_processed_total{channel, outcome}`, `response_seconds` (histogram, buckets
0.25 s to 60 s), `guardrail_blocks_total{guardrail}`, `classification_confidence` (histogram in
tenths, where drift shows first), plus `pipeline_failures_total{stage}`. `observe()` is called
once per ticket inside `safe_process()`, so the harness and the API feed the same counters and
monitoring can never break processing (it swallows its own errors). The API serves the exposition
at GET /metrics and `python -m src.api` also starts the Prometheus server on METRICS_PORT (8001),
as the guide's snippet does; the harness writes a `metrics.prom` snapshot at the end of each run so
a batch run leaves the same evidence. `monitoring/prometheus.yml` is the guide's scrape config;
`monitoring/grafana_dashboard.json` is a six-panel dashboard (tickets per hour by channel and
outcome; auto-answered against escalated; latency p50 and p95; guardrail activations; confidence
distribution; failures by stage) written as a Grafana JSON model with PromQL over these metrics.
It was not opened in a running Grafana here; that is recorded as unverified.

Live check: with the API running, two tickets posted, both `:8000/metrics` and `:8001/metrics`
showed `tickets_processed_total{channel="email",outcome="escalate"} 1`,
`{channel="chat",outcome="auto_respond"} 1`, `response_seconds_count 2`,
`classification_confidence_count 2`. 145 tests pass.

## Fairness audit (B-14, NFR-06, 16 Sep 2026)

`python -m evaluation.fairness_audit --results <results.jsonl> [--results ...] --output <dir>`
segments a run by tier, fluency, ticket length (short under 120 characters), region and channel
and writes the Governance Framework section 3 table with 95% Wilson intervals
(`evaluation/results/fairness_audit/fairness_audit.md` and `.json`). Definitions are the metrics
report's: resolution rate = auto-responded and not blocked; quality score = routing accuracy
against the labels; variation = best segment minus this one. For each segment the script also
prints the facts behind a gap (share labelled escalate, share with no passage above the
threshold, mean length, mean confidence, retrieval hit rate) and leaves the Explanation column to
the author.

Results (quality score, max variation in points; "separated" means the segment's interval does
not overlap the best segment's):

| Group | Validation (n=80) | Development (n=500) | Separated segments |
|---|---|---|---|
| tier | 14.2 | 7.4 | none |
| fluency | 22.4 | 2.6 | none |
| ticket length | 28.6 | 11.7 | none |
| region | 26.5 | 7.5 | none |
| channel | 8.7 | 6.5 | none |

The 5-point condition is not met as a point estimate on any group except fluency on the
development set, but no gap is statistically established: every segment's interval overlaps the
best segment's on both sets (validation segments are 8 to 42 tickets; one ticket moves an
8-ticket segment by 12.5 points). Facts for the explanation: non-fluent tickets on the development
set retrieve the expected article less often (88.5% vs 94.8%, n=87 vs 270), the effect the
Governance Framework predicts, but their routing quality is within 2.6 points; on validation the
non-fluent gap (57.9% vs 80.3%, n=19) comes with a 100% retrieval hit rate and a higher share of
tickets labelled escalate (57.9% vs 34.4%), so it is the mixed-label ceiling, not retrieval.
Short tickets score higher because 36.7% of them get no passage above the threshold and escalate,
which matches their labels (46.9% labelled escalate vs 36.8% for long tickets). The interpretation
of these facts belongs to the author (report and Governance section 3). 148 tests pass.

## Governance (B-17, 16 Sep 2026)

`Docs/governance.md` follows the Governance Framework section by section with the run figures:
decision logging and the coverage check (2006/500, 324/80, 16/4 rows reconciled), the risk
register R-01 to R-10 (the framework's eight plus the two Stage 1 risks, ratings kept from
Stage 1, owners proposed from the interview roster and not yet agreed by anyone at CloudServe),
the fairness table from B-14, the five guardrails mapped to their implementation and measured
activations, the incident procedure written for an on-call engineer with the exact commands, the
kill switch answers, the declaration (drafted for the author's confirmation) and the AI
assistance declaration required by Project Instructions section 09.

Kill switch, made runtime: before B-17 the only switch was `KILL_SWITCH=true` read at start-up, so
stopping automatic answers needed a restart. Now a flag file (`KILL_SWITCH_FILE`, default
`storage/KILL_SWITCH`) is checked on every ticket at routing and again before an answer is
released, so a ticket that was past routing when the switch went on still escalates with its
draft in the package. `python -m src.killswitch on|off|status` writes who set it and when into
the file; `GET /health` reports the live state. Five tests cover the env setting, the flag file
without restart, the in-flight re-check, the CLI and the health endpoint. Exercised once for
real: status RUNNING, on (file written with user and UTC time), off. 152 tests pass.

Not built, recorded: an article-age rule that escalates when the cited article is older than a
threshold (R-05); a load test (R-07).

### First CI run: the clean-checkout failure (B-13, 16 Sep 2026)

The first push failed 26 tests on the runner with `FileNotFoundError: prompts/build/PR-02_classifier_v1.0.txt`
(and PR-03). The four build prompts were never in git: `.gitignore` carried the Python packaging
rule `build/`, which also matches `prompts/build/`. Locally everything passed because the files
were on disk. This is the failure the Build Specification predicts for step two of the graders'
procedure ("the README assumes something that exists only on the author's machine"); CI caught
it before the clean-clone rehearsal (B-19) would have. Fix: the rules are anchored to the repo
root (`/build/`, `/dist/`) and `prompts/build/` is committed. Every other ignored path was
reviewed: only Word lock files, run logs, storage and caches remain ignored. The same suite was
also run in a clean Linux container (python:3.11, CPU torch) to confirm nothing else is
platform-specific.

Second run (commit a12ba80, prompts committed): both jobs green, `test` 152 passed, `smoke-no-key` 4 of 4 escalated with the provider disconnected and the log reconciled on the runner.

## README and clean-clone rehearsal (B-19, 16 Sep 2026)

The README was rewritten from the graders' eleven-step procedure (Build Specification section
06) and then followed literally in a fresh clone on this machine (Windows, uv-provided Python
3.11.15, new virtual environment, pinned install, empty storage and reply cache). Findings, each
fixed before the rehearsal was repeated:

1. `uv venv` creates an environment without pip, so the README's fallback line for machines
   without a 3.11 interpreter now reads `uv venv --python 3.11 --seed .venv`.
2. The first clone sat in a deep temporary folder and `pip install` failed on Windows' 260-character
   path limit inside `jedi` (pulled in by the pack's Jupyter pins). The README now says to clone
   into a short path. The install from a short path succeeds; pip prints one harmless notice
   (uv-seeded `wheel` wants a newer `packaging` than the pinned 23.2).
3. `data/samples/` (one ticket per channel and the four trigger tickets as single JSON files for
   the README's curl commands) was created for B-19 and had not been committed, so the clone's
   curl calls sent empty bodies and received 422. Committed with this item; the 422 shape is in the
   troubleshooting list.

Rehearsal result in the clone: 152 tests pass; the API starts with the documented command
(models downloaded, 116 chunks indexed, 500-ticket neighbour memory loaded, startup complete);
one ticket per channel returned escalate, auto-respond, escalate, auto-respond with reasons; the
trigger ticket was blocked (grounding), its five log rows readable at `/decisions/TRIG-PII-001`,
metrics live; the kill switch turned on from the command line took effect on the next ticket
and showed in `/health`; the unattended run over the first 12 development tickets completed with
0 failures, 48 log rows reconciled 12/12; the fairness audit command ran; a search of every
commit for the key pattern found nothing. The validation set was not run again (run-once rule).
The clone, which held a copy of the key in its `.env`, was deleted afterwards.


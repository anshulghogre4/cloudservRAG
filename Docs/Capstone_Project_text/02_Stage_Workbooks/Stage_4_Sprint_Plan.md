FORWARD DEPLOYED AI ENGINEERING

Capstone Project

Stage Four: Sprint Plan

Deciding who does what, in what order, and what finished means

A plan is not a list of tasks. It is a statement of sequence, ownership and
completion that the team has actually agreed to.

| WEEK TWO · DAY ONE |
|---|

How to plan three weeks of work

You have already lost a third of the project to discovery and requirements, which is as it should be. What remains has to be sequenced carefully, because several parts of the build depend on others and the dependencies are not always obvious until you hit them.

Figure 1. The shape of the three weeks, including the compulsory requirements revision.

Three rules that make the difference

Every item has an estimate in hours and a priority. When you run short of time, and you will, the priority column is what decides for you rather than whatever felt urgent that morning.

Every item has a definition of done written before work starts. Written afterwards, it describes whatever happened to be produced.

The retrieval layer and the evaluation harness come early, not late. Almost everything else depends on one or the other, and leaving the harness until the end means discovering your results too late to act on them.

The full unattended run over the hidden evaluation set happens in week two, not week three. It is the gate the project turns on, and it always exposes problems that never appear when you are testing one ticket at a time.

1   Section one: your capacity

Before you plan anything, work out honestly how much time you actually have. Plans built on optimistic capacity fail in week two rather than week three, which is worse, because by then you have committed to an architecture that assumed the time existed.

| Week | Hours realistically available | Other commitments that week | Days you cannot work |
|---|---|---|---|
| Week one |  |  |  |
| Week two |  |  |  |
| Week three |  |  |  |

| On working aloneWorking individually removes the coordination overhead and replaces it with a different problem: nobody will notice when you have been stuck for six hours. Set yourself a rule that anything blocking you for more than an hour gets written down and either escalated or worked around, and check that list at the end of each day. |
|---|

2   Section two: the backlog

List every item of work. Estimate in hours rather than in vague sizes, because hours can be compared against the capacity you recorded above. Mark dependencies explicitly, because the order matters more when there is only one of you.

| ID | Item | Est. hours | Priority | Depends on | Definition of done |
|---|---|---|---|---|---|
| B-01 | Environment and dependency setup | 2 | Must | — | .venv created; requirements.txt and .env.example copied to root; .env in .gitignore; one real model call returns text (Setup Guide step 5); python -m pytest runs an empty suite. |
| B-02 | Data loading and normalisation | 3 | Must | B-01 | src/ingest.py turns a JSON ticket into the Ticket object; T-01 and T-02 pass; one ticket per channel printed normalised (Build Spec day-one checkpoint). |
| B-03 | Document chunking and embedding | 3 | Must | B-02 | 29 articles chunked by section with doc_id, section, applies_to metadata; embedded with all-MiniLM-L6-v2 into Chroma at CHROMA_PATH; chunk count logged; two chunk sizes tried and the choice recorded in docs/architecture.md. |
| B-04 | Vector store and retrieval | 3 | Must | B-03 | src/retrieve.py returns top-k passages with scores and ids; T-06 passes; hit rate on answerable dev tickets measured and ≥85% (T-07); relevance threshold chosen from dev-set scores and returns [] below it (T-08). |
| B-05 | Evaluation harness | 5 | Must | B-02 | python -m evaluation.harness --input <file> --output <dir> processes every ticket in any file with the schema; writes results.jsonl and metrics.json with the four metric groups from Build Spec §04; T-20 passes; runs on the dev set end to end with stub components. |
| B-06 | Intent and urgency classifier | 4 | Must | B-02 | src/classify.py uses PR-02; T-03 and T-04 pass; per-class precision and confusion matrix on dev set produced; calibration table produced (T-05); fallback reason "classification failed: provider unavailable" logged. |
| B-07 | Routing logic and thresholds | 2 | Must | B-06 | src/route.py decision table from Stage 3 FR-05; threshold chosen from the calibration curve and written in docs/architecture.md; T-09, T-10, T-11 pass; zero auto-responses on must_not_auto_respond tickets. |
| B-08 | Answer generation with citations | 4 | Must | B-04 | src/generate.py uses PR-03; T-12, T-13 pass; every citation resolves to a retrieved passage; disclosure line appended by code (T-19). |
| B-09 | Guardrails and validation | 4 | Must | B-08 | src/guardrails.py: private-data scan, forbidden-claims scan, grounding check, instruction-like escalation; each can block; T-15, T-16, T-17, T-24 pass; a hand-made trigger ticket is blocked (Build Spec day-four checkpoint). |
| B-10 | Decision logging | 3 | Must | B-07 | src/logging_store.py writes the Governance §1 record to SQLite for every stage; T-18 reconciles rows to tickets including failures; escalation package fields present (T-14). |
| B-11 | First full unattended run over the hidden evaluation set (THE GATE) | 3 | Must | B-05, B-09, B-10 | Harness run on the full development set with no intervention; every ticket answered or escalated; metrics.json produced; then one run on the validation set, date and run count recorded. |
| B-12 | Monitoring and dashboards | 2 | should | B-10 | Prometheus counters and histogram exposed on :8001; prometheus.yml committed; Grafana dashboard JSON committed if time allows. |
| B-13 | Continuous integration pipeline | 1 | Must | B-11 | .github/workflows/ci.yml runs pytest on push with no key; green on GitHub. |
| B-14 | Fairness audit | 2 | Must | B-11 | Metrics segmented by tier, region, fluency and ticket length from the validation run; table filled in Governance §3; variation from best computed. |
| B-15 | Report, video and submission package | 12 | Must | all | Report PDF in the prescribed order; 18–22 min video with success, escalation, guardrail block and the unattended run; workbooks and effort log exported; archive named per Submission Guide. |
| B-16 | Single-ticket API endpoint (FR-18) | 2 | Must | B-09 | src/api.py FastAPI /tickets accepts one ticket and returns the decision, draft or escalation package; one ticket per channel submitted by hand (Build Spec §06 steps 5–7). |
| B-17 | Governance framework | 3 | Must | B-14 | Risk register R-01 to R-08 with owners; incident procedure; kill switch (config flag that forces escalate, no deploy); declaration. |
| B-18 | PRD revision and Stage 5 log | 2 | Must | B-11 | PRD v2.0 with the changes in memory note (FR-05 applies-to rule, FR-18, feedback-loop exclusion, FR-02 fallback); Stage 5 Sections 1–4 filled; Section 5 written by you. |
| B-19 | README and clean-clone rehearsal | 2 | Must | B-13 | Fresh clone in an empty folder, README followed literally, harness and tests run; every missing step fixed. |

3   Section three: the week two plan in detail

| Day | What will be finished by the end of the day | Hours | Risk to this |
|---|---|---|---|
| Tue 15 Sept | Stage 4 saved; B-01 done; prompts committed; first commit of workbooks, analysis and prompts | 3 | Model provider key or rate limit not working; fix before anything else |
| Wed 16 Sept | B-02, B-03, B-04, B-05 skeleton: ingest, retrieval hit rate measured, harness runs end to end with stub classify and generate | 8 | Chunking choice eats time; cap at two configurations |
| Thu 17 Sept | B-06, B-07, B-08: classifier with calibration table, threshold chosen, cited drafts on twenty tickets | 8 | Small model's per-class precision below 85%; fallback is PR-02 v1.1 with examples, recorded in change history |
| Fri 18 Sept | B-09, B-10, B-16, then B-11: guardrails block a trigger ticket, log reconciles, endpoint works, full dev-set run unattended, then the single validation run; B-18 PRD revision started | 9 | Rate limits during the unattended run; backoff and cache must be in place before starting it |

4   Section four: the week three plan in detail

| Day | What will be finished by the end of the day | Hours | Risk to this |
|---|---|---|---|
| Fri 18 Sept (evening) | B-18 Stage 5 log complete except your reflection | 2 | None if B-11 ran |
| Sat 19 Sept | B-14 fairness audit, B-17 governance, B-13 CI green, B-12 metrics endpoint, B-19 clean-clone rehearsal, first video take | 9 | Clean clone exposes a missing step; that is what the rehearsal is for |
| Sun 20 Sept | B-15: report, second video take, workbooks exported, archive built, checklist, submit before 23:59 | 9 | Video overruns; record by noon, leave the afternoon for the report |

5   Section five: what you will drop if you run out of time

You will run out of time. Every student does. Deciding now what gets cut is far better than deciding in a panic on the final Wednesday, and it protects the parts that carry the most marks.

| Item | Cut order | Consequence of cutting it | What you will say about it in the report |
|---|---|---|---|
| FR-16 urgency ordering (Could) | 1st | No urgency-based queue order; flag still emitted by classifier | Deferred; Stage 1 §2 row 4 shows the need, left for the next iteration |
| Grafana dashboard (B-12 second half) | 2nd | Prometheus metrics exposed but no dashboard | Metrics endpoint exists; dashboard JSON not built in the time available |
| PR-07 model-scored rubric | 3rd | Satisfaction proxy from the human-scored sample only | Sample size and scorer stated; model scoring dropped |
| Second chunking configuration | 4th | One chunk size, chosen by reasoning not measurement | Stated as a limitation; the comparison is listed as next work |
| Hybrid search and few-shot classifier experiments | 5th | Embeddings only, zero-shot prompt | Recorded in Stage 5 Section 4 |

6   Section six: the daily check-in record

Ten minutes at the start of each day, answering the same three questions. Keeping this record is what makes your effort log accurate rather than reconstructed, and it is where you will notice a blocker that has quietly consumed two days.

| Date | Finished since yesterday | Doing today | Blocked by |
|---|---|---|---|
| 15 Sept | Stage 3 saved and synced; prompt files created | Stage 4 saved; B-01 environment; first commit | Provider key not yet verified |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

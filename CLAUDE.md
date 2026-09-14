# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Session start: load the pack context first

The course pack is mirrored as plain markdown under `Docs/Capstone_Project_text/` (generated from the `.docx` originals by `python scripts/extract_pack.py`; re-run it after editing any workbook). At the start of every session, before doing any task, read in this order:

1. `Docs/Capstone_Project_text/00_PROJECT_INSTRUCTIONS.md` and `00_CONTENTS.md` (rules, deadline, submission, AI-use rules)
2. `Docs/Capstone_Project_text/01_Read_First/` — `00_Start_Here.md`, `01_Project_Brief.md`, `02_Build_Specification.md`, `README.md`
3. Then whatever the current stage needs: `02_Stage_Workbooks/` (the workbook being filled), `03_Reference/` (Setup, Evaluation, Governance), `05_Datasets/` (Dataset Guide, Stakeholder Interviews), `04_Submission/`

Project-specific facts not in the pack: the user's deadline is **20 September 2026** (not 13 September). The user is doing all six stages in under a week, so prioritise the gate and the compulsory artefacts.

AI-use rule from Project Instructions §09 that governs Claude on this project: Claude may write code, debug, draft prompts, explain, and review writing. Claude must not invent discovery findings, or write the problem statement, the evaluation interpretation, or the reflection. Do the evidence work with real numbers and quotes, and ask the user to author those three pieces. Keep a list of AI-assisted work for the report's declaration.

Standing rules from the user (14 Sep 2026): no code until the reading and the stage workbooks are complete; invent nothing, every workbook entry traces to a transcript line or a count on the data; use only `development_tickets.json` for now. **Do not open, analyse or summarise `validation_tickets.json` until the app is built.** It is the genuine held-out test.

Pack inconsistencies to be aware of: the hidden set is described as 120 tickets in most places and "one hundred" in a few; the Project Brief §06 and Contents page describe `validation_tickets.json` as a run-once final set, while the Dataset Guide, Build Spec and README say the 80 validation tickets may be used freely and the graded set is hidden. Follow the Dataset Guide and Build Spec.

## What this repository is

An individual capstone project ("cloudservRAG") for a Forward Deployed AI Engineering course: an AI-assisted customer support system for a fictional client, CloudServe Solutions. The client asked for a chatbot; the assessed job is a ticket pipeline that classifies, retrieves from a documentation corpus, decides whether to auto-respond or escalate, generates cited answers, validates them with blocking guardrails, and logs every decision.

**There is no application code yet.** The repo currently holds only `README.md` and the course pack under `Docs/Capstone_Project/`. Everything below about layout and commands is the *prescribed* target from the pack, which the graders will test against. Read `Docs/Capstone_Project/01_Read_First/README.md` for the walkthrough; the `.docx` files are the authoritative specs (extract text with `python -c "import zipfile,re;print(re.sub(r'<[^>]+>','',zipfile.ZipFile('<file>.docx').read('word/document.xml').decode()))"`).

## The gate and the twelve acceptance criteria

Before anything else is marked, the repo is cloned onto a clean machine, the README is followed literally, and the evaluation harness is run unattended over a **hidden 120-ticket set** (same schema as the supplied tickets). Design every decision around that. Pass/fail criteria A1–A12 in `01_Read_First/02_Build_Specification.docx`, condensed:

- A1 runs from clean checkout via README commands. A12 tests run and pass with one documented command.
- A2 all four channels (`email`, `chat`, `docs_comment`, `forum`) normalise into one internal representation; missing fields, odd characters and empty bodies must not fail.
- A3 every ticket gets intent + urgency + a numeric confidence in [0,1]; classifier returns a defined fallback instead of raising, and records alternatives considered.
- A4 retrieval returns passages whose ids resolve to the real corpus; applies a relevance threshold and returns **nothing** rather than something irrelevant.
- A5 routing is deterministic (same ticket → same decision) with a threshold derived from data, and records a human-readable reason.
- A6 citations resolve to passages actually retrieved. Generation must separate ticket text from instructions (prompt-injection) and emit a parseable structure.
- A7 at least one guardrail can *block* (warn-only does not count) and runs on every response in the real run, never behind a disable flag.
- A8 every automated decision is persisted; logged decisions must reconcile exactly with tickets processed, including failures.
- A9 the harness processes the whole input file in one unattended run. **It must take `--input` and `--output` paths as arguments**, never a hardcoded filename.
- A10 that run emits a metrics report with no manual step (volume, business, technical, governance figures listed in Build Spec §04).
- A11 no crash on empty retrieval, provider timeout/outage, rate limiting, or malformed input. Graders will disconnect the model provider entirely; degrade and continue.

## Prescribed repository layout and commands

From `03_Reference/Setup_Guide.docx` §08 and `04_Submission/Submission_Guide.docx`. Adopt it as-is; the submission is checked against it.

```
src/            ingest.py classify.py retrieve.py route.py generate.py guardrails.py logging_store.py api.py
prompts/        build/  evaluation/  README.md (the versioned prompt register)
tests/
evaluation/     harness.py  results/ (dated output per run)
docs/           architecture.md
data/           small samples only
storage/        generated at runtime; in .gitignore along with .env
.github/workflows/ci.yml
```

Illustrative commands the pack expects the README to document (Python ≥ 3.10, always inside `.venv`):

```
python -m venv .venv && .venv\Scripts\activate          # Windows
python -m pip install -r requirements.txt
cp .env.example .env                                     # then fill OPENROUTER_API_KEY
python -m src.api                                        # FastAPI app; Prometheus metrics on :8001
python -m evaluation.harness --input <tickets.json> --output evaluation/results/
python -m pytest tests/ -v                               # single test: python -m pytest tests/test_x.py::test_name -v
```

The pinned `requirements.txt` and `.env.example` live in `Docs/Capstone_Project/06_Configuration/` and must be copied to the repo root. Env vars: `OPENROUTER_API_KEY`, `MODEL_NAME` (default `meta-llama/llama-3.1-8b-instruct` via OpenRouter), `EMBEDDING_MODEL` (`all-MiniLM-L6-v2`, local sentence-transformers), `CHROMA_PATH`, `DATABASE_URL` (SQLite), `CONFIDENCE_THRESHOLD`, `RETRIEVAL_TOP_K`. CI runs on Python 3.11 (`.github/workflows/ci.yml` template in Setup Guide §07); this machine has Python 3.13, so verify the pinned builds (langchain 0.1.0, chromadb 0.3.21, numpy 1.24, pandas 2.0.0) actually install before relying on them.

## Architecture

Six components in sequence — Ingest → Classify → Retrieve → Route → Generate → Validate — over three cross-cutting concerns: decision logging, guardrails, monitoring (Prometheus counters/histograms, Grafana). Keep the model provider and vector store behind swappable layers so tests can run with recorded responses and no API key. The pack recommends LangChain/LangGraph, Chroma (local, on disk), FastAPI, SQLite for the decision log.

Key behavioural rules that span components:
- **Escalation is a first-class outcome**, not a failure. Escalations carry the drafted summary and retrieved sources. Intents flagged `must_not_auto_respond` in the data (`compliance_request`, `feature_request`, `security_incident`, `unclear_request`) must always escalate; auto-responding to one is a governance failure.
- **Confidence must be calibrated** (stated confidence within 5 points of observed accuracy per bin), because the routing threshold is meaningless otherwise. Pick the threshold from development-set data and be able to show the curve.
- **Decision log record** (Governance Framework §1) minimum fields: decision_id, timestamp, ticket_id, stage (`classification | routing | generation | validation`), input_summary, model, prediction{value, confidence}, alternatives[], sources_used[{doc_id, score}], threshold_applied, action_taken (`auto_respond | escalate | block`), reason, guardrail_results{pii, grounding, tone}, prompt_version, requirement_ids. Every prompt has a version id (e.g. `PR-02 v1.3`) and every requirement an id (`FR-03`); log both so traceability is queryable.
- **Guardrails** (Governance §4): private data → block and escalate, never redact-and-send; grounding → block with unsupported claim flagged; instruction integrity; tone/scope (no refund or timeline commitments); confidence floor (missing confidence ≠ high confidence). Include a kill switch that stops auto-responding without a deploy.
- **Free tier only.** Rate limits are a design problem: backoff, queuing, and caching model responses (also makes runs reproducible).

## Data

All datasets are in `Docs/Capstone_Project/05_Datasets/`; `Dataset_Guide.docx` documents every field.

- `development_tickets.json` (500) and `validation_tickets.json` (80): same schema. Top-level `ticket_id, channel, subject` (empty for chat), `body, received_at, customer_id, customer_name, customer_tier` (enterprise/business/standard), `customer_region`, `language_fluency` (fluent/non_fluent), plus `labels{intent, urgency, expected_route, answerable_from_docs, expected_doc_ids[], must_not_auto_respond}` and `history{first_contact_resolution, resolution_time_minutes, csat_rating, escalated, repeat_contact}`. `history` is the human baseline to beat, not a target to reproduce. 22 intent classes, unevenly distributed.
- `documentation.json` (29 articles): `doc_id` (e.g. `DOC-AUTH-001`), `title, category, applies_to, content` (markdown with a fixed Symptoms / Common causes / Resolution steps / Notes structure), `related_docs[], last_reviewed_days_ago`. Chunk with that structure in mind; splitting inside a resolution sequence yields passages that retrieve well but read incomplete. Not every intent has an article, deliberately.
- `ground_truth_responses.json` (200): `reference_response`, `must_mention[]`, `must_not_claim[]` per ticket, usable for automatic checks.

**Known discrepancy:** the Chroma snippet in the Setup Guide reads `doc["id"]`, but the real field is `doc_id`.

Develop on the 500, check on the 80 as often as wanted, report validation figures as validation figures. Never tune toward a number; the graded set is unseen.

## Evaluation targets (Evaluation_Framework.docx)

Business: first-contact resolution 42% → ≥60%, escalation ≤30%, time to first reply → under 5 minutes (report median and p95). Technical: per-class precision ≥85% with confusion matrix, hallucination ≤5%, citation accuracy ≥95%, p95 latency <3s, availability ≥99.5% including provider failure. Governance (hard conditions): zero private data in outbound text, <5 percentage points quality variation across segments (tier, fluency, ticket length), 100% decision-log coverage, calibration within 5 points. Report business outcomes first and interpret them; a raw accuracy figure alone loses marks.

## Repo hygiene specific to this project

- Never commit `.env` or `storage/`; the submission is scanned for credentials, including git history.
- `Docs/` contains Word lock/temp files (`~$*.docx`, `~WRL*.tmp`); do not commit those.
- Commit steadily. Graders review the history for evidence of work across the three weeks rather than one final commit.
- Substantial model-generated code must be attributed in the report's AI-use declaration.
- Rehearse the graders' procedure early: clone into a fresh directory and follow the README from line one.

# Governance (B-17)

Follows the Governance Framework (`Docs/Capstone_Project/03_Reference/Governance_Framework.docx`)
section by section. Every figure comes from the runs recorded in `Docs/architecture.md`
(development set run 3, 500 tickets; validation run, 80 tickets, 16 September 2026). Owners
marked *proposed* are the CloudServe roles from the interviews; nobody at CloudServe has agreed
them, and until they do the accountable person for every item is the author (Anshul Ghogre).
Section 6 was drafted from the build evidence and confirmed by the author on 20 September 2026.

## 1. Decision logging

Every stage writes one row to an append-only SQLite log (`src/logging_store.py`, WAL journal,
synchronous FULL, no update or delete path in the code). The row carries the framework's minimum
record: decision_id, timestamp, ticket_id, stage (classification, routing, generation,
validation), input_summary (ticket text only, never customer fields), model name and version,
prediction value and confidence, alternatives, sources_used with scores, threshold_applied,
action_taken, reason, guardrail_results, prompt_version and requirement_ids, plus run_id and
latency. Rows can be read back per ticket (`GET /decisions/{ticket_id}`) or exported as JSONL.

Coverage check: the harness reconciles logged rows against processed tickets after every run and
writes the result into `metrics.json` and `run_summary.md`; a component crash still produces its
routing and validation rows. Development run 3: 2006 rows for 500 tickets, 500/500 with routing
and validation rows. Validation run: 324 rows for 80 tickets, 80/80. Provider-disconnected smoke
run: 16 rows for 4 tickets, 4/4.

## 2. Risk register

Likelihood and impact keep the ratings from the Stage 1 workbook where the same risk appears.
"Measured" means observed on the development and validation runs.

| ID | Risk | Likelihood | Impact | Mitigation in the design | Owner |
|---|---|---|---|---|---|
| R-01 | The system answers confidently and incorrectly | High if unchecked | Severe | Every factual sentence of a draft is verified against a retrieved passage (sentence cosine, lexical containment, NLI contradiction); unverifiable sentences block the draft (6 of 500 development, 4 of 80 validation). Citations are validated against the passages actually retrieved (100% resolve). Confidence is calibrated (ECE 0.005 / 0.013) and the 0.80 threshold escalates the rest. Compliance, security, feature and unclear requests never auto-answer (0 violations on 580 tickets). Every auto-reply carries the automated-draft disclosure. | Author; proposed Daniel Okonkwo (tier two reviews blocked and escalated drafts) |
| R-02 | Private data appears in an outbound response | Medium | Severe | Customer name and id are never placed in any prompt or log summary. Every draft is scanned for the ticket's own name and id and for key, email, phone and address patterns; a hit blocks and escalates, never redacts and sends. 0 detections on 580 tickets; the block path is proven by a trigger ticket in the tests. | Author; proposed Marcus Adeyemi (accountable for the autumn compliance review) |
| R-03 | A customer's input is treated as an instruction | Medium | High | Ticket text is placed inside `<ticket>` tags after the instructions in every prompt; the classifier flags instruction-like text and the router escalates it without drafting; an injection pattern check runs on the ticket; the attempt is logged with the input summary. Validation: 1 flagged, escalated. | Author |
| R-04 | Some customer groups receive worse answers | Medium | High | Fairness audit (`python -m evaluation.fairness_audit`) segments every run by tier, fluency, length, region and channel with Wilson intervals. Measured: no segment statistically separated from the best on either set; non-fluent tickets retrieve the expected article less often on the development set (88.5% vs 94.8%) with routing quality within 2.6 points. To be re-run on every evaluation run; the 5-point condition is a release criterion, not a one-off check. | Author; proposed Marcus Adeyemi |
| R-05 | The documentation the system relies on goes stale | Medium | High | The corpus is the 29 reviewed articles only (no private files). Every answer names the article ids it drew on, so a wrong answer points at the article to fix; `last_reviewed_days_ago` is kept as chunk metadata. Re-indexing is one command with no code change. Not built: an age threshold that escalates when the cited article is older than N days; recorded as a follow-up. | Proposed Ines Varga (documentation owner); author for the index |
| R-06 | The model provider becomes unavailable | Medium (free-tier pacing, 20 requests per minute) | Medium | Backoff on 408/429/5xx, 30 s timeout, on-disk reply cache; on failure the classifier keeps the neighbour vote's intent and the ticket escalates with the reason and a template summary; nothing crashes. Proven by the disconnected-provider smoke run (4/4 escalated, log complete) and repeated in CI on every push. | Author |
| R-07 | Latency degrades under load | Medium | Medium | Single process, 20 requests per minute pacing; measured p95 16.8 s live (2 to 3 provider calls per ticket), 0.5 s without the provider. Latency is a Prometheus histogram with p50 and p95 on the dashboard. Not load-tested; the NFR-01 3 s target is recorded as not met with a remote free-tier model. | Author |
| R-08 | Costs rise unexpectedly with volume | Low | Low | About $0.03 per 500 tickets on the paid llama-3.1-8b endpoint; replies cached by prompt hash; the provider key carries a $5 spending limit; ticket and failure counters make volume visible. | Author; proposed Marcus Adeyemi |
| R-09 | A never-auto ticket is answered automatically (Stage 1 risk) | Medium (17.4% of tickets) | Severe | Deterministic routing rule before the threshold; 0 violations on 580 tickets; the metric is in every run report. | Author |
| R-10 | The system makes a commitment about money or timing (Stage 1 risk) | Medium | High | Tone guardrail blocks any draft stating a refund issued, a fix on CloudServe's side or a delivery date; PR-03 forbids them; billing and data-residency policy remains an open question for the client. | Author; proposed Daniel Okonkwo |

## 3. Fairness audit

Produced by `python -m evaluation.fairness_audit --results evaluation/results/2026-09-16_validation/results.jsonl --results evaluation/results/2026-09-16_dev_full/results.jsonl --output evaluation/results/fairness_audit`.
Definitions: resolution rate = auto-responded and not blocked; quality score = routing accuracy
against the labels; 95% Wilson intervals; variation from best in points.

Validation run (80 tickets):

| Segment | Tickets | Resolution rate | Quality score | Variation from best | Interval overlaps best | Explanation |
|---|---|---|---|---|---|---|
| Enterprise customers | 8 | 87.5% | 87.5% (52.9 to 97.8) | best | yes | (author) |
| Business customers | 30 | 90.0% | 73.3% (55.5 to 85.8) | 14.2 pts | yes | (author) |
| Standard customers | 42 | 61.9% | 73.8% (58.9 to 84.7) | 13.7 pts | yes | (author) |
| Tickets in fluent English | 61 | 75.4% | 80.3% (68.7 to 88.4) | best | yes | (author) |
| Tickets in non-fluent English | 19 | 73.7% | 57.9% (36.3 to 76.9) | 22.4 pts | yes | (author) |
| Short tickets (under 120 characters) | 10 | 40.0% | 100% (72.2 to 100) | best | yes | (author) |
| Long or complex tickets | 70 | 80.0% | 71.4% (60.0 to 80.7) | 28.6 pts | yes | (author) |

Development run 3 (500 tickets): tier 7.4 points, fluency 2.6, ticket length 11.7, region 7.5,
channel 6.5; no segment separated from the best. Facts behind the gaps (for the author's
explanation): non-fluent tickets retrieve the expected article at 88.5% against 94.8% for fluent
(n=87 vs 270), the effect the framework predicts; on validation the non-fluent group has a 100%
retrieval hit rate but 57.9% of its tickets are labelled escalate against 34.4%, so the gap is
the mixed-label routing ceiling; short tickets score higher because 36.7% receive no passage
above the threshold and escalate, matching their labels. The full tables with intervals are in
`evaluation/results/fairness_audit/fairness_audit.md`.

## 4. Guardrails

All five run inside the pipeline on every response in every run, harness and API alike; none is
behind a disable flag (the NLI model can be switched off, in which case cosine and lexical
support still run and still block).

| Guardrail | What it checks (implementation) | What happens when it fires |
|---|---|---|
| Private data | The ticket's customer name and id, and patterns for keys, emails, phone numbers and addresses, in the draft (`check_private_data`). | Block; escalate with the draft attached to the engineer; logged as `pii: block`. Never redacted and sent. |
| Grounding | Every factual sentence against the retrieved passages: sentence cosine >= 0.50 or lexical containment >= 0.50, and NLI contradiction < 0.85; headings, symptom and cause lines and courtesy sentences are not claims (`Grounder.check`). | Block; escalate with the unsupported sentence quoted in the reason; logged as `grounding: block`. |
| Instruction integrity | Ticket text isolated in `<ticket>` tags after the instructions; the classifier's instruction-like flag and an injection pattern check on the ticket (`check_injection`). | Escalate before any draft is written (equivalent to a block: nothing is sent); the input summary is logged for review. |
| Tone and scope | Statements that a refund has been issued, that the issue is fixed on CloudServe's side, or a delivery date (`check_forbidden_claims`); PR-03 forbids them and requires the automated-draft disclosure. | Block; escalate; logged as `tone: block`. |
| Confidence floor | Routing is a decision table: kill switch, classification failed, instruction-like, never-auto intent, confidence below 0.80, no grounded source. A failed classification carries confidence 0.0 and its own rule. | Escalate with the rule and threshold in the reason and the log row. |

Measured activations: development run 3, 6 grounding blocks, 0 PII, 0 tone; validation, 4
grounding blocks, 0 PII, 0 tone; 1 instruction-like escalation. Blocked drafts travel to the
engineer inside the escalation package, never to the customer.

## 5. Incident response

Written for an on-call engineer who has never seen the system. Commands run from the repository
root inside the virtual environment. Times are design targets from the build, not measured
incidents.

| Step | What to do | Who | How long |
|---|---|---|---|
| 1. Detect | A wrong, leaked or committed answer is reported by an agent or customer, or the dashboard shows guardrail blocks, failures or p95 latency climbing (`monitoring/grafana_dashboard.json`; `GET /health`). Note the ticket id. | Whoever sees it (agent, tier two, on-call) | Minutes |
| 2. Contain | Stop automatic answers: `python -m src.killswitch on <your name>`. Confirm with `python -m src.killswitch status` or `GET /health` (`kill_switch: true`). Every ticket now escalates with the reason "kill switch". | On-call engineer or support manager | Under one minute; effective on the next ticket |
| 3. Assess | `GET /decisions/<ticket_id>` (or `evaluation/results/<run>/results.jsonl`) shows every stage: intent and confidence, passages and scores, prompt version, guardrail verdicts, reason. Decide whether it is a prompt, threshold, article or guardrail failure. | On-call engineer with tier two | 15 to 30 minutes |
| 4. Notify | Tell the support manager (proposed: Marcus Adeyemi) what was sent, to whom, and that automatic answers are stopped; for private data or a commitment, notify compliance the same day. | On-call engineer | Within one hour |
| 5. Remediate | Prompt: new version in `prompts/README.md`, re-run `python -m evaluation.harness` on the validation set, compare `run_summary.md`. Threshold or guardrail: change `.env`, same re-run. Article: hand the doc id to the documentation owner (proposed: Ines Varga), re-index. Then `python -m src.killswitch off`. | Author or maintaining engineer | Hours to a day |
| 6. Review | Record the incident, its trigger and the change in the revision log (Stage 5 pattern); add a trigger ticket to `tests/fixtures/trigger_tickets.json` so CI checks it from then on. | Author with tier two | One hour, within a week |

### The kill switch

| Question | Answer |
|---|---|
| What is the mechanism? | Two: `KILL_SWITCH=true` in the environment (read at start-up), and a flag file (`KILL_SWITCH_FILE`, default `storage/KILL_SWITCH`) created with `python -m src.killswitch on`. The router checks it on every ticket before any other rule, and the pipeline checks it again before an answer is released. No deployment or restart. |
| Who is authorised to use it? | Anyone with shell access to the host: the on-call engineer and the support manager (proposed: Marcus Adeyemi). Turning it off is the same command with `off` and should follow step 5. |
| How long until it takes effect? | The next ticket, under one second; the file check costs one `exists()` call per ticket. |
| What happens to tickets in flight? | A ticket past routing is re-checked before release: its draft goes into the escalation package instead of to the customer. Tickets already answered before the switch are not recalled; they are identifiable in the log by timestamp and `action_taken`. |
| How is it tested? | `tests/test_route.py::test_kill_switch_flag_file_takes_effect_without_restart`, `tests/test_pipeline.py::test_kill_switch`, `tests/test_pipeline.py::test_kill_switch_file_while_in_flight_escalates_before_release`, `tests/test_killswitch.py` (CLI on/status/off), `tests/test_api.py::test_health_reports_kill_switch`; run on every push by CI. |

## 6. The declaration

| Statement | Position |
|---|---|
| This system must never ... | send a customer a statement that is not in the support documentation, a commitment about money or dates, another customer's private data, or any automatic answer to a compliance, security, feature or unclear request. |
| The mechanism that enforces that is ... | blocking guardrails that run on every draft in every run (grounding with contradiction check, private data, tone) plus a deterministic never-auto rule before the confidence threshold, an automated-draft disclosure on every reply, an append-only decision log that reconciles to the ticket count, and a kill switch that stops automatic answers without a restart. |
| The most likely way it could still cause harm is ... | a fluent, cited answer to a ticket that a person should have handled: 95 of 114 development routing errors are auto-answers on tickets labelled escalate whose text matches auto-labelled tickets, and the labels' policy on billing and data residency is an open question; second, a correct citation of an article that has gone stale. |
| We would not deploy this without first ... | a pilot in which agents review every blocked and a sample of auto-answered drafts, the client's decision on billing and data-residency routing, first-reply timestamps to measure the SLA, a load test against the latency target, and the fairness audit re-run on pilot tickets with intervals that separate. |

## 7. AI assistance declaration (Project Instructions section 09)

Work in this repository done with Claude (Anthropic, Claude Code), reviewed by the author:

- Code: every module under `src/`, `evaluation/`, `tests/`, `scripts/`, the CI workflow, the
  monitoring configuration and dashboard, with the author directing each backlog item, the
  method (research, tests first, measurement before adoption) and the decisions recorded in
  `Docs/architecture.md`.
- Prompts: PR-01 to PR-07 drafted with Claude; versions and change history in `prompts/README.md`.
- Documents: `Docs/architecture.md` (decision record), this governance document (sections 1 to 5
  and 7 from build evidence; section 6 drafted for the author's confirmation), the Stage 5
  revision log sections 1 to 4 (tables from build evidence; section 5 written by the author), the
  Stage 2 workbook's synchronisation to PRD version 2.0 (21 cells, 17 September), the Stage 1, 3
  and 4 workbook figures and quotes supplied as evidence and written into the workbooks by the
  author, the report figures (`report/make_figures.py`, every value read from the recorded runs)
  and the report's narrative (`report/report.html`, drafted from the workbooks, the build record
  and the run outputs, edited by the author), and the pre-populated effort-log draft (dates and
  tasks from the commit history and workbook dates; hours entered by the author).
- The problem statement is the author's own. The evaluation interpretation, the lesson of the
  requirements revision and the reflection (report sections 7.4, 9 and 10.3; Stage 5 section 5)
  were drafted by Claude on the submission day at the author's request and edited by the author;
  this is declared in the report rather than presented as unaided work.

FORWARD DEPLOYED AI ENGINEERING

Capstone Project

Stage Two: Requirements

The product requirements document you write from your findings

Everything here must trace back to your discovery workbook. A requirement that
cannot be traced is a preference, and preferences do not belong in a PRD.

| WEEK ONE · DAYS FOUR AND FIVE |
|---|

What this document is and why it matters

A product requirements document states what is being built, for whom, and how anyone will know when it is finished. It is not a design document and it is not a plan. It should be specific enough that two different engineers reading it would build broadly the same thing, and general enough that it does not dictate how they do it.

You will write version one at the end of week one and you will revise it during week two. That revision is compulsory. Write this version with the expectation that parts of it will turn out to be wrong, and record your assumptions clearly so that you can tell which ones failed when they do.

Figure 1. The requirements document is expected to change once building starts.

1   Document control

| Field | Value |
|---|---|
| Version | 1.0 |
| Written by | Anshul Ghogre |
| Date | 07/09/26 |
| Status | Draft for review |
| Approved by | Self |

2   The problem in one paragraph

Copy across the paragraph you wrote at the end of your discovery workbook. If you find yourself wanting to improve it as you copy, go back and improve it in the workbook first, so that the two do not drift apart.

| Problem statement |
|---|
| CloudServe asked for a chatbot to answer the easy tickets so the team can handle the hard ones. The evidence says the team is not short of answers; it is short of a way to reach them. Seven in ten tickets already have their answer written in the twenty-nine support articles, yet more than a third of those tickets are still handed to tier two, because agents cannot find the right article quickly and fall back on memory and private notes. Nearly half of what reaches tier two could have been closed at tier one, and it arrives with no summary, so the engineer re-reads the thread and asks the customer questions they have already answered. That double handling, not just the wait, is what customers mark down: tickets passed on score 2.6 out of 5 against 3.4 for those closed first time, and almost four in ten of them come back a second time. Enterprise customers, who hold the stricter agreement, are currently served slowest. The problem is that known answers are not reaching agents or customers at the first touch, and that every hand-over loses the context the next person needs. Any fix must say nothing rather than say something wrong, must always pass security, compliance, feature and unclear requests to a person, and must be able to explain every decision it makes. |
|  |

3   Who this is for

Describe each group of users separately. A requirement that serves everybody usually serves nobody particularly well.

| User group | What they need from this system | What they currently do instead | How you will know it worked for them |
|---|---|---|---|
| Customers raising tickets | 1) A correct answer at first touch, within the 2 h agreement. 2) Honesty when the system is unsure. 3) To know when a reply is automated. | 1) Wait until next day. 2) Search the docs themselves, find it half the time. 3) Re-answer questions on escalation. | 1) Median time to answer under 5 min for auto-answered tickets. 2) Repeat contacts down from 21.6%. 3) Satisfaction proxy above 4.0. |
| Tier one support agents | 1) A draft with the source article attached. 2) No more searching by keyword. 3) Not to carry the blame for a wrong automated answer. | 1) Answer from memory and private files. 2) Escalate when not confident. 3) Sort by age. | 1) Known-type tickets closed without human work. 2) Time per remaining ticket falls (Sofia's "half of every ticket"). 3) No wrong answer sent. |
| Tier two and specialist agents | 1) Escalations that carry a summary, the sources checked, and what was uncertain. 2) Only genuinely hard tickets. | 1) Receive the raw ticket. 2) Re-read and re-ask. 3) Half their queue is tier-one work. | 1) Every escalation carries the context package. 2) Answerable tickets reaching tier two fall from 138 of 500. |
| The head of support | 1) FCR up, escalation down, without headcount. 2) Every automated decision explainable for the autumn compliance review. 3) No worse service for enterprise. | 1) Reports a red SLA number. 2) Has never analysed the ticket data. | 1) FCR toward 60 to 65%, escalation toward 30%. 2) A decision log that reconciles to every ticket. 3) Tier gap not widened. |
| Documentation owner | to see which article each answer came from. | finds out a year late that agents do not use the articles. | every answer and escalation names its article ids. |
|  |  |  |  |

4   Functional requirements

Each requirement gets an identifier, a statement, a priority and a link back to the discovery evidence that produced it. The identifiers matter because your specifications, your prompts and your test cases will all refer to them.

Use the priority scale consistently. Must means the system is not acceptable without it. Should means it is expected but could be deferred with a stated consequence. Could means it would add value if time allows. Will not means it has been considered and deliberately excluded, and recording those is as useful as recording the rest.

| ID | Requirement | Priority | Discovery evidence | Acceptance criteria |
|---|---|---|---|---|
| FR-01 | The system shall accept tickets from email, chat, docs comment and forum and normalise them into one internal record that keeps the original text and channel. | Must | Section 2 row 2 (four channels; all chat subjects empty) | One ticket from each channel processes without error; empty subject, missing field and unusual characters do not crash it. |
| FR-02 | The system shall assign an intent (one of the 22 classes) and an urgency (high/medium/low) to every ticket, with a confidence between 0 and 1, and record the alternatives considered. | must | Section 1 Marcus row (no breakdown known); Section 3 step 2; Section 2 rows 3, 4 | Every processed ticket has intent, urgency, confidence in [0,1] and at least one alternative; a fallback class is returned when classification fails. |
| FR-03 | The system shall find the passages of the 29 support articles relevant to the ticket and return them with article ids and scores. | Must | Section 2 row 8; Section 1 Ines and Sofia rows; Section 3 step 4 | For answerable development tickets, the expected article appears in the returned set at least 85% of the time; every returned id resolves to a real article. |
| FR-04 | The system shall return no passages, rather than irrelevant ones, when nothing in the corpus meets the relevance threshold. | Must | Section 2 row 8 (143 non-answerable); Section 1 Ines row (novel incidents) | For feature_request and unclear_request tickets, retrieval returns nothing or the ticket is escalated; never an invented citation. |
| FR-05 | The system shall decide auto-respond or escalate using a confidence threshold derived from development data, deterministically, and record a plain-language reason. | Must | Section 3 step 6; Section 1 Marcus row (explainability); Section 4 row 7 | Same ticket twice gives the same decision; every decision has a reason a support manager can read; the threshold and its derivation are documented. |
| FR-06 | The system shall always escalate compliance, security, feature and unclear requests regardless of confidence. | Must | Section 3 row 6; Section 5 risk 5; Section 1 Daniel and Sofia rows | Zero auto-responses on tickets labelled must_not_auto_respond in the development set. |
| FR-07 | The system shall draft an answer only from the retrieved passages, with a citation on each factual claim, and say plainly when it does not know. | Must | Section 1 Sofia row (draft plus page); Section 3 step 5; Section 5 risk 1 | Every citation resolves to a passage actually retrieved for that ticket; drafts with no retrieved passage contain no factual claims. |
| FR-08 | Every escalation shall carry a summary of the ticket, the predicted intent, the retrieved article ids, the draft, and a statement of what the system was unsure about. | Must | Section 1 Daniel row; Section 3 step 7; Section 1 disagreements row 1 | Every escalated record in the log contains all five fields. |
| FR-09 | The system shall scan every outbound draft for private data (names, ids, keys, addresses) and block and escalate if found. | Must | Section 5 risk 2; Section 5 source 1 (name and id on every ticket) | A ticket engineered to elicit a name or id is blocked, not sent; the block is logged. |
| FR-10 | The system shall block any draft that makes a claim unsupported by the retrieved passages, or that states a refund has been issued, the issue is fixed on CloudServe's side, or a delivery date. | Must | Section 5 risks 1 and 6; Section 5 source 3 (the three universal forbidden claims) | A draft containing any forbidden phrase is blocked; a sample of 50 drafts reviewed shows hallucination at or below 5%. |
| FR-11 | The system shall write every automated decision (classification, routing, generation, validation) to a persistent log with input summary, prediction, confidence, alternatives, sources, threshold, action, reason, guardrail results, prompt version and requirement ids. | Must | Section 1 Marcus row (compliance review); Section 4 row 7 | Logged decisions reconcile exactly with tickets processed, including failures. |
| FR-12 | Every automated reply shall state that it was drafted automatically and that a person will confirm if needed. | Should | Section 1 Ravi row | Every auto-response contains the disclosure line. |
| FR-13 | The system shall process an entire ticket file in one unattended run, taking input and output paths as arguments, and produce a metrics report with the volume, business, technical and governance figures. | Must | Build Specification A9, A10; Section 5 source 1 (hidden set) | One documented command; every ticket produces an answer or a logged escalation; the report file appears without manual steps. |
| FR-14 | The system shall continue processing when retrieval returns nothing, the model provider times out, is rate limited, or is unavailable, and when input is malformed | Must | Section 5 risk 10 (provider dependency); Build Specification A11 | With the provider disconnected the run completes, every ticket escalates with a logged reason, nothing crashes. |
| FR-15 | The system shall separate ticket text from its own instructions so customer text cannot redirect it. | Must | Section 5 risk 9 | A ticket containing instruction-like text is answered or escalated normally and the attempt is logged. |
| FR-16 | The system shall order or flag tickets by predicted urgency so high-urgency tickets are not left behind older low-urgency ones. | Could | Section 2 row 4; Section 1 Ravi row; Section 1 nobody-said row 3 | Output includes an urgency flag per ticket; ordering by urgency is available in the batch output. |
| FR-17 | The system will not answer feature requests, roadmap or timing questions, or draft from agents' private answer files. | Will not | Section 1 Ines and Daniel rows; Section 5 source 3 | Covered by FR-04, FR-06 and the corpus being the 29 articles only. |

5   Non-functional requirements

These describe how well the system must do the things it does. They are frequently what distinguishes a demonstration from something that could actually be deployed.

| ID | Category | Requirement | How it will be verified |
|---|---|---|---|
| NFR-01 | Latency | 95th percentile end-to-end time per ticket under 3s (chat customers abandon; Ravi). | Harness timing on the validation run. |
| NFR-02 | Availability | 99.5%; with the provider down, the system escalates rather than stops. | Induced outage test in the harness. |
| NFR-03 | Accuracy | Intent precision ≥85% per class; citation accuracy ≥95%; hallucination ≤5%. | Classification report and confusion matrix; citation check; 50-sample human review with two assessors. |
| NFR-04 | Privacy | Zero private data in outbound text. | Automated scan of every draft plus manual sample. |
| NFR-05 | Auditability | 100% of decisions logged; log reconciles to tickets processed; each entry names prompt version and requirement ids. | Count log rows vs tickets after the run. |
| NFR-06 | Fairness | Under 5 percentage points variation in resolution quality across fluency, tier and region. | Segmented metrics from the harness, compared with the human baseline in Stage 1 Section 2 rows 9, 10. |
| NFR-07 | Cost | Free tier only; responses cached; rate limits handled with backoff. | Full run completes within the free allowance; no paid calls. |
| NFR-08 | Calibration | Stated confidence within 5 points of observed accuracy per band. | Calibration table from the Evaluation Framework. |
| NFR-09 | Determinism | Same input, same routing decision. | Run a ticket twice, compare. |
|  |  |  |  |

6   What is deliberately out of scope

Recording what you are not building is one of the most valuable things a requirements document does, because it is the section that prevents an argument in week three.

| Not building | Why not | What would have to change for this to be reconsidered |
|---|---|---|
| Replacing agents. | Sofia says there is more than enough work; the aim is fewer hand-overs. | never within this project. |
| Automatic answers for compliance, security, feature and unclear requests. | labelled must-never; Daniel and Sofia. | only with a client policy change and a human-in-the-loop design. |
| Any commitment about refunds, fixes or dates. | contractual (Daniel); forbidden on all 200 reference answers. | never |
| Writing or editing documentation. | Ines owns it; the system reports which article was used so she can fix the right thing. | if coverage gaps are found, hand a list to Ines. |
| Consolidating agents' private files. | unreviewed and stale; not in the pack. | if Ines reviews and merges them into the knowledge base. |
| Live connectors to email, chat, docs and forum systems. | the pack provides tickets as files with a channel field; the gate tests file processing. | after the pilot, once channel behaviour is measured. |
| Measuring true time to first reply. | no field exists; resolution time is the proxy. | when CloudServe supplies first-reply timestamps. |
| Translating non-fluent tickets. | no evidence it is needed; the fairness audit will say. | if NFR-06 fails on the fluency segment. |
| A feedback loop that learns from agent corrections | The pack contains no correction data; the architecture diagram names it as a cross-cutting concern but nothing in the datasets supports it | After a pilot, once agents have corrected real drafts |

7   Assumptions and their consequences

Every assumption you are making is a place where this document could turn out to be wrong. Listing them now is what makes the revision in stage five a considered update rather than a scramble.

| Assumption | Why you believe it | What happens if it is false | How you will find out |
|---|---|---|---|
| The 29 articles are accurate. | Ines, reviewed on rotation. | grounded answers are confidently wrong. | citation accuracy review and Ines's article ids on every answer. |
| The hidden set has the same distribution as the development set. | Dataset Guide says so. | threshold and per-class precision shift. | validation run and per-class report. |
| The labels' expected route is the right policy for billing and data residency. | labels mark them answerable; forbidden-claim rule covers the risk. | auto-answers on contractual matters. | must_not_claim guardrail hits; open question to client. |
| A small free-tier model can classify 22 intents at ≥85% precision. | intents are distinct and the corpus is small. | routing rests on bad input. | classification report on development data; fallback to a lighter method if needed. |
| Confidence can be calibrated well enough for a threshold. | Evaluation Framework provides the method. | threshold is meaningless. | calibration table. |
| The system's "first contact resolution" (auto-answered, not blocked) is comparable to the human FCR baseline. | same definition, closed without a human | business figures are not comparable. | state the definition in the metrics report and the report caveat. |
| Non-fluent tickets will retrieve worse than fluent ones. | Governance Framework warning; shorter bodies (127 vs 142 chars). | no fairness action needed. | NFR-06 segmented results. |
| Free-tier rate limits allow 80 to 120 tickets in one unattended run with backoff and caching. | Build Specification says rate limits are a design problem. | gate fails. | full unattended development-set run before the validation run. |
| Resolution time is an acceptable proxy for time to first reply. | only field available. | the SLA claim in the report is weaker. | ask the client; caveat in the report. |

8   Success measures

State the measures this system will be judged on, with the baseline and the target for each, and say who is accountable for reporting them.

| Measure | Baseline | Target | Measured how | Reported by |
|---|---|---|---|---|
| First contact resolution | 42% (client), 43.8% (dev data) | 60% or better | Harness: auto-answered and not blocked ÷ processed | You, in the metrics report and report §7 |
| Time to first reply | 8 to 12 hours | Under 5 min for automated replies; median and p95 | Harness timing | you |
| Customer satisfaction | 3.2 (client), 2.97 (dev data) | 4.0 proxy | Rubric scoring of a sample; state size and scorer | You |
| Escalation rate | 58% (client), 56.2% (dev data) | 30% or lower | Harness: escalated ÷ processed | You |
| Repeat contacts | 21.6% (dev data) | Halved | Cannot be observed post-launch in this project; report the baseline and the mechanism (escalation with context) | You, with caveat |
| Classification precision | none | 85% per class | Classification report | You |
| Citation accuracy | none | 95% | Citation check | You |
| Hallucination rate | None | 5% or lower | 50-sample two-assessor review | You |
| Private data occurrences | none | 0 | Outbound scan | You |
| Cross-group variation | fluency gap in human data: FCR 45.8 vs 43.2 | under 5 points | Segmented harness metrics | you |

9   Open questions

The things you do not yet know. Each one needs an owner and a date by which it will be resolved, otherwise it will still be open in week three.

| Question | Why it matters | Owner | Resolve by |
|---|---|---|---|
| where does the 8 to 12 h first-reply figure come from, and can timestamps be supplied? | the SLA metric cannot be baselined. |  |  |
| Should billing and data-residency tickets auto-respond (labels) or always escalate (Daniel)? | scope of FR-06. |  |  |
| What are the enterprise agreement terms? | NFR-06 and Marcus's warning. |  |  |
| Who operates the kill switch, and how fast must it act? | governance framework requires one |  |  |
| Who scores the CSAT proxy rubric, and on what sample size? | target 4.0 needs a stated method. |  |  |
| Does CloudServe want replies labelled as automated? | Ravi wants it; Marcus did no say. |  |  |
| Will Ines consolidate the private files into the knowledge base? | coverage could grow beyond 71.4%. |  | Out of scope |
| Does the system need a single-ticket API endpoint in addition to the batch harness? | Build Spec §06 says graders submit one ticket per channel and one guardrail-trigger ticket by hand before the batch run |  | recorded as FR-18 in the Stage 5 revision log |

| The review before you move onRead your finished PRD and ask, for each requirement in turn, whether an engineer who had not attended any of your interviews could build it from what is written. Where the answer is no, the requirement is not finished. This check takes twenty minutes and it is the single highest-value thing you can do at the end of week one. |
|---|

FORWARD DEPLOYED AI ENGINEERING

Capstone Project

Build Specification

What the system must actually do to count as working

This is the part of the project that is not negotiable. The documents you write
exist to make this build sound. They do not substitute for it.

| PASS OR FAIL · NO PARTIAL CREDIT |
|---|

What this document contains

01   The gate   What has to work before anything else is marked

02   The twelve acceptance criteria   Each one testable, each one pass or fail

03   What each component must do   Component by component requirements

04   The end to end run   The single test the whole project turns on

05   Build checkpoints   Where you must be by each day of week two

06   How it will be tested   The exact procedure that will be run against your code

07   Cost and free tier use   What you are expected to spend, which is nothing

08   What does not count as working   The shortcuts that will be found

01   The gate

This project produces a working piece of software. Everything else in the pack exists to make that software worth building and possible to trust, but the software itself is the deliverable, and it is checked first.

Before your discovery workbook, your requirements document, your report or your video are read, one question is asked of your repository. It is checked out onto a machine that is not yours, your own instructions are followed, and your evaluation harness is asked to process the full validation set in a single unattended run. What happens next depends on how far it gets.

Figure 1. The gate has three outcomes rather than two.

The three outcomes

| Outcome | What it means | Consequence |
|---|---|---|
| It runs cleanly | The system starts from your documented instructions and processes the whole set unattended. | Marked in full across all six areas, with no cap. |
| It runs but needs help | The system starts and processes a substantial share, but the run needs intervention or some tickets fail. | Implementation marks are capped. Every other area is marked in full and is unaffected. |
| It will not start | The system cannot be launched at all from your documented instructions. | You are given one 48-hour repair window for setup and documentation only, then it is re-run. |

| Why there is a repair windowA submission that fails to start usually fails for an environmental reason: a package that was never pinned, a step that lived in your head rather than your README, a path that existed only on your machine. Three weeks of legitimate work should not be lost to that. The window covers setup and documentation only, not changes to behaviour, and the repair must be visible in your commit history. |
|---|

What is never counted against you

Your system depends on an external model provider. If that provider is unavailable, throttling the free tier, or degrading while your work is being assessed, that is not a defect in your work and it will not reduce your marks. Acceptance criterion A11 asks you to handle exactly this condition, and a system that degrades gracefully during an outage gains credit rather than losing it. This is also why you record the full run in your video: where live assessment is impossible, that recording is the evidence.

Where the marks sit once you are through the gate

| Area | Weight | What earns it |
|---|---|---|
| Implementation | 35% | The system itself: whether it works, how it is built, and whether someone else can run and read it. |
| Evaluation | 20% | Honest measurement, business outcomes alongside technical ones, results interpreted. |
| Discovery and problem framing | 15% | Evidence gathered from the transcripts and the data, and a problem statement that follows from it. |
| Requirements and traceability | 10% | Requirements specific enough to build from, with a visible chain to the code. |
| Governance and risk | 10% | Decisions logged, risks assessed with real mitigations, fairness tested. |
| Communication | 10% | A video and report a non-technical stakeholder could follow. |

Implementation is the largest single component and it is the one with a gate in front of it. Plan your three weeks accordingly.

Figure 2. Roughly where your hours should go. Half the project is the build.

02   The twelve acceptance criteria

Each of these is checked directly. Each is pass or fail. There is no credit for a criterion that is nearly met, because a system that nearly ingests four channels ingests three.

| # | Criterion | How it is judged |
|---|---|---|
| A1 | The system runs from a clean checkout by following your README, using the commands you documented. | Cloned into an empty directory, instructions followed literally. It either starts or it does not. |
| A2 | Tickets from all four channels are ingested and normalised into one internal representation. | A ticket from each channel is passed in. All four are handled without channel-specific breakage. |
| A3 | Every ticket is classified for intent and urgency, with a numeric confidence attached. | The output carries a class and a confidence between zero and one. |
| A4 | Retrieval runs against the supplied documentation corpus and returns identifiable source passages. | The returned sources resolve back to real passages in the corpus, not to invented references. |
| A5 | Routing applies a threshold you set, and the same input produces the same routing decision. | Run the same ticket twice. The decision does not change. |
| A6 | Generated answers carry citations that resolve to the passages actually retrieved. | Citations are followed and checked against the text they claim to support. |
| A7 | At least one guardrail can block a response, and does so when triggered. | A ticket engineered to trigger it is submitted. The response is blocked rather than sent. |
| A8 | Every automated decision is written to a persistent log with the required fields. | The log is opened. Decisions are counted against tickets processed and must reconcile. |
| A9 | The system processes the full evaluation set in a single unattended run. | Started once and left alone. No manual intervention, no restarts, no skipped tickets. Then re-run against a file you have never seen. |
| A10 | That run produces a metrics report without further manual work. | A file appears containing the measures defined in the evaluation framework. |
| A11 | The system handles failure without crashing: no retrieval hit, provider timeout or outage, rate limiting, malformed input. | Each condition is induced, including disconnecting the model provider entirely. The system degrades and continues rather than stopping. |
| A12 | Tests run with a single documented command and pass. | The command in your README is run. The suite executes and reports. |

| A9 is the one that fails peopleSystems that work beautifully on a ticket at a time frequently collapse on the fortieth consecutive ticket, because of a rate limit, an unhandled encoding, an empty retrieval result or a memory leak. Run the full set end to end early in week two, not at the end of week three. It is the single most useful thing you can do to protect your grade. |
|---|

03   What each component must do

The architecture in the Project Brief describes the shape of the system. This section states the behaviour each part must exhibit. How you achieve it is your decision and your design choices are what carry the implementation marks.

Ingest

Accepts tickets from email, live chat, documentation comments and the community forum.

Produces one normalised internal representation regardless of source channel.

Preserves the original text and the channel, because both matter downstream.

Handles missing fields, unusual characters and empty bodies without failing.

Classify

Assigns an intent category and an urgency level to every ticket.

Attaches a numeric confidence that reflects the actual probability of being correct.

Returns a defined fallback rather than raising an exception when it cannot classify.

Records the alternatives it considered, not only the option it chose.

Retrieve

Searches the supplied documentation corpus and returns ranked passages with scores.

Returns identifiers that resolve to the real corpus, so citations can be verified.

Applies a relevance threshold and returns nothing rather than something irrelevant.

Chunking strategy is a decision you make, justify and are able to explain.

Route

Decides between answering automatically and escalating, using a threshold you determined from data.

Is deterministic: the same input yields the same decision.

Records the reason for the decision in language a support manager could read.

Escalations carry the drafted summary and the retrieved sources with them.

Generate

Produces an answer grounded in the retrieved passages, with citations attached to claims.

States plainly when it does not know rather than filling the gap.

Separates the ticket content from your instructions so that customer text cannot redirect the system.

Produces output in a defined structure your code can parse reliably.

Validate

Runs on every generated response before it is released, not only in testing.

Checks at minimum for private data and for claims unsupported by the retrieved sources.

Can block. A guardrail that only warns is not a guardrail.

Records what it checked and what it found, whether or not it blocked.

04   The end to end run

This is the test the project turns on, so it is worth being precise about what it involves.

| You do not hold the set your grade depends onYour pack contains 500 development tickets and 80 validation tickets. The final assessment runs against a hidden set of 120 tickets drawn from the same population, which is not distributed and which you will not see. Your harness must therefore accept an input path rather than a hardcoded filename, because it will be pointed at that file after you submit. A harness that only works against your own copy of the data cannot be run, and that is treated as a failure of A9. |
|---|

What is required

A single documented command starts the run, taking an input path and an output path as arguments.

Every ticket in the supplied file is processed, however many there are.

Nobody intervenes: no restarts, no manual retries, no skipping a ticket that misbehaves.

Every ticket produces either a sent answer or a logged escalation. None are silently dropped.

Every decision is written to the log.

A metrics report is produced at the end without further manual work.

The run completes in a reasonable time. If it takes six hours, say why in your report.

What the metrics report must contain

The exact format is yours to choose, but these figures must be present and must be calculated by your code rather than by hand afterwards.

| Group | Figures required |
|---|---|
| Volume | Tickets processed, answered automatically, escalated, blocked by guardrails. |
| Business | First contact resolution, mean and median response time, escalation rate. |
| Technical | Classification precision and recall per class, retrieval hit rate, latency at median and 95th percentile. |
| Governance | Decisions logged, guardrail activations by type, any private data detections. |

A worked interpretation of these figures belongs in your report. The report explains what the numbers mean; the system produces them.

A reasonable command structure

This is illustrative rather than prescriptive. What matters is that it is one command and that it is documented in your README.

| # start the APIpython -m src.api# run the full hidden evaluation, unattendedpython -m evaluation.harness --input data/validation_tickets.json \ --output evaluation/results/# run the testspython -m pytest tests/ -v |
|---|

05   Build checkpoints

Week two is the build. If you reach the end of it without a system that runs end to end, you will spend week three finishing the build instead of doing the governance, measurement and presentation that carry the remaining marks, and the project will suffer twice over.

Figure 3. Where you should be at the end of each day of week two.

| By the end of | What must work | How you check it |
|---|---|---|
| Day one | Ingest. A ticket from each of the four channels comes through normalised. | Print the normalised object for one ticket from each channel. |
| Day two | Retrieval. The corpus is embedded and search returns passages you can trace back. | Query with a known question and confirm the returned passage is the right one. |
| Day three | Classification and routing. Confidence scored, threshold applied, decision logged. | Run twenty tickets and read the log. Every decision has a reason. |
| Day four | Generation and guardrails. Cited answers produced, at least one guardrail blocking. | Submit a ticket engineered to trigger the guardrail and confirm it blocks. |
| Day five | The full chain, unattended, over the full evaluation set. | Start it, leave the room, come back to a metrics report. |

| If you are behind at day threeCut scope rather than cutting the end to end run. A system that handles two intent categories properly and runs the full set unattended passes the gate. A system that handles eight categories beautifully but has never processed more than five tickets in sequence does not. Your sprint plan has a section for deciding what to drop; use it. |
|---|

06   How it will be tested

This is the procedure that will be run against your submission. Run it against yourself first, on a machine that is not the one you built on.

Your repository is cloned into an empty directory on a clean machine.

Your README is opened and its instructions are followed literally, in order, without improvisation.

The environment is created and dependencies installed exactly as you describe.

Configuration is set from your .env.example, with a working key substituted in.

The system is started using your documented command.

One ticket from each channel is submitted and the responses are inspected.

A ticket engineered to trigger a guardrail is submitted, and the block is confirmed.

The full full validation run is started and left alone until it finishes.

The metrics report and the decision log are opened and reconciled against each other.

The test suite is run with your documented command.

The repository is searched for credentials and for attribution of code you did not write.

| The rehearsal that saves projectsClone your own repository into a fresh directory and work through the eleven steps above yourself, in your second week rather than your third. Roughly half of all submissions fail at step two because the README assumes something that exists only on the author's machine. |
|---|

07   Cost, and what you are expected to spend

This project is designed to be completed at no cost. Every component of the stack is free or open source, and the model providers named in the setup guide have free tiers sufficient for the work. You are not expected to spend your own money, and no part of the assessment advantages a student who does.

| Constraint | What it means for you |
|---|---|
| Free tiers only | Build and test within the free allowance of your chosen provider. Nothing in the acceptance criteria requires paid capacity. |
| Rate limits are a design problem | Free tiers throttle. Handling that with backoff, queuing and caching is part of the engineering, not an obstacle to it. |
| Caching is encouraged | Cache model responses during development. It saves your allowance, makes runs reproducible, and is good practice regardless. |
| Local models are permitted | If you prefer to run a small model locally rather than call an API, that is an acceptable design choice. Justify it in your report. |
| No advantage for spending | Marks are for engineering judgement, not model capability. A well-built system on a small free model out-scores a thin one on an expensive model. |

| If cost becomes a blocker, say so earlyIf you find yourself unable to complete a run within a free allowance, raise it rather than paying for capacity or quietly reducing your scope. It is a solvable problem and almost always indicates a design issue, such as calling the model where a cache or a rule would do. |
|---|

08   What does not count as working

Each of the following has been submitted before and each was found. They are listed so that nobody discovers the boundary by accident.

| This | Why it fails |
|---|---|
| A notebook that produces good output when cells are run in the right order by hand. | It is not a system. A9 requires an unattended run started by one command. |
| A demonstration on five hand-picked tickets. | The hidden set is one hundred tickets and it is processed in full. |
| Guardrails present in the code but disabled by a flag during the run. | A7 requires the guardrail to block. Code that could block does not satisfy it. |
| Citations generated as plausible-looking references rather than resolved from retrieval. | A6 is checked by following the citation to the passage. |
| Retrieval that returns something for every query regardless of relevance. | Returning nothing is a valid and often correct answer. Always returning something hides failure. |
| A decision log written only for the tickets that succeeded. | A8 reconciles logged decisions against tickets processed. Gaps are visible immediately. |
| A README written from memory after the build rather than tested against a clean checkout. | Step two of the test procedure is where this is discovered. |
| Tuning against the hidden evaluation set until the numbers improve. | That measures how well you fitted one hundred tickets, not how the system handles unseen ones. |

None of this is intended to be adversarial. It is intended to be clear, so that you spend your three weeks building something that genuinely works rather than something that demonstrates well and falls over on contact with the full set.

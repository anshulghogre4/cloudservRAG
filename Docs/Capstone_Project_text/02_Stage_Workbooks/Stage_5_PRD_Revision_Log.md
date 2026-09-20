FORWARD DEPLOYED AI ENGINEERING

Capstone Project

Stage Five: Revision Log

Recording what your requirements got wrong and why

You are required to revise your requirements document at least once during the
build. This is where you record what changed and what prompted the change.

| WEEK TWO INTO WEEK THREE · COMPULSORY |
|---|

Why this is compulsory

A requirements document written before any code exists is a set of educated guesses. Some of those guesses will be wrong, and building is how you find out which ones. A student that reaches the end of three weeks with an unchanged PRD has either been extraordinarily lucky or has stopped consulting the document, and the second is far more common than the first.

This log is not a confession. It is evidence that you were paying attention. The students who score well here are the ones who can point to a specific thing they discovered while building, explain how it contradicted an assumption they had written down, and show what they changed as a result.

Figure 1. The revision sits in the middle of the build, not at the end.

| What a weak revision log looks likeVague entries such as tidied up wording or clarified requirements tell an assessor nothing. A strong entry names the requirement, states what it said before, states what it says now, identifies the specific thing that prompted the change, and says who agreed to it. |
|---|

1   Section one: revision summary

| Field | Value |
|---|---|
| New version number | 2.0 |
| Date of revision | 16/09/26 |
| Who carried out the revision | Anshul Ghogre |
| Who reviewed and agreed it | Self (individual project). FR-06 scope and plan policy would need Daniel; recorded as open. |
| Number of requirements changed | 10 (FR-02, FR-04, FR-07, FR-10, FR-11, FR-16, NFR-01, NFR-06, NFR-07, NFR-08) |
| Number of requirements added | 1 (FR-18) |
| Number of requirements removed | 0 |

2   Section two: the changes

One row per change. Be specific about the trigger; that column is what distinguishes a considered revision from a tidying exercise.

| Requirement ID | What it said in version one | What it says now | What prompted the change | Agreed by |
|---|---|---|---|---|
| FR-02 | The system shall assign an intent (one of 22), an urgency and a confidence in [0,1] to every ticket and record the alternatives considered (the language model was the implied classifier). | Intent is the weighted vote of the 7 nearest labelled development tickets, using the same embedder as retrieval. The model supplies the instruction-like flag and the reason; its intent is kept as the first alternative when it disagrees. Confidence is the calibrated combination of neighbour share and agreement. On provider failure the fallback reason reads "classification failed: provider unavailable" so outages are not counted as unclear_request. | classify_check (B-06): model alone 0.710 accuracy, 0.798 macro precision (below the 85% target); neighbour vote 0.992 leave-one-out (0.980 excluding near-duplicates); when both agree (70.4% of tickets) they are 100% correct. | Self |
| FR-04 | Return no passages rather than irrelevant ones when nothing meets the relevance threshold (implying the threshold detects non-answerable tickets). | The threshold (0.40) removes only off-topic text. Non-answerable tickets are the router's job: never-auto intents and the confidence threshold. | retrieval_check (B-04): non-answerable tickets' median top score 0.635 vs 0.644 for answerable, indistinguishable. 0.40 cuts 100% of unclear_request and keeps 97.8% of answerable tickets. | Self |
| FR-07 | Draft only from retrieved passages, with a citation on each factual claim, and say plainly when it does not know. | Every factual sentence is verified against a retrieved passage (sentence cosine >= 0.50 or lexical containment >= 0.50, and NLI contradiction < 0.85). Supported uncited sentences get the citation attached by code. An unverifiable sentence blocks the draft. | generate_check (B-08): 38 of 70 factual sentences in v1.2 drafts had no citation. guardrail_check (B-09): the known inverted fact (DEV-0404, "without a restart") passed chunk-level cosine. | Self |
| FR-10 | Block any draft with a claim unsupported by the retrieved passages or stating a refund issued, a fix on CloudServe's side, or a delivery date. | Adds the NLI contradiction check. States that headings, Symptoms and Common-causes lines, and courtesy or narration sentences are not claims. Accepts an expected false-block rate of 2 to 3% of tickets (blocked drafts escalate with the draft attached). | Development run 1 (B-11): 43 blocks, 37 false (premise was a heading or a cause line; filler scored as claims). Validation run: 4 blocks, 2 filler; not tuned on the validation set. | Self |
| FR-11 | Persist every automated decision; acceptance: logged decisions reconcile exactly with tickets processed, including failures. | Unchanged requirement; the harness now reconciles the log after every run, writes the result into metrics.json and run_summary.md, and writes routing and validation rows itself when the pipeline raises. | Development run 1 (B-11) showed the harness never called reconcile(): A8 was asserted, not checked. Run 3: 2006 rows, 500/500 reconciled; validation: 324 rows, 80/80. | Self |
| FR-16 | Could: order or flag tickets by predicted urgency so high-urgency tickets are not left behind. | Could: an advisory urgency flag per ticket and an optional ordering switch in the harness (--sort-urgency). The requirement states that predicted urgency is near the majority baseline and must not be relied on for SLA decisions. | classify_check (B-06): urgency accuracy 0.46 (model) and 0.49 (neighbours) against a 0.45 majority baseline. | Self |
| NFR-01 | 95th percentile end-to-end time per ticket under 3 s. | p95 under 3 s for the local pipeline (measured 0.53 s with cached provider replies). Provider round trips are reported separately: validation p95 13.7 s, development live run p95 16.8 s. The 3 s end-to-end target is recorded as not achievable with a remote free-tier model making 2 to 3 calls per ticket. | First live 20-ticket run (B-10): median 9.9 s, p95 20 s. | Self |
| NFR-06 | Under 5 percentage points variation in resolution quality across fluency, tier and region. | Adds ticket length and channel (Evaluation Framework segments). Segment figures must be reported with Wilson intervals; a point estimate on a segment of a few tickets is not evidence either way. | Validation run (n=80): 28.6 points on ticket length and 26.5 on region from segments of a handful of tickets; development run (n=500): 11.7 and 7.5. | Self |
| NFR-07 | Free tier only; responses cached; rate limits handled with backoff; no paid calls. | The paid llama-3.1-8b endpoint on OpenRouter at about $0.03 per 500-ticket run (project total under $0.25); replies cached on disk; 20 requests per minute pacing with backoff. | B-06: the :free variant is capped at 50 requests a day and cannot complete a run. | Self |
| NFR-08 | Stated confidence within 5 points of observed accuracy per band. | Per band with at least 20 tickets; smaller bands are reported but not judged. | Development run 1 (B-11): the test failed on a 2-ticket band (stated 0.69, observed 1.0). Run 3 and validation pass; ECE 0.005 and 0.013. | Self |
| FR-18 (new) | Not present. | Must: a single-ticket API endpoint that returns the decision and the draft or the escalation package for one ticket. Planned as B-16; not yet built at this revision. | Build Specification section 06: graders submit one ticket per channel and a guardrail-trigger ticket by hand before the batch run. | Self |
|  |  |  |  |  |

3   Section three: assumptions that turned out to be wrong

Go back to the assumptions section of your version one PRD. For each assumption, say whether it held. The ones that did not are the most interesting part of your report.

| Assumption from version one | Did it hold? | What you found instead | What you changed because of it |
|---|---|---|---|
| The 29 articles are accurate. | Not falsified. | The grounding check caught model errors (inverted facts), never an article error. Not independently tested. | Nothing. |
| The hidden set has the same distribution as the development set. | Held for the validation set. | Validation vs development: FCR 75.0% vs 77.4%, routing 75.0% vs 77.2%, intent 0.988 vs 0.992. | Nothing. |
| The labels' expected route is the right policy for billing and data residency. | Partly failed. | 95 of 114 development routing errors are auto-answers on tickets labelled escalate whose text matches auto-labelled tickets (35 duplicate-body groups with mixed labels); the label ceiling on routing accuracy is 0.938. | Routing accuracy is reported against that ceiling; the policy question stays open for Daniel. |
| A small free-tier model can classify 22 intents at >= 85% precision. | Failed. | 0.798 macro precision, 0.710 accuracy on the development set. | FR-02: neighbour vote is the primary intent signal. |
| Confidence can be calibrated well enough for a threshold. | Held, after changing the method. | Platt scaling degenerated to a step function; smoothed histogram binning gives ECE 0.005 (development) and 0.013 (validation). | NFR-08 wording (bands with n >= 20). |
| The system's first-contact resolution is comparable to the human baseline. | Partly. | With perfect routing the labels allow at most 62% FCR (oracle run); the system reports 77% because it auto-answers tickets labelled escalate; repeat contacts are not observable offline. | The metrics report states the definition; the caveat goes in the report. |
| Non-fluent tickets will retrieve worse than fluent ones. | Did not hold on the development set. | 2.6 points variation (routing 0.725 vs 0.742, n=120 non-fluent). | Nothing; translation stays out of scope. |
| Free-tier rate limits allow 80 to 120 tickets in one unattended run. | Held only with the paid endpoint. | The :free variant caps at 50 requests a day; the paid endpoint completes 500 tickets for about $0.03. | NFR-07. |
| Resolution time is an acceptable proxy for time to first reply. | Untested. | No first-reply timestamps exist in the data. | Nothing; caveat stands. |
| (Not listed in v1) Embedding similarity is enough to check grounding. | Failed. | Chunk-level cosine passed the inverted fact and blocked 31 of 57 correct drafts. | FR-07 and FR-10: sentence-level checks plus NLI contradiction. |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

4   Section four: what you decided not to change

Some things will look wrong during the build and turn out to be right, or right but not worth the cost of changing. Recording those decisions is as valuable as recording the changes.

| What looked wrong | Why you left it | What it would have cost to change | Revisit when? |
|---|---|---|---|
| Hybrid BM25 plus RRF search (architecture diagram) instead of dense only. | Measured worse: hit@1 0.894 vs 0.905, hit@5 0.972 vs 0.989. | A day of work plus a dependency. | If the hidden-set hit rate falls under 85%. |
| FR-05 plan-applicability rule (escalate when the article's plan excludes the customer's tier). | Routing accuracy 0.784 to 0.756, 28 expected auto-answers lost; PR-03 rule 7 handles plan wording in the draft. | A routing rule and tests. | When the client states plan policy. |
| Learned answerability (neighbour vote on answerable_from_docs) as a routing signal. | Routing accuracy 0.784 to 0.762. | Model and tests. | With a larger labelled set. |
| Capping chunks per article in retrieval so more articles reach the drafter. | Hit rate 0.933 to 0.938 at best (two tickets). | A retrieval change and re-tuning. | If the drafter is found ignoring a second article. |
| Few-shot classifier prompt (architecture diagram) instead of zero-shot PR-02. | Neighbours became the primary signal; a few-shot example leaked verbatim into an answer in PR-03 v1.1. | Prompt rework and re-measurement. | If the neighbour memory is unavailable in production. |
| PostgreSQL decision log (architecture diagram) instead of SQLite. | SQLite with WAL and synchronous FULL is append-only and meets A8. | A database server in the clean-checkout test. | At pilot. |
| Guardrails AI hub validators instead of in-house guardrails. | Needs openai >= 1.30 against the pinned stack; 23 to 45 extra packages; model downloads at first use. | Dependency surface in the graders' clean install. | As production hardening after the pilot. |
| A verbatim bypass around the NLI check for drafts that copy a cause line word for word. | A negation flip would use the same path and pass unchecked. | Hallucination risk. | With a stronger NLI model. |
| Adjusting the filler filter after the validation run blocked two courtesy sentences. | Adjusting on the validation set would be tuning toward the set. | Nothing. | After a pilot, with new tickets. |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

5   Section five: the reflection

Answer these in full sentences. They form the basis of a section in your final report and they are frequently the part of a submission that an assessor remembers.

| Question | Your answer |
|---|---|
| What did you most misunderstand about the problem when you wrote version one? | That the requirements I could not measure were still requirements. Version one assumed a small free-tier model would classify 22 intents at 85 per cent precision, that a retrieval threshold could tell me no article existed, that three seconds was a software target, and that embedding similarity was a grounding check. All four were beliefs without a number beside them; the first measurement of each (71 per cent accuracy, a feature request scoring like the article it asks to change, a 10-second provider round trip, an inverted fact passing the check) overturned it within an hour. The one I most misunderstood was latency: two or three provider calls per ticket make it a provider target, not a pipeline target; the local pipeline runs in 0.5 s. |
| Which piece of discovery work would have caught it earlier? | Timing one live provider call during the setup step would have moved the 3-second target from the requirements to the risk register a week earlier. Running the classifier prompt on 50 development tickets before writing FR-02 would have shown the 71 per cent figure before the neighbour vote was an afterthought. Plotting the top retrieval score for answerable against non-answerable tickets, which took ten minutes in B-04, would have rewritten FR-04 before it was written. |
| What would you do differently if you started this project again on Monday? | Run the end-to-end harness on 20 real tickets on the first build day and keep it running after every item. The first full run found three defects that 106 passing unit tests had not: an intent accuracy of exactly 1.0 that was the classifier finding each ticket in its own memory, a reconciliation check the harness never called, and 43 blocked drafts of which 37 were wrong. Set up continuous integration before the build rather than after; it caught the four ungitted prompt files on the first push, and I would not have. Put a measurement plan beside every assumption in the PRD, with the number that would falsify it, so the revision log is planned rather than reconstructed. |
| What is still uncertain, and what would you need to resolve it? | Whether the automatic answers on tickets the labellers would have escalated (95 of 114 routing disagreements) are good answers or confident ones; only a pilot with agents reviewing a sample can settle it. Whether the 2 to 3 per cent false-block rate of the grounding guardrail is acceptable to agents, which needs the same review of blocked drafts. Whether the non-fluent retrieval gap (88.5 against 94.8 per cent on the development set) is real, which needs a larger sample with intervals that separate. And the client's policy on billing and data-residency tickets, which needs Daniel and Marcus, not more data. |

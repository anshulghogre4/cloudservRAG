FORWARD DEPLOYED AI ENGINEERING

Capstone Project

Project Brief

An intelligent customer support system for CloudServe Solutions

The full brief. The client situation, the system you are being asked to design,
the targets you are held to, and the constraints you must work within.

| THE CORE DOCUMENT |
|---|

What this document contains

01   The client and the situation   Who CloudServe are and what is going wrong

02   The request and the real problem   Why the chatbot answer is the wrong one

03   What you are required to produce   The six stages and their outputs

04   The system you are designing   High level and low level architecture

05   How the system decides   Routing, confidence and escalation

06   The data you have been given   Four files and what each is for

07   How success is measured   Business, technical and governance targets

08   Risk and governance obligations   What must be true before this could go live

09   Technical constraints   The stack and the rules around it

10   Frequently misunderstood points   The things people get wrong every cohort

01   The client and the situation

CloudServe Solutions sells cloud infrastructure and developer operations tooling to other businesses. They employ around one hundred and fifty people, they serve just over two hundred corporate customers, and they turn over roughly twelve million dollars a year. They are not a start-up and they are not an enterprise. They are at the awkward size where the informal processes that worked at forty customers have quietly stopped working at two hundred.

Where the pain is showing up

Their support function is the part that has broken first. The numbers below are the ones their head of support brought to the first meeting, and they are the numbers against which your work will eventually be judged.

| What they measure | Where they are now | Where they need to be | Why it matters to them |
|---|---|---|---|
| Tickets received each week | Over 500 | No target; volume is growing | Volume is rising faster than headcount |
| Average time to first reply | 8 to 12 hours | Under 2 hours | Their service agreement promises two hours and they are breaching it |
| Resolved on first contact | 42 per cent | 65 per cent or better | Everything else has to be picked up a second time by someone more senior |
| Customer satisfaction | 3.2 out of 5 | 4.2 out of 5 | Renewal conversations have started going badly |
| Support team attrition | Rising | Stable | Two experienced agents left last quarter and cited workload |

The four channels

Tickets arrive through four different routes, and they do not behave the same way. This matters more than it first appears, because a solution that works beautifully for one channel can be actively unhelpful in another.

Email, which carries the longest and least structured messages and the highest proportion of genuinely complex problems.

Live chat, where customers expect an answer within minutes and abandon the conversation if they do not get one.

Comments raised against the API documentation, which are usually narrow, technical and answerable from existing material.

The community forum, where other customers sometimes answer first and the support team is arriving late to a conversation already in progress.

| The first thing worth noticingA large share of the incoming volume is made up of questions that have already been answered somewhere in CloudServe's own documentation. Nobody at CloudServe has said this to you, and it is not written down anywhere in the brief. It is the sort of thing you are expected to find for yourself during discovery, and finding it changes what you build. |
|---|

02   The request and the real problem

CloudServe asked for a chatbot. If you build a chatbot, you will have satisfied the request and failed the assignment, and it is worth being precise about why.

A chatbot is a delivery mechanism. It is a way of putting an answer in front of a person. It says nothing about where the answer comes from, whether the answer is correct, what happens when the answer is not known, who is accountable when the answer is wrong, or whether the underlying reason the question was asked has been addressed at all. CloudServe named the mechanism because the mechanism is the part they could picture.

Your job is to work backwards from the mechanism to the outcome. The outcome CloudServe actually needs is that fewer tickets require a human being, that the ones which do reach a human arrive with useful context attached, and that customers stop waiting half a day for an answer that already existed in the documentation.

Figure 1. Discovery is a loop rather than a phase. You stop when new interviews stop surprising you.

The questions worth asking before you design anything

The mind map below sets out the six areas your discovery work needs to cover. The Stage 1 workbook turns each of these into tables you are required to complete, so treat this diagram as the map and the workbook as the route.

Figure 2. The six areas of discovery. Each becomes a section of the Stage 1 workbook.

03   What you are required to produce

The project moves through six stages. Each one has a named output, and each output is the input to the next stage. The table below is the definitive list, and the workbooks in folder two give you the structure for each item.

| Stage | What you produce | How it is used next | Due by |
|---|---|---|---|
| 1. Discovery | Completed discovery workbook: interview notes, evidence tables, a problem statement supported by that evidence. | Every requirement in your PRD must be traceable back to something recorded here. | End of week one, day three |
| 2. Requirements | Product requirements document, version one. Scope, users, requirements, acceptance criteria, out of scope. | Your specifications and prompts are written directly from it. | End of week one |
| 3. Prompt library | Specification documents and a versioned prompt library covering build, review and evaluation prompts. | This is what you actually implement against. | Week two, day two |
| 4. Sprint plan | Backlog with estimates, owners and an explicit definition of done for each item. | It governs the order and the pace of the build. | Week two, day one |
| 5. Build and revision | Working system, evaluation results, and a revised PRD with a completed revision log. | The revision log is assessed directly. | End of week two into week three |
| 6. Submission | Video, report, workbooks with effort log, and source code archive. | This is what is marked. | End of week three |

| Traceability is assessed, not assumedWhen your work is reviewed, someone will pick a requirement from your PRD at random and ask you which piece of discovery evidence produced it. Then they will pick a prompt and ask which requirement it serves. If the chain breaks, the marks in that section go with it. Keep the references in as you write rather than reconstructing them afterwards. |
|---|

04   The system you are designing

The architecture below is a starting point rather than a specification. You are expected to justify it, adapt it where your discovery findings warrant, and be able to explain any departure from it. Following it exactly without explaining why is not really designed anything.

The high level view

Six processing components sit in sequence, and three concerns cut across all of them. The cross-cutting concerns are the part most often left until the end, and leaving them until the end is the reason they end up bolted on rather than built in.

Figure 3. The high level architecture. Six components in sequence over three cross-cutting concerns.

| Behaviour is specified separatelyThis section describes the shape of the system. What each component must actually do, criterion by criterion, is set out in the Build Specification, and that document is what your software is tested against. Read it alongside this one. |
|---|

What each component is responsible for

| Component | Responsibility | The failure mode to design against |
|---|---|---|
| Ingest | Normalise incoming tickets from four channels into one internal representation. | Channel-specific quirks leaking into every downstream component. |
| Classify | Predict intent and urgency, and produce a calibrated confidence score alongside them. | A confidence number that does not actually correspond to the probability of being right. |
| Retrieve | Find the documentation passages that bear on this ticket. | Retrieving something plausible but irrelevant, which is worse than retrieving nothing. |
| Route | Decide whether to answer automatically or escalate, and record why. | A threshold chosen because it looked reasonable rather than because it was measured. |
| Generate | Draft an answer grounded in the retrieved passages, with citations. | Fluent text that is not actually supported by the sources cited. |
| Validate | Check the draft for private data, unsupported claims and tone before release. | Guardrails that only run in testing and are quietly disabled for the demonstration. |

The low level view

Underneath the six components sit three layers. Separating them is what makes the system testable, because it lets you swap the model provider or the vector store without rewriting the parts that depend on them.

Figure 4. The three layers and the components within each one.

Notice that the decision log sits in the persistence layer alongside the metrics rather than being treated as an afterthought. Every decision your system takes has to be reconstructable months later, and that requirement shapes the schema you design on day one.

05   How the system decides

The routing decision is where most of the value and most of the danger sits. Answer too readily and you send confident nonsense to paying customers. Escalate too readily and you have built an expensive system that has not reduced anybody's workload.

Figure 5. The routing decision tree. Each branch must be logged with the reason it was taken.

The thresholds are yours to set and yours to defend

The figure shows a confidence threshold of 0.80. That number is illustrative. Part of your work is to determine what the threshold should actually be, using your evaluation data, and to be able to explain the trade-off you accepted when you chose it.

| If you set the threshold | What happens | Who pays for it |
|---|---|---|
| Too low | The system answers questions it does not really understand. | The customer, who receives a wrong answer, and the support team, who then handle a complaint as well as the original question. |
| Too high | Almost everything escalates and automation rates stay flat. | CloudServe, who have paid for a system that did not change their numbers. |
| About right | The system answers what it can defend and escalates the rest with context attached. | Nobody, which is the point. |

| Escalation is a feature, not a failureA ticket that escalates with a correct summary, the relevant documentation already attached and a clear statement of what the system was unsure about is significantly more valuable to an agent than a raw ticket. Students who treat escalation as the losing branch tend to build systems that hide their own uncertainty. |
|---|

06   The data you have been given

Four files sit in the datasets folder. They serve different purposes and mixing them up will invalidate your evaluation, so the distinctions below matter.

| File | What it contains | What it is for | The rule |
|---|---|---|---|
| development_tickets.json | Roughly five hundred support tickets with intent, urgency, satisfaction rating and channel. | Understanding the problem and developing your classifier. | Use freely. |
| documentation.json | CloudServe's own support documentation. | The knowledge base your retrieval layer searches. | Use freely. |
| ground_truth_responses.json | Two hundred reference answers written by senior agents. | A reference for what a good answer looks like, and a comparison set during development. | Use freely, but do not confuse it with the test set. |
| validation_tickets.json | Eighty labelled tickets for checking your own progress. | Your final evaluation, run once, near the end. | Do not look at these while building. Do not tune against them. |

| Why the hidden evaluation set is protectedIf you evaluate against the test set repeatedly and adjust your system after each run, you have not measured how your system performs on unseen tickets. You have measured how well you fitted it to those hundred tickets. Report your evaluation date and the number of runs in your report; a single honest run is worth more than an inflated one. |
|---|

07   How success is measured

There are three tiers of measurement and they are not equally important. The pyramid below shows how they relate. Technical performance is the foundation, because nothing works without it, but the client does not buy technical performance. They buy the business outcomes in the middle band, and the governance tier at the top functions as a set of conditions that must hold regardless of how good the other two look.

Figure 6. The three tiers of measurement and how they relate.

Business outcomes

| Measure | Baseline today | Target | How you calculate it |
|---|---|---|---|
| First contact resolution | 42% | 60% or better | Tickets closed without escalation, divided by total tickets. |
| Average time to first reply | 8 to 12 hours | Under 5 minutes | Mean of the interval between arrival and reply. |
| Customer satisfaction | 3.2 / 5 | 4.0 or better | Mean rating across reviewed responses. |
| Escalation rate | 58% | 30% or lower | Tickets passed to a human, divided by total tickets. |
| Repeat contacts | Not measured | Reduced by half | Tickets from the same customer on the same issue within seven days. |

Technical performance

| Measure | Target | Why this target |
|---|---|---|
| Intent classification precision | 85% or better | Below this, routing decisions rest on unreliable input. |
| Hallucination rate | 5% or lower | Every unsupported claim is a potential complaint. |
| Citation accuracy | 95% or better | A citation that does not support the sentence is worse than no citation. |
| Response latency, 95th percentile | Under 3 seconds | Live chat customers leave before a slower system answers. |
| Availability | 99.5% or better | Support does not stop because the model provider is having a difficult morning. |

Governance conditions

These are not targets to be approached. They are conditions that either hold or do not, and a system that fails any of them is not fit to be deployed regardless of its other numbers.

| Condition | Requirement |
|---|---|
| Private data in outbound responses | Zero occurrences. There is no acceptable rate. |
| Quality across customer groups | Under five percentage points of difference between groups. |
| Decision logging | Complete coverage. Every automated decision reconstructable. |
| Confidence calibration | Stated confidence within five points of observed accuracy. |

08   Risk and governance obligations

You are building something that will speak to paying customers without a human reading it first. That fact carries obligations, and they are assessed as heavily as the code.

Figure 7. The risk matrix. Anything in the darkest band needs a written mitigation before you build.

What you are required to have in place

A completed risk register in which each risk has a likelihood, an impact, a named mitigation and a person accountable for it.

A decision log that captures, for every automated decision, the input, the prediction, the confidence, the sources used, the action taken and the reason for it.

A fairness audit comparing the quality of responses across customer groups, with the method and the sample size stated.

An incident procedure specific enough that someone unfamiliar with your system could follow it at two in the morning.

A stated position on what your system must never do, and the mechanism that enforces it.

| The question that separates strong governance from theatreAsk yourself what would have to go wrong for your system to cause real harm to a real customer, and then ask what in your design would actually stop it. If the answer is that the model is generally quite reliable, you have described a hope rather than a control. |
|---|

09   Technical constraints

Everything in the stack below is free or open source. You are not required to spend money on this project, and being blocked by cost almost certainly means a wrong turn was taken somewhere earlier.

| Layer | What to use | Notes |
|---|---|---|
| Language | Python 3.10 or later | Earlier versions will not run parts of the stack. |
| Orchestration | LangChain with LangGraph | LangGraph handles the multi-step routing cleanly. |
| Vector store | Chroma | Runs locally with no service to provision. |
| Embeddings | all-MiniLM-L6-v2 | Small, fast and adequate for this corpus. |
| Model access | OpenRouter or Groq | Both have usable free tiers. |
| Interface | FastAPI | Gives you documentation generation without extra work. |
| Storage | PostgreSQL or SQLite | SQLite is fine for the decision log at this scale. |
| Monitoring | Prometheus with Grafana | The setup guide walks through both. |
| Automation | GitHub Actions | Free for the repository sizes involved here. |

Rules that apply regardless of your technical choices

No credential, key or token may appear anywhere in your committed source code.

The system must run from a clean checkout by following your own written instructions, on a machine that is not yours.

Any component you did not write must be attributed, including code generated by a model.

The hidden evaluation set is used once, at the end, and the date of that run is reported.

10   Frequently misunderstood points

The following come up in nearly every cohort. Reading them now costs you five minutes and may save you several days.

Building before understanding

The most common failure is starting to write code on the first morning because the architecture seems obvious. It always seems obvious. The people who do best spend the first three days almost entirely on discovery and then build faster, because they are not rewriting components they misunderstood.

Treating the PRD as paperwork

The requirements document is not a formality you complete so that you can get to the interesting part. It is the thing that decides what the interesting part turns out to be. A vague PRD produces a vague system and there is no recovering from it later.

Reporting accuracy and stopping

A classification accuracy figure, presented on its own, tells the client nothing they can act on. Report what changed for the business, state your uncertainty, and be prepared to explain what your numbers do not cover.

Leaving governance to the final afternoon

Governance that is added at the end is always shallow, because the design decisions that would have made it meaningful were taken weeks earlier. Decide in week one what your decision log will record, and the rest becomes straightforward.

Underestimating the video

Twenty minutes of clear explanation is considerably harder than it sounds. The first attempt always overruns and exposes the parts you cannot yet explain without hesitating. Record a first version by the middle of your final week so that there is time for a second.

Writing the effort log from memory at the end

It will be inaccurate, and it will show every stage landing implausibly close to its estimate. Fill it in every second day; it takes two minutes and it supplies the material for the reflection section of your report.

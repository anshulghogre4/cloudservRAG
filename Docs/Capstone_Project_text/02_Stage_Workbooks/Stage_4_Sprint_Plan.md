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
| B-01 | Environment and dependency setup |  |  | — |  |
| B-02 | Data loading and normalisation |  |  | B-01 |  |
| B-03 | Document chunking and embedding |  |  | B-02 |  |
| B-04 | Vector store and retrieval |  |  | B-03 |  |
| B-05 | Evaluation harness |  |  | B-02 |  |
| B-06 | Intent and urgency classifier |  |  | B-02 |  |
| B-07 | Routing logic and thresholds |  |  | B-06 |  |
| B-08 | Answer generation with citations |  |  | B-04 |  |
| B-09 | Guardrails and validation |  |  | B-08 |  |
| B-10 | Decision logging |  |  | B-07 |  |
| B-11 | First full unattended run over the hidden evaluation set (THE GATE) |  |  | B-05, B-09 |  |
| B-12 | Monitoring and dashboards |  |  | B-10 |  |
| B-13 | Continuous integration pipeline |  |  | B-11 |  |
| B-14 | Fairness audit |  |  | B-11 |  |
| B-15 | Report, video and submission package |  |  | all |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

3   Section three: the week two plan in detail

| Day | What will be finished by the end of the day | Hours | Risk to this |
|---|---|---|---|
| Monday |  |  |  |
| Tuesday |  |  |  |
| Wednesday |  |  |  |
| Thursday |  |  |  |
| Friday |  |  |  |

4   Section four: the week three plan in detail

| Day | What will be finished by the end of the day | Hours | Risk to this |
|---|---|---|---|
| Monday |  |  |  |
| Tuesday |  |  |  |
| Wednesday |  |  |  |
| Thursday |  |  |  |
| Friday | Final presentation and submission |  |  |

5   Section five: what you will drop if you run out of time

You will run out of time. Every student does. Deciding now what gets cut is far better than deciding in a panic on the final Wednesday, and it protects the parts that carry the most marks.

| Item | Cut order | Consequence of cutting it | What you will say about it in the report |
|---|---|---|---|
|  | 1st to go |  |  |
|  | 2nd to go |  |  |
|  | 3rd to go |  |  |
|  |  |  |  |
|  |  |  |  |

6   Section six: the daily check-in record

Ten minutes at the start of each day, answering the same three questions. Keeping this record is what makes your effort log accurate rather than reconstructed, and it is where you will notice a blocker that has quietly consumed two days.

| Date | Finished since yesterday | Doing today | Blocked by |
|---|---|---|---|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

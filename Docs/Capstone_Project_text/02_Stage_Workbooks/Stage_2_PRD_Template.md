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
| Written by |  |
| Date |  |
| Status | Draft for review |
| Approved by |  |

2   The problem in one paragraph

Copy across the paragraph you wrote at the end of your discovery workbook. If you find yourself wanting to improve it as you copy, go back and improve it in the workbook first, so that the two do not drift apart.

| Problem statement |
|---|
|  |
|  |

3   Who this is for

Describe each group of users separately. A requirement that serves everybody usually serves nobody particularly well.

| User group | What they need from this system | What they currently do instead | How you will know it worked for them |
|---|---|---|---|
| Customers raising tickets |  |  |  |
| Tier one support agents |  |  |  |
| Tier two and specialist agents |  |  |  |
| The head of support |  |  |  |
|  |  |  |  |
|  |  |  |  |

4   Functional requirements

Each requirement gets an identifier, a statement, a priority and a link back to the discovery evidence that produced it. The identifiers matter because your specifications, your prompts and your test cases will all refer to them.

Use the priority scale consistently. Must means the system is not acceptable without it. Should means it is expected but could be deferred with a stated consequence. Could means it would add value if time allows. Will not means it has been considered and deliberately excluded, and recording those is as useful as recording the rest.

| ID | Requirement | Priority | Discovery evidence | Acceptance criteria |
|---|---|---|---|---|
| FR-01 | The system shall ... | Must | Section _, row _ |  |
| FR-02 |  |  |  |  |
| FR-03 |  |  |  |  |
| FR-04 |  |  |  |  |
| FR-05 |  |  |  |  |
| FR-06 |  |  |  |  |
| FR-07 |  |  |  |  |
| FR-08 |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

5   Non-functional requirements

These describe how well the system must do the things it does. They are frequently what distinguishes a demonstration from something that could actually be deployed.

| ID | Category | Requirement | How it will be verified |
|---|---|---|---|
| NFR-01 | Latency |  |  |
| NFR-02 | Availability |  |  |
| NFR-03 | Accuracy |  |  |
| NFR-04 | Privacy |  |  |
| NFR-05 | Auditability |  |  |
| NFR-06 | Fairness |  |  |
| NFR-07 | Cost |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

6   What is deliberately out of scope

Recording what you are not building is one of the most valuable things a requirements document does, because it is the section that prevents an argument in week three.

| Not building | Why not | What would have to change for this to be reconsidered |
|---|---|---|
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

7   Assumptions and their consequences

Every assumption you are making is a place where this document could turn out to be wrong. Listing them now is what makes the revision in stage five a considered update rather than a scramble.

| Assumption | Why you believe it | What happens if it is false | How you will find out |
|---|---|---|---|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

8   Success measures

State the measures this system will be judged on, with the baseline and the target for each, and say who is accountable for reporting them.

| Measure | Baseline | Target | Measured how | Reported by |
|---|---|---|---|---|
| First contact resolution | 42% |  |  |  |
| Time to first reply | 8 to 12 hours |  |  |  |
| Customer satisfaction | 3.2 / 5 |  |  |  |
| Escalation rate |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

9   Open questions

The things you do not yet know. Each one needs an owner and a date by which it will be resolved, otherwise it will still be open in week three.

| Question | Why it matters | Owner | Resolve by |
|---|---|---|---|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

| The review before you move onRead your finished PRD and ask, for each requirement in turn, whether an engineer who had not attended any of your interviews could build it from what is written. Where the answer is no, the requirement is not finished. This check takes twenty minutes and it is the single highest-value thing you can do at the end of week one. |
|---|

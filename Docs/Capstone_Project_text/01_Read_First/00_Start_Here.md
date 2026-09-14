FORWARD DEPLOYED AI ENGINEERING

Capstone Project

Start Here

Your guide to the capstone project

Read this document before you open anything else. It takes about fifteen minutes
and it will save you a great deal of confusion later.

| INDIVIDUAL PROJECT · DEADLINE 13 SEPTEMBER |
|---|

What this document contains

01   What you are being asked to do   The brief in plain language

02   How the project is structured   Six stages, three weeks, one chain of artefacts

03   What is in this pack   Every file and the moment you will need it

04   How to work through it   A step by step reading and working order

05   What you hand in at the end   The four parts of the submission

06   How your work will be judged   The marking weights and what earns them

01   What you are being asked to do

A software company called CloudServe Solutions has come to you with a problem. Their customer support team is drowning. They receive more than five hundred tickets every week across four different channels, they take between eight and twelve hours to reply when their own service agreement promises two, and they resolve fewer than half of those tickets without passing them to someone else. Their customers have noticed. Their satisfaction score has fallen to 3.2 out of 5.

When they came to you, they asked for a chatbot. That is the request you have been given, and it is not the job you have been given. The job is to work out what is actually going wrong inside that support function, to design something that fixes it, to build that thing, to prove that it works, and to be able to defend every decision you made along the way.

| The distinction that matters mostAn ordinary engineer builds what the client asked for. A forward deployed engineer works out what the client needed and then explains the difference. Almost all of the marks in this capstone sit on the second behaviour, and the diagram below is worth sitting with for a minute before you go any further. |
|---|

Figure 1. The same request produces two completely different projects depending on how you respond to it.

02   How the project is structured

The capstone runs for three weeks and moves through six stages. Each stage produces a document or a piece of working software, and that output becomes the input to the stage that follows it. You cannot skip ahead, because stage three is written from the contents of stage two, and stage two is written from the evidence you gathered in stage one.

Figure 2. The six stages and the week in which each one falls.

This chain is deliberate. A great many student projects fail because somebody opened an editor on the first morning and started writing code against a vague idea of the problem. By forcing the requirements to come out of recorded evidence, and the prompts and specifications to come out of the requirements, the structure makes that failure much harder to fall into.

Figure 3. Each artefact is built from the one above it. Nothing appears from nowhere.

| One rule that surprises peopleYou are required to revise your requirements document at least once during the build, and to record what you changed and why. This is not a punishment for getting it wrong the first time. Requirements that survive three weeks of contact with real code without a single amendment almost always mean that nobody was reading them. |
|---|

03   What is in this pack

The pack is organised into four folders. The table below tells you what each file is for and the point in the project at which you will actually need it. You do not need to read everything at the start, and trying to will slow you down.

Folder one: read first

| File | What it is for | When you need it |
|---|---|---|
| Start Here | This document. Orientation and working order. | Before anything else |
| Project Brief | The full brief: client situation, architecture, targets, constraints. | Day one, then constantly |
| Build Specification | What the system must do to count as working. Twelve acceptance criteria. | Day one, then all of week two |
| README | A step by step walkthrough written in plain prose. | Day one and whenever you are stuck |

Folder two: stage workbooks

| File | What it is for | When you need it |
|---|---|---|
| Stage 1 — Discovery Workbook | Fillable tables for interviews, evidence and problem framing. | Week one, days one to three |
| Stage 2 — PRD Template | The requirements document you write from your discovery findings. | Week one, days four and five |
| Stage 3 — Prompt Library | Where every prompt and specification is recorded and versioned. | Week two, from day one |
| Stage 4 — Sprint Plan | Backlog, estimates, owners and the definition of done. | Week two, day one |
| Stage 5 — PRD Revision Log | The record of what changed in your requirements and why. | Week two into week three |

Folder three: reference material

| File | What it is for | When you need it |
|---|---|---|
| Setup Guide | Environment, keys, database, monitoring and continuous integration. | Week one, day one |
| Evaluation Framework | Every metric, how it is calculated, and the target you are held to. | Week two onward |
| Governance Framework | Risk, fairness, audit logging and incident response. | Week three |
| Datasets | Tickets, documentation, expert answers and the hidden evaluation set. | From week one |
| Configuration | Package list and the environment variable template. | Week one, day one |

Folder four: submission

| File | What it is for | When you need it |
|---|---|---|
| Submission Guide | The exact format for the video, the report and the code archive. | Read in week one, use in week three |
| Effort Log | Your hours by stage and task, and estimates against reality. | Fill in as you go, submit at the end |

| Read the submission guide in week one, not week threeEvery cohort produces somebody who discovers on the final afternoon that the effort log needed entries throughout rather than one summary written from memory, or that the video had to include a live demonstration. Neither can be fixed retrospectively. Spend ten minutes on the submission guide during your first week. |
|---|

04   How to work through it

The following order has been tested across several cohorts. You are free to deviate from it, but if you are not sure where to begin, begin here.

Before you write any code at all

Read this document to the end. You are nearly there already.

Read the Project Brief in full. Allow two to three hours and do not skim the sections on evaluation and governance.

Read the Build Specification. It defines what your software must actually do, and it is the document you will return to most often during week two.

Skim the Submission Guide so that you know what the finish line looks like.

Work through the Setup Guide until you can install the packages and reach the model provider from your own machine. Do this on day one, not day four.

Week one, which is about understanding rather than building

Open the Discovery Workbook and fill it in. This means interviewing your stakeholders, reading the ticket data, and writing down what you find rather than what you assumed.

Look for patterns across your evidence and write the problem statement that the evidence supports, which may not be the problem you expected to find.

Write the first version of your requirements document using the PRD Template.

Design your architecture and complete the risk assessment.

Week two, which is about building and measuring

Turn your requirements into specifications and prompts using the Prompt Library.

Plan the sprint. Decide who owns what and what finished means for each item.

Build the pipeline, the retrieval layer, the agents and the guardrails, working to the daily checkpoints in the Build Specification.

Run the full evaluation set end to end, unattended, by the end of the week. This is the gate.

Run your evaluation against the hidden evaluation set and record the results honestly.

Revise the requirements document. By now you will know what was wrong with it.

Week three, which is about trust and presentation

Complete the governance framework and run the fairness audit.

Set up monitoring and the continuous integration pipeline.

Record the video, write the report and finish the effort log.

Package everything in the required format and submit.

Figure 4. The three weeks laid out as a timeline. The dark bar is the compulsory revision.

05   What you hand in at the end

Your submission has four parts and the deadline is 13 September at 23:59. All four parts are required; a missing part is an incomplete submission rather than a deduction, so please treat the list below as a checklist rather than a set of suggestions.

Figure 5. The four parts of the submission and how they are packaged.

| Part | What it is | Notes |
|---|---|---|
| Video | A single recording of roughly twenty minutes explaining the project. | A live demonstration must be included, showing an escalation and a guardrail. |
| Report | The written project report following the prescribed section order. | Between twenty and thirty pages, submitted as a PDF. |
| Workbooks and effort log | Your five completed stage workbooks plus your hours by stage and task. | Entries throughout, not a summary written at the end. |
| Source code | The complete repository with history and a working README. | Must run from a clean checkout by following your own instructions. |

The Submission Guide gives the exact naming convention, the folder layout and the section order for each part. Follow it precisely, because a submission that has to be unpicked and reassembled before it can be assessed reflects poorly on work that may otherwise be strong.

06   How your work will be judged

This project produces working software. That is the deliverable, it carries the largest share of the marks, and there is a pass or fail gate in front of it. The remaining marks go to the thinking that makes the software worth trusting.

| Area | Weight | What earns the marks |
|---|---|---|
| Implementation | 35% | A system that meets the twelve acceptance criteria, is built sensibly, and can be run and read by someone else. |
| Evaluation | 20% | Honest measurement against the hidden evaluation set, business outcomes reported alongside technical ones, and results interpreted rather than merely listed. |
| Discovery and problem framing | 15% | Evidence gathered first hand, a problem statement that follows from it, and a clear account of why the obvious answer was the wrong one. |
| Requirements and traceability | 10% | Requirements specific enough to build from, and a visible chain from evidence to requirement to specification to code. |
| Governance and risk | 10% | Decisions logged, risks assessed with mitigations, fairness tested, and an incident procedure that someone could actually follow. |
| Communication | 10% | A video and a report that a non-technical stakeholder could follow, with every claim explained rather than asserted. |

| Before any of that is marked, there is a gateYour system is checked out onto a machine that is not yours and asked to process all one hundred evaluation tickets unattended. If it cannot, the project does not pass, whatever the documents look like. The Build Specification sets out the twelve criteria in full, and it is the document to read immediately after this one. |
|---|

| A note on the evaluation marksIt is common to report a strong accuracy figure and stop there. Accuracy tells the client almost nothing about whether their support function improved. The marks in this section go to work that says what changed for the business, by how much, and with what confidence. |
|---|

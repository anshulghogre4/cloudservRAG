FORWARD DEPLOYED AI ENGINEERING

Capstone Project

Project Instructions

What to do, what to submit, and by when

This is an individual project. Read these instructions in full before you begin,
and read them again in your final week before you package your submission.

| SUBMISSION DEADLINE · 13 SEPTEMBER |
|---|

What this document contains

01   The headline facts   Everything you need on one page

02   What the project asks of you   The brief in short

03   How to work through it   Six stages across three weeks

04   Milestones and dates   Where you should be, and when

05   A note on the data   What you have, and the set you do not have

06   What you submit   Files, video, naming and packaging

07   The video presentation   Length, structure and what to show

08   Working individually   What help is allowed and what is not

09   Using AI tools   Permitted, expected, and how to declare it

10   How you will be marked   Weightings and what earns them

11   Before you submit   The final checklist

01   The headline facts

If you read nothing else on this page, read this table.

|  |  |
|---|---|
| What this is | An individual capstone project. You design, build, evaluate and govern an AI powered customer support system for a client called CloudServe Solutions. |
| The deliverable | Working software. There is a gate: your system must process the full validation set unattended from a clean checkout. The gate has three outcomes, set out in section nine. |
| How long you have | Three weeks. |
| Deadline | 13 September, 23:59. Late submissions are treated under the policy in section seven. |
| What you submit | One archive containing your project files and a video presentation. |
| Video length | Twenty minutes, give or take two. |
| Working arrangement | Individually. Discussion with peers is allowed; shared work is not. |
| AI tool use | Permitted and expected. It must be declared. See section eight. |
| Cost to you | Nothing. Free tiers only, and no part of the marking advantages paid capacity. |
| Where to start | Read Start Here, then the Project Brief, then the Build Specification. |

| The single most important thing to understandThe client has asked you for a chatbot. If you build a chatbot, you will have answered the request and failed the project. Your task is to work out what is actually wrong inside their support function and address that instead. Roughly a third of the available marks rest on this distinction, and the Project Brief explains it in detail. |
|---|

02   What the project asks of you

CloudServe Solutions is a software company of around one hundred and fifty people serving just over two hundred corporate customers. Their support function has broken down. They receive more than five hundred tickets a week, they take between eight and twelve hours to reply when their service agreement promises two, and they resolve fewer than half of those tickets without escalating. Their customer satisfaction has fallen to 3.2 out of 5.

You are being asked to do six things, in order: understand the problem properly by talking to people and examining the evidence, write down what the system must do and why, turn those requirements into specifications and prompts, plan the work, build and measure it, and then present it as you would to a paying client.

The structure of the pack enforces that order. Each stage produces an artefact that becomes the input to the next, so it is difficult to skip the thinking and start writing code, which is the most common way projects of this kind fail.

Figure 1. The six stages and the week in which each falls.

03   How to work through it

The reading comes first and it is not a delay. Allow the better part of your first day for it and for getting your environment working.

Day one

Read 01_Read_First / 00_Start_Here.docx. Fifteen minutes, and everything else makes more sense afterwards.

Read 01_Read_First / 01_Project_Brief.docx in full. Two to three hours. Do not skim the evaluation and governance sections.

Read 01_Read_First / 02_Build_Specification.docx. It defines what your software must do, criterion by criterion.

Skim 04_Submission / Submission_Guide.docx so that you know what the finish line looks like.

Work through 03_Reference / Setup_Guide.docx until a real call to the model provider returns real text.

Week one, which is about understanding rather than building

Complete Stage 1, the Discovery Workbook. Interview your stakeholders, read the ticket data, and record what you actually find.

Write your problem statement in the final section, then test it on somebody you interviewed. If they hesitate, your framing needs work.

Write version one of your requirements using the Stage 2 template. Every requirement references the discovery evidence behind it.

Week two, which is about building and measuring

Complete Stage 3, turning requirements into specifications and a versioned prompt library.

Complete Stage 4, the sprint plan, and decide now what you will drop if time runs short.

Build the pipeline, retrieval, agents and guardrails, following the daily checkpoints in the Build Specification.

Run the full evaluation set end to end, unattended, before the week closes. This is the gate and it must clear in week two.

Run your evaluation and record the results honestly, including the ones you did not want.

Revise your requirements and complete Stage 5. This revision is compulsory.

Week three, which is about trust and presentation

Complete the governance framework: risk register, fairness audit, decision logging, incident procedure.

Set up monitoring and the continuous integration pipeline.

Record your video, write your report, and finish your effort log.

Package everything in the required format and submit before the deadline.

Figure 2. Roughly where your hours should go. If building exceeds half your time, something upstream was left unfinished.

04   Milestones and dates

The deadline is 13 September at 23:59. Working backwards from it, you should be at the following points by the end of each week. Nothing is collected at the milestones, but if you are behind at one of them you will not recover the time later.

| By the end of | You should have | Which means |
|---|---|---|
| Week one | A completed discovery workbook and version one of your requirements document. | You know what the real problem is, you can evidence it, and you have written down what you are building. |
| Week two | A system that clears the gate, an evaluation run, and a revised requirements document. | The full hidden set has been processed unattended in a single run, you have the metrics report it produced, and you have recorded what your first requirements got wrong. |
| Week three | Governance complete, video recorded, report written, submission packaged. | Everything in section five exists, is named correctly, and has been checked. |

A suggested calendar

Adjust these to your own start date. What matters is the three week shape rather than the specific days.

| Period | Focus | Ends |
|---|---|---|
| Week one | Discovery, requirements, architecture and risk | 30 August |
| Week two | Prompt library, sprint plan, build, evaluation, revision | 6 September |
| Week three | Governance, monitoring, report, video, packaging | 13 September |
| Deadline | Submission uploaded | 13 September, 23:59 |

| Do not leave the video until the final dayRecording takes considerably longer than people expect, because the first attempt always runs over and reveals the parts you cannot yet explain cleanly. Record a first version by the middle of your final week so that you have time for a second. |
|---|

05   A note on the data

Your pack contains three things you will build against: 500 development tickets with full labels, 80 validation tickets you can check yourself against as often as you like, and 29 knowledge base articles that form the corpus your system retrieves from. There are also 200 reference responses written by senior agents, and transcripts of five stakeholder interviews that are your primary discovery evidence.

What your pack does not contain is the set your grade finally depends on. After submission, your evaluation harness is run against a hidden set of 120 tickets drawn from the same population and using the same schema. You will not see it beforehand.

| The practical consequenceYour harness must take an input path and an output path as arguments rather than pointing at a filename you hardcoded, because it will be run against a file you have never seen. A harness that only works against your own copy of the data cannot be run at all. This is the single most common avoidable failure in this assessment. |
|---|

This arrangement also means there is nothing to gain from tuning until a number looks good. The set you can see is not the set that decides your grade, so the honest path and the effective path are the same one.

06   What you submit

One archive containing four folders. All four are required. A submission missing one is treated as incomplete rather than as a submission with a deduction.

The archive name

| Name your archive exactly like thisFirstnameLastname_Capstone_Submission.zip For example: PriyaSharma_Capstone_Submission.zip No spaces, no version numbers, no dates in the filename. |
|---|

What goes in each folder

| Folder | Contents | Format |
|---|---|---|
| 01_Video | Your recorded presentation, or a text file containing a shareable link if the file is large. | MP4, 1080p or better. Name it FirstnameLastname_Capstone_Video.mp4 |
| 02_Report | Your written project report following the section order in the Submission Guide. | One PDF, twenty to thirty pages excluding appendices. |
| 03_Workbooks | Your five completed stage workbooks: discovery, requirements, prompt library, sprint plan, revision log. | PDF or DOCX. Include your effort log here as well. |
| 04_Source_Code | The complete repository, including history, tests and a working README. | A folder or a nested archive. Must run from a clean checkout. |

The rules that catch people out

Your repository must run by following your own README, on a machine that is not yours. Clone it into a fresh directory and test this before you package anything.

No API key, token or password may appear anywhere in your code or its history. Submissions are scanned, and a key found is a serious finding whether or not it still works.

The hidden evaluation set is used once, near the end. State in your report the date you ran it and how many times.

Anything you did not write yourself must be attributed, including code produced by an AI tool.

07   The video presentation

The video is where you explain your project as you would to the client. It carries meaningful weight and it is the part most students underprepare. It is not a set of slides read aloud, and it must include the system actually running.

The requirements

| Requirement | Detail |
|---|---|
| Length | Twenty minutes, give or take two. Substantially shorter suggests thin work; anything beyond twenty-two minutes is marked on the first twenty-two. |
| You on camera | You must be visible at least while introducing yourself and at the close. |
| Live demonstration | At least seven minutes showing the system running on real tickets, including one case that escalates, one guardrail firing, and part of the unattended run over the hidden evaluation set. |
| Audio | Clearly audible throughout. Test it before you record twenty minutes. |
| Screen legibility | Increase your font sizes before recording. Code that cannot be read on playback counts as not shown. |
| Format and name | MP4, 1080p or better, named FirstnameLastname_Capstone_Video.mp4 |

The structure to follow

These timings are a guide, but the order matters. Opening with your architecture rather than the problem loses the audience in the first two minutes.

| Minutes | Section | What to cover |
|---|---|---|
| 0 to 2 | The problem | What the client asked for, what you found instead, why the difference matters. |
| 2 to 5 | Discovery | The two or three findings that changed your design, with the evidence behind them. |
| 5 to 7 | The system | The architecture, explained so a non-engineer could follow it. |
| 7 to 14 | The demonstration | Run it. Show a success, an escalation, a guardrail blocking, and evidence of the full unattended run. |
| 14 to 17 | The numbers | Business outcomes first, then technical, then governance. State your uncertainty. |
| 17 to 18 | Risk and governance | What could go wrong and what in your design prevents it. |
| 18 to 20 | What you would do next | Including what you got wrong and what your requirements revision changed. |

| The advice that most improves a videoRecord it twice. Your first attempt will run to twenty-eight minutes and you will discover which parts you cannot actually explain. The second will be tighter and noticeably better. Budget half a day rather than an hour. |
|---|

08   Working individually

This is an individual project. The work you submit must be your own, and you are expected to be able to explain every part of it in your video and in any follow-up questions.

What is allowed

Discussing the problem, approaches and concepts with other students.

Asking for help with an error message, an environment problem or a library question.

Reading documentation, tutorials, papers and public repositories.

Using libraries, frameworks and public datasets, with attribution.

Using AI tools as described in the next section.

What is not allowed

Sharing code, prompts, workbooks or reports with another student, in either direction.

Submitting work that you cannot explain in full.

Presenting someone else's implementation, or a public repository's implementation, as your own.

Reusing a submission from a previous cohort.

Effort log

You are asked to keep a short record of your hours by stage and task. Fill it in as you go, at least every second day; a log reconstructed from memory in the final week is both inaccurate and obvious. It is submitted alongside your workbooks, and it forms the basis of the reflection section of your report, where being able to say what you underestimated and by how much is genuinely valuable.

Cost

This project costs nothing to complete. Every tool in the stack is free or open source and the model providers named in the setup guide have free tiers sufficient for the work. No part of the marking advantages a student who pays for additional capacity, and a well-built system running on a small free model will out-score a thin one running on an expensive one. If you find yourself unable to finish a run within a free allowance, raise it rather than paying; it almost always indicates a design problem worth fixing.

Late submission

| When it arrives | What happens |
|---|---|
| On or before 13 September, 23:59 | Marked in full. |
| Within 48 hours of the deadline | Marked, with a deduction applied to the total. |
| More than 48 hours late | Not marked without a documented extension agreed in advance. |
| Extension needed | Request it before the deadline, not afterwards, with a reason. |

09   Using AI tools

You are training to build systems with language models, so it would be strange to forbid you from using them. AI assistance is permitted and expected. What matters is that you remain the author of your own judgement and that you are open about where the tools helped.

Use them freely for

Writing and debugging code, provided you understand what the code does.

Drafting and refining the prompts that run inside your system.

Explaining concepts, libraries and error messages.

Reviewing your own writing and specifications for gaps.

Do not use them for

Inventing discovery findings. Your evidence must come from the data and the people you spoke to, not from a model's guess about what a support team is probably like.

Producing your problem statement, your evaluation interpretation or your reflection. These are the parts where your judgement is what is being assessed.

Generating code you cannot explain. You will be asked about it.

How to declare it

Include a short section in your report, half a page is plenty, stating which tools you used, for what, and where you overrode or corrected their output. Declaring substantial use honestly carries no penalty. Undeclared use that becomes obvious does.

| A useful testFor any part of your submission, ask whether you could be stopped mid-sentence and asked why you did it that way, and answer without hesitating. Where the answer is no, that is the part to go back and understand properly before you submit. |
|---|

10   How you will be marked

This project produces working software. Before any of the marking below begins, your repository is checked out onto a machine that is not yours and asked to process all one hundred evaluation tickets unattended. That is a gate rather than a criterion: if it does not happen, the project does not pass, whatever the documents look like.

Figure 3. The gate is checked before the marking begins.

Once you are through it, the marks are distributed as follows.

| Area | Weight | What earns the marks |
|---|---|---|
| Implementation | 35% | A system meeting the twelve acceptance criteria in the Build Specification, built sensibly and readable by someone else. |
| Evaluation | 20% | Honest measurement against the hidden evaluation set, business outcomes alongside technical ones, results interpreted rather than listed. |
| Discovery and problem framing | 15% | Evidence gathered first hand, and a problem statement that follows from it. |
| Requirements and traceability | 10% | Requirements specific enough to build from, with a visible chain to the code. |
| Governance and risk | 10% | Decisions logged, risks assessed with real mitigations, fairness tested. |
| Communication | 10% | A video and report a non-technical stakeholder could follow. |

Implementation is the largest single component and it is the one with a gate in front of it. The documents you write are not an alternative to building the system; they are what make the system worth trusting once it runs. A working, modest system that is honestly measured and clearly explained will out-score an ambitious one that never quite ran.

11   Before you submit

Work through this on the day before the deadline rather than on the day itself.

| □ | Check |
|---|---|
| □ | The archive is named FirstnameLastname_Capstone_Submission.zip with no spaces. |
| □ | It contains exactly four folders: 01_Video, 02_Report, 03_Workbooks, 04_Source_Code. |
| □ | The video plays, the audio is audible, and the screen content is legible on playback. |
| □ | The video runs between eighteen and twenty-two minutes. |
| □ | The system processes the full validation set unattended in a single run. |
| □ | Your harness accepts an input path and an output path as arguments. |
| □ | All twelve acceptance criteria in the Build Specification are met. |
| □ | The demonstration shows a success, an escalation, and a guardrail blocking something. |
| □ | The report is a single PDF and follows the prescribed section order. |
| □ | Every figure and table in the report is numbered and referred to in the text. |
| □ | All five stage workbooks are included and actually completed. |
| □ | The requirements revision log shows at least one substantive change with its trigger. |
| □ | The effort log has entries throughout the three weeks, not just at the end. |
| □ | The repository runs from a clean checkout by following your own README. |
| □ | No credentials appear anywhere in the code or its history. |
| □ | The report states when you ran the hidden evaluation set and how many times. |
| □ | The report contains your declaration of AI tool use. |
| □ | Submitted before 13 September, 23:59. |

If you are uncertain about any requirement in this document, ask before the final week rather than after the deadline.

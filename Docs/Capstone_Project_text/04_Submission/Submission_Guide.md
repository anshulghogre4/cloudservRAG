FORWARD DEPLOYED AI ENGINEERING

Capstone Project

Stage Six: Submission

Exactly what you hand in, and in what format

Read this in week one rather than week three. Several of the requirements here
cannot be satisfied retrospectively.

| INDIVIDUAL PROJECT · DEADLINE 13 SEPTEMBER |
|---|

The four parts

Your submission consists of four parts, packaged as a single archive. All four are required. A submission missing any one of them is treated as incomplete rather than as a submission with a deduction, so please check the list twice before you upload.

Figure 1. The four parts and the single archive that contains them.

The archive

Everything goes into one compressed archive, named using your own full name exactly as it appears on your enrolment, with no spaces and no version suffixes.

| Archive nameFirstnameLastname_Capstone_Submission.zip For example: PriyaSharma_Capstone_Submission.zip No spaces, no version numbers, no dates in the filename. |
|---|

The folder layout inside the archive

Use exactly these four folder names, in this order. Do not add folders at the top level and do not nest the whole submission inside another folder.

| Folder | Contents |
|---|---|
| 01_Video | The recording, or a text file containing the link if the file is too large. |
| 02_Report | The project report as a single PDF. |
| 03_Workbooks | Your five completed stage workbooks and your effort log. |
| 04_Source_Code | The complete repository. |

1   Part one: the video

You will record a single video of roughly twenty minutes in which you explain the project and demonstrate the system working. This is not a presentation of slides read aloud. It is the closest thing in this assessment to the conversation you would actually have with a client, and it is weighted accordingly.

The requirements

| Requirement | Detail |
|---|---|
| Length | Twenty minutes, give or take two. Substantially shorter suggests the work is thin; substantially longer will be marked on the first twenty-two minutes only. |
| You on camera | You must be visible at least while introducing yourself and at the close. |
| Live demonstration | At least seven minutes must show the system actually running on real tickets, including one case that escalates, one guardrail blocking, and evidence of the unattended run over the full evaluation set. |
| Audio | Clearly audible throughout. Test your recording setup before committing to twenty minutes. |
| Format | MP4, 1080p or better, with clearly audible speech. |
| Screen content | Legible at normal playback. Increase your font sizes before you record. |
| File name | FirstnameLastname_Capstone_Video.mp4 |

The structure to follow

The timings below are a guide rather than a rule, but the order matters. Students who open with their architecture rather than the problem tend to lose the audience in the first two minutes and never quite recover them.

| Minutes | Section | What to cover |
|---|---|---|
| 0 to 2 | The problem | What CloudServe asked for, what you found instead, and why the difference matters. |
| 2 to 5 | What discovery told you | The two or three findings that changed your design. Cite your evidence. |
| 5 to 7 | The system | Walk through the architecture at a level a non-engineer could follow. |
| 7 to 14 | The demonstration | Run it live. Show a success, an escalation, a guardrail firing, and the full unattended run. |
| 14 to 17 | What the numbers say | Business outcomes first, then technical, then governance. State your uncertainty. |
| 17 to 18 | Governance and risk | What could go wrong, and what in your design stops it. |
| 18 to 20 | What you would do next | Including what you got wrong and what your PRD revision changed. |

| The thing that most improves a videoRecord it twice. The first take will be twenty-eight minutes long and you will discover which parts you cannot actually explain. The second take will be tighter, calmer and noticeably better. Budget half a day for this rather than an hour. |
|---|

2   Part two: the report

The report is a written account of the project, submitted as a single PDF of between twenty and thirty pages excluding appendices. Use the section order below; assessors read many of these and a predictable structure genuinely helps your work land well.

| # | Section | What belongs in it | Pages |
|---|---|---|---|
| 1 | Executive summary | One page. The problem, what you built, what it achieved, and the single most important caveat. | 1 |
| 2 | The problem | What was asked for, what discovery revealed, and the gap between them. | 2 to 3 |
| 3 | Discovery findings | Your evidence, presented as findings rather than as raw tables. Appendix the tables. | 3 to 4 |
| 4 | Requirements | How the requirements followed from the findings. Reference the identifiers. | 2 to 3 |
| 5 | Architecture and design | The system, the alternatives you considered, and why you chose as you did. | 3 to 4 |
| 6 | Implementation | How it was built, what was difficult, and what you would restructure. | 2 to 3 |
| 7 | Evaluation | Method, results, interpretation, and the limits of what you measured. | 3 to 4 |
| 8 | Governance and risk | Register, fairness audit, decision logging and incident procedure. | 2 to 3 |
| 9 | The requirements revision | What changed, what prompted it, and what it taught you. | 1 to 2 |
| 10 | Conclusions | What you would do next, and what remains uncertain. | 1 to 2 |
| — | Appendices | Filled workbooks, prompt register, full result tables, code listings. | Unlimited |

How the report is expected to read

Full sentences and continuous prose. Bullet lists are for genuinely enumerable things, not for avoiding the work of writing.

Every figure and table numbered, captioned and referred to in the text.

Every claim about performance accompanied by how it was measured and on what data.

Anything you did not do stated plainly rather than left for the reader to notice.

File name: FirstnameLastname_Capstone_Report.pdf

| On honesty in the evaluation sectionA report that says our escalation rate was higher than we targeted, and here is what we think caused it will always be marked above one that quietly omits the figure. Assessors have read a great many of these and they notice absences. |
|---|

3   Part three: the workbooks and effort log

You submit your five completed stage workbooks alongside a short record of the hours you spent by stage and task. The workbooks are the evidence that the project followed the intended sequence. The effort log exists because estimating your own work is a skill, and comparing what you estimated against what it took is one of the more useful things you will take away from these three weeks.

What is required

| Requirement | Detail |
|---|---|
| Granularity | Entries at the level of a task within a day, not a summary of the week. |
| Frequency | Filled in as you go, at least every second day. A log written from memory in the final week is obvious and marked accordingly. |
| Hours | Actual hours worked, not planned hours. Totals by stage. |
| Workbooks | All five stage workbooks included and genuinely completed, not skeleton copies. |
| File name | FirstnameLastname_Effort_Log.pdf |

| A note on honest estimatesAlmost nobody finishes a stage in the hours they expected. A log showing that discovery took half as long as planned and evaluation took twice as long is a normal, credible record and gives you something worth writing about. A log showing every stage landing exactly on estimate is not, and invites the scrutiny it deserves. |
|---|

4   Part four: the source code

You submit the whole repository, not a selection of the interesting files. It must run from a clean checkout by following your own instructions on a machine that is not yours.

Required repository structure

| Path | What goes there |
|---|---|
| README.md | Setup and run instructions, written for someone who has never seen the project. |
| requirements.txt | Pinned dependencies. |
| .env.example | Every variable your system needs, with placeholder values only. |
| src/ | The application code, organised by component. |
| prompts/ | The prompt library as files, versioned. |
| tests/ | Your tests, runnable with a single command. |
| evaluation/ | The harness, the results and the analysis notebook or scripts. |
| docs/ | Architecture notes and any diagrams. |
| data/ | Small sample data only. Do not commit large files. |
| .github/workflows/ | The continuous integration configuration. |

| The gate comes firstBefore any of this is assessed, your repository is checked out onto a machine that is not yours and asked to process the full evaluation set unattended. The twelve acceptance criteria in the Build Specification define what that means. A submission that cannot clear the gate does not pass, however complete the rest of it looks. |
|---|

The checks that will be run against your repository

A clean checkout is made and your README instructions are followed exactly. If it does not run, that is what is recorded.

The full hidden set is processed unattended, and the twelve acceptance criteria are checked one at a time.

The repository is searched for credentials. Any key, token or password found is treated as a serious finding regardless of whether it is still valid.

Commit history is reviewed for evidence of steady work across the three weeks rather than a single large commit at the end.

Tests are run with the single command your README specifies.

Attribution is checked for any substantial code you did not write yourself, including code generated by a model.

| Before you package anythingClone your own repository into a fresh directory, follow your own README from the first line, and see whether it works. Roughly half of all students discover a missing step at this point, and discovering it yourself is considerably better than the alternative. |
|---|

5   The final checklist

Work through this on the day before you submit rather than on the day itself.

| □ | Check |
|---|---|
| □ | The archive is named FirstnameLastname_Capstone_Submission.zip with no spaces. |
| □ | It contains exactly four top-level folders with the prescribed names. |
| □ | The video runs, the audio is audible and the screen content is legible. |
| □ | The video runs between eighteen and twenty-two minutes. |
| □ | The live demonstration includes a success, an escalation and a guardrail firing. |
| □ | The report is a single PDF and follows the prescribed section order. |
| □ | Every figure and table in the report is numbered and referred to in the text. |
| □ | The effort log has entries throughout the three weeks, not only at the end. |
| □ | The repository runs from a clean checkout following your own README. |
| □ | No credentials appear anywhere in the repository or its history. |
| □ | All five stage workbooks are included and completed. |
| □ | The requirements revision log shows at least one substantive change. |
| □ | The hidden evaluation set was used once, and the report says when. |
| □ | The report contains your declaration of AI tool use. |
| □ | Submitted before 13 September, 23:59. |

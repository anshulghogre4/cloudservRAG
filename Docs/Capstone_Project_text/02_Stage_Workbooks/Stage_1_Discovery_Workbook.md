FORWARD DEPLOYED AI ENGINEERING

Capstone Project

Stage One: Discovery

The workbook you complete before you design anything

Fill this in first. Nothing in the later stages is valid unless it can be traced
back to something you recorded on these pages.

| WEEK ONE · DAYS ONE TO THREE |
|---|

How to use this workbook

This workbook is a set of tables for you to complete. The prompts in the left-hand column tell you what belongs in each row; the remaining columns are yours to fill in. Where a table has blank rows at the bottom, add as many more as you need.

Work through the sections in order. Section one establishes who you are talking to, sections two to five gather the evidence, and section six is where you turn that evidence into a problem statement. Do not attempt section six before the others are genuinely finished, because the whole point of the exercise is that the conclusion follows from the evidence rather than the other way round.

| What finished looks likeYou are finished with discovery when a further interview tells you nothing you did not already know, and when every claim in your problem statement can be pointed at a specific row in one of these tables. If either of those is not yet true, you are not finished, however much time has passed. |
|---|

Figure 1. Discovery repeats until the answers stop changing.

1   Section one: what the interviews tell you

Your discovery evidence is in two places: the five stakeholder interview transcripts in the datasets folder, and the ticket data itself. Start with the transcripts. Read all five before you write anything, then come back and fill in the table below.

The prompts in the left column are the people you spoke to. For each, record what you were trying to learn from them, what they actually told you, and, importantly, what they seemed not to know about their own operation. That last column is often where the useful material is, because each of the five can only see their own part of the problem.

| Who | What they told you | What they appear not to know | What you want to verify in the data |
|---|---|---|---|
| Marcus Adeyemi, Head of Support | Issue over delayed response.FCR % needs to be at least 65% (most important)Chat bot response should be accurate and quick.Types Details or break down they do not know. | The right context for the ticket template to give answer for the query.Why the % of FCR is less.He talked about compliance, but what to keep and what not to keep, he has no Idea.No Deep details of Tickets are available | Why it’s taking time for employees to take time to look for correct refs.What casuing FCR to move to tier 2 too often. |
| Sofia Restrepo, Tier One Agent |  |  |  |
| Daniel Okonkwo, Tier Two Engineer |  |  |  |
| Ines Varga, Technical Writer |  |  |  |
| Ravi Menon, Customer |  |  |  |

Where the accounts disagree

At least three points of disagreement run through the transcripts, and each can be settled by going to the ticket data rather than by deciding whose account sounds more convincing. Identify them, then resolve them with evidence.

| The disagreement | Who says what | How the data settles it | What follows from the answer |
|---|---|---|---|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

What nobody said

Real stakeholders leave out the things so familiar to them that they no longer notice them. Record anything you expected somebody to raise that none of the five actually did.

| What was never mentioned | Why you would have expected it | How you will check it |
|---|---|---|
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

2   Section two: what the ticket data shows

Before you interpret anything, count it. Load development_tickets.json and fill in the table below from the data itself rather than from impression. Where a figure surprises you, write the surprise down; those are usually the most productive threads to pull.

| What to measure | Your figure | Where the figure came from | What surprised you about it |
|---|---|---|---|
| Total tickets in the sample |  |  |  |
| Split by channel |  |  |  |
| Split by intent category |  |  |  |
| Split by urgency |  |  |  |
| Proportion marked resolved on first contact |  |  |  |
| Average satisfaction rating |  |  |  |
| Most frequent single question |  |  |  |
| Proportion answerable from existing documentation |  |  |  |
| Proportion marked non-fluent, and their outcomes |  |  |  |
| Outcomes by customer tier |  |  |  |
| Proportion that are repeat contacts |  |  |  |
|  |  |  |  |
|  |  |  |  |

| Two rows matter more than the restThe proportion of tickets already answerable from existing documentation tells you whether CloudServe lack answers or merely lack a way of reaching them. Those are different problems with different solutions. The non-fluent segment matters for a different reason: something in the transcripts points at it, and the data will tell you whether that person was right. |
|---|

3   Section three: where the time actually goes

Understanding volume is not the same as understanding effort. A category that accounts for five per cent of tickets but forty per cent of agent hours is where the real problem lives. Work out, as far as your evidence allows, how effort is distributed.

| Ticket category | Share of volume | Estimated share of effort | Why the two differ | Evidence for your estimate |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

The steps an agent takes on a typical ticket

Sofia describes her working process in some detail in the second transcript. Reconstruct it as a sequence of steps and record roughly where the time goes at each one. The steps that sound trivial are frequently where the minutes accumulate.

| Step | What the agent does | Roughly how long | Could this be automated? Say why or why not |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

4   Section four: what the client counts as success

You cannot improve a number nobody is watching. Marcus names the figures he reports and is explicit about which one he actually cares about, and they are not the same. Record what CloudServe measure, who watches each measure, and what would have to change for this project to be considered worthwhile.

| Measure | Who watches it | Current value | What they would call success | How confident are you in this? |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

The sentence test

Complete the following sentence using only figures you recorded above. If you cannot complete it, your discovery is not finished.

| Prompt | Your answer |
|---|---|
| This project will have been worth doing if, within three months of launch, ... |  |
| We will know it did not work if we see ... |  |
| The measure the client will actually be judged on internally is ... |  |

5   Section five: data, constraints and risk

Everything you build depends on data that already exists, and every piece of that data carries constraints. Record what exists, what condition it is in, and what you are not permitted to do with it. Ines and Daniel both raise concerns about data quality that belong in this table.

| Data source | What it contains | Quality and gaps | Access constraints | Private data present? |
|---|---|---|---|---|
| Support tickets |  |  |  |  |
| Documentation |  |  |  |  |
| Past resolutions |  |  |  |  |
| Customer records |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

Initial risk register

List what could go wrong once this system is speaking to customers without supervision. You will develop these further in stage five, but the first pass belongs here, while the problem is still fresh and you have not yet become attached to a particular design.

| What could go wrong | How likely | How bad | Who it affects | First thought on preventing it |
|---|---|---|---|---|
| The system answers confidently and incorrectly |  |  |  |  |
| Private information appears in a reply |  |  |  |  |
| Some customers get consistently worse answers |  |  |  |  |
| The documentation the system relies on goes out of date |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

6   Section six: the problem statement

Now, and only now, write down what the problem actually is. Every clause of what you write must be supported by a row you have already filled in, and you are asked to cite those rows explicitly. This is the paragraph your entire project rests on.

| Element | Your statement | Which section and row supports it |
|---|---|---|
| What the client asked for |  |  |
| What the evidence suggests they actually need |  |  |
| The gap between those two |  |  |
| Who is affected and how |  |  |
| What will change if this is solved |  |  |
| What is explicitly not in scope |  |  |

The one paragraph version

Write the problem in a single paragraph, in language the head of support would recognise and agree with. No technical vocabulary. If you cannot express it without mentioning retrieval or embeddings, you are describing your solution rather than their problem.

| Problem statement |
|---|
|  |
|  |
|  |

| Before you move to stage twoRead your problem statement back against each of the five transcripts in turn and ask whether that person would recognise it as a description of their situation. If any of the five would object, either your framing is off or you have found something they cannot see, and you should be able to say which. A statement that all five would simply agree with is usually one that has not gone far enough. |
|---|

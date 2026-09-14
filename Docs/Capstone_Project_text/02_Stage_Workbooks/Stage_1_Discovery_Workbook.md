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
| Marcus Adeyemi, Head of Support | Issue over delayed response.FCR % needs to be at least 65% (most important)Chat bot response should be accurate and quick.Types Details or break down they do not know. | The right context for the ticket template to give answer for the query.Why the % of FCR is less.He talked about compliance, but what to keep and what not to keep, he has no Idea.No Deep details of Tickets are available | Why it’s taking time for employees to take time to look for correct refs.What causing FCR to move to tier 2 too often. |
| Sofia Restrepo, Tier One Agent | Queue is 40 to 70 tickets, worst on Mondays, sorted by age.Known ticket takes 4 to 5 min; unusual one up to 40 min, then escalated anyway.7 out of 10 tickets she could answer without looking anything up.Time goes to finding the answer and writing it out, not knowing it.Docs are good but search is painful, so agents keep private answer files.Escalates for 3 reasons: does not know, not confident, or security.Wants a draft plus the relevant page attached; would save half of every ticket.Non-fluent tickets take longer, get answered wrongly, have the worst CSAT. | The knowledge base already covers what she reconstructs from memory (Ines).Her private answer file may be stale (Daniel).Data does not show non-fluent tickets scoring worst.Sorting by age leaves urgent tickets waiting longest. | Share of tickets answerable from docs (her 7 in 10).Non-fluent CSAT and FCR vs fluent.How fast known-type tickets actually resolve |
| Daniel Okonkwo, Tier Two Engineer | About half of what reaches him could have been resolved at tier one.Marcus sees the escalation rate, not what is inside it.Escalations arrive as the raw ticket: no summary, no note of what was tried.He re-reads and re-asks the customer; that causes more frustration than waiting.Wants context: what it is about, relevant docs, what was uncertain. "Show its working."Private snippet files hold answers that were right 2 years ago and are wrong now.Would not automate security, billing disputes, data location. | Labels mark only 4 intents as never-auto; billing and data residency are mostly answerable.That his "half" is measurable, not an impression: 138 of 281 escalated tickets were answerable from the docs, and 92 were labelled auto-respondable.That the ticket labels disagree with his never-automate list: only security, compliance, feature requests and unclear requests are marked never-auto; billing (87.5%) and data residency (72.4%) are mostly labelled answerable. Recorded as a disagreement to resolve, not as his error. | Share of escalated tickets answerable from docs (his "half"): 49.1%.Share of escalations whose expected route was auto-respond: 32.7%.Repeat contact rate on escalated vs resolved tickets: 38.4% vs 0%.Which intents the labels mark as never-auto, against his list. |
| Ines Varga, Technical Writer | 29 articles, reviewed on rotation, accurate within the cycle.Used externally; internally the support team does not use them at all.Cause is search: keyword match on titles; customers phrase problems differently.Wants every answer to name its article, to tell article error from system error.Not covered: feature requests, roadmap, novel incidents.Asked twice to consolidate private files; nothing happened. | How much ticket volume her 29 articles already cover.That the corpus has no freshness field (every article shows 0 days since review). | Share of tickets whose expected answer is in the 29 articles.Which intents have no article at all.Whether every article is actually used by some ticket. |
| Ravi Menon, Customer | Support is slow but decent; the waiting is the problem, not the people.Cost of waiting depends on urgency; same queue, different cost.Finds the answer himself about half the time; the reply is the same thing.Accepts automation only if honest: says what it thinks, cites the page, a person confirms.Wants to know when a reply is automated so he can calibrate trust.Believes enterprise customers get answers in about an hour; will notice at renewal. | Enterprise is the slowest tier in the data, not the fastest.Nobody prioritises the queue by urgency today. | Resolution time by urgency.Resolution time and FCR by tier.Answerable share for his kind of question (API usage). |

Where the accounts disagree

At least three points of disagreement run through the transcripts, and each can be settled by going to the ticket data rather than by deciding whose account sounds more convincing. Identify them, then resolve them with evidence.

| The disagreement | Who says what | How the data settles it | What follows from the answer |
|---|---|---|---|
| Is the problem speed, or tickets bouncing to tier two? | 1) Marcus reports response time (SLA) but says FCR matters more. 2) Daniel: half of escalations were resolvable at tier one. 3) Ravi: the waiting is the problem. | 1) 281 escalated (56.2%). 2) 138 of them answerable from docs (49.1%). 3) 92 had expected route auto-respond (32.7%).4) Escalated CSAT 2.63 vs 3.41 resolved. 5) Repeat contact 38.4% on escalated, 0% on resolved. | 1) Daniel is right almost exactly. 2) The bounce, not just the wait, drives low CSAT and repeats. 3) Reducing escalation of answerable tickets is the lever. |
| Do non-fluent customers get the worst outcomes? | 1) Sofia: yes, and nobody has noticed. 2) Nobody else mentions it. | 1) 120 non-fluent tickets (24%). 2) CSAT 3.04 vs 2.95 fluent. 3) FCR 45.8% vs 43.2%. 4) Median resolution 198 vs 216 min. 5) Only standard-tier non-fluent is worse: CSAT 2.86, median 502 min. | 1) Not supported overall in the human baseline. 2) Governance Framework warns retrieval does worse on non-fluent text. 3) Must be measured on the system's own output, by fluency and tier. |
| Is the documentation the problem, or finding it? | 1) Sofia: docs are fine, cannot find things. 2) Ines: articles accurate, search is keyword-on-title. 3) Daniel: circulating answers are stale (private files, not the knowledge base). 4) Marcus: canned library failed on findability. | 1) 357 tickets answerable (71.4%). 2) Only 61.3% of those resolved first time; 138 escalated anyway. 3) Every article is the expected source for at least one ticket. 4) Answerable median 48 min vs 750 min not answerable. 5) All 29 articles show 0 days since review. | 1) Content exists; delivery fails. 2) Retrieval with citation is the fix, not writing new docs. 3) Never learn from private files. 4) No staleness signal exists, so it must be built. |
| Do enterprise customers get faster service? | 1) Ravi: about an hour. 2) Marcus: they will notice if it gets worse. | 1) Enterprise median 369 min vs business 141, standard 266. 2) Enterprise FCR 37.3%, lowest tier. 3) Only on high urgency is enterprise fastest (198 vs 292 vs 347 min). | 1) Ravi's belief is wrong on resolution time. 2) Marcus's concern still holds: do not widen the gap. 3) Tier is a fairness segment. 4) Caveat: resolution time is not first-reply time; no first-reply field exists. |

What nobody said

Real stakeholders leave out the things so familiar to them that they no longer notice them. Record anything you expected somebody to raise that none of the five actually did.

| What was never mentioned | Why you would have expected it | How you will check it |
|---|---|---|
| Repeat contacts | Daniel describes re-asking customers, which creates them. | 21.6% of tickets; 0% of resolved, 38.4% of escalated; highest in compliance (11) and feature requests (10). |
| Channel differences | the brief says channels behave differently. | docs_comment worst FCR 34.6% and repeat 33.3%; forum best FCR 50.9%; chat lowest CSAT 2.72; all 155 chat tickets have empty subject. |
| Urgency ordering of the queue | Ravi says cost depends on urgency; Sofia sorts by age. | high urgency has the longest median (342 min) and lowest FCR (39.7%); low urgency 132 min, 48.4%. |
| How first-reply time is measured | it is the red SLA number Marcus reports. | no first-reply field in the data; only resolution minutes. Record as open question. |
| Regional variation | Dataset Guide names region as a fairness segment. | latin_america CSAT 2.73 lowest; asia_pacific FCR 39.5% and answerable 63.9% lowest. |

2   Section two: what the ticket data shows

Before you interpret anything, count it. Load development_tickets.json and fill in the table below from the data itself rather than from impression. Where a figure surprises you, write the surprise down; those are usually the most productive threads to pull.

| What to measure | Your figure | Where the figure came from | What surprised you about it |
|---|---|---|---|
| Total tickets in the sample | 1) 500 tickets. 2) 220 distinct customers, 150 of them with more than one ticket. 3) Received 1 March to 30 May 2026, about 13 weeks. | Count of records in development_tickets.json; distinct customer_id; min and max of received_at. (in codebase) analysis/discovery_counts.py. | 1) About 39 tickets a week, far below Marcus's 500+ a week, so this is a labelled sample, not the queue. 2) Fridays have the most arrivals (85), not Mondays (75); Sofia's "Mondays are worst" describes backlog, not arrivals. |
| Split by channel | 1) email 212 (42.4%). 2) chat 155 (31.0%). 3) docs_comment 78 (15.6%). 4) forum 55 (11.0%). | count of channel field. | 1) docs_comment, which the brief calls "usually answerable from existing material", has the worst FCR (34.6%) and the highest repeat rate (33.3%). 2) chat has the lowest CSAT (2.72). 3) All 155 chat tickets have an empty subject. |
| Split by intent category | 1) 22 classes, each between 13 and 29 tickets. 2) Largest: data_export 29, data_residency 29, rollback_request 28, deployment_failure 27. 3) Smallest: rate_limit 13, unclear_request 15, configuration_help 17. | count of labels.intent. | 1) Flat distribution, no dominant intent; the biggest class is only 5.8% of volume. 2) Sofia's "same ones over and over" examples (password lockouts 20, rate limits 13, invoices 24, rollbacks 28) are not the largest classes; rate limits is the smallest. |
| Split by urgency | 1) high 146 (29.2%). 2) medium 226 (45.2%). 3) low 128 (25.6%). | count of labels.urgency; median of history.resolution_time_minutes per urgency. | 1) High-urgency tickets take longest to resolve: median 342 min vs 188 medium vs 132 low. 2) High urgency also has the lowest FCR (39.7%). Urgency is not shortening the wait today. |
| Proportion marked resolved on first contact | 1) 43.8% (219 of 500). 2) Escalated 56.2% (281). | history.first_contact_resolution and history.escalated. | 1) Matches Marcus's 42% and the brief's 58% escalation within two points, so his numbers are reliable. 2) Resolved tickets average CSAT 3.41; escalated 2.63. |
| Average satisfaction rating | 1) 2.97 out of 5.2) Distribution: 1 star 89, 2 stars 107, 3 stars 114, 4 stars 109, 5 stars 81. | mean of history.csat_rating. | 1) Lower than the 3.2 the client reports. 2) Nearly flat distribution; 39% of tickets rate 1 or 2. |
| Most frequent single question | 1) By intent: data_export and data_residency, 29 each. 2) By exact subject line: "Please add per-project spend caps", 12 tickets, then "Connecting our CI pipeline", 11. | count of labels.intent; count of identical subject strings. | 1) The most repeated subject is a feature request, which has no documentation and must always escalate. 2) Repetition does not mean answerable. |
| Proportion answerable from existing documentation | 1) 71.4% (357 of 500). 2) Of those, only 61.3% were resolved on first contact; 138 answerable tickets were escalated anyway. 3) Not answerable: 143 (28.6%), all escalated, median 750 min. | labels.answerable_from_docs crossed with history.first_contact_resolution and history.escalated. | 1) 138 tickets, 27.6% of the whole sample, had a documented answer and still went to tier two. 2) Answerable tickets resolve in a median of 48 min; non-answerable in 750 min. 3) CloudServe does not lack answers; it lacks a way of reaching them. |
| Proportion marked non-fluent, and their outcomes | 1) 24.0% (120). 2) FCR 45.8% vs 43.2% fluent. 3) CSAT 3.04 vs 2.95. 4) Median resolution 198 min vs 216. 5) Repeat contact 19.2% vs 22.4%. 6) Bodies shorter: 127 vs 142 characters. | language_fluency crossed with the history fields; mean length of body. | 1) Sofia's claim that non-fluent tickets have the worst satisfaction is not supported in the historical data. 2) It holds only for standard-tier non-fluent customers: CSAT 2.86 and median 502 min. 3) The human baseline shows no bias, but the Governance Framework warns a retrieval system usually does, so this must be re-measured on the system's own output. |
| Outcomes by customer tier | 1) enterprise 83 (16.6%): FCR 37.3%, CSAT 3.05, median 369 min. 2) business 164 (32.8%): FCR 48.2%, CSAT 2.91, median 141 min. 3) standard 253 (50.6%): FCR 43.1%, CSAT 2.98, median 266 min. | customer_tier crossed with the history fields. | 1) Enterprise, the tier with the stricter agreement, has the lowest FCR and slowest median resolution. 2) Only on high-urgency tickets is enterprise fastest (198 vs 292 vs 347 min). 3) Ravi's belief that enterprise gets answers in an hour is not borne out. |
| Proportion that are repeat contacts | 1) 21.6% (108). 2) 0% of first-contact resolutions; 38.4% of escalated tickets. 3) Highest in compliance_request (11) and feature_request (10). | history.repeat_contact crossed with first_contact_resolution and intent. | 1) Repeat contact is entirely a property of escalated tickets. 2) Nobody at CloudServe measures it; the brief lists it as "not measured". |
|  |  |  |  |
|  |  |  |  |

| Two rows matter more than the restThe proportion of tickets already answerable from existing documentation tells you whether CloudServe lack answers or merely lack a way of reaching them. Those are different problems with different solutions. The non-fluent segment matters for a different reason: something in the transcripts points at it, and the data will tell you whether that person was right. |
|---|

3   Section three: where the time actually goes

Understanding volume is not the same as understanding effort. A category that accounts for five per cent of tickets but forty per cent of agent hours is where the real problem lives. Work out, as far as your evidence allows, how effort is distributed.

| Ticket category | Share of volume | Estimated share of effort | Why the two differ | Evidence for your estimate |
|---|---|---|---|---|
| security_incident | 5.2% (26 tickets) | 9.7%. | 1) Escalated 100% of the time. 2) Median resolution 734 min, the longest of any intent. 3) Only 53.8% have a matching article. | counts script, effort table; Sofia: security is escalated "every time regardless". |
| compliance_request | 5.2% (26). | 8.4%. | 1) Escalated 100%. 2) Median 678 min. 3) Lowest CSAT of any intent, 2.35. 4) Repeat contact 42.3%. | counts script; Marcus's autumn compliance review; Daniel's data-location concern. |
| feature_request | 4.0% (20). | 6.9%. | 1) No article exists, 0% answerable. 2) Escalated 100%. 3) Repeat contact 50%, the highest. 4) The single most repeated subject line ("per-project spend caps", 12 tickets) is one of these. | counts script; Ines: "no answer to retrieve". |
| data_residency | 5.8% (29). | 7.1%. | 1) 69% escalated even though 72.4% are answerable from DOC-DATA-003. 2) Median 319 min. | counts script; Daniel: "we get those wrong occasionally even as humans and the consequence is a compliance problem". |
| deployment_failure, performance_degradation, database_issue (diagnostic problems) | 15.2% (76). | 17.7%. | 1) 59 to 73% escalated although about 70% are answerable.2) Medians 384 to 482 min. 3) Only 38 to 44% of performance and database tickets are labelled auto-respondable, so retrieval alone will not clear them. | counts script; Ravi: "my deployment is failing at nine in the morning and I cannot ship". |
| the four never-auto intents together (security, compliance, feature, unclear) | 17.4% (87). | 28.7%. | 1) None can be automated. 2) All escalated, CSAT 2.63, repeat 37.9%. 3) This is the work agents should be freed for. | counts script, 9.7 + 8.4 + 6.9 + 3.7; Marcus: "answering the easy ones so my people can do the hard ones". |
| high-answerable, low-effort intents (rate_limit, onboarding, sso_configuration, api_key_issue, quota_or_overage, account_access, data_export) | 30.4% (152). | 17.7% | 1) 77 to 93% answerable. 2) Medians 35 to 47 min. 3) FCR 56 to 77%, the best in the sample. 4) Effort ratio 0.29 to 0.70, meaning each ticket costs less than average. | counts script; Sofia: "if it is one I have seen before, four or five minutes". |

The steps an agent takes on a typical ticket

Sofia describes her working process in some detail in the second transcript. Reconstruct it as a sequence of steps and record roughly where the time goes at each one. The steps that sound trivial are frequently where the minutes accumulate.

| Step | What the agent does | Roughly how long | Could this be automated? Say why or why not |
|---|---|---|---|
| 1 | Open the queue and pick a ticketOpens 40 to 70 tickets. Sorts by age. 3) Takes the oldest, "the ones about to breach". | Not stated | Yes. 1) Ordering is a rule. 2) Today high-urgency tickets are slowest (median 342 min vs 132 low), so age-ordering works against Ravi's point that cost depends on urgency. 3) Needs urgency classification first. |
| 2 | Read the ticket and work out what is being asked Reads subject and body. Infers the actual problem. On non-fluent tickets "I have to work out what they are actually asking… sometimes I get it wrong" | inside the 4 to 5 min for known tickets; the main cost on non-fluent ones. | Partly. 1) Intent and urgency classification with a confidence score. 2) Must escalate when unsure rather than guess, which is Sofia's own failure mode. |
| 3 | Decide whether it is one seen before Recognises the pattern. "Seven out of ten I could answer without looking anything up." | seconds. | Yes. 1) Same classifier as step 2. 2) Confidence must be calibrated so "seen before" is measured, not assumed. 3) Data: 71.4% answerable confirms her 7 in 10. |
| 4 | Find the answerCopies from a personal answer file. Or searches the documentation, which is "painful, so most of us do not". Canned library was abandoned because "finding the right one took longer than writing the answer". | "finding it and writing it out" is where the time goes; up to 40 min on unusual tickets. | Yes, this is the core lever. 1) Retrieval by meaning over the 29 articles, not keyword-on-title (Ines). 2) Returns the article id so Ines can trace errors. 3) Never from private files, which Daniel says are stale. |
| 5 | Write the answer outTypes or adapts the answer. 2) Ines: agents reproduce her articles "almost word for word… from memory". | the other half of "finding it and writing it out". | Yes. 1) A draft grounded in the retrieved article with citations. 2) Sofia: "a ticket with a draft and the relevant page attached… would save me half of every ticket". |
| 6 | Decide to send or escalateSends if confident. Escalates if she does not know, is not confident, or it is security.Fear of being wrong: "if I get it wrong it comes back worse". | Not stated | Yes for the decision. 1) A measured confidence threshold. 2) Security and the other never-auto intents always escalate. 3) Reason logged, because Marcus must "say why it did what it did". |
| 7 | Forward the escalation (Daniel's view)Forwards "just the original ticket". Tier two reads the whole thread. 3) Often asks the customer something already asked. | Daniel would be "twice as fast" with context. | Yes. 1) Attach the draft, retrieved sources, and what the system was unsure about. 2) This is where Daniel says "customer frustration really comes from, more than the waiting", and where 38.4% of escalated tickets become repeat contacts. |
|  |  |  |  |

4   Section four: what the client counts as success

You cannot improve a number nobody is watching. Marcus names the figures he reports and is explicit about which one he actually cares about, and they are not the same. Record what CloudServe measure, who watches each measure, and what would have to change for this project to be considered worthwhile.

| Measure | Who watches it | Current value | What they would call success | How confident are you in this? |
|---|---|---|---|---|
| Time to first reply | 1) The executive team, via Marcus's report. 2) It is the SLA figure: "Response time is what is in the agreement so it is what gets reported." | 1) 8 to 12 hours (Marcus, and the brief). 2) Not verifiable in the data: no first-reply timestamp exists; nearest proxy is resolution time, median 214 min, only 45% within 2 h. | Under 2 hours, the SLA. Under 5 minutes for the automated first response (Evaluation Framework). | Medium. Stated by the client and the pack, but no field in the data to confirm it. |
| First contact resolution | 1) Marcus: "First contact resolution, if I am being honest, more than response time." 2) Not what he reports upward. | 1) 42% (Marcus, brief). 2) 43.8% in the development data. | 1) 65%, the benchmark Marcus quotes. 2) 60% or better, the brief and Evaluation Framework target. | High. Transcript and data agree within two points. |
| Escalation rate | 1) Marcus sees the rate. 2) Daniel: "Marcus sees the escalation rate, not what is inside the escalations." | 1) 58% (brief). 2) 56.2% in the data, and 49.1% of those escalations were answerable from the docs. | 30% or lower (brief). Reported alongside FCR, since they mirror each other. | High. Two sources agree. |
| Customer satisfaction | 1) Marcus. 2) Sales, indirectly: "renewal conversations have started going badly" (brief). | 1) 3.2 out of 5 (brief). 2) 2.97 in the data; 39% of tickets rate 1 or 2; resolved tickets 3.41, escalated 2.63. | 4.2 (brief) or 4.0 (Evaluation Framework). | Medium. The two sources differ by 0.23, and the project can only measure a rubric proxy, not live customers. |
| Cost of an escalated ticket | Marcus, as budget owner: "every ticket that bounces to tier two costs us roughly four times what a resolved one costs." | 1) About 4× a resolved ticket. 2) Not in the data. 3) 138 answerable tickets were escalated, so that cost was paid 138 times unnecessarily in the sample. | Fewer escalations of answerable tickets; headcount not increased ("three more headcount that I am not going to get"). | Low. A single verbal estimate, no cost data. |
| Repeat contacts | Nobody today. The brief lists it as "not measured". | 21.6% in the data; 0% of resolved tickets, 38.4% of escalated. | Halved (brief and Evaluation Framework). | High for the baseline, since it is counted directly; the target is the pack's, not the client's. |
| No wrong answer sent to a customer | 1) Marcus: "If it sends something wrong to a customer… I would rather it said nothing than said something wrong." 2) Sofia fears picking up the angry follow-up. 3) Ravi: "I will act on it and break something." | Not measured today. | Zero confidently wrong automated answers; escalation instead of guessing. | High that it is the client's first failure condition. Three of five stakeholders name it unprompted. |
| Enterprise service level | Marcus and Ravi | enterprise is the slowest tier, median 369 min, FCR 37.3%; | no widening of the gap, under 5 points variation across groups. | medium |

The sentence test

Complete the following sentence using only figures you recorded above. If you cannot complete it, your discovery is not finished.

| Prompt | Your answer |
|---|---|
| This project will have been worth doing if, within three months of launch, ... | 1) first contact resolution rises from 42 to 44% toward 60 to 65%.2) escalation falls from 56 to 58% toward 30%.3) the answerable tickets that today reach tier two, 138 of 500 in the sample, are answered on first contact.4) repeat contacts fall from 21.6% toward 11%. 5) no confidently wrong answer has been sent. |
| We will know it did not work if we see ... | 1) a wrong answer sent to a customer. 2) escalations still arriving without a draft and sources, so tier two is no faster.3) agent workload rising as it did with canned.4) the enterprise tier falling further behind. |
| The measure the client will actually be judged on internally is ... | time to first reply against the 2-hour SLA, because it is the number the executive team sees every quarter, even though Marcus himself says first contact resolution matters more . |

5   Section five: data, constraints and risk

Everything you build depends on data that already exists, and every piece of that data carries constraints. Record what exists, what condition it is in, and what you are not permitted to do with it. Ines and Daniel both raise concerns about data quality that belong in this table.

| Data source | What it contains | Quality and gaps | Access constraints | Private data present? |
|---|---|---|---|---|
| Support tickets | 1) 500 tickets, 4 channels. 2) Subject, body, timestamp, customer id and name, tier, region, fluency flag. 3) Labels: intent, urgency, expected route, answerable, expected doc ids, must-not-auto. 4) History: FCR, resolution minutes, CSAT, escalated, repeat. | 1) Labels consistent; every expected doc id resolves to a real article. 2) All 155 chat tickets have an empty subject. 3) No first-reply timestamp, so the SLA figure cannot be checked. 4) Sample is 13 weeks at about 39 a week, not the full queue. 5) History is a failing baseline, not a target (Dataset Guide). | 1) Development set: use freely. 2) Validation set (80): held back until the system is built. 3) Hidden set (120): never seen; harness must take an input path. | Yes. customer_name and customer_id on every ticket. Free text scan found no emails, keys, IPs, card or phone numbers; 39 tickets match a loose account-id pattern, to check by hand. |
| Documentation | 1) 29 knowledge-base articles in 10 categories. 2) Markdown with fixed headings: Symptoms, Common causes, Resolution, Notes. 3) applies_to, related_docs, last_reviewed_days_ago. | 1) Accurate "within the review cycle" (Ines). 2) Covers 71.4% of tickets; every article is the expected source for at least one ticket. 3) No article for feature requests, unclear requests, roadmap, or novel incidents. 4) last_reviewed_days_ago is 0 on all 29, so there is no usable staleness signal. 5) Dataset Guide says "eight categories" but lists and the data hold ten. | Free. It is the retrieval corpus. | No |
| Past resolutions | 1) The history block per ticket: outcome only, no answer text. 2)ground_truth_responses.json: 200 answers by senior agents with must_mention and must_not_claim lists. 3) Agents' private snippet files (Sofia, Daniel, Ines all mention them). | 1) History gives no answer text to learn from. 2) Reference answers cover 200 of the 500 tickets and 20 of 22 intents; must_not_claim is the same three items on all 200 (refund issued, fixed on our side, delivery date); must_mention is empty on 141. 3) Private files are unreviewed; Daniel: answers "correct two years ago and have not been right since"; Ines asked twice to consolidate them. | 1) History and reference answers: free. 2) Private files: not in the pack, and must not be used as a source. | Reference answers: none observed. Private files: unknown. |
| Customer records | Only what the ticket carries: customer_id, customer_name, tier, region, fluency flag. No separate customer table. | 1) No contract terms or per-tier SLA, although Marcus says enterprise "have a different agreement". 2) No renewal data. 3) 220 customers, 150 with more than one ticket, so repeat behaviour is traceable. | Not provided; assume nothing beyond the ticket fields. | Yes, name and id. |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

Initial risk register

List what could go wrong once this system is speaking to customers without supervision. You will develop these further in stage five, but the first pass belongs here, while the problem is still fresh and you have not yet become attached to a particular design.

| What could go wrong | How likely | How bad | Who it affects | First thought on preventing it |
|---|---|---|---|---|
| The system answers confidently and incorrectly | High if unchecked; the model will fill gaps, and security tickets are only 54% answerable so retrieval can return something plausible. | Severe. Marcus's first failure condition; customers "will screenshot a confidently incorrect answer and put it on the internet". | The customer who acts on it (Ravi: "I will act on it and break something"), then the agent who picks up the follow-up (Sofia). | 1) Answer only from a retrieved article, with the article id. 2) Calibrated confidence and a measured threshold. 3) Escalate when unsure. 4) Tell the customer it is automated (Ravi). |
| Private information appears in a reply | Medium. Name and id sit on every ticket and the model sees them. | Severe. Governance condition is zero occurrences. | The customer whose data leaks; CloudServe's autumn compliance review. | 1) Never pass ticket fields into the reply. 2) Scan every outbound draft. 3) Block and escalate, never redact and send. |
| Some customers get consistently worse answers | Medium. Human baseline shows little fluency gap, but the Governance Framework says retrieval systems usually do worse on non-fluent phrasing; latin_america already has the lowest CSAT (2.73) and asia_pacific the lowest FCR (39.5%). | High. Renewal risk; fairness condition is under 5 points variation. | Non-fluent customers, standard tier, latin_america and asia_pacific regions. | Measure the system's output by fluency, tier and region against the human baseline before launch, not after. |
| The documentation the system relies on goes out of date | Medium. No freshness field exists; Ines reviews on rotation by hand. | High. A stale article becomes a scaled mistake (Daniel). | Every customer on the affected intent; Ines, who must find the fault. | 1) Retrieve only from the 29 reviewed articles, never private files. 2) Log the article id on every answer so Ines can tell an article error from a system error. 3) Flag articles by age once a review date exists. |
| A never-auto ticket is answered automatically | Medium; 17.4% of tickets are in these four intents | Severe; the Dataset Guide calls it a governance failure, not a scoring loss. | customers, compliance | hard rule that compliance, security, feature and unclear intents escalate regardless of confidence; low-confidence classification also escalates. |
| The system makes a commitment about money or timing | Medium; billing (87.5%) and data residency (72.4%) are labelled answerable. | High; Daniel: "those become contractual quickly". | CloudServe commercially. | block any reply containing the three universal forbidden claims: a refund issued, fixed on our side, a delivery date. |
| Escalations arrive without context | High;it is how it works today. | Medium; the project fails to reduce workload, Marcus's second failure. | tier two and the customers re-asked questions. | every escalation carries the draft, retrieved sources and what the system was unsure about. |
| The system makes more work than it saves | Medium; the canned response library failed this way. | High; agents stop using it. | tier one. | keep Sofia's requested format, draft plus page; measure agent time per ticket before and after. |
| Customer text is treated as an instruction | Medium; every input is free text from strangers. | High; the system can be redirected. | CloudServe | separate ticket content from system instructions; detect and block, log the input for review. |

6   Section six: the problem statement

Now, and only now, write down what the problem actually is. Every clause of what you write must be supported by a row you have already filled in, and you are asked to cite those rows explicitly. This is the paragraph your entire project rests on.

| Element | Your statement | Which section and row supports it |
|---|---|---|
| What the client asked for | 1) A chatbot. 2) Marcus pictures it "answering the easy ones so my people can do the hard ones". 3) He has "no strong view about how it works". 4) The number he needs down is response time, without extra headcount. | Section 1, Marcus , Section 4, row 1. |
| What the evidence suggests they actually need | 1) 71.4% of tickets already have an answer in the 29 articles. 2) 138 of those still went to tier two. 3) Agents cannot find the articles because search is keyword-on-title, so they answer from memory and private files. 4) Half of escalations (49.1%) were resolvable at tier one. 5) Escalations arrive with no context, so tier two re-reads and re-asks. 6) Agents want a draft with the source page attached, not a replacement. | Section 2, row 8; Section 1, disagreements rows 1 and 3; Section 1, Sofia row point 5, Ines row point 3, Daniel row points 3 to 5; Section 3, steps 4, 5 and 7. |
| The gap between those two | 1) A chatbot delivers answers; it does not decide where answers come from, when to stay silent, or who is accountable. 2) The client's first failure condition is a wrong answer sent, so the system must be able to say nothing and escalate. 3) 17.4% of tickets must never be automated at all. 4) The value is as much in better escalations as in automatic answers. | Section 1, Marcus row (failure conditions); Section 4, row 7; Section 2, row 12; Section 1, Daniel row point 5; Section 5, risks 1 and 5. |
| Who is affected and how | 1) Customers: median 214 min to resolution, p95 21 hours, only 45% inside the 2-hour SLA; the cost of waiting depends on urgency, but urgent tickets are slowest. 2) Escalated customers: CSAT 2.63 vs 3.41, and 38.4% come back. 3) Tier one: time lost finding and writing known answers. 4) Tier two: half their queue is not tier-two work. 5) Enterprise: slowest tier despite the stricter agreement. 6) The team: two agents left citing workload. | Section 2, rows 4, 5, 10, 11, 13; Section 1, Ravi row points 1 and 2; Section 3, steps 4 to 7; Section 1, disagreements row 4; Section 4, extra row on attrition. |
| What will change if this is solved | 1) FCR from 42 to 44% toward 60 to 65%. 2) Escalation from 56 to 58% toward 30%. 3) Repeat contacts halved from 21.6%. 4) Agents freed for the 28.7% of effort that can never be automated. 5) Tier two "twice as fast" when escalations carry context. 6) Every decision explainable for the compliance review. | Section 4, rows 2, 3, 6; Section 3, row 6; Section 1, Daniel row point 5; Section 1, Marcus row (compliance). |
| What is explicitly not in scope | 1) Automatic answers for compliance, security, feature and unclear requests (87 tickets). 2) Any commitment about refunds, fixes, or delivery dates. 3) Learning from agents' private snippet files. 4) Writing new documentation; that stays with Ines. 5) Measuring time to first reply directly, since no such field exists; resolution time is the stated proxy. | Section 2, row 12; Section 5, risk 6 and data source 3; Section 1, Ines row points 4 and 5; Section 1, nobody-said row 4; Section 2, row 13. |

The one paragraph version

Write the problem in a single paragraph, in language the head of support would recognise and agree with. No technical vocabulary. If you cannot express it without mentioning retrieval or embeddings, you are describing your solution rather than their problem.

| Problem statement |
|---|
|  |
|  |
|  |

| Before you move to stage twoRead your problem statement back against each of the five transcripts in turn and ask whether that person would recognise it as a description of their situation. If any of the five would object, either your framing is off or you have found something they cannot see, and you should be able to say which. A statement that all five would simply agree with is usually one that has not gone far enough. |
|---|

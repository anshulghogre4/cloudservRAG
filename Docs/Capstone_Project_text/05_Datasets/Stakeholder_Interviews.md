FORWARD DEPLOYED AI ENGINEERING

Capstone Project

Stakeholder Interviews

Transcripts from your discovery conversations at CloudServe

These are your primary evidence. Read them the way you would read your own
notes: for what people say, what they avoid saying, and where they disagree.

| DISCOVERY EVIDENCE · STAGE ONE |
|---|

How to use these transcripts

CloudServe Solutions is a fictional client, so you cannot walk into their office. What you have instead is the next best thing: transcripts of five conversations conducted on your behalf, with the people you would have wanted to speak to. They are your primary discovery evidence and your Stage 1 workbook is filled in from them, alongside the ticket data.

Treat them as you would treat real interviews rather than as a briefing document. Real stakeholders describe the part of the problem they can see, they contradict each other, they are occasionally wrong about their own operation, and they leave out the things that are so familiar to them that they no longer notice. All of that is present here.

| What you are looking forNobody in these transcripts states the central problem outright. Several of them describe one facet of it, and two of them contradict one another on a point of fact that you can settle by going to the ticket data. Finding what they are collectively describing, and evidencing it, is the substance of Stage 1. |
|---|

Who you spoke to

| Person | Role | Time with CloudServe | Why they matter |
|---|---|---|---|
| Marcus Adeyemi | Head of Customer Support | Four years | Owns the numbers and the budget. Commissioned this work. |
| Sofia Restrepo | Tier One Support Agent | Fourteen months | Handles first-line volume. Sees every ticket before anyone else. |
| Daniel Okonkwo | Tier Two Support Engineer | Three years | Takes escalations. Sees what tier one could not resolve. |
| Ines Varga | Technical Writer, owns documentation | Two years | Maintains the knowledge base your system will retrieve from. |
| Ravi Menon | Customer, platform lead at a mid-size client | Customer for two years | Raises tickets. Experiences the current service. |

The interviewer is shown as INTERVIEWER. Timestamps and small talk have been removed. Nothing else has been edited.

1   Interview one: Marcus Adeyemi, Head of Customer Support

Forty minutes, conducted remotely.

INTERVIEWER:  Can you describe the problem as you see it?

MARCUS:  We are underwater. We take somewhere north of five hundred tickets a week now and we have six agents. Our service agreement says first response inside two hours and we are averaging somewhere between eight and twelve. I have been reporting a red number to the executive team for two quarters and I have run out of ways to explain it.

INTERVIEWER:  What have you already tried?

MARCUS:  We hired two people last year. It helped for about a month and then volume caught up. We tried a canned response library, which the agents hated because finding the right one took longer than writing the answer. We looked at outsourcing tier one and the quotes were more than my entire team costs.

Note: Spending more time looking for right  context to pick the template to answer.

INTERVIEWER:  You have asked for a chatbot. What do you picture it doing?

MARCUS:  Honestly? I picture it answering the easy ones so my people can do the hard ones. I do not have a strong view about how it works. What I need is for the response time number to come down without me asking for three more headcount that I am not going to get.

INTERVIEWER:  Which number matters most to you?

MARCUS:  First contact resolution, if I am being honest, more than response time. Response time is what is in the agreement so it is what gets reported. But every ticket that bounces to tier two costs us roughly four times what a resolved one costs, and it makes the customer angrier than waiting would have. We are at forty-two per cent. The industry benchmark people quote at me is sixty-five.

Note: Lot of tickets going to Tier 2 instead being resolved on Tier 1 It self.

INTERVIEWER:  What would make this project a failure in your eyes?

MARCUS:  If it sends something wrong to a customer. We are a platform company, our customers are engineers, they will screenshot a confidently incorrect answer and put it on the internet within the hour. I would rather it said nothing than said something wrong. The second failure would be if it makes more work for the agents than it saves, which is what happened with the canned responses.

Note: Should not respond with wrong answer and at the same time should be  quick.

INTERVIEWER:  Do you know what your tickets are actually about?

MARCUS:  Broadly. Authentication, deployment problems, billing questions, API questions. If you asked me for a breakdown I would be guessing. We have the data, we have never really sat down with it. That is probably an admission I should not be making.

Note: They Do not know the breakdown what it’really for, as they have not seen the data, means they need a classification of tickets and intent , and priority.

INTERVIEWER:  Anything you are worried about that we have not covered?

MARCUS:  Two things. Enterprise customers have a different agreement and they will notice immediately if they get worse service than they were getting. And I have a compliance review in the autumn, so whatever we do has to be explainable. I need to be able to say why it did what it did.

Note: it should be accurate if not raise it to tier 2, and why and why not needs to be logged to be compliant with the compliance.

2   Interview two: Sofia Restrepo, Tier One Support Agent

Thirty-five minutes, conducted remotely.

INTERVIEWER:  Walk me through a typical morning.

SOFIA:  I open the queue and it is somewhere between forty and seventy tickets depending on the day. Mondays are worst. I sort by age because the oldest ones are the ones about to breach, and then I just work down.

INTERVIEWER:  How long does a ticket take?

SOFIA:  It depends enormously. If it is one I have seen before, four or five minutes. If it is something unusual, it can be forty minutes and then I escalate it anyway.

INTERVIEWER:  What proportion are ones you have seen before?

SOFIA:  Most of them. Genuinely most. I would say seven out of ten I could answer without looking anything up, because I have answered the same question that month already. Password lockouts, rate limits, why is my invoice higher, my deployment keeps rolling back. The same ones over and over.

INTERVIEWER:  If the answer is already known, where does the time go?

SOFIA:  Finding it and writing it out. We have documentation, and it is good documentation, but searching it is painful, so most of us do not. I have a personal file of answers I have written before and I copy from that. Everyone has their own. Daniel has one too, and his is better than mine.

INTERVIEWER:  Have you told anyone the search is the problem?

SOFIA:  I mentioned it to Ines once. I think she thought I meant the documentation was bad, which is not what I meant. The documentation is fine. I cannot find things in it.

INTERVIEWER:  What makes you escalate?

SOFIA:  Three things. I do not know the answer. Or I think I know but I am not confident enough to send it, because if I get it wrong it comes back worse. Or it is a security thing, which we are told to escalate every time regardless.

INTERVIEWER:  How do you feel about a system answering tickets automatically?

SOFIA:  Nervous, but not for the reason you would expect. I am not worried about my job, there is more than enough work. I am worried it will send a wrong answer and I will be the one who picks up the angry follow-up and has to apologise for something I did not write. If it hands me a ticket with a draft and the relevant page attached, that would genuinely help. That would save me half of every ticket.

INTERVIEWER:  Anything about particular customers?

SOFIA:  The ones where English is not their first language take longer, because I have to work out what they are actually asking before I can answer it. Sometimes I get it wrong and answer the wrong question, and then we go round again. Those tickets have our worst satisfaction scores and I do not think anyone has noticed.

3   Interview three: Daniel Okonkwo, Tier Two Support Engineer

Thirty minutes, conducted remotely.

INTERVIEWER:  What reaches you?

DANIEL:  In theory, things tier one cannot resolve. In practice, about half of what reaches me is something tier one could have resolved if they had been confident, or if they had found the right page. The other half is genuinely hard and that is the part of the job I like.

INTERVIEWER:  Half sounds high. Marcus did not mention that.

DANIEL:  Marcus sees the escalation rate, not what is inside the escalations. If you look at the tickets I closed last week, a good number were answered by pasting a link and two sentences. That is not a tier two problem, that is a confidence problem or a findability problem.

INTERVIEWER:  What does an escalation arrive looking like?

DANIEL:  Usually just the original ticket, forwarded. No summary, no note about what was already tried. So the first thing I do is read the whole thread and often ask the customer something they were already asked. That is where the customer frustration really comes from, more than the waiting.

INTERVIEWER:  What would help you most?

DANIEL:  Context. If an escalation arrived saying here is the ticket, here is what I think it is about, here is the documentation that seemed relevant, and here is specifically what I was not confident about, I would be twice as fast. I do not need it to be right. I need it to show its working.

INTERVIEWER:  Any concerns about automation?

DANIEL:  One. Whatever you build will be trained on what we do now, and some of what we do now is wrong. There are answers circulating in people's personal snippet files that were correct two years ago and have not been right since. If you learn from those you will scale up a mistake.

INTERVIEWER:  Which ticket types worry you if automated?

DANIEL:  Anything touching security or account compromise, obviously. Billing disputes, because those become contractual quickly and nothing automated should be making commitments about money. And anything involving data location, because we get those wrong occasionally even as humans and the consequence is a compliance problem.

4   Interview four: Ines Varga, Technical Writer

Twenty-five minutes, conducted remotely.

INTERVIEWER:  Tell me about the documentation.

INES:  There are twenty-nine articles in the support knowledge base, separate from the product documentation. I wrote most of them and I review them on a rotation. They cover the things support answers repeatedly: authentication, deployment, the API, billing, data, security, account management.

INTERVIEWER:  How much are they used?

INES:  Externally, quite a lot. Internally, I do not think the support team uses them at all, and it took me a year to work out that this was happening. I would see a ticket answered with a paragraph that was almost word for word one of my articles, reconstructed from memory rather than copied.

INTERVIEWER:  Do you know why?

INES:  Search. Our internal search matches on titles and exact terms, and customers do not describe problems in the words I used for the title. Someone writes my deployment keeps dying and my article is called resolving container health check failures. There is no path between those two phrases in a keyword search.

INTERVIEWER:  Are they accurate?

INES:  The twenty-nine in the knowledge base, yes, within the review cycle. What worries me is what is not in there. Every agent has a private file of answers and none of that has been reviewed by anyone. I have asked for those to be consolidated twice.

INTERVIEWER:  If a system retrieved from your articles, would you be comfortable?

INES:  More comfortable than with the private files, considerably. But I would want to know which article an answer came from, so that when an answer is wrong I can tell whether the article is wrong or the system misread it. Those need fixing in completely different places.

INTERVIEWER:  What is not covered?

INES:  Feature requests, obviously, since there is no answer to retrieve. Anything about roadmap or timing. And genuinely novel incidents, where by definition there is no article yet. That last category is small but it is the one where a wrong answer does the most damage.

5   Interview five: Ravi Menon, Customer

Twenty minutes, conducted remotely. Platform lead at a client of roughly two hundred people.

INTERVIEWER:  How would you describe support at CloudServe?

RAVI:  Slow but decent once you get there. The people are good. The waiting is the problem. If I raise something at four in the afternoon I have accepted that I am not hearing back until the next day.

INTERVIEWER:  Does the waiting matter equally for everything?

RAVI:  No, and I think this is the bit that gets missed. If I am asking how pagination works, I can wait, it is mildly annoying. If my deployment is failing at nine in the morning and I cannot ship, four hours is a serious problem. Same queue, completely different cost to me.

INTERVIEWER:  What do you do while you wait?

RAVI:  Search the documentation myself, usually. I find the answer maybe half the time. When I do find it, the reply that eventually arrives is normally the same thing, and I have burned two hours.

INTERVIEWER:  How would you feel about an automated first response?

RAVI:  Fine, provided it is honest. If it says here is what I think, here is the page it came from, and a person will confirm, that is useful and I can act on it at my own risk. What I would not accept is something that sounds certain and is wrong, because I will act on it and break something.

INTERVIEWER:  Would you want to know it was automated?

RAVI:  Yes. Not because I object, but because I calibrate how much I trust it. If I know a person wrote it I will act without checking. If I know a machine drafted it I will verify first. Hiding that would be the thing that annoys me.

INTERVIEWER:  Anything else?

RAVI:  One thing. We are on the business plan and I have a colleague at a company on the enterprise plan who gets answers in about an hour. I understand why. But if this change makes that gap bigger, we will notice, and it will come up at renewal.

6   Working with this evidence

Where the transcripts disagree

At least three points of disagreement are present, and each can be settled by going to the ticket data rather than by deciding whose account you find more convincing. Identifying them and resolving them with evidence is exactly what the Stage 1 workbook is asking for.

What nobody says outright

Every interview touches a different edge of the same underlying situation. No single person describes it whole, because each of them can only see their own part of the operation. Assembling it is your work, and the sentence you end up writing in your problem statement should be one that none of the five could have produced on their own.

Following up

Real discovery is iterative and you may finish the transcripts wishing you had asked something else. Where that happens, treat the ticket data as the place to answer it. If a question genuinely cannot be answered from either the transcripts or the data, record it in your workbook as an open question with the assumption you are making in its absence. That is a legitimate and well-marked outcome; inventing an answer is not.

| A cautionIt is tempting to read these transcripts looking for the answer you already suspect. Resist that for one pass. Read them once for what people actually said, note the two claims that surprised you, and only then start forming a view. The strongest submissions each cohort are the ones that changed their mind somewhere between the transcripts and the problem statement. |
|---|

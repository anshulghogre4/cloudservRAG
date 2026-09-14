FORWARD DEPLOYED AI ENGINEERING

Capstone Project

Stage Three: Prompt Library

Turning requirements into specifications and prompts

Your requirements describe what the system must do. This stage turns each of them
into something precise enough to build against and to test.

| WEEK TWO · DAYS ONE AND TWO |
|---|

Why the prompt library exists

In a conventional software project, the step between a requirement and working code is a technical specification. In a system built around language models, a large part of that specification is the prompt itself. The prompt is not a throwaway string that lives in the middle of a function; it is the place where a requirement becomes behaviour, and it deserves the same version control and review as any other design artefact.

Students who keep their prompts scattered through the codebase end up unable to answer simple questions. Which requirement does this instruction serve? What did it say last week? Why was that example added? A library solves all three problems and costs very little to maintain if you start it on day one.

Figure 1. The four categories of prompt and how they descend from the requirements document.

The four categories

| Category | What these prompts do | When you use them |
|---|---|---|
| Specification prompts | Convert a requirement into a technical specification and a set of acceptance criteria. | At the start of week two, before you build. |
| Build prompts | The instructions that run inside the system itself: classification, retrieval framing, answer drafting. | Throughout the build. |
| Review prompts | Critique your own specifications and code against the requirements they came from. | After each component is drafted. |
| Evaluation prompts | Judge answer quality, detect unsupported claims, compare against expert answers. | During the evaluation run in week two. |

1   Section one: from requirement to specification

Take each functional requirement from your PRD and write the specification it implies. Use the specification prompts to help you draft these, but you are accountable for the result; a specification that contradicts your own requirements will be noticed.

| Requirement ID | Specification summary | Inputs | Outputs | Acceptance criteria |
|---|---|---|---|---|
| FR-01 |  |  |  |  |
| FR-02 |  |  |  |  |
| FR-03 |  |  |  |  |
| FR-04 |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

2   Section two: the prompt register

Every prompt in your system gets an entry. Fill in one block per prompt, and copy the block as many times as you need. The version number changes whenever the text changes, and the reason for the change is recorded rather than lost.

Prompt PR-01

| Field | Value |
|---|---|
| Name and purpose |  |
| Category | Specification / Build / Review / Evaluation |
| Serves requirement |  |
| Version | 1.0 |
| Model used |  |
| Inputs it expects |  |
| Output format required |  |
| How you know it worked |  |
| Known weaknesses |  |
| Change history |  |

Prompt text:

| Full prompt text as used in the system |
|---|
|  |
|  |

Prompt PR-02

| Field | Value |
|---|---|
| Name and purpose |  |
| Category | Specification / Build / Review / Evaluation |
| Serves requirement |  |
| Version | 1.0 |
| Model used |  |
| Inputs it expects |  |
| Output format required |  |
| How you know it worked |  |
| Known weaknesses |  |
| Change history |  |

Prompt text:

| Full prompt text as used in the system |
|---|
|  |
|  |

Prompt PR-03

| Field | Value |
|---|---|
| Name and purpose |  |
| Category | Specification / Build / Review / Evaluation |
| Serves requirement |  |
| Version | 1.0 |
| Model used |  |
| Inputs it expects |  |
| Output format required |  |
| How you know it worked |  |
| Known weaknesses |  |
| Change history |  |

Prompt text:

| Full prompt text as used in the system |
|---|
|  |
|  |

3   Section three: what makes a prompt worth keeping

The register above records your prompts. This section is about whether they are any good. Work through the checklist for each build prompt before you rely on it.

| Check | What you are looking for |
|---|---|
| Does it state the role and the task separately? | A prompt that mixes who the model is with what it should do tends to produce inconsistent output. |
| Are the inputs clearly delimited? | Ticket text and instructions must be distinguishable, or a customer can accidentally instruct your system. |
| Is the output format specified exactly? | If you are parsing the response, the format is part of the contract and must be stated. |
| Does it say what to do when the answer is not known? | Without this instruction the model will invent something, because inventing something is what it does. |
| Are the examples representative? | Examples drawn only from easy cases teach the model that every case is easy. |
| Does it forbid what must never happen? | Constraints stated positively are followed more reliably than constraints implied by omission. |

| The injection problem you must handleYour system reads text written by customers and passes it to a model. A customer can write text that looks like an instruction. If your prompt does not clearly separate the ticket content from your own instructions, you have built a system that strangers can reprogram. Record in the register how each build prompt defends against this. |
|---|

4   Section four: traceability check

Complete this table before you move to the sprint plan. It is the evidence that your prompts descend from your requirements rather than from convenience.

| Requirement ID | Specification written? | Prompts covering it | Test case identifier | Gaps |
|---|---|---|---|---|
| FR-01 |  |  |  |  |
| FR-02 |  |  |  |  |
| FR-03 |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

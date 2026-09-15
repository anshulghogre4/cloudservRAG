# Prompt register

Source of truth for every prompt in the system. The full register with inputs, outputs, known
weaknesses and change history is in `Docs/Capstone_Project/02_Stage_Workbooks/Stage_3_Prompt_Library.docx`;
this file lists what exists and where. A prompt's version changes whenever its text changes, and the
old file is kept.

Placeholders in `{BRACES}` are filled by code at run time. Customer text is always placed inside
XML-style tags after the rules and is treated as data, never as instructions (FR-15).

| ID | Name | Category | Serves | Version | PRD version | Model | File |
|---|---|---|---|---|---|---|---|
| PR-01 | Specification drafter | Specification | FR-01 to FR-17 (offline) | 1.0 | 1.0 | any, run by hand | `specification/PR-01_spec_drafter_v1.0.txt` |
| PR-02 | Intent and urgency classifier | Build | FR-02, FR-15, FR-16 | 1.0 | 1.0 | meta-llama/llama-3.1-8b-instruct, temp 0 | `build/PR-02_classifier_v1.0.txt` |
| PR-03 | Grounded answer drafter | Build | FR-07, FR-10, FR-15 | 1.0 | 1.0 | meta-llama/llama-3.1-8b-instruct, temp 0 | `build/PR-03_drafter_v1.0.txt` |
| PR-04 | Escalation summary | Build | FR-08 | 1.0 | 1.0 | meta-llama/llama-3.1-8b-instruct, temp 0 | `build/PR-04_escalation_summary_v1.0.txt` |
| PR-05 | Requirement review | Review | whichever FR the component implements | 1.0 | 1.0 | any, run by hand | `review/PR-05_requirement_review_v1.0.txt` |
| PR-06 | Grounding and citation judge | Evaluation | FR-07, FR-10; NFR-03 | 1.0 | 1.0 | meta-llama/llama-3.1-8b-instruct, temp 0 | `evaluation/PR-06_grounding_judge_v1.0.txt` |
| PR-07 | Answer quality rubric | Evaluation | PRD §8 satisfaction proxy; NFR-03 | 1.0 | 1.0 | meta-llama/llama-3.1-8b-instruct, temp 0 | `evaluation/PR-07_quality_rubric_v1.0.txt` |

Requirements met by code rather than a prompt: FR-01 ingest, FR-03 and FR-04 retrieval, FR-05 and
FR-06 routing, FR-09 private-data scan, FR-10 forbidden-claim scan, FR-11 logging, FR-12 disclosure
line, FR-13 harness, FR-14 resilience, FR-16 urgency flag.

## Change history

| Date | Prompt | Version | Change | Reason |
|---|---|---|---|---|
| 2026-09-15 | all | 1.0 | Initial | Stage 3 prompt library |

"""B-08 / FR-07, FR-12, FR-15: grounded answer drafting with citations.

T-12  test_citations_in_passages    every citation resolves to a passage retrieved for that ticket
T-13  test_unknown_when_empty       no passages -> unknown, no factual claim, no model call needed
T-19  test_disclosure_line          the disclosure is appended by code, exactly once
plus  prompt content (passages, tier, ticket in tags, no customer fields), parse failure, provider failure,
      sentence splitting and per-sentence citation map for the grounding guardrail.
"""
import json

import pytest

from src.generate import (DISCLOSURE, Draft, add_disclosure, build_prompt, citation_map, format_passages,
                          generate, split_sentences)
from src.ingest import normalise_ticket
from src.llm import ProviderUnavailable
from src.retrieve import Passage


class FakeLLM:
    def __init__(self, reply=None, error=None):
        self.reply, self.error, self.prompts = reply, error, []

    def complete(self, prompt, **kw):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return self.reply


def passage(doc_id="DOC-API-001", section="Resolution", text="Read the rate limit headers. Implement exponential backoff."):
    return Passage(doc_id=doc_id, section=section, title="Understanding API rate limits and quota tiers",
                   applies_to="All plans", text=text, score=0.7, chunk_id=f"{doc_id}#{section.lower()}")


@pytest.fixture
def ticket():
    return normalise_ticket({"ticket_id": "T1", "channel": "email", "subject": "429 errors",
                             "body": "We keep getting 429 too many requests.", "customer_name": "Priya Sharma",
                             "customer_id": "CUST-1042", "customer_tier": "business",
                             "customer_region": "europe", "language_fluency": "fluent"})


GOOD = json.dumps({"answer": "Thank you for getting in touch. Please read the rate limit headers returned with "
                             "every response [DOC-API-001]. Implement exponential backoff on 429 responses [DOC-API-001]. "
                             "Do reply with what you observe.",
                   "citations": ["DOC-API-001"], "unknown": False})


def test_citations_in_passages(ticket):
    llm = FakeLLM(reply=GOOD)
    d = generate(ticket, [passage()], llm)
    assert isinstance(d, Draft) and d.unknown is False and d.error is None
    assert d.citations == ["DOC-API-001"]
    assert set(d.citations) <= {"DOC-API-001"}


def test_citation_to_unretrieved_doc_is_dropped_and_flagged(ticket):
    reply = json.dumps({"answer": "Rotate the key [DOC-AUTH-004]. Read the headers [DOC-API-001].",
                        "citations": ["DOC-AUTH-004", "DOC-API-001"], "unknown": False})
    d = generate(ticket, [passage()], FakeLLM(reply=reply))
    assert d.citations == ["DOC-API-001"]
    assert d.invalid_citations == ["DOC-AUTH-004"]


def test_unknown_when_empty(ticket):
    llm = FakeLLM(reply="should not be called")
    d = generate(ticket, [], llm)
    assert d.unknown is True and d.citations == [] and llm.prompts == []
    assert "engineer" in d.answer.lower()
    assert "[DOC" not in d.answer


def test_prompt_contains_passages_tier_and_tagged_ticket_but_no_customer_fields(ticket):
    llm = FakeLLM(reply=GOOD)
    generate(ticket, [passage()], llm)
    p = llm.prompts[0]
    assert "<passages>" in p and "DOC-API-001" in p and "Read the rate limit headers" in p
    assert "business plan" in p
    assert "<ticket>" in p and "429 too many requests" in p
    assert "Priya" not in p and "CUST-1042" not in p


def test_parse_failure_is_reported(ticket):
    d = generate(ticket, [passage()], FakeLLM(reply="Sure! Here is my answer without JSON."))
    assert d.error and "parse" in d.error.lower() and d.unknown is True


def test_provider_failure_is_reported(ticket):
    d = generate(ticket, [passage()], FakeLLM(error=ProviderUnavailable("provider unavailable: 503")))
    assert d.error and "provider" in d.error.lower() and d.unknown is True


def test_disclosure_line(ticket):
    d = generate(ticket, [passage()], FakeLLM(reply=GOOD))
    out = add_disclosure(d.answer)
    assert out.endswith(DISCLOSURE)
    assert add_disclosure(out) == out            # idempotent


def test_split_sentences_and_citation_map():
    text = ("Thank you for getting in touch. Read the headers [DOC-API-001]. "
            "Back off on 429 responses [DOC-API-001][DOC-API-002]. Please reply with what you see.")
    sents = split_sentences(text)
    assert len(sents) == 4
    cm = citation_map(text)
    assert cm[0]["citations"] == [] and cm[1]["citations"] == ["DOC-API-001"]
    assert cm[2]["citations"] == ["DOC-API-001", "DOC-API-002"]
    assert "[DOC" not in cm[1]["sentence"]        # markers stripped from the sentence text


def test_long_marker_form_is_normalised(ticket):
    reply = json.dumps({"answer": "Check the scope of the variable [DOC-API-001 | Resolution | All plans]. "
                                  "Redeploy afterwards [DOC-API-001].", "citations": [], "unknown": False})
    d = generate(ticket, [passage()], FakeLLM(reply=reply))
    assert d.citations == ["DOC-API-001"]
    assert "| Resolution" not in d.answer and d.answer.count("[DOC-API-001]") == 2
    cm = citation_map(d.answer)
    assert all(x["citations"] == ["DOC-API-001"] for x in cm)


def test_prompt_version_is_current():
    from src.generate import PROMPT_PATH, PROMPT_VERSION
    assert PROMPT_PATH.exists() and PROMPT_VERSION.split()[-1] in PROMPT_PATH.name


def test_format_passages_lists_id_section_and_plan():
    s = format_passages([passage(), passage("DOC-API-002", "Notes", "Cursors expire after one hour.")])
    assert "[DOC-API-001 | Resolution | All plans]" in s and "Cursors expire" in s


def test_trailing_marker_only_fragment_is_merged_into_previous_sentence():
    text = "Store secrets as secrets. Refer to the documentation for details. [DOC-DEPLOY-004] [DOC-DEPLOY-004] [DOC-DEPLOY-004]."
    cm = citation_map(text)
    assert [x["sentence"] for x in cm] == ["Store secrets as secrets.", "Refer to the documentation for details."]
    assert cm[1]["citations"] == ["DOC-DEPLOY-004"]

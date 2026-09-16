"""B-16 (FR-18): the single-ticket API the graders use by hand (Build Spec section 06, steps 5 to 7).

Offline: the app is created with a stub pipeline, so no models, key or network are needed.
Covers: one ticket per channel; a guardrail-trigger ticket reports the block; malformed bodies are
handled, never a 500; a crashing component returns an escalation with the reason (A11); the
decision rows for a ticket can be read back (A8); health reports the kill switch.
"""
import json

import pytest
from fastapi.testclient import TestClient

from src.api import create_app
from src.config import Settings
from src.ingest import load_tickets
from src.models import TicketResult
from tests.conftest import FIXTURES
from tests.test_harness import LoggingStub, OracleStub


class BlockingStub(OracleStub):
    """Blocks any ticket whose id starts with TRIG-, as the real guardrails would."""

    def process(self, ticket):
        r = super().process(ticket)
        if ticket.ticket_id.startswith("TRIG-"):
            r.action, r.answer, r.citations = "block", None, []
            r.guardrails = {**r.guardrails, "pii": "block"}
            r.route_reason = "Blocked by guardrail (pii) and escalated: the draft contained customer name."
            r.escalation = {"summary": "s", "uncertainty": "u", "draft": "draft text"}
        return r


@pytest.fixture
def settings(tmp_path):
    return Settings(database_url=f"sqlite:///{(tmp_path / 'd.db').as_posix()}")


@pytest.fixture
def client(settings):
    return TestClient(create_app(pipeline=BlockingStub(), settings=settings))


def test_one_ticket_per_channel(client, sample_tickets):
    seen = set()
    for raw in sample_tickets:
        r = client.post("/tickets", json=raw)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["ticket_id"] == raw["ticket_id"] and body["channel"] == raw["channel"]
        assert body["action"] in {"auto_respond", "escalate", "block"}
        assert body["intent"] and 0.0 <= body["confidence"] <= 1.0
        assert body["route_reason"]
        if body["action"] == "auto_respond":
            assert body["answer"] and body["citations"]
        else:
            assert body["escalation"]
        seen.add(body["channel"])
    assert seen == {"email", "chat", "docs_comment", "forum"}


def test_guardrail_trigger_reports_block(client):
    trig = json.loads((FIXTURES / "trigger_tickets.json").read_text(encoding="utf-8"))[0]
    r = client.post("/tickets", json=trig)
    assert r.status_code == 200
    body = r.json()
    assert body["action"] == "block" and body["answer"] is None
    assert "block" in body["guardrails"].values() and "blocked" in body["route_reason"].lower()
    assert body["escalation"]["draft"]                    # the blocked draft travels with the escalation


def test_malformed_bodies_are_handled_not_500(client):
    assert client.post("/tickets", json={}).status_code == 200                       # nothing at all
    assert client.post("/tickets", json={"channel": "fax", "body": None}).status_code == 200
    r = client.post("/tickets", json={"channel": "chat", "body": "\u0000‮ weird 😀"})
    assert r.status_code == 200 and r.json()["channel"] == "chat"
    assert client.post("/tickets", json=[1, 2, 3]).status_code == 422                # not a ticket object
    assert client.post("/tickets", content=b"not json", headers={"content-type": "application/json"}).status_code == 422


def test_component_crash_returns_escalation_with_reason(settings, sample_tickets):
    victim = sample_tickets[0]
    c = TestClient(create_app(pipeline=OracleStub(fail_on=[victim["ticket_id"]]), settings=settings))
    r = c.post("/tickets", json=victim)
    assert r.status_code == 200
    body = r.json()
    assert body["action"] == "escalate" and body["error"] and "crash" in body["error"]


def test_decisions_can_be_read_back(settings, tmp_path, sample_tickets):
    c = TestClient(create_app(pipeline=LoggingStub(tmp_path / "log.db"), settings=settings))
    raw = sample_tickets[0]
    assert c.post("/tickets", json=raw).status_code == 200
    r = c.get(f"/decisions/{raw['ticket_id']}")
    assert r.status_code == 200
    rows = r.json()["decisions"]
    assert {row["stage"] for row in rows} == {"classification", "routing", "generation", "validation"}
    assert c.get("/decisions/NO-SUCH-TICKET").json()["decisions"] == []


def test_health_reports_kill_switch(tmp_path):
    s = Settings(kill_switch=True, database_url=f"sqlite:///{(tmp_path / 'd.db').as_posix()}")
    c = TestClient(create_app(pipeline=OracleStub(), settings=s))
    r = c.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok" and body["kill_switch"] is True and body["pipeline_ready"] is True

"""B-02 / FR-01: ingest normalises every channel into one Ticket and never raises.

T-01  test_four_channels        one real ticket per channel becomes a Ticket with the same shape
T-02  test_empty_and_malformed  empty body, missing fields, odd characters, unknown channel -> Ticket + warning
"""
import pytest

from src.ingest import Ticket, normalise_ticket, load_tickets, CHANNELS


def test_four_channels(sample_tickets):
    seen = set()
    for raw in sample_tickets:
        t = normalise_ticket(raw)
        assert isinstance(t, Ticket)
        assert t.channel in CHANNELS
        assert t.ticket_id == raw["ticket_id"]
        assert t.subject == raw["subject"]           # original text preserved
        assert t.body == raw["body"]
        assert t.raw == raw                          # nothing dropped
        assert t.customer.tier == raw["customer_tier"]
        assert t.customer.region == raw["customer_region"]
        assert t.customer.fluency == raw["language_fluency"]
        assert t.text.strip()                        # something to classify
        if raw["subject"]:
            assert t.text.startswith(raw["subject"])
        else:
            assert t.text == raw["body"]             # chat: empty subject omitted, not "\n" + body
        assert t.warnings == []
        seen.add(t.channel)
    assert seen == set(CHANNELS)


def test_empty_and_malformed(edge_tickets):
    out = [normalise_ticket(raw) for raw in edge_tickets]   # must not raise
    assert len(out) == len(edge_tickets)

    empty = out[0]
    assert empty.text == "" and "empty" in " ".join(empty.warnings).lower()

    odd = out[1]
    assert "\u0000" not in odd.text                 # control characters stripped
    assert "日本語" in odd.text                      # unicode kept
    assert odd.customer.tier == "unknown"           # missing field -> explicit placeholder, logged
    assert odd.warnings

    nulls = out[2]
    assert nulls.subject == "" and nulls.body == "" and nulls.customer.tier == "unknown"

    no_id = out[3]
    assert no_id.ticket_id.startswith("UNKNOWN-")   # generated id so it can still be logged
    assert no_id.warnings

    bad_channel = out[4]
    assert bad_channel.channel == "unknown"
    assert any("channel" in w for w in bad_channel.warnings)


def test_load_tickets_reads_any_path(tmp_path, sample_tickets):
    import json
    p = tmp_path / "anything.json"
    p.write_text(json.dumps(sample_tickets), encoding="utf-8")
    tickets = load_tickets(p)
    assert [t.ticket_id for t in tickets] == [r["ticket_id"] for r in sample_tickets]


def test_load_tickets_rejects_non_list(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text('{"not": "a list"}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_tickets(p)

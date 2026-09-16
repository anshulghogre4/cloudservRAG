"""B-14: fairness audit shapes and arithmetic, offline on stub results."""
import json

from evaluation import harness
from evaluation.fairness_audit import audit, main, render
from tests.test_harness import OracleStub


def _records(tmp_path, sample_tickets):
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps(sample_tickets), encoding="utf-8")
    out = tmp_path / "run"
    harness.run(input_path=inp, output_dir=out, pipeline=OracleStub())
    return out / "results.jsonl", [json.loads(l) for l in (out / "results.jsonl").read_text(encoding="utf-8").splitlines()]


def test_audit_groups_segments_and_variation(tmp_path, sample_tickets):
    _, records = _records(tmp_path, sample_tickets)
    a = audit(records)
    assert a["tickets"] == len(records)
    assert set(a["groups"]) == {"tier", "fluency", "ticket_length", "region", "channel"}
    for g in a["groups"].values():
        segs = g["segments"]
        assert sum(s["tickets"] for s in segs.values()) == len(records)
        best = g["best"]
        assert segs[best]["variation_from_best_pts"] == 0.0 and segs[best]["ci_overlaps_best"] is True
        for s in segs.values():
            for key in ("resolution", "quality"):
                lo, hi = s[key]["ci"]
                assert 0.0 <= lo <= hi <= 1.0
                if s[key]["rate"] is not None:
                    assert lo <= s[key]["rate"] <= hi
            assert s["variation_from_best_pts"] is None or s["variation_from_best_pts"] >= 0
        assert g["within_5_points"] == (g["max_variation_pts"] <= 5.0)


def test_render_has_governance_columns(tmp_path, sample_tickets):
    _, records = _records(tmp_path, sample_tickets)
    text = render("x", audit(records))
    assert "| Segment | Tickets in segment | Resolution rate | Quality score | Variation from best |" in text
    assert "Tickets in fluent English" in text or "Tickets in non-fluent English" in text


def test_cli_writes_json_and_markdown(tmp_path, sample_tickets):
    path, _ = _records(tmp_path, sample_tickets)
    out = tmp_path / "audit"
    assert main(["--results", str(path), "--output", str(out)]) == 0
    rep = json.loads((out / "fairness_audit.json").read_text(encoding="utf-8"))
    assert "run" in rep and (out / "fairness_audit.md").exists()

"""Governance section 5 (B-17): the kill switch CLI and the in-flight re-check."""
from src import killswitch
from src.config import Settings


def test_cli_on_status_off(tmp_path, monkeypatch, capsys):
    s = Settings(kill_switch_file=tmp_path / "KILL")
    monkeypatch.setattr(killswitch, "load_settings", lambda: s)
    assert killswitch.main(["status"]) == 0 and "RUNNING" in capsys.readouterr().out
    assert killswitch.main(["on", "night-engineer"]) == 0
    out = capsys.readouterr().out
    assert "STOPPED" in out and "night-engineer" in out and s.kill_switch_active()
    assert killswitch.main(["off"]) == 0 and "RUNNING" in capsys.readouterr().out
    assert not s.kill_switch_active()
    assert killswitch.main(["bogus"]) == 2


def test_env_setting_still_counts(tmp_path):
    s = Settings(kill_switch=True, kill_switch_file=tmp_path / "KILL")
    assert s.kill_switch_active() and "environment" in killswitch.status(s)

"""Kill switch (Governance Framework section 5, B-17): stop automatic answers without a deployment.

Two mechanisms, checked on every ticket at routing and again before an answer is released:
  1. KILL_SWITCH=true in the environment or .env (read at start-up).
  2. A flag file (KILL_SWITCH_FILE, default storage/KILL_SWITCH) that can be created while the
     system is running; the next ticket escalates, no restart needed.

    python -m src.killswitch on       create the flag file (with who/when inside it)
    python -m src.killswitch off      remove it
    python -m src.killswitch status   print whether automatic answers are stopped, and why
"""
from __future__ import annotations

import getpass
import sys
from datetime import datetime, timezone

from src.config import Settings, load_settings


def status(settings: Settings) -> str:
    if settings.kill_switch:
        return "STOPPED: KILL_SWITCH=true in the environment (restart with KILL_SWITCH=false to resume)"
    if settings.kill_switch_file.exists():
        return f"STOPPED: flag file present at {settings.kill_switch_file} ({settings.kill_switch_file.read_text(encoding='utf-8').strip()})"
    return "RUNNING: automatic answers enabled"


def on(settings: Settings, who: str | None = None) -> None:
    settings.kill_switch_file.parent.mkdir(parents=True, exist_ok=True)
    settings.kill_switch_file.write_text(
        f"set by {who or getpass.getuser()} at {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n", encoding="utf-8")


def off(settings: Settings) -> None:
    if settings.kill_switch_file.exists():
        settings.kill_switch_file.unlink()


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    settings = load_settings()
    cmd = args[0] if args else "status"
    if cmd == "on":
        on(settings, args[1] if len(args) > 1 else None)
    elif cmd == "off":
        off(settings)
    elif cmd != "status":
        print(__doc__)
        return 2
    print(status(settings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Command-line client for the support pipeline API: readable, coloured output (FR-18).

The API returns one JSON record per ticket, which is what a program wants and what `curl` prints
as a single unreadable line. This client calls the same endpoints and lays the reply out for a
person: the decision, the reason, the passages, the guardrail verdicts, and the reply or the
escalation package. It changes only the presentation, never the decision. Standard library only,
so it runs wherever the project runs (Windows, macOS, Linux).

    python -m src.client health
    python -m src.client ticket data/samples/ticket_chat.json
    python -m src.client decisions TRIG-PII-001          # rows of the most recent submission
    python -m src.client decisions TRIG-PII-001 --all    # every logged row
    python -m src.client run evaluation/results/my_run    # summary of a harness output directory
    python -m src.client metrics                          # live Prometheus metrics, readable
    python -m src.client ticket data/samples/ticket_chat.json --raw   # the raw JSON, indented

Options: --url http://127.0.0.1:8000 (default), --no-color. Colour is switched off automatically
when the output is not a terminal or NO_COLOR is set.
"""
from __future__ import annotations

import json
import os
import sys
import textwrap
import urllib.error
import urllib.request
from pathlib import Path

URL = "http://127.0.0.1:8000"
WIDTH = 100
# Colour only when writing to a real terminal; respects the NO_COLOR convention (no-color.org).
# Works in Windows Terminal, the VS Code terminal, PowerShell and cmd on Windows 10+, macOS and Linux.
USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
if os.environ.get("FORCE_COLOR"):
    USE_COLOR = True

if os.name == "nt":
    os.system("")  # switches on ANSI escape handling in Windows consoles
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

CODES = {"reset": "0", "bold": "1", "dim": "2", "red": "91", "green": "92", "yellow": "93", "blue": "94",
         "magenta": "95", "cyan": "96", "white": "97", "bg_red": "41;97", "bg_green": "42;30", "bg_yellow": "43;30"}


def c(text: str, *styles: str) -> str:
    if not USE_COLOR or not styles:
        return str(text)
    return "\033[" + ";".join(CODES[s] for s in styles) + "m" + str(text) + "\033[0m"


def rule(title: str = "", style: str = "cyan") -> None:
    line = f"== {title} " if title else ""
    print(c(line + "=" * max(4, WIDTH - len(line)), style, "bold"))


def field(label: str, value, style: str = "white") -> None:
    print(f"  {c(label.ljust(14), 'dim')} {c(value, style)}")


def wrap(text: str, indent: str = "  ") -> str:
    out = []
    for para in str(text).split("\n"):
        out.append(textwrap.fill(para, WIDTH - len(indent), initial_indent=indent, subsequent_indent=indent,
                                 break_on_hyphens=False, break_long_words=False) if para.strip() else "")
    return "\n".join(out)


def call(path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(URL + path, data=data, headers={"content-type": "application/json"},
                                 method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        print(c(f"Cannot reach the API at {URL}: {exc}. Start it with: python -m src.api", "red", "bold"))
        sys.exit(1)


ACTION_STYLE = {"auto_respond": ("bg_green", "ANSWERED AUTOMATICALLY"), "escalate": ("bg_yellow", "ESCALATED TO A PERSON"),
                "block": ("bg_red", "BLOCKED BY A GUARDRAIL, ESCALATED")}
VERDICT_STYLE = {"pass": "green", "block": "red", "skipped": "dim"}


def highlight_citations(text: str) -> str:
    import re
    return re.sub(r"\[(DOC-[A-Z]+-\d+)\]", lambda m: c("[" + m.group(1) + "]", "cyan", "bold"), text)


def show_ticket(path: str, raw: bool) -> None:
    ticket = json.loads(Path(path).read_text(encoding="utf-8"))
    rule(f"TICKET  {ticket.get('ticket_id', '?')}   channel: {ticket.get('channel', '?')}   file: {path}")
    if ticket.get("subject"):
        field("subject", ticket["subject"])
    print(wrap(ticket.get("body", ""), "  | "))
    print()
    r = call("/tickets", ticket)
    if raw:
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return

    style, label = ACTION_STYLE.get(r.get("action"), ("bold", str(r.get("action"))))
    print("  " + c(f"  {label}  ", style, "bold"))
    print()
    conf = r.get("confidence") or 0.0
    field("intent", r.get("intent"), "bold")
    field("confidence", f"{conf:.2f}   (threshold 0.80)", "green" if conf >= 0.80 else "yellow")
    field("urgency", f"{r.get('urgency')}  (advisory)")
    alts = r.get("alternatives") or []
    if alts:
        field("alternatives", ", ".join(f"{a.get('intent')} {a.get('confidence', 0):.2f}" for a in alts))
    if r.get("instruction_like"):
        field("injection", "ticket text contains instructions aimed at the system", "red")
    print()
    print(c("  Why", "bold"))
    print(wrap(r.get("route_reason", ""), "    "))

    retrieved = r.get("retrieved") or []
    if retrieved:
        print()
        print(c("  Retrieved passages (cosine, threshold 0.40)", "bold"))
        for p in retrieved:
            print(f"    {c(p['doc_id'].ljust(15), 'cyan')} {str(p.get('section', '')).ljust(15)} {p.get('score', 0):.3f}")

    g = r.get("guardrails") or {}
    print()
    print(c("  Guardrails  ", "bold") + "   ".join(f"{k}: {c(v.upper(), VERDICT_STYLE.get(v, 'white'), 'bold')}"
                                                   for k, v in g.items()))

    if r.get("answer"):
        print()
        rule("REPLY SENT TO THE CUSTOMER", "green")
        print(highlight_citations(wrap(r["answer"])))
        field("citations", ", ".join(r.get("citations") or []), "cyan")
    esc = r.get("escalation")
    if esc:
        print()
        rule("ESCALATION PACKAGE FOR THE ENGINEER", "yellow")
        print(c("  Summary", "bold"))
        print(wrap(esc.get("summary", ""), "    "))
        print(c("  What the system was unsure about", "bold"))
        print(wrap(esc.get("uncertainty", ""), "    "))
        field("articles", ", ".join(esc.get("doc_ids") or []) or "none", "cyan")
        if esc.get("draft"):
            print(c("  Draft (not sent to the customer)", "bold"))
            print(c(wrap(esc["draft"], "    "), "dim"))
        else:
            field("draft", "none (no answer was attempted)", "dim")
    print()
    field("latency", f"{(r.get('latency_ms') or 0) / 1000:.2f} s")
    pv = r.get("prompt_versions") or {}
    if pv:
        field("prompts", ", ".join(pv.values()))
    if r.get("error"):
        field("error", r["error"], "red")
    rule()


def show_decisions(ticket_id: str, show_all: bool) -> None:
    d = call(f"/decisions/{ticket_id}")
    rows = d.get("decisions") or []
    rule(f"DECISION LOG  {ticket_id}   {len(rows)} rows in the append-only log")
    if not rows:
        print(c("  no rows for this ticket", "yellow"))
        return
    if not show_all:
        # one submission = the rows from its classification row onward; show the most recent one
        starts = [i for i, x in enumerate(rows) if x.get("stage") == "classification"]
        rows = rows[starts[-1]:] if starts else rows[-5:]
        print(c(f"  showing the most recent submission ({len(rows)} rows); add --all for every row", "dim"))
    for x in rows:
        action = x.get("action_taken")
        style = {"block": "red", "escalate": "yellow", "auto_respond": "green"}.get(action, "white")
        print()
        print(f"  {c(str(x.get('stage', '')).upper().ljust(15), 'cyan', 'bold')} {c(action, style, 'bold')}"
              f"   {c(x.get('timestamp', '')[:19], 'dim')}")
        conf = x.get("prediction_confidence")
        pred = f"{x.get('prediction_value')}" + (f"  (confidence {conf:.2f})" if isinstance(conf, (int, float)) else "")
        field("prediction", pred)
        if x.get("threshold_applied") is not None:
            field("threshold", x.get("threshold_applied"))
        print(wrap("reason: " + str(x.get("reason", "")), "    "))
        for key in ("sources_used", "guardrail_results", "requirement_ids"):
            val = x.get(key)
            if isinstance(val, str):
                try:
                    val = json.loads(val)
                except json.JSONDecodeError:
                    pass
            if val:
                if key == "sources_used":
                    val = ", ".join(f"{s.get('doc_id')}" + (f" {s['score']:.2f}" if "score" in s else "") for s in val)
                elif key == "guardrail_results":
                    val = "  ".join(f"{k}: {c(str(v).upper(), VERDICT_STYLE.get(v, 'white'))}" for k, v in val.items())
                else:
                    val = ", ".join(val)
                field(key.replace("_", " "), val)
        if x.get("prompt_version"):
            field("prompt version", x["prompt_version"])
    rule()


def show_health() -> None:
    h = call("/health")
    rule("HEALTH")
    field("status", h.get("status"), "green" if h.get("status") == "ok" else "red")
    ks = h.get("kill_switch")
    field("kill switch", "ON: every ticket escalates" if ks else "off: automatic answers enabled", "red" if ks else "green")
    field("model", h.get("model"))
    field("version", h.get("version"))
    field("pipeline", "ready" if h.get("pipeline_ready") else "not ready")
    rule()


def show_run(directory: str) -> None:
    d = Path(directory)
    m = json.loads((d / "metrics.json").read_text(encoding="utf-8"))
    meta = json.loads((d / "run_meta.json").read_text(encoding="utf-8"))
    rule(f"UNATTENDED RUN  {d.name}")
    field("input", meta.get("input"))
    field("tickets", meta.get("tickets"))
    field("duration", f"{meta.get('duration_s', 0):.0f} s   (version {meta.get('version')}, model {meta.get('model')})")
    v = m["volume"]
    print()
    print(c("  Volume", "bold"))
    print(f"    processed {c(v['processed'], 'bold')}    {c('answered ' + str(v['auto_responded']), 'green', 'bold')}"
          f"    {c('escalated ' + str(v['escalated']), 'yellow', 'bold')}    {c('blocked ' + str(v['blocked']), 'red', 'bold')}")
    b = m["business"]
    print(c("  Business", "bold"))
    f_, e_ = b["first_contact_resolution"], b["escalation_rate"]
    print(f"    first-contact resolution {c(format(f_['value'], '.1%'), 'green', 'bold')}  (95% CI {f_['ci95'][0]:.1%} to {f_['ci95'][1]:.1%}; baseline 42%, target 60%)")
    print(f"    escalation rate          {c(format(e_['value'], '.1%'), 'green', 'bold')}  (95% CI {e_['ci95'][0]:.1%} to {e_['ci95'][1]:.1%}; baseline 58%, target 30%)")
    t = m["technical"]
    print(c("  Technical", "bold"))
    cl = t.get("classification") or {}
    if cl:
        print(f"    intent macro precision {cl.get('macro_precision', 0):.1%}, recall {cl.get('macro_recall', 0):.1%}")
    if t.get("retrieval_hit_rate") is not None:
        print(f"    retrieval hit rate {t['retrieval_hit_rate']:.1%}; citations resolve {t.get('citation_resolves_to_retrieved', 0):.0%}")
    print(f"    latency median {t.get('latency_ms_median', 0) / 1000:.2f} s, p95 {t.get('latency_ms_p95', 0) / 1000:.2f} s")
    g = m["governance"]
    print(c("  Governance", "bold"))
    print(f"    private data detections {c(g.get('private_data_detections'), 'green', 'bold')}    "
          f"never-auto violations {c(g.get('must_not_auto_respond_violations'), 'green', 'bold')}    "
          f"failed tickets {c(g.get('failed_tickets'), 'green', 'bold')}")
    print(f"    guardrail blocks {g.get('guardrail_activations')}")
    log = g.get("decision_log") or {}
    ok = log.get("complete")
    print("    decision log " + c("RECONCILED" if ok else "INCOMPLETE", "green" if ok else "red", "bold")
          + f": {log.get('rows_total')} rows for {log.get('tickets')} tickets; routing {log.get('tickets_with_routing')}/{log.get('tickets')},"
            f" validation {log.get('tickets_with_validation')}/{log.get('tickets')}")
    rule()


def _fetch_text(path: str) -> str:
    try:
        with urllib.request.urlopen(URL + path, timeout=30) as r:
            return r.read().decode("utf-8")
    except urllib.error.URLError as exc:
        print(c(f"Cannot reach the API at {URL}: {exc}. Start it with: python -m src.api", "red", "bold"))
        sys.exit(1)


def _parse_prometheus(text: str) -> list[tuple[str, dict, float]]:
    import re
    out = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([a-zA-Z_:][\w:]*)(\{(.*)\})?\s+([-+0-9.eE]+|NaN|\+Inf)$", line)
        if not m:
            continue
        labels = dict(re.findall(r'(\w+)="([^"]*)"', m.group(3) or ""))
        try:
            out.append((m.group(1), labels, float(m.group(4))))
        except ValueError:
            continue
    return out


def _quantile(buckets: list[tuple[float, float]], q: float) -> float | None:
    """Same linear interpolation Prometheus' histogram_quantile uses, over cumulative buckets."""
    buckets = sorted(buckets)
    if not buckets or buckets[-1][1] <= 0:
        return None
    rank = q * buckets[-1][1]
    prev_le, prev_n = 0.0, 0.0
    for le, n in buckets:
        if n >= rank:
            if le == float("inf"):
                return prev_le
            return prev_le + (le - prev_le) * ((rank - prev_n) / (n - prev_n) if n > prev_n else 0)
        prev_le, prev_n = le, n
    return None


def _bar(value: float, top: float, width: int = 30) -> str:
    n = int(round(width * value / top)) if top else 0
    return "#" * n


def show_metrics() -> None:
    """Monitoring view (B-12): the Prometheus metrics the API exposes, since the process started.
    The same series feed monitoring/grafana_dashboard.json; this view needs no Docker."""
    samples = _parse_prometheus(_fetch_text("/metrics"))
    rule("MONITORING  live Prometheus metrics from the running API (also scraped at :8001/metrics)")
    tickets = [(l.get("channel", "?"), l.get("outcome", "?"), v) for n, l, v in samples if n == "tickets_processed_total"]
    total = sum(v for _, _, v in tickets)
    field("tickets", f"{total:.0f} processed since the API started", "bold")
    colour = {"auto_respond": "green", "escalate": "yellow", "block": "red"}
    print()
    print(c("  Tickets by outcome", "bold"))
    top = max([v for _, _, v in tickets] + [1])
    for outcome in ("auto_respond", "escalate", "block"):
        v = sum(x for _, o, x in tickets if o == outcome)
        share = f"{v / total:.0%}" if total else "0%"
        print(f"    {outcome.ljust(14)} {c(_bar(v, max(total, 1)), colour[outcome])} {v:.0f}  ({share})")
    print(c("  Tickets by channel and outcome", "bold"))
    for ch in sorted({t[0] for t in tickets}):
        parts = [f"{c(o, colour.get(o, 'white'))} {v:.0f}" for cc, o, v in tickets if cc == ch]
        print(f"    {ch.ljust(14)} " + "   ".join(parts))
    blocks = [(l.get("guardrail", "?"), v) for n, l, v in samples if n == "guardrail_blocks_total"]
    print(c("  Guardrail blocks", "bold"))
    print("    " + ("   ".join(f"{g}: {c(format(v, '.0f'), 'red', 'bold')}" for g, v in blocks) if blocks else "none"))
    fails = [(l.get("stage", "?"), v) for n, l, v in samples if n == "pipeline_failures_total" and v]
    print(c("  Pipeline failures", "bold"))
    print("    " + ("   ".join(f"{s}: {c(format(v, '.0f'), 'red', 'bold')}" for s, v in fails) if fails else c("none", "green")))
    lat = [(float(l["le"].replace("+Inf", "inf")), v) for n, l, v in samples if n == "response_seconds_bucket" and "le" in l]
    count = next((v for n, _, v in samples if n == "response_seconds_count"), 0)
    total_s = next((v for n, _, v in samples if n == "response_seconds_sum"), 0)
    print(c("  Response time per ticket", "bold"))
    if count:
        p50, p95 = _quantile(lat, 0.5), _quantile(lat, 0.95)
        print(f"    mean {total_s / count:.2f} s    p50 {p50:.2f} s    p95 {p95:.2f} s    (target: p95 under 3 s)")
    else:
        print("    no tickets yet")
    conf = sorted((float(l["le"].replace("+Inf", "inf")), v) for n, l, v in samples
                  if n == "classification_confidence_bucket" and "le" in l)
    if conf and conf[-1][1]:
        print(c("  Classification confidence (where drift would show first)", "bold"))
        prev_le, prev_n = 0.0, 0.0
        per = []
        for le, n in conf:
            if le != float("inf"):
                per.append((prev_le, le, n - prev_n))
                prev_le, prev_n = le, n
        top = max([p[2] for p in per] + [1])
        for lo, hi, n in per:
            if n:
                print(f"    {lo:.1f} to {hi:.1f}   {c(_bar(n, top), 'cyan')} {n:.0f}")
    print()
    print(c("  Grafana: docker compose -f monitoring/docker-compose.yml up -d, then http://localhost:3000", "dim"))
    rule()


def main(argv: list[str]) -> int:
    global URL, USE_COLOR
    args = [a for a in argv if not a.startswith("--")]
    if "--no-color" in argv:
        USE_COLOR = False
    if "--url" in argv:
        URL = argv[argv.index("--url") + 1]
        args = [a for a in args if a != URL]
    if not args:
        print(__doc__)
        return 1
    cmd = args[0]
    if cmd == "health":
        show_health()
    elif cmd == "ticket" and len(args) > 1:
        show_ticket(args[1], raw="--raw" in argv)
    elif cmd == "decisions" and len(args) > 1:
        show_decisions(args[1], show_all="--all" in argv)
    elif cmd == "run" and len(args) > 1:
        show_run(args[1])
    elif cmd == "metrics":
        show_metrics()
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

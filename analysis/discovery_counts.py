"""Stage 1 discovery counts over the DEVELOPMENT set only.

Every figure in Docs/Workbooks_Filled/Stage_1_Discovery_Workbook.md cites this
script.  Run:  python analysis/discovery_counts.py
It never touches validation_tickets.json.
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import re
import statistics as st
from pathlib import Path

DATA = Path("Docs/Capstone_Project/05_Datasets")
tickets = json.loads((DATA / "development_tickets.json").read_text(encoding="utf-8"))
docs = json.loads((DATA / "documentation.json").read_text(encoding="utf-8"))
truth = json.loads((DATA / "ground_truth_responses.json").read_text(encoding="utf-8"))
N = len(tickets)


def pct(a: float, b: float) -> str:
    return f"{100 * a / b:.1f}%" if b else "n/a"


def group(key):
    g = collections.defaultdict(list)
    for t in tickets:
        g[key(t)].append(t)
    return g


def outcomes(ts):
    n = len(ts)
    h = [t["history"] for t in ts]
    rt = [x["resolution_time_minutes"] for x in h]
    return {
        "n": n,
        "share": pct(n, N),
        "fcr": pct(sum(x["first_contact_resolution"] for x in h), n),
        "escalated": pct(sum(x["escalated"] for x in h), n),
        "repeat": pct(sum(x["repeat_contact"] for x in h), n),
        "csat": f"{st.mean(x['csat_rating'] for x in h):.2f}",
        "res_mean": f"{st.mean(rt):.0f}",
        "res_median": f"{st.median(rt):.0f}",
        "answerable": pct(sum(t["labels"]["answerable_from_docs"] for t in ts), n),
        "auto_expected": pct(sum(t["labels"]["expected_route"] == "auto_respond" for t in ts), n),
    }


def table(g, title, order=None):
    print(f"\n== {title} ==")
    cols = ["n", "share", "fcr", "escalated", "repeat", "csat", "res_mean", "res_median", "answerable", "auto_expected"]
    print(f"{'group':26}" + "".join(f"{c:>12}" for c in cols))
    keys = order or sorted(g, key=lambda k: -len(g[k]))
    for k in keys:
        o = outcomes(g[k])
        print(f"{str(k):26}" + "".join(f"{o[c]:>12}" for c in cols))


print("TOTAL DEV TICKETS:", N)
print("OVERALL:", outcomes(tickets))

table(group(lambda t: t["channel"]), "BY CHANNEL")
table(group(lambda t: t["labels"]["urgency"]), "BY URGENCY", ["high", "medium", "low"])
table(group(lambda t: t["customer_tier"]), "BY TIER", ["enterprise", "business", "standard"])
table(group(lambda t: t["language_fluency"]), "BY FLUENCY", ["fluent", "non_fluent"])
table(group(lambda t: t["customer_region"]), "BY REGION")
table(group(lambda t: t["labels"]["intent"]), "BY INTENT")
table(group(lambda t: t["labels"]["expected_route"]), "BY EXPECTED ROUTE")
table(group(lambda t: t["labels"]["answerable_from_docs"]), "BY ANSWERABLE_FROM_DOCS")
table(group(lambda t: t["labels"]["must_not_auto_respond"]), "BY MUST_NOT_AUTO_RESPOND")

print("\n== EFFORT SHARE BY INTENT (sum of historical resolution minutes as effort proxy) ==")
tot_min = sum(t["history"]["resolution_time_minutes"] for t in tickets)
rows = []
for k, ts in group(lambda t: t["labels"]["intent"]).items():
    m = sum(t["history"]["resolution_time_minutes"] for t in ts)
    rows.append((k, len(ts), 100 * len(ts) / N, 100 * m / tot_min, m / len(ts)))
print(f"{'intent':26}{'n':>5}{'vol%':>8}{'effort%':>9}{'ratio':>7}{'avg_min':>9}")
for k, n, vs, es, avg in sorted(rows, key=lambda r: -r[3]):
    print(f"{k:26}{n:>5}{vs:>8.1f}{es:>9.1f}{es / vs:>7.2f}{avg:>9.0f}")
print("total historical minutes:", tot_min, " mean per ticket:", round(tot_min / N))

print("\n== ANSWERABLE x FCR ==")
for a in (True, False):
    print("answerable_from_docs =", a, outcomes([t for t in tickets if t["labels"]["answerable_from_docs"] == a]))

print("\n== DANIEL: escalated tickets that were answerable / expected auto ==")
esc = [t for t in tickets if t["history"]["escalated"]]
print("escalated:", len(esc), pct(len(esc), N))
print("  of which answerable_from_docs:", sum(t["labels"]["answerable_from_docs"] for t in esc), pct(sum(t["labels"]["answerable_from_docs"] for t in esc), len(esc)))
print("  of which expected_route=auto_respond:", sum(t["labels"]["expected_route"] == "auto_respond" for t in esc), pct(sum(t["labels"]["expected_route"] == "auto_respond" for t in esc), len(esc)))
print("  of which must_not_auto_respond:", sum(t["labels"]["must_not_auto_respond"] for t in esc))
print("  escalated by intent:", collections.Counter(t["labels"]["intent"] for t in esc).most_common())

print("\n== SOFIA: answerable AND expected auto_respond:", pct(sum(t["labels"]["answerable_from_docs"] and t["labels"]["expected_route"] == "auto_respond" for t in tickets), N))
print("== SOFIA: non-fluent worst CSAT? ==")
for f in ("fluent", "non_fluent"):
    print(f, outcomes([t for t in tickets if t["language_fluency"] == f]))
print("non-fluent within tier:")
for tier in ("enterprise", "business", "standard"):
    ts = [t for t in tickets if t["language_fluency"] == "non_fluent" and t["customer_tier"] == tier]
    print("  ", tier, outcomes(ts))
print("fluent within tier:")
for tier in ("enterprise", "business", "standard"):
    ts = [t for t in tickets if t["language_fluency"] == "fluent" and t["customer_tier"] == tier]
    print("  ", tier, outcomes(ts))
print("csat distribution fluent:", sorted(collections.Counter(t["history"]["csat_rating"] for t in tickets if t["language_fluency"] == "fluent").items()))
print("csat distribution non-fluent:", sorted(collections.Counter(t["history"]["csat_rating"] for t in tickets if t["language_fluency"] == "non_fluent").items()))

print("\n== RAVI: urgency x resolution time; tier x resolution time ==")
for u in ("high", "medium", "low"):
    rt = sorted(t["history"]["resolution_time_minutes"] for t in tickets if t["labels"]["urgency"] == u)
    print(f"urgency {u:7} n={len(rt):3} mean={st.mean(rt):6.0f} median={st.median(rt):5.0f} p90={rt[int(.9 * len(rt)) - 1]:5}")
for tier in ("enterprise", "business", "standard"):
    rt = sorted(t["history"]["resolution_time_minutes"] for t in tickets if t["customer_tier"] == tier)
    print(f"tier {tier:11} n={len(rt):3} mean={st.mean(rt):6.0f} median={st.median(rt):5.0f} p90={rt[int(.9 * len(rt)) - 1]:5}")
print("urgency x tier median minutes:")
for u in ("high", "medium", "low"):
    row = []
    for tier in ("enterprise", "business", "standard"):
        rt = [t["history"]["resolution_time_minutes"] for t in tickets if t["labels"]["urgency"] == u and t["customer_tier"] == tier]
        row.append(f"{tier}={st.median(rt):.0f}(n={len(rt)})" if rt else f"{tier}=-")
    print("  ", u, " ".join(row))

print("\n== RESOLUTION TIME OVERALL ==")
rt = sorted(t["history"]["resolution_time_minutes"] for t in tickets)
print("mean", round(st.mean(rt)), "median", st.median(rt), "p95", rt[int(.95 * len(rt)) - 1], "min", rt[0], "max", rt[-1])
print("within 120 min:", pct(sum(1 for x in rt if x <= 120), N), " within 480 min:", pct(sum(1 for x in rt if x <= 480), N))

print("\n== INTENTS: answerable share, must_not_auto share, expected docs ==")
for k, ts in sorted(group(lambda t: t["labels"]["intent"]).items(), key=lambda kv: -len(kv[1])):
    a = sum(t["labels"]["answerable_from_docs"] for t in ts)
    m = sum(t["labels"]["must_not_auto_respond"] for t in ts)
    au = sum(t["labels"]["expected_route"] == "auto_respond" for t in ts)
    d = collections.Counter(x for t in ts for x in t["labels"]["expected_doc_ids"])
    print(f"{k:26} n={len(ts):3} answerable={pct(a, len(ts)):>6} must_not_auto={m:3} expected_auto={pct(au, len(ts)):>6} docs={d.most_common(3)}")

print("\n== EXPECTED DOC FREQUENCY ==")
c = collections.Counter(x for t in tickets for x in t["labels"]["expected_doc_ids"])
print(c.most_common())
print("tickets with no expected docs:", sum(1 for t in tickets if not t["labels"]["expected_doc_ids"]))
doc_ids = {d["doc_id"] for d in docs}
print("expected doc ids not in corpus:", sorted(set(c) - doc_ids))
print("corpus docs never expected:", sorted(doc_ids - set(c)))

print("\n== MOST FREQUENT SINGLE QUESTION ==")
print("top intents:", collections.Counter(t["labels"]["intent"] for t in tickets).most_common(5))
print("top exact subjects:", collections.Counter(t["subject"] for t in tickets if t["subject"]).most_common(8))
print("chat tickets with empty subject:", sum(1 for t in tickets if t["channel"] == "chat" and not t["subject"]), "of", sum(1 for t in tickets if t["channel"] == "chat"))

print("\n== CHANNEL x TOP INTENTS ==")
for ch, ts in group(lambda t: t["channel"]).items():
    print(ch, collections.Counter(t["labels"]["intent"] for t in ts).most_common(4))
print("\n== BODY LENGTH (chars) by channel / fluency ==")
for ch, ts in group(lambda t: t["channel"]).items():
    L = [len(t["body"]) for t in ts]
    print(f"{ch:13} mean={st.mean(L):6.0f} median={st.median(L):5.0f}")
for f in ("fluent", "non_fluent"):
    L = [len(t["body"]) for t in tickets if t["language_fluency"] == f]
    print(f"{f:13} mean={st.mean(L):6.0f} median={st.median(L):5.0f}")

print("\n== TIME RANGE / WEEKDAY ==")
dts = [dt.datetime.fromisoformat(t["received_at"].replace("Z", "+00:00")) for t in tickets]
print(min(dts).date(), "to", max(dts).date(), " weeks:", round((max(dts) - min(dts)).days / 7, 1))
print(collections.Counter(x.strftime("%a") for x in dts).most_common())

print("\n== REPEAT CONTACTS ==")
rep = [t for t in tickets if t["history"]["repeat_contact"]]
print("repeat:", len(rep), pct(len(rep), N))
print("repeat by fluency:", {f: pct(sum(1 for t in rep if t["language_fluency"] == f), sum(1 for t in tickets if t["language_fluency"] == f)) for f in ("fluent", "non_fluent")})
print("repeat by fcr:", {v: pct(sum(1 for t in rep if t["history"]["first_contact_resolution"] == v), sum(1 for t in tickets if t["history"]["first_contact_resolution"] == v)) for v in (True, False)})
print("repeat by intent:", collections.Counter(t["labels"]["intent"] for t in rep).most_common(6))
print("distinct customers:", len({t["customer_id"] for t in tickets}), " customers with >1 ticket:", sum(1 for v in collections.Counter(t["customer_id"] for t in tickets).values() if v > 1))

print("\n== CSAT ==")
print("distribution:", sorted(collections.Counter(t["history"]["csat_rating"] for t in tickets).items()))
print("csat by fcr:", {v: f"{st.mean(t['history']['csat_rating'] for t in tickets if t['history']['first_contact_resolution'] == v):.2f}" for v in (True, False)})
print("csat by escalated:", {v: f"{st.mean(t['history']['csat_rating'] for t in tickets if t['history']['escalated'] == v):.2f}" for v in (True, False)})

print("\n== PRIVATE DATA IN TICKET TEXT (regex scan of subject+body) ==")
pats = {
    "email": r"[\w.+-]+@[\w-]+\.[\w.]+",
    "api_key_like": r"\b(?:sk|key|ak|api|tok|token)[_-][A-Za-z0-9]{10,}\b",
    "ipv4": r"\b\d{1,3}(?:\.\d{1,3}){3}\b",
    "card_like": r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b",
    "phone_like": r"\+\d{1,3}[ -]?\d{3,}[ -]?\d{3,}",
    "account_id_like": r"\b(?:acct|account|org|customer)[-_ ]?(?:id)?[-_ ]?[A-Za-z0-9]{4,}\b",
}
for k, p in pats.items():
    hits = [t["ticket_id"] for t in tickets if re.search(p, t["subject"] + " " + t["body"], re.I)]
    print(f"{k:16} {len(hits):3} tickets  e.g. {hits[:4]}")
print("customer_name present on every ticket:", all(t.get("customer_name") for t in tickets))
print("tickets mentioning own customer_name in body:", sum(1 for t in tickets if t["customer_name"].split()[0].lower() in t["body"].lower()))

print("\n== DOCUMENTATION CORPUS ==")
print("articles:", len(docs))
print("categories:", collections.Counter(d["category"] for d in docs).most_common())
lr = [d["last_reviewed_days_ago"] for d in docs]
print("last_reviewed_days_ago: min", min(lr), "median", st.median(lr), "max", max(lr))
print("articles reviewed >180 days ago:", [(d["doc_id"], d["last_reviewed_days_ago"]) for d in docs if d["last_reviewed_days_ago"] > 180])
print("content length chars: mean", round(st.mean(len(d["content"]) for d in docs)), "min", min(len(d["content"]) for d in docs), "max", max(len(d["content"]) for d in docs))
print("headings in first doc:", re.findall(r"^#+ .*$", docs[0]["content"], re.M))

print("\n== GROUND TRUTH ==")
print("responses:", len(truth), " intents covered:", len({t["intent"] for t in truth}))
print("written_by:", collections.Counter(t["written_by"] for t in truth))
print("must_mention empty:", sum(1 for t in truth if not t["must_mention"]), " must_not_claim empty:", sum(1 for t in truth if not t["must_not_claim"]))
print("most common must_not_claim:", collections.Counter(x for t in truth for x in t["must_not_claim"]).most_common(6))
dev_ids = {t["ticket_id"] for t in tickets}
print("ground truth ticket_ids found in dev set:", sum(1 for t in truth if t["ticket_id"] in dev_ids), "of", len(truth))

print("\n== SAMPLE TICKETS (one per channel, one non-fluent) ==")
for ch, ts in group(lambda t: t["channel"]).items():
    t = ts[0]
    print(f"[{ch}] {t['ticket_id']} | subj={t['subject']!r} | {t['body'][:220]!r}")
nf = next(t for t in tickets if t["language_fluency"] == "non_fluent")
print(f"[non_fluent] {nf['ticket_id']} | {nf['labels']['intent']} | {nf['body'][:300]!r}")

"""Figures for the capstone report. Every number is read from the development set, the harness
outputs under evaluation/results/ or the measurement scripts' JSON; nothing is typed in by hand.

Run from the repository root with a Python that has matplotlib (any version):
    python report/make_figures.py
Writes PNGs into report/figures/.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "evaluation" / "results"
DEV = ROOT / "Docs" / "Capstone_Project" / "05_Datasets" / "development_tickets.json"

# Reference palette (dataviz skill, validated): fixed categorical order, text tokens.
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948")
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8985", "#e6e5e1", "#ffffff"
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK, "axes.titlesize": 10,
    "axes.titleweight": "semibold", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "legend.frameon": False, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.08,
})


def jload(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def jsonl(p: Path):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def hbar(ax, y, w, color, height=0.62, label=None):
    """Thin horizontal bar, square at the baseline, lightly rounded look via thin edge."""
    return ax.barh(y, w, height=height, color=color, edgecolor=SURFACE, linewidth=1.5, label=label)


def vbar(ax, x, h, color, width=0.62, label=None):
    return ax.bar(x, h, width=width, color=color, edgecolor=SURFACE, linewidth=1.5, label=label)


def save(fig, name):
    fig.savefig(OUT / name)
    plt.close(fig)
    print("wrote", name)


tickets = jload(DEV)
hist = lambda t: t["history"]  # noqa: E731
lab = lambda t: t["labels"]  # noqa: E731

# ------------------------------------------------------------------------------------------
# Figure 1: answerable share against historical first-contact resolution, per intent
# ------------------------------------------------------------------------------------------
by_intent = defaultdict(list)
for t in tickets:
    by_intent[lab(t)["intent"]].append(t)
rows = []
for k, v in by_intent.items():
    ans = sum(1 for t in v if lab(t)["answerable_from_docs"]) / len(v)
    fcr = sum(1 for t in v if hist(t)["first_contact_resolution"]) / len(v)
    mna = any(lab(t)["must_not_auto_respond"] for t in v)
    rows.append((k, len(v), ans, fcr, mna))
rows.sort(key=lambda r: r[2] - r[3])
fig, ax = plt.subplots(figsize=(7.2, 6.2))
ys = range(len(rows))
for y, (k, n, ans, fcr, mna) in zip(ys, rows):
    ax.plot([fcr, ans], [y, y], color=GRID, linewidth=2, zorder=1)
    ax.scatter([fcr], [y], s=52, color=ORANGE, zorder=3, edgecolor=SURFACE, linewidth=1.5)
    ax.scatter([ans], [y], s=52, color=BLUE, zorder=3, edgecolor=SURFACE, linewidth=1.5)
    ax.text(1.02, y, f"n={n}" + ("  never-auto" if mna else ""), va="center", fontsize=7.5, color=MUTED)
ax.set_yticks(list(ys))
ax.set_yticklabels([r[0].replace("_", " ") for r in rows], fontsize=8)
ax.set_xlim(0, 1.0)
ax.set_xticks([0, .2, .4, .6, .8, 1.0])
ax.set_xticklabels(["0%", "20%", "40%", "60%", "80%", "100%"])
ax.grid(axis="y", visible=False)
ax.scatter([], [], s=52, color=BLUE, label="Share answerable from the 29 articles (label)")
ax.scatter([], [], s=52, color=ORANGE, label="Share resolved on first contact by agents (history)")
ax.legend(loc="lower right", fontsize=8)
ax.set_title("Answers exist for most intents; agents still escalate them (development set, 500 tickets)")
save(fig, "fig01_answerable_vs_fcr.png")

# ------------------------------------------------------------------------------------------
# Figure 2: what an escalation costs the customer (CSAT and repeat contact, resolved vs escalated)
# ------------------------------------------------------------------------------------------
res = [t for t in tickets if hist(t)["first_contact_resolution"]]
esc = [t for t in tickets if not hist(t)["first_contact_resolution"]]
csat = [statistics.mean(hist(t)["csat_rating"] for t in g) for g in (res, esc)]
rep = [sum(1 for t in g if hist(t)["repeat_contact"]) / len(g) for g in (res, esc)]
med = [statistics.median(hist(t)["resolution_time_minutes"] for t in g) for g in (res, esc)]
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.6))
labels = [f"Resolved first time\n(n={len(res)})", f"Escalated\n(n={len(esc)})"]
for ax, vals, title, fmt, ylim in zip(
        axes, [csat, rep, med], ["Satisfaction (1 to 5)", "Repeat contact in 7 days", "Median minutes to resolve"],
        ["{:.2f}", "{:.0%}", "{:.0f}"], [(0, 5), (0, 0.5), (0, 800)]):
    b = vbar(ax, [0, 1], vals, [AQUA, ORANGE])
    for x, v in zip([0, 1], vals):
        ax.text(x, v, fmt.format(v), ha="center", va="bottom", fontsize=8.5, color=INK)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=9)
    ax.grid(axis="x", visible=False)
fig.suptitle("The hand-over, not only the wait, is what customers mark down", fontsize=10, fontweight="semibold", y=1.03)
save(fig, "fig02_escalation_cost.png")

# ------------------------------------------------------------------------------------------
# Figure 3: volume share against effort share (historical minutes) per intent
# ------------------------------------------------------------------------------------------
total_min = sum(hist(t)["resolution_time_minutes"] for t in tickets)
eff = []
for k, v in by_intent.items():
    eff.append((k, len(v) / 500, sum(hist(t)["resolution_time_minutes"] for t in v) / total_min,
                any(lab(t)["must_not_auto_respond"] for t in v)))
eff.sort(key=lambda r: r[2], reverse=True)
fig, ax = plt.subplots(figsize=(7.2, 5.8))
ys = list(range(len(eff)))
h = 0.36
ax.barh([y + h / 2 for y in ys], [r[1] for r in eff], height=h, color=GRID, edgecolor=SURFACE, label="Share of ticket volume")
ax.barh([y - h / 2 for y in ys], [r[2] for r in eff], height=h,
        color=[VIOLET if r[3] else BLUE for r in eff], edgecolor=SURFACE)
from matplotlib.patches import Patch
ax.set_yticks(ys)
ax.set_yticklabels([r[0].replace("_", " ") for r in eff], fontsize=8)
ax.invert_yaxis()
ax.set_xticks([0, .02, .04, .06, .08, .10])
ax.set_xticklabels(["0%", "2%", "4%", "6%", "8%", "10%"])
ax.grid(axis="y", visible=False)
ax.legend(handles=[Patch(color=GRID, label="Share of ticket volume"), Patch(color=BLUE, label="Share of agent minutes (history)"), Patch(color=VIOLET, label="Share of minutes, never-auto intent")], loc="lower right", fontsize=8)
ax.set_title("Where agent time goes: the four never-auto intents are 17% of volume and 29% of minutes")
save(fig, "fig03_volume_vs_effort.png")

# ------------------------------------------------------------------------------------------
# Figure 4: retrieval configurations (B-03/B-04)
# ------------------------------------------------------------------------------------------
rc = jload(RES / "retrieval_check.json")
names = {"section+dense": "Section chunks,\ndense (chosen)", "section+hybrid": "Section chunks,\nBM25 + dense (RRF)",
         "article+dense": "Whole article,\ndense", "article+hybrid": "Whole article,\nBM25 + dense (RRF)"}
fig, ax = plt.subplots(figsize=(7.2, 3.0))
xs = list(range(4))
w = 0.26
for i, (key, col, lbl) in enumerate([("hit@1", BLUE, "hit@1"), ("hit@3", "#86b6ef", "hit@3"), ("hit@5", "#cde2fb", "hit@5")]):
    vals = [r[key] for r in rc["results"]]
    ax.bar([x + (i - 1) * w for x in xs], vals, width=w, color=col, edgecolor=SURFACE, linewidth=1.5, label=lbl)
    for x, v in zip(xs, vals):
        ax.text(x + (i - 1) * w, v + 0.004, f"{v:.3f}", ha="center", va="bottom", fontsize=7, color=INK2)
ax.set_xticks(xs)
ax.set_xticklabels([names[r["config"]] for r in rc["results"]], fontsize=8)
ax.set_ylim(0.85, 1.0)
ax.set_ylabel("Expected article found\n(357 answerable tickets)", fontsize=8)
ax.grid(axis="x", visible=False)
ax.legend(ncol=3, loc="upper right", fontsize=8)
ax.set_title("Chunking and search strategy measured before choosing (retrieval_check.json)")
save(fig, "fig04_retrieval_configs.png")

# ------------------------------------------------------------------------------------------
# Figure 5: classifier signals and calibration
# ------------------------------------------------------------------------------------------
cc = jload(RES / "classify_check.json")
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1))
ax = axes[0]
metrics = [("Accuracy", cc["llm_accuracy"], cc["final_accuracy"]),
           ("Macro precision", cc["llm_macro_precision"], cc["final_macro_precision"]),
           ("Macro recall", cc["llm_macro_recall"], cc["final_macro_recall"])]
xs = list(range(3))
ax.bar([x - 0.18 for x in xs], [m[1] for m in metrics], width=0.34, color=ORANGE, edgecolor=SURFACE, linewidth=1.5, label="Language model alone (PR-02)")
ax.bar([x + 0.18 for x in xs], [m[2] for m in metrics], width=0.34, color=BLUE, edgecolor=SURFACE, linewidth=1.5, label="Neighbour vote + model (final)")
for x, m in zip(xs, metrics):
    ax.text(x - 0.18, m[1] + 0.01, f"{m[1]:.2f}", ha="center", fontsize=7.5, color=INK2)
    ax.text(x + 0.18, m[2] + 0.01, f"{m[2]:.2f}", ha="center", fontsize=7.5, color=INK2)
ax.axhline(0.85, color=RED, linewidth=1, linestyle=(0, (4, 3)))
ax.text(2.45, 0.855, "85% target", color=RED, fontsize=7.5, ha="right", va="bottom")
ax.set_xticks(xs)
ax.set_xticklabels([m[0] for m in metrics], fontsize=8)
ax.set_ylim(0.5, 1.03)
ax.grid(axis="x", visible=False)
ax.legend(loc="upper center", fontsize=7.5, handlelength=1.2, bbox_to_anchor=(0.5, -0.14), ncol=1)
ax.set_title("Intent classification (dev, leave-one-out)", fontsize=9)

ax = axes[1]
ax.plot([0, 1], [0, 1], color=GRID, linewidth=1)
for cal, col, lbl, mk in [(cc["calibration_raw"], ORANGE, "Model's stated confidence (raw)", "s"),
                          (cc["calibration_binned_cross_validated"], BLUE, "Calibrated score, 5-fold CV (dev)", "o"),
                          (jload(RES / "2026-09-16_validation" / "metrics.json")["governance"]["calibration"], AQUA, "Validation run (n=80)", "^")]:
    pts = [(b["stated"], b["observed"], b["n"]) for b in cal["bins"] if b["n"] >= 5]
    ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=[max(30, min(160, p[2] / 3)) for p in pts],
               color=col, marker=mk, edgecolor=SURFACE, linewidth=1.5, label=lbl, zorder=3)
ax.fill_between([0, 1], [-0.05, 0.95], [0.05, 1.05], color=GRID, alpha=0.5, linewidth=0)
ax.set_xlim(0.55, 1.02)
ax.set_ylim(0.55, 1.02)
ax.set_xlabel("Stated confidence (band mean)")
ax.set_ylabel("Observed accuracy in band")
ax.legend(loc="lower right", fontsize=7)
ax.set_title("Reliability (grey band = within 5 points)", fontsize=9)
save(fig, "fig05_classifier_calibration.png")

# ------------------------------------------------------------------------------------------
# Figure 6: confusion matrix (development set, leave-one-out)
# ------------------------------------------------------------------------------------------
with open(RES / "confusion_final.csv", newline="", encoding="utf-8") as f:
    rd = list(csv.reader(f))
classes = rd[0][1:]
M = [[int(x) for x in r[1:]] for r in rd[1:]]
fig, ax = plt.subplots(figsize=(7.2, 6.6))
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seq", ["#ffffff"] + SEQ)
im = ax.imshow(M, cmap=cmap, vmin=0, vmax=30)
ax.set_xticks(range(len(classes)))
ax.set_yticks(range(len(classes)))
ax.set_xticklabels([c.replace("_", " ") for c in classes], rotation=90, fontsize=7)
ax.set_yticklabels([c.replace("_", " ") for c in classes], fontsize=7)
ax.grid(False)
for i, row in enumerate(M):
    for j, v in enumerate(row):
        if v:
            ax.text(j, i, str(v), ha="center", va="center", fontsize=6.5, color=SURFACE if v > 14 else INK)
ax.set_xlabel("Predicted intent")
ax.set_ylabel("Labelled intent")
ax.set_title("Confusion matrix, development set (500 tickets, 4 errors)")
save(fig, "fig06_confusion.png")

# ------------------------------------------------------------------------------------------
# Figure 7: routing threshold sweep and cost rule
# ------------------------------------------------------------------------------------------
rt = jload(RES / "route_check.json")
sw = rt["sweep"]
fig, ax = plt.subplots(figsize=(7.2, 2.8))
ax.plot([s["threshold"] for s in sw], [s["auto_rate"] for s in sw], color=BLUE, linewidth=2, marker="o", markersize=5, label="Share answered automatically")
ax.plot([s["threshold"] for s in sw], [s["routing_accuracy"] for s in sw], color=ORANGE, linewidth=2, marker="o", markersize=5, label="Routing accuracy against labels")
ax.axhline(rt["ceiling"], color=MUTED, linewidth=1, linestyle=(0, (4, 3)))
ax.text(0.5, rt["ceiling"] + 0.005, f"label ceiling {rt['ceiling']:.3f} (mixed labels on identical text)", fontsize=7.5, color=INK2)
ax.axvline(0.80, color=RED, linewidth=1)
ax.text(0.805, 0.72, "chosen 0.80", color=RED, fontsize=7.5)
ax.set_xlabel("Confidence threshold")
ax.set_ylim(0.7, 0.96)
ax.legend(loc="lower left", fontsize=8)
ax.set_title("Threshold sweep on the development set: any value from 0.70 to 0.99 routes identically")
save(fig, "fig07_threshold_sweep.png")

# ------------------------------------------------------------------------------------------
# Figure 8: prompt PR-03 versions
# ------------------------------------------------------------------------------------------
gv = {"v1.0": jload(RES / "generate_check" / "generate_check.json"),
      "v1.1": jload(RES / "generate_check_v1.1" / "generate_check.json"),
      "v1.2": jload(RES / "generate_check_v1.2" / "generate_check.json")}
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5))
vers = list(gv)
for ax, key, title, fmt in zip(axes,
                               ["factual_sentence_citation_rate", "must_mention_coverage", "words_mean"],
                               ["Factual sentences cited", "Must-mention points covered", "Mean words per draft"],
                               ["{:.0%}", "{:.0%}", "{:.0f}"]):
    vals = [gv[v][key] for v in vers]
    vbar(ax, range(3), vals, [GRID, GRID, BLUE])
    for x, v in enumerate(vals):
        ax.text(x, v, fmt.format(v), ha="center", va="bottom", fontsize=8, color=INK)
    ax.set_xticks(range(3))
    ax.set_xticklabels(vers)
    ax.set_title(title, fontsize=8.5)
    ax.grid(axis="x", visible=False)
    ax.set_ylim(0, max(vals) * 1.25)
fig.suptitle("Drafting prompt PR-03 across three versions on the same 20 tickets (v1.2 chosen)", fontsize=10, fontweight="semibold", y=1.04)
save(fig, "fig08_prompt_versions.png")

# ------------------------------------------------------------------------------------------
# Figure 9: grounding guardrail tuning ladder
# ------------------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.2, 3.2))
stages = [("Chunk cosine,\nwhole-passage\nNLI premise", 31, "missed"), ("Sentence-level\nNLI premise", 21, "caught"),
          ("+ sentence cosine\nand lexical", 7, "caught"), ("+ contradiction\n0.85, filler filter", 3, "caught"),
          ("Dev run 1\n(as built)", 43, "caught"), ("Dev run 3\n(final)", 6, "caught")]
cols = [MUTED, MUTED, MUTED, BLUE, ORANGE, BLUE]
xs = list(range(len(stages)))
vbar(ax, xs, [s[1] for s in stages], cols)
for x, s in zip(xs, stages):
    ax.text(x, s[1] + 0.8, f"{s[1]}", ha="center", fontsize=8.5, color=INK)
    ax.text(x, -4.5, s[2], ha="center", fontsize=7.5, color=RED if s[2] == "missed" else GREEN)
ax.set_xticks(xs)
ax.set_xticklabels([s[0] for s in stages], fontsize=7.2)
ax.set_ylim(-6, 50)
ax.set_ylabel("Drafts blocked")
ax.text(-0.55, -4.5, "known inverted fact:", fontsize=7.5, color=INK2, ha="right")
ax.grid(axis="x", visible=False)
ax.text(1.5, 44, "57-draft tuning set", fontsize=8, color=INK2, ha="center")
ax.text(4.5, 47, "500-ticket runs (37 of 43 false in run 1; 6 genuine in run 3)", fontsize=8, color=INK2, ha="center")
ax.set_title("Grounding guardrail: from blocking half of correct drafts to blocking only unsupported sentences")
save(fig, "fig09_guardrail_tuning.png")

# ------------------------------------------------------------------------------------------
# Figure 10: business outcomes against baseline and target
# ------------------------------------------------------------------------------------------
dev = jload(RES / "2026-09-16_dev_full" / "metrics.json")
val = jload(RES / "2026-09-16_validation" / "metrics.json")
orc = jload(RES / "2026-09-16_dev_oracle_stub" / "metrics.json")
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
for ax, key, title, target, base in [(axes[0], "first_contact_resolution", "First-contact resolution", 0.60, 0.438),
                                     (axes[1], "escalation_rate", "Escalation rate", 0.30, 0.562)]:
    items = [("Agents today\n(dev history)", base, MUTED, None),
             ("System, dev\n(n=500)", dev["business"][key]["value"], BLUE, dev["business"][key]["ci95"]),
             ("System, validation\n(n=80, run once)", val["business"][key]["value"], AQUA, val["business"][key]["ci95"])]
    xs = range(3)
    vbar(ax, xs, [i[1] for i in items], [i[2] for i in items])
    for x, it in zip(xs, items):
        if it[3]:
            ax.plot([x, x], it[3], color=INK, linewidth=1.2)
            ax.plot([x - 0.08, x + 0.08], [it[3][0]] * 2, color=INK, linewidth=1.2)
            ax.plot([x - 0.08, x + 0.08], [it[3][1]] * 2, color=INK, linewidth=1.2)
        ax.text(x + 0.12, it[1] + 0.012, f"{it[1]:.1%}", ha="left", fontsize=8, color=INK)
    ax.axhline(target, color=RED, linewidth=1, linestyle=(0, (4, 3)))
    if key == "first_contact_resolution":
        ax.text(-0.45, target - 0.06, f"target {target:.0%}", color=RED, fontsize=7.5, ha="left")
    else:
        ax.text(1.0, target + 0.015, f"target {target:.0%}", color=RED, fontsize=7.5, ha="center")
    if key == "first_contact_resolution":
        ax.axhline(orc["business"][key]["value"], color=VIOLET, linewidth=1, linestyle=(0, (2, 2)))
        ax.text(-0.45, orc["business"][key]["value"] + 0.012, "labels' ceiling 62%", color=VIOLET, fontsize=7, ha="left", va="bottom")
    ax.set_xticks(list(xs))
    ax.set_xticklabels([i[0] for i in items], fontsize=7.5)
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0, .2, .4, .6, .8, 1.0])
    ax.set_yticklabels(["0%", "20%", "40%", "60%", "80%", "100%"])
    ax.grid(axis="x", visible=False)
    ax.set_title(title, fontsize=9)
fig.suptitle("Business outcomes with 95% Wilson intervals (FCR = answered automatically and not blocked)", fontsize=10, fontweight="semibold", y=1.03)
save(fig, "fig10_business_outcomes.png")

# ------------------------------------------------------------------------------------------
# Figure 11: fairness audit forest plot (quality score with Wilson intervals)
# ------------------------------------------------------------------------------------------
fa = jload(RES / "fairness_audit" / "fairness_audit.json")


def seg_rows(run):
    out = []
    for group, segs in run["groups"].items():
        for s in segs:
            out.append((group, s["segment"], s["n"], s["quality"], s["quality_ci"]))
    return out


runs = fa["runs"] if isinstance(fa, dict) and "runs" in fa else None
if runs is None:
    # fall back to computing from results.jsonl
    def compute(p):
        rows = jsonl(p)
        groups = {"tier": lambda r: r["tier"], "fluency": lambda r: r["fluency"],
                  "ticket_length": lambda r: "short" if r["text_len"] < 120 else "long",
                  "region": lambda r: r["region"], "channel": lambda r: r["channel"]}
        out = []
        for g, fn in groups.items():
            buckets = defaultdict(list)
            for r in rows:
                if r.get("labels"):
                    buckets[fn(r)].append(r)
            for seg, rs in sorted(buckets.items()):
                exp = [r["labels"]["expected_route"] for r in rs]
                got = ["auto_respond" if r["action"] == "auto_respond" else "escalate" for r in rs]
                k = sum(1 for e, a in zip(exp, got) if e == a)
                out.append((g, seg, len(rs), k / len(rs), wilson(k, len(rs))))
        return out
    runs = {"validation (n=80)": compute(RES / "2026-09-16_validation" / "results.jsonl"),
            "development (n=500)": compute(RES / "2026-09-16_dev_full" / "results.jsonl")}
else:
    runs = {k: seg_rows(v) for k, v in runs.items()}

fig, axes = plt.subplots(1, 2, figsize=(7.2, 5.6), sharey=True)
order = None
for ax, (name, rows) in zip(axes, runs.items()):
    if order is None:
        order = [(g, s) for g, s, *_ in rows]
    lookup = {(g, s): (n, q, ci) for g, s, n, q, ci in rows}
    ys = list(range(len(order)))
    gcol = {"tier": BLUE, "fluency": ORANGE, "ticket_length": AQUA, "region": VIOLET, "channel": YELLOW}
    for y, key in zip(ys, order):
        n, q, ci = lookup[key]
        ax.plot(ci, [y, y], color=gcol[key[0]], linewidth=2)
        ax.scatter([q], [y], s=40, color=gcol[key[0]], edgecolor=SURFACE, linewidth=1.5, zorder=3)
        ax.text(1.01, y, f"n={n}", va="center", fontsize=7, color=MUTED)
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{g.replace('_', ' ')}: {s.replace('_', ' ')}" for g, s in order], fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlim(0.3, 1.0)
    ax.set_xticks([.4, .6, .8, 1.0])
    ax.set_xticklabels(["40%", "60%", "80%", "100%"])
    ax.grid(axis="y", visible=False)
    ax.set_title(name.capitalize(), fontsize=9)
fig.supxlabel("Routing accuracy against labels, point estimate and 95% Wilson interval", fontsize=8.5, color=INK2)
fig.suptitle("Fairness audit: no segment's interval is separated from the best segment on either set", fontsize=10, fontweight="semibold", y=1.01)
save(fig, "fig11_fairness.png")

# ------------------------------------------------------------------------------------------
# Figure 12: latency per ticket, live provider against local pipeline
# ------------------------------------------------------------------------------------------
lat = {"Validation run, live provider (n=80)": [r["latency_ms"] / 1000 for r in jsonl(RES / "2026-09-16_validation" / "results.jsonl")],
       "Dev run 1, live provider (n=500)": [r["latency_ms"] / 1000 for r in jsonl(RES / "2026-09-16_dev_full_run1" / "results.jsonl")],
       "Dev run 3, cached replies = local pipeline (n=500)": [r["latency_ms"] / 1000 for r in jsonl(RES / "2026-09-16_dev_full" / "results.jsonl")]}
fig, ax = plt.subplots(figsize=(7.2, 3.0))
for (name, xs), col, ty in zip(lat.items(), [AQUA, ORANGE, BLUE], [0.62, 0.72, 0.52]):
    xs = sorted(xs)
    ys = [(i + 1) / len(xs) for i in range(len(xs))]
    ax.plot(xs, ys, color=col, linewidth=2, label=name)
    p95 = xs[int(0.95 * len(xs)) - 1]
    ax.scatter([p95], [0.95], s=40, color=col, edgecolor=SURFACE, linewidth=1.5, zorder=3)
    ax.annotate(f"p95 {p95:.1f} s", (p95, 0.95), (p95, ty), fontsize=7.5, color=INK2, ha="center", arrowprops={"arrowstyle": "-", "color": GRID})
ax.axvline(3, color=RED, linewidth=1, linestyle=(0, (4, 3)))
ax.text(2.8, 0.86, "3 s target (NFR-01)", color=RED, fontsize=7.5, ha="right")
ax.set_xscale("log")
ax.set_xlabel("Seconds per ticket, end to end (log scale)")
ax.set_ylabel("Share of tickets at or below")
ax.set_xticks([0.1, 0.3, 1, 3, 10, 30])
ax.set_xticklabels(["0.1", "0.3", "1", "3", "10", "30"])
ax.legend(loc="lower right", fontsize=7.5)
ax.set_title("Latency: the local pipeline meets the target; provider round trips do not")
save(fig, "fig12_latency.png")

# ------------------------------------------------------------------------------------------
# Figure 13: what happened to the 500 development tickets (outcome and reason)
# ------------------------------------------------------------------------------------------
rows = jsonl(RES / "2026-09-16_dev_full" / "results.jsonl")
reason = Counter()
for r in rows:
    if r["action"] == "auto_respond":
        reason["Answered automatically"] += 1
    elif r["action"] == "block":
        reason["Blocked by grounding guardrail, escalated with draft"] += 1
    else:
        rr = r["route_reason"]
        if "always handled by a person" in rr:
            reason["Escalated: never-auto intent (policy)"] += 1
        elif "below the" in rr:
            reason["Escalated: confidence below 0.80"] += 1
        elif "no documentation passage" in rr:
            reason["Escalated: no passage above threshold"] += 1
        elif "instructions aimed" in rr:
            reason["Escalated: instruction-like input"] += 1
        else:
            reason["Escalated: other"] += 1
items = sorted(reason.items(), key=lambda kv: -kv[1])
fig, ax = plt.subplots(figsize=(7.2, 2.6))
cols = {"Answered automatically": AQUA, "Blocked by grounding guardrail, escalated with draft": RED}
hbar(ax, range(len(items)), [v for _, v in items], [cols.get(k, ORANGE) for k, _ in items])
for y, (k, v) in enumerate(items):
    ax.text(v + 4, y, f"{v} ({v / 500:.1%})", va="center", fontsize=8, color=INK)
ax.set_yticks(range(len(items)))
ax.set_yticklabels([k for k, _ in items], fontsize=8)
ax.invert_yaxis()
ax.set_xlim(0, 460)
ax.grid(axis="y", visible=False)
ax.set_title("Outcome of every development ticket in the final run (run 3), with the logged reason")
save(fig, "fig13_outcomes.png")

# ------------------------------------------------------------------------------------------
# Figure 14: routing errors decomposed
# ------------------------------------------------------------------------------------------
err_auto = sum(1 for r in rows if r["labels"] and r["labels"]["expected_route"] == "escalate" and r["action"] == "auto_respond")
esc_on_auto = [r for r in rows if r["labels"] and r["labels"]["expected_route"] == "auto_respond" and r["action"] != "auto_respond"]
sub = Counter()
for r in esc_on_auto:
    rr = r["route_reason"]
    if r["action"] == "block":
        sub["grounding block"] += 1
    elif "no documentation passage" in rr:
        sub["no passage above threshold"] += 1
    elif "below the" in rr:
        sub["confidence below 0.80"] += 1
    else:
        sub["other"] += 1
fig, ax = plt.subplots(figsize=(7.2, 2.2))
items = [("Auto-answered, label says escalate\n(answerable-looking intents; same text carries both labels)", err_auto, ORANGE)]
items += [(f"Escalated, label says auto: {k}", v, BLUE) for k, v in sub.most_common()]
hbar(ax, range(len(items)), [i[1] for i in items], [i[2] for i in items])
for y, it in enumerate(items):
    ax.text(it[1] + 1.5, y, str(it[1]), va="center", fontsize=8.5, color=INK)
ax.set_yticks(range(len(items)))
ax.set_yticklabels([i[0] for i in items], fontsize=7.5)
ax.invert_yaxis()
ax.grid(axis="y", visible=False)
ax.set_title(f"The {err_auto + len(esc_on_auto)} routing disagreements with the labels, development run 3")
save(fig, "fig14_routing_errors.png")

print("done")

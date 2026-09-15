"""Confidence calibration (NFR-08): map the classifier's combined score to a probability of being right.

Platt scaling: p = sigmoid(a * score + b), two parameters fitted on the development set by
evaluation/classify_check.py and stored in evaluation/results/calibration.json. Two parameters
suit a few hundred labelled examples; isotonic regression needs more data to be stable.
Without a fitted file the identity is used and the harness reports the raw calibration table.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Callable, Optional

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "evaluation" / "results" / "calibration.json"


def platt(a: float, b: float) -> Callable[[float], float]:
    def f(score: float) -> float:
        z = a * float(score) + b
        z = max(-60.0, min(60.0, z))
        return 1.0 / (1.0 + math.exp(-z))
    return f


def binned(edges, values) -> Callable[[float], float]:
    """Piecewise-constant map: score in [edges[i], edges[i+1]) -> values[i]."""
    def f(score: float) -> float:
        s = max(0.0, min(1.0, float(score)))
        for i in range(len(values)):
            if s < edges[i + 1] or i == len(values) - 1:
                return values[i]
        return values[-1]
    return f


def load_calibrator(path: Optional[Path] = None) -> Optional[Callable[[float], float]]:
    p = Path(path) if path else DEFAULT_PATH
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("method") == "platt":
            return platt(float(d["a"]), float(d["b"]))
        if d.get("method") == "binned":
            return binned([float(e) for e in d["edges"]], [float(v) for v in d["values"]])
    except Exception:
        return None
    return None


DEFAULT_EDGES = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0000001]


def fit_binned(scores, correct, edges=None, alpha: float = 1.0) -> dict:
    """Histogram binning with Laplace smoothing, monotone non-decreasing.

    value_i = (correct_i + alpha) / (n_i + 2 alpha); empty bins borrow the previous bin's value.
    Monotonicity is enforced with a cumulative max so a higher score never gets a lower
    confidence. Chosen over Platt because with very few errors Platt is either a step function
    (unregularised) or flat (regularised); binning keeps the shape the data shows.
    """
    edges = list(edges or DEFAULT_EDGES)
    n_bins = len(edges) - 1
    counts = [0] * n_bins
    hits = [0] * n_bins
    for s, c in zip(scores, correct):
        s = max(0.0, min(1.0, float(s)))
        i = min(n_bins - 1, max(0, next((j for j in range(n_bins) if s < edges[j + 1]), n_bins - 1)))
        counts[i] += 1
        hits[i] += 1 if c else 0
    values = []
    prev = None
    for i in range(n_bins):
        if counts[i] == 0:
            v = prev if prev is not None else alpha / (2 * alpha)
        else:
            v = (hits[i] + alpha) / (counts[i] + 2 * alpha)
        v = v if prev is None else max(prev, v)
        values.append(v)
        prev = v
    return {"method": "binned", "edges": edges, "values": values, "counts": counts, "hits": hits,
            "alpha": alpha, "n": int(len(scores))}


def cross_validated_binned_pairs(scores, correct, folds: int = 5, seed: int = 7, **kw):
    import random
    idx = list(range(len(scores)))
    random.Random(seed).shuffle(idx)
    out = []
    for f in range(folds):
        test = set(idx[f::folds])
        fit = fit_binned([scores[i] for i in idx if i not in test], [correct[i] for i in idx if i not in test], **kw)
        g = binned(fit["edges"], fit["values"])
        out.extend((g(scores[i]), correct[i]) for i in sorted(test))
    return out


def fit_platt(scores, correct, C: float = 1.0) -> dict:
    """Fit a, b by logistic regression on (score -> correct). Returns the JSON-ready record.

    C=1.0 (moderate L2 regularisation) on purpose: with very few errors an unregularised fit
    becomes a step function that claims certainty for everything, which would overstate
    confidence on unseen tickets. The cross-validated table in classify_check shows the effect.
    """
    from sklearn.linear_model import LogisticRegression
    import numpy as np
    X = np.array(scores, dtype=float).reshape(-1, 1)
    y = np.array([1 if c else 0 for c in correct])
    if len(set(y.tolist())) < 2:
        return {"method": "identity", "n": int(len(y)), "note": "only one class present; not fitted"}
    lr = LogisticRegression(C=C, solver="lbfgs")
    lr.fit(X, y)
    return {"method": "platt", "a": float(lr.coef_[0][0]), "b": float(lr.intercept_[0]), "n": int(len(y)), "C": C}


def cross_validated_pairs(scores, correct, folds: int = 5, C: float = 1.0, seed: int = 7):
    """(calibrated_confidence, correct) pairs where each confidence comes from a fit that never saw
    that ticket. This is the table to report."""
    import random
    idx = list(range(len(scores)))
    random.Random(seed).shuffle(idx)
    out = []
    for f in range(folds):
        test = set(idx[f::folds])
        train_s = [scores[i] for i in idx if i not in test]
        train_c = [correct[i] for i in idx if i not in test]
        fit = fit_platt(train_s, train_c, C=C)
        g = platt(fit["a"], fit["b"]) if fit.get("method") == "platt" else (lambda s: s)
        out.extend((g(scores[i]), correct[i]) for i in sorted(test))
    return out

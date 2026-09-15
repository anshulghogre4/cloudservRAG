"""B-06 / NFR-08: calibration helpers."""
import json

import pytest

from src.calibration import (binned, cross_validated_binned_pairs, cross_validated_pairs, fit_binned,
                             fit_platt, load_calibrator, platt)


def test_platt_is_monotone_and_bounded():
    f = platt(2.0, -1.0)
    xs = [i / 10 for i in range(11)]
    ys = [f(x) for x in xs]
    assert all(0.0 <= y <= 1.0 for y in ys)
    assert ys == sorted(ys)


def test_fit_platt_learns_direction():
    scores = [0.1] * 20 + [0.9] * 20
    correct = [False] * 18 + [True] * 2 + [True] * 19 + [False]
    fit = fit_platt(scores, correct)
    f = platt(fit["a"], fit["b"])
    assert f(0.9) > f(0.1) and fit["a"] > 0


def test_fit_binned_smooths_and_is_monotone():
    scores = [0.1, 0.1, 0.3, 0.3, 0.3, 0.5, 0.9, 0.9, 0.9, 0.9]
    correct = [False, False, True, True, False, True, True, True, True, True]
    fit = fit_binned(scores, correct)
    v = fit["values"]
    assert v == sorted(v)                                # monotone
    assert 0.0 < v[0] < 0.5                              # Laplace smoothing: not exactly 0
    assert v[-1] < 1.0                                   # and not exactly 1
    assert fit["counts"][3] == 0                         # the empty 0.6-0.8 bin
    assert v[3] == v[2]                                  # borrows the previous value
    g = binned(fit["edges"], fit["values"])
    assert g(0.0) == v[0] and g(1.0) == v[-1] and g(0.45) == v[2]


def test_cross_validation_returns_one_pair_per_example():
    scores = [i / 100 for i in range(100)]
    correct = [s > 0.3 for s in scores]
    assert len(cross_validated_pairs(scores, correct)) == 100
    assert len(cross_validated_binned_pairs(scores, correct)) == 100


def test_load_calibrator_reads_both_methods(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"method": "platt", "a": 1.0, "b": 0.0}), encoding="utf-8")
    assert load_calibrator(p)(0.0) == pytest.approx(0.5)
    p.write_text(json.dumps({"method": "binned", "edges": [0, 0.5, 1.0000001], "values": [0.2, 0.9]}), encoding="utf-8")
    f = load_calibrator(p)
    assert f(0.1) == 0.2 and f(0.7) == 0.9
    assert load_calibrator(tmp_path / "missing.json") is None

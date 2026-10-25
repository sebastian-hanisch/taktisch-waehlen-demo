"""Randfälle: kleinste und größte Reglerwerte für jedes Profilmodell und jede Regel, ungültige Eingaben, Determinismus, Struktur der Messreihen bei kleinen Zahlen."""

import time

import numpy as np
import pytest

import tkw_algorithm as A
import tkw_constants as C
import tkw_evaluation as ev
from tkw_scenario import make_profile


def test_every_model_and_rule_at_the_extreme_settings():
    for model in C.MODELS:
        for m, n in ((C.M_MIN, C.N_MIN), (C.M_MAX, C.N_MIN), (C.M_MIN, C.N_MAX), (C.M_MAX, C.N_MAX)):
            for rule in C.RULES:
                a = ev.analyse(ev.Settings(model, rule, m, n, 1))
                assert a.profile.shape == (n, m) and ev.verdict_state(a)[0] in ("success", "info", "warning")
                assert all(0 <= r.voters <= n and 0 <= r.voters_free <= r.voters for r in a.results.values())
                assert len(ev.rule_rows(a)) == 5


def test_the_largest_setting_runs_fast_enough_for_the_app():
    t = time.perf_counter()
    ev.analyse(ev.Settings("random", "irv", C.M_MAX, C.N_MAX, 1))
    assert time.perf_counter() - t < 10


def test_dictator_row_is_always_zero():
    for model in C.MODELS:
        a = ev.analyse(ev.Settings(model, "dictator", 4, 31, 7))
        assert a.results["dictator"].voters == 0 and a.results["dictator"].best is None


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        make_profile("x", 3, 5, 1)
    with pytest.raises(ValueError):
        make_profile("random", 1, 5, 1)
    with pytest.raises(ValueError):
        make_profile("random", 3, 0, 1)


def test_the_same_settings_give_the_same_analysis():
    a, b = ev.analyse(ev.Settings("camps", "borda", 4, 21, 7)), ev.analyse(ev.Settings("camps", "borda", 4, 21, 7))
    assert (a.profile == b.profile).all() and a.results["borda"] == b.results["borda"]
    c = ev.analyse(ev.Settings("camps", "borda", 4, 21, 8))
    assert not (a.profile == c.profile).all()


def test_the_tiebreak_is_a_permutation():
    for model in C.MODELS:
        _, tb = make_profile(model, 5, 21, 3)
        assert sorted(tb.tolist()) == [0, 1, 2, 3, 4]


def test_series_structure_with_small_numbers():
    rows = ev.series_rules(ms=(3,), ns=(5,), runs=10)
    assert [(r["rule"], r["m"], r["n"]) for r in rows] == [(rule, 3, 5) for rule in A.COUNT_RULES]
    assert all(0 <= r["profiles_free"] <= r["profiles"] <= 1 and 0 <= r["voters_free"] <= r["voters"] <= 1 for r in rows)
    assert next(r for r in rows if r["rule"] == "plurality")["profiles_free"] == 0.0
    mod = ev.series_models(m=3, n=5, runs=10)
    assert [(r["model"], r["rule"]) for r in mod] == [(mo, ru) for mo in C.MODELS for ru in A.COUNT_RULES]

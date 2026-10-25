"""Abbildungen: Spuren je Figur, Werte, Achsen gesperrt."""

import numpy as np

import tkw_constants as C
import tkw_evaluation as ev
import tkw_visualization as V


def _locked(fig):
    return fig.layout.xaxis.fixedrange is True and fig.layout.yaxis.fixedrange is True


def analysis(seven, tb_ba):
    s = ev.Settings("random", "plurality", 3, 7, 0)
    return ev.Analysis(s, seven, tb_ba, {r: ev.evaluate_rule(r, seven, tb_ba) for r in C.RULES})


def test_voters_figure_by_hand(seven, tb_ba):
    fig = V.build_voters(analysis(seven, tb_ba))
    assert list(fig.data[0].x) == list(C.RULES.values()) and _locked(fig)
    assert np.isclose(fig.data[0].y[0], 2 / 7) and fig.data[0].y[-1] == 0.0 and list(fig.data[0].text)[0] == "2 von 7"
    assert fig.data[0].marker.color[0] == C.RULE_COLORS["plurality"] and fig.data[0].marker.color[1] == "rgba(150,150,150,0.55)"      # nur die gewählte Regel ist farbig


def rows_series():
    rows = []
    for rule in ("plurality", "borda", "copeland", "irv"):
        for m in (3, 4):
            for n in (5, 11):
                rows.append({"rule": rule, "m": m, "n": n, "profiles": 0.2, "profiles_free": 0.0, "voters": 0.05, "voters_free": 0.0})
    return rows


def test_series_figure_has_a_line_per_rule_plus_the_dictator():
    fig = V.build_series(rows_series(), 3)
    assert [t.name for t in fig.data] == [C.RULES[r] for r in ("plurality", "borda", "copeland", "irv", "dictator")] and _locked(fig)
    assert list(fig.data[0].x) == [5, 11] and list(fig.data[-1].y) == [0.0, 0.0]
    fig2 = V.build_series(rows_series(), 3, key="voters")
    assert list(fig2.data[0].y) == [0.05, 0.05]


def test_models_figure_has_a_bar_per_rule():
    rows = [{"model": mo, "rule": ru, "profiles": 0.1} for mo in C.MODELS for ru in ("plurality", "borda", "copeland", "irv")]
    fig = V.build_models(rows)
    assert [t.name for t in fig.data] == [C.RULES[r] for r in ("plurality", "borda", "copeland", "irv")] and _locked(fig)
    assert list(fig.data[0].x) == ["Zufall", "einspitzig", "zwei Lager"]

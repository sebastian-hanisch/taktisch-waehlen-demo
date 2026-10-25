"""Befunde der README als Bänder: jede Zahl, die dort steht, ist hier an den festen Plänen der App geprüft (Seeds und Profile wie in messen.py).

Bänder statt Punktwerte: die Zufallszahlen eines numpy-Generators sind nicht über Versionen stabil. Je Zelle 150 Profile: die Standardabweichung eines Anteils
liegt bei höchstens 4 Prozentpunkten, die Bänder sind deshalb ±10 Punkte breit. Nullen und Sätze stehen ohne Band.
"""

import pytest

import tkw_algorithm as A
import tkw_constants as C
import tkw_evaluation as ev

BAND = 0.10


@pytest.fixture(scope="module")
def rules():
    return {(r["rule"], r["m"], r["n"]): r for r in ev.series_rules()}


@pytest.fixture(scope="module")
def models():
    return {(r["model"], r["rule"]): r for r in ev.series_models()}


def test_plurality_is_never_manipulable_without_a_tie(rules, models):
    assert all(r["profiles_free"] == 0.0 and r["voters_free"] == 0.0 for (rule, _, _), r in rules.items() if rule == "plurality")
    assert all(r["profiles_free"] == 0.0 for (_, rule), r in models.items() if rule == "plurality")


def test_with_three_candidates_borda_and_copeland_need_a_tie_in_these_samples(rules):
    for rule in ("borda", "copeland"):
        for n in C.SERIES_NS:
            assert rules[(rule, 3, n)]["profiles_free"] == 0.0, (rule, n)


def test_with_four_candidates_borda_has_manipulations_without_a_tie_and_copeland_still_has_none(rules):
    assert all(rules[("borda", 4, n)]["profiles_free"] > 0.05 for n in C.SERIES_NS) and rules[("borda", 4, 5)]["profiles_free"] == pytest.approx(0.26, abs=BAND)
    assert all(rules[("copeland", 4, n)]["profiles_free"] == 0.0 for n in C.SERIES_NS)


def test_the_sofortstichwahl_has_manipulations_without_a_tie_already_with_three_candidates(rules):
    assert all(rules[("irv", m, n)]["profiles_free"] > 0.0 for m in C.SERIES_MS for n in C.SERIES_NS)
    assert rules[("irv", 3, 5)]["profiles_free"] == pytest.approx(0.10, abs=0.08)


def test_with_the_tie_break_every_rule_can_be_manipulated_in_a_tenth_to_half_of_the_random_profiles(rules):
    for key, r in rules.items():
        assert 0.03 < r["profiles"] < 0.65, key
    assert rules[("plurality", 3, 11)]["profiles"] == pytest.approx(0.28, abs=BAND) and rules[("borda", 4, 5)]["profiles"] == pytest.approx(0.527, abs=BAND)
    assert rules[("copeland", 3, 51)]["profiles"] == pytest.approx(0.053, abs=0.07)


def test_the_shares_of_manipulable_profiles_fall_with_the_number_of_voters_for_four_candidates(rules):
    assert rules[("plurality", 4, 11)]["profiles"] == pytest.approx(0.40, abs=BAND) and rules[("plurality", 4, 51)]["profiles"] == pytest.approx(0.193, abs=BAND)
    assert rules[("plurality", 4, 51)]["profiles"] < rules[("plurality", 4, 11)]["profiles"] and rules[("copeland", 4, 51)]["profiles"] < rules[("copeland", 4, 11)]["profiles"] + 0.05


def test_few_voters_manipulate_on_average(rules):
    for key, r in rules.items():
        assert r["voters"] < 0.25, key
    assert rules[("borda", 4, 5)]["voters"] == pytest.approx(0.196, abs=BAND) and rules[("plurality", 3, 51)]["voters"] == pytest.approx(0.026, abs=0.04)


def test_four_candidates_21_voters_by_profile_model(models):
    assert models[("random", "plurality")]["profiles"] == pytest.approx(0.327, abs=BAND) and models[("random", "borda")]["profiles_free"] == pytest.approx(0.10, abs=0.08)
    assert models[("single", "copeland")]["profiles"] == pytest.approx(0.007, abs=0.06) and models[("single", "copeland")]["profiles_free"] == 0.0
    assert models[("single", "irv")]["profiles"] == pytest.approx(0.347, abs=BAND) and models[("single", "irv")]["profiles_free"] == pytest.approx(0.10, abs=0.08)
    assert models[("camps", "borda")]["profiles"] == pytest.approx(0.333, abs=BAND) and models[("camps", "irv")]["profiles"] == pytest.approx(0.193, abs=BAND)
    assert models[("single", "irv")]["profiles"] > models[("single", "copeland")]["profiles"] + 0.2          # bei einspitzigen Profilen trennt Copeland sich von den anderen


def test_the_presets_tell_the_stories_in_their_help_texts():
    d = ev.analyse(ev.Settings(**C.PRESETS["Mehrheitswahl, drei Kandidaten"]))
    assert d.selected.voters == 3 and d.selected.voters_free == 0 and d.selected.best.gain == 1
    b = ev.analyse(ev.Settings(**C.PRESETS["Borda: leicht zu überlisten"]))
    assert b.selected.voters == 10 and b.selected.best.gain == 2 and b.settings.n == 21
    i = ev.analyse(ev.Settings(**C.PRESETS["Sofortstichwahl: hier unüberlistbar"]))
    assert i.selected.voters == 0
    k = ev.analyse(ev.Settings(**C.PRESETS["Zwei Lager: taktisches Wählen"]))
    assert k.selected.voters == 6 and k.selected.best.gain == 2
    e = ev.analyse(ev.Settings(**C.PRESETS["Einspitzig: Copeland fast sicher"]))
    assert e.selected.voters == 0
    t = ev.analyse(ev.Settings(**C.PRESETS["Diktatur: nichts zu gewinnen"]))
    assert t.selected.voters == 0 and t.selected.winner == int(t.profile[0, 0])


def test_the_dictator_rule_has_no_manipulator_for_any_candidate_count():
    for m in (3, 4, 5):
        for seed in range(3):
            a = ev.analyse(ev.Settings("random", "dictator", m, 11, seed))
            assert a.results["dictator"].voters == 0


def test_the_smallest_examples():
    with_lot = ev.smallest_examples()
    assert [r["Wähler"] for r in with_lot] == [2, 2, 2, 2]
    free = ev.smallest_examples(tie_free=True)
    assert [r["Wähler"] for r in free] == ["–", "–", "–", 5]
    assert A.COUNT_RULES == ("plurality", "borda", "copeland", "irv")

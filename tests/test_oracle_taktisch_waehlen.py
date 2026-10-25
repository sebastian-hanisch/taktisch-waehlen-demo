"""Orakel (DEMO-PLAYBOOK §12): unabhängige Rechenwege für Regeln, Gleichstandsmarken und die Manipulationsprüfung.

(1) Naive Auswertung der Regeln mit einfachen Schleifen (samt Marke „Gleichstand“) gegen die Zählvektor-Fassung.
(2) Prüfung auf Wählerebene mit der naiven Auswertung (jeder Wähler, jede der m! Rangfolgen) gegen die schnelle Prüfung über Zählvektoren, mit und ohne Gleichstand.
(3) Jede gemeldete Manipulation wird nachgespielt; die Mehrheitswahl lässt sich nie ohne Gleichstand manipulieren (Satz); die Diktatur nie.
(4) Aufzählung ALLER Profile bis 4 Wähler: Wahl des kleinsten Gegenbeispiels gegen naive Suche.
"""

import itertools

import numpy as np
import pytest

import tkw_algorithm as A
from tkw_scenario import make_profile


def naive_outcome(rule, profile, tiebreak):
    """(Sieger, Gleichstand-Marke) mit einfachen Schleifen. Marke: Gleichstand an der Spitze (Punkteregeln) bzw. in irgendeiner Runde (Sofortstichwahl)."""
    rows = profile.tolist()
    m = len(rows[0])
    if rule == "dictator":
        return rows[0][0], False
    if rule in ("plurality", "borda", "copeland"):
        if rule == "plurality":
            scores = [float(sum(1 for r in rows if r[0] == c)) for c in range(m)]
        elif rule == "borda":
            scores = [float(sum(m - 1 - r.index(c) for r in rows)) for c in range(m)]
        else:
            w = [[sum(1 for r in rows if r.index(a) < r.index(b)) for b in range(m)] for a in range(m)]
            scores = [sum(1.0 if w[a][b] > w[b][a] else (0.5 if w[a][b] == w[b][a] else 0.0) for b in range(m) if b != a) for a in range(m)]
        best = max(scores)
        top = [c for c in range(m) if scores[c] == best]
        return min(top, key=lambda c: tiebreak[c]), len(top) > 1
    alive = set(range(m))
    tied = False
    while len(alive) > 1:
        counts = {c: 0 for c in alive}
        for r in rows:
            for c in r:
                if c in alive:
                    counts[c] += 1
                    break
        low = min(counts.values())
        losers = [c for c in alive if counts[c] == low]
        tied |= len(losers) > 1
        alive.discard(max(losers, key=lambda c: tiebreak[c]))
    return next(iter(alive)), tied


def naive_manipulators(rule, profile, tiebreak):
    """(Wähler, die manipulieren können, davon ohne Gleichstand), jeder Wähler gegen alle anderen Rangfolgen, mit der naiven Auswertung."""
    n, m = profile.shape
    base, base_tied = naive_outcome(rule, profile, tiebreak)
    voters = free = 0
    for v in range(n):
        true = profile[v].tolist()
        rank_of = {c: i for i, c in enumerate(true)}
        any_win = any_free = False
        for alt in itertools.permutations(range(m)):
            if list(alt) == true:
                continue
            changed = profile.copy()
            changed[v] = alt
            new, new_tied = naive_outcome(rule, changed, tiebreak)
            if rank_of[new] < rank_of[base]:
                any_win = True
                if not base_tied and not new_tied:
                    any_free = True
        voters += any_win
        free += any_free
    return voters, free


@pytest.mark.parametrize("rule", A.COUNT_RULES)
def test_rules_match_the_naive_evaluation(rule):
    rng = np.random.default_rng(10)
    for t in range(60):
        m = int(rng.integers(2, 6))
        n = int(rng.integers(1, 30))
        model = list(A.PROFILE_MODELS)[t % 3]
        profile = A.PROFILE_MODELS[model](n, m, rng)
        tb = rng.permutation(m)
        assert A.winner_profile(rule, profile, tb) == naive_outcome(rule, profile, tb)[0], (rule, t)


@pytest.mark.parametrize("rule", A.COUNT_RULES)
@pytest.mark.parametrize("m", [3, 4])
def test_fast_manipulation_check_matches_the_naive_voter_level_search(rule, m):
    rng = np.random.default_rng(20 + m)
    for t in range(12 if m == 4 else 25):
        n = int(rng.integers(3, 10 if m == 4 else 14))
        model = list(A.PROFILE_MODELS)[t % 3]
        profile = A.PROFILE_MODELS[model](n, m, rng)
        tb = rng.permutation(m)
        s = A.manipulation_counts(rule, A.counts_of(profile), m, tb)
        assert (s.voters, s.voters_free) == naive_manipulators(rule, profile, tb), (rule, m, t)
        assert s.voters == A.manipulators_voter_level(rule, profile, tb)


def test_every_reported_manipulation_is_real_when_replayed():
    rng = np.random.default_rng(30)
    checked = 0
    for t in range(60):
        m = int(rng.integers(3, 5))
        profile, tb = make_profile(list(A.PROFILE_MODELS)[t % 3], m, int(rng.integers(5, 15)), 1000 + t)
        c = A.counts_of(profile)
        for rule in A.COUNT_RULES:
            s = A.manipulation_counts(rule, c, m, tb)
            for b in (s.best, s.best_free):
                if b is None:
                    continue
                v = next(i for i in range(len(profile)) if tuple(profile[i]) == b.ranking)
                changed = profile.copy()
                changed[v] = b.ballot
                assert A.winner_profile(rule, profile, tb) == b.honest and A.winner_profile(rule, changed, tb) == b.result
                rank_of = {cand: i for i, cand in enumerate(b.ranking)}
                assert rank_of[b.honest] - rank_of[b.result] == b.gain > 0
                checked += 1
    assert checked > 50


def test_plurality_is_never_manipulable_without_a_tie_and_the_dictator_never():
    rng = np.random.default_rng(40)
    for t in range(300):
        m = int(rng.integers(3, 6))
        profile, tb = make_profile(list(A.PROFILE_MODELS)[t % 3], m, int(rng.integers(3, 40)), 2000 + t)
        s = A.manipulation_counts("plurality", A.counts_of(profile), m, tb)
        assert s.voters_free == 0 and s.best_free is None, t
        if t < 40:
            assert A.manipulators_voter_level("dictator", profile, tb) == 0


def test_exhaustive_search_of_the_smallest_example_matches_a_naive_search():
    tb = np.array([0, 1, 2])
    rankings = list(itertools.permutations(range(3)))
    for rule in A.COUNT_RULES:
        found = A.smallest_manipulable_profile(rule, 3, tb, 4)
        naive = None
        for n in range(1, 5):
            for combo in itertools.combinations_with_replacement(range(6), n):
                profile = np.array([rankings[i] for i in combo])
                if naive_manipulators(rule, profile, tb)[0] > 0:
                    naive = n
                    break
            if naive:
                break
        assert (found[0] if found else None) == naive, rule


def naive_best(rule, profile, tb, free):
    """Beispiel mit dem größten Gewinn nach der Regel der App: erste Rangfolge (in der Reihenfolge von all_rankings) mit dem größten Gewinn, darin die erste Ersatz-Rangfolge mit diesem Gewinn."""
    m = profile.shape[1]
    rk = A.all_rankings(m).tolist()
    base, base_tied = naive_outcome(rule, profile, tb)
    best = None
    for i, true in enumerate(rk):
        if true not in profile.tolist():
            continue
        v = profile.tolist().index(true)
        rank_of = {c: p for p, c in enumerate(true)}
        gain_i, ballot_i, result_i = 0, None, None
        for j, alt in enumerate(rk):
            if j == i:
                continue
            changed = profile.copy()
            changed[v] = alt
            new, new_tied = naive_outcome(rule, changed, tb)
            if free and (base_tied or new_tied):
                continue
            gain = rank_of[base] - rank_of[new]
            if gain > gain_i:
                gain_i, ballot_i, result_i = gain, alt, new
        if gain_i > 0 and (best is None or gain_i > best[0]):
            best = (gain_i, tuple(true), tuple(ballot_i), base, result_i)
    return best


@pytest.mark.parametrize("rule", A.COUNT_RULES)
def test_the_reported_example_is_the_first_one_with_the_largest_gain(rule):
    rng = np.random.default_rng(50)
    checked = 0
    for t in range(150):
        m = 3 + t % 2
        profile, tb = make_profile(list(A.PROFILE_MODELS)[t % 3], m, int(rng.integers(5, 12)), 3000 + t)
        s = A.manipulation_counts(rule, A.counts_of(profile), m, tb)
        for free, got in ((False, s.best), (True, s.best_free)):
            want = naive_best(rule, profile, tb, free)
            if want is None:
                assert got is None
            else:
                assert (got.gain, got.ranking, got.ballot, got.honest, got.result) == want, (rule, t, free)
                checked += 1
    assert checked > 3


def test_voter_level_check_equals_the_fast_check_on_all_small_profiles():
    tb = np.array([0, 1, 2])
    rk = A.all_rankings(3)
    for n in (1, 2, 3, 4):
        for comp in A.compositions(n, 6):
            profile = np.array([rk[i] for i, cnt in enumerate(comp) for _ in range(cnt)])
            for rule in A.COUNT_RULES:
                assert A.manipulation_counts(rule, np.array(comp), 3, tb).voters == A.manipulators_voter_level(rule, profile, tb), (rule, comp)


def test_smallest_example_search_respects_its_bounds():
    tb = np.array([0, 1, 2])
    assert A.smallest_manipulable_profile("irv", 3, tb, 5, tie_free=True)[0] == 5
    assert A.smallest_manipulable_profile("irv", 3, tb, 4, tie_free=True) is None
    assert A.smallest_manipulable_profile("plurality", 3, tb, 1) is None and A.smallest_manipulable_profile("plurality", 3, tb, 2)[0] == 2

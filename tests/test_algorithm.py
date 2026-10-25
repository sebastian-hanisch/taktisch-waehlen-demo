"""Kern von Hand: jede Einheit an den Mini-Profilen aus conftest.py, mit der Rechnung im Kommentar."""

import numpy as np
import pytest

import tkw_algorithm as A


def test_all_rankings_and_tables_for_three_candidates():
    rk = A.all_rankings(3)
    assert rk.shape == (6, 3) and rk.tolist()[0] == [0, 1, 2] and rk.tolist()[-1] == [2, 1, 0]
    pos, before, index = A.ranking_tables(3)
    i = index[(1, 2, 0)]
    assert pos[i].tolist() == [2, 0, 1]                             # B > C > A: A auf Platz 2, B auf 0, C auf 1
    assert before[i].tolist() == [[False, False, False], [True, False, True], [True, False, False]]
    assert before[i, 1, 0] and before[i, 1, 2] and before[i, 2, 0] and not before[i, 0, 1]


def test_counts_of_by_hand(seven):
    c = A.counts_of(seven)
    rk = A.all_rankings(3).tolist()
    assert c.sum() == 7 and c[rk.index([0, 1, 2])] == 3 and c[rk.index([1, 2, 0])] == 2 and c[rk.index([2, 1, 0])] == 2


def test_winners_of_the_four_rules_by_hand(seven, tb_id):
    c = A.counts_of(seven)
    assert [A.winner_counts(r, c, 3, tb_id) for r in A.COUNT_RULES] == [0, 1, 1, 1]            # Mehrheitswahl A, Borda B (9), Copeland B (2), Sofortstichwahl B
    assert A.winner_profile("dictator", seven, tb_id) == 0 and A.winner_profile("dictator", seven[::-1].copy(), tb_id) == 2


def test_pick_and_copeland_scores():
    assert A.pick(np.array([3, 5, 5]), np.array([0, 1, 2])) == 1 and A.pick(np.array([3, 5, 5]), np.array([2, 1, 0])) == 2
    w = np.array([[0, 2, 2], [2, 0, 3], [2, 1, 0]])
    assert A.copeland_scores(w).tolist() == [1.0, 1.5, 0.5]


def test_plurality_is_manipulable_only_through_the_tie_break(seven, tb_ba, tb_id):
    c = A.counts_of(seven)
    # Mehrheitswahl: A 3, B 2, C 2. Mit Gleichstand B vor A: ein Wähler mit C>B>A gibt B an -> B 3, A 3, B gewinnt (Rangplatz 1 statt 2).
    s = A.manipulation_counts("plurality", c, 3, tb_ba)
    assert s.voters == 2 and s.voters_free == 0 and s.best.honest == 0 and s.best.result == 1 and s.best.gain == 1
    assert s.best.ranking == (2, 1, 0) and s.best.ballot[0] == 1
    # Mit A vor B gewinnt A auch beim Gleichstand: nichts zu holen.
    s = A.manipulation_counts("plurality", c, 3, tb_id)
    assert s.voters == 0 and s.best is None and s.voters_free == 0


def test_unanimous_voters_cannot_gain_anything(tb_id):
    c = A.counts_of(np.array([[1, 0, 2]] * 5))
    for rule in A.COUNT_RULES:
        s = A.manipulation_counts(rule, c, 3, tb_id)
        assert s.voters == 0 and s.voters_free == 0 and s.best is None


def test_with_two_candidates_nothing_can_be_manipulated(tb_id):
    tb = np.array([0, 1])
    rng = np.random.default_rng(1)
    for _ in range(40):
        p = A.profile_random(int(2 * rng.integers(1, 15) + 1), 2, rng)
        for rule in A.COUNT_RULES:
            assert A.manipulation_counts(rule, A.counts_of(p), 2, tb).voters == 0
        assert A.manipulators_voter_level("dictator", p, tb) == 0


def test_the_dictator_cannot_be_manipulated(seven, tb_id):
    assert A.manipulators_voter_level("dictator", seven, tb_id) == 0
    rng = np.random.default_rng(2)
    for m in (3, 4):
        p = A.profile_random(9, m, rng)
        assert A.manipulators_voter_level("dictator", p, np.arange(m)) == 0


def test_all_ballot_winners_equal_the_scalar_rule_for_every_alternative(tb_ba):
    rng = np.random.default_rng(3)
    for m in (3, 4):
        for _ in range(10):
            p = A.profile_random(int(rng.integers(3, 12)), m, rng)
            c = A.counts_of(p)
            tb = rng.permutation(m)
            for rule in A.COUNT_RULES:
                for i in np.flatnonzero(c > 0):
                    winners, tied = A.winners_for_all_ballots(rule, c, int(i), m, tb)
                    for j in range(len(c)):
                        c2 = c.copy()
                        c2[i] -= 1
                        c2[j] += 1
                        assert winners[j] == A.winner_counts(rule, c2, m, tb), (rule, int(i), j)
                    assert winners[i] == A.winner_counts(rule, c, m, tb) and tied.dtype == bool


def test_compositions_count():
    assert len(list(A.compositions(3, 6))) == 56 and len(list(A.compositions(5, 3))) == 21           # C(8, 5) und C(7, 2)
    assert all(sum(c) == 4 for c in A.compositions(4, 5))


def test_smallest_examples_by_hand(tb_id):
    # Zwei Wähler: 1 x B>A>C und 1 x C>A>B. Erststimmen B 1, C 1: Gleichstand, A vor B vor C -> B. Der Wähler C>A>B gibt A>B>C an: A 1, B 1 -> A gewinnt (Platz 1 statt 2).
    n, c, b = A.smallest_manipulable_profile("plurality", 3, tb_id, 5)
    assert n == 2 and b.honest == 1 and b.result == 0 and b.gain == 1
    assert A.smallest_manipulable_profile("plurality", 3, tb_id, 7, tie_free=True) is None             # Satz: Mehrheitswahl nie ohne Gleichstand
    n, c, b = A.smallest_manipulable_profile("irv", 3, tb_id, 7, tie_free=True)
    assert n == 5 and b.gain >= 1


def test_profile_shapes_and_each_row_is_a_permutation():
    rng = np.random.default_rng(4)
    for model, gen in A.PROFILE_MODELS.items():
        p = gen(40, 5, rng)
        assert p.shape == (40, 5) and all(sorted(row) == [0, 1, 2, 3, 4] for row in p.tolist()), model


def test_mallows_with_phi_zero_is_the_base_order():
    p = A.mallows_profile(30, [2, 0, 1], 1e-12, np.random.default_rng(5))
    assert (p == np.array([2, 0, 1])[None, :]).all()


def test_unknown_rule_raises(seven, tb_id):
    with pytest.raises(ValueError):
        A.winner_counts("x", A.counts_of(seven), 3, tb_id)
    with pytest.raises(ValueError):
        A.winners_for_all_ballots("x", A.counts_of(seven), 0, 3, tb_id)


def test_borda_manipulation_where_the_only_working_ballot_shares_no_position_with_the_true_ranking():
    # Wähler 1: A>B>C>D, Wähler 2: C>D>B>A. Borda ehrlich: A 3, B 2+1 = 3, C 1+3 = 4, D 0+2 = 2: C gewinnt (für Wähler 1 der dritte Platz).
    # Gibt Wähler 1 B>A>D>C an: A 2, B 3+1 = 4, C 0+3 = 3, D 1+2 = 3: B gewinnt (zweiter Platz). Das ist die EINZIGE Rangfolge, die hilft, und sie unterscheidet sich an jeder Stelle von A>B>C>D.
    p = np.array([[0, 1, 2, 3], [2, 3, 1, 0]])
    tb = np.array([3, 2, 1, 0])
    s = A.manipulation_counts("borda", A.counts_of(p), 4, tb)
    assert (s.voters, s.voters_free) == (1, 1) and s.best.honest == 2 and s.best.result == 1 and s.best.gain == 1
    assert s.best.ranking == (0, 1, 2, 3) and s.best.ballot == (1, 0, 3, 2) and all(a != b for a, b in zip(s.best.ranking, s.best.ballot))
    assert A.manipulators_voter_level("borda", p, tb) == 1

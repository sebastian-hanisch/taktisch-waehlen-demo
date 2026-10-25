"""Verdikte (reine Funktionen): Art und jede Zahl im Text an handgesetzten Profilen und Werten, jeder Zweig."""

import numpy as np

import tkw_algorithm as A
import tkw_constants as C
import tkw_evaluation as ev
from tkw_evaluation import Analysis, Settings


def make(profile, tiebreak, rule="plurality", model="random"):
    p = np.asarray(profile)
    s = Settings(model, rule, p.shape[1], p.shape[0], 0)
    return Analysis(s, p, tiebreak, {r: ev.evaluate_rule(r, p, tiebreak) for r in C.RULES})


FIVE = [[0, 1, 2]] * 2 + [[1, 0, 2]] + [[2, 1, 0]] * 2             # 2 x A>B>C, 1 x B>A>C, 2 x C>B>A


def test_num_pct_label_and_texts():
    assert ev.num(3.14159, 2) == "3,14" and ev.pct(0.456) == "46 %" and ev.pct(0.0456, 1) == "4,6 %" and ev.label(0) == "A" and ev.label(4) == "E"
    assert ev.ranking_text((2, 1, 0)) == "C > B > A"
    b = A.Manipulation((2, 1, 0), (1, 0, 2), 0, 1, 1)
    assert ev.manipulation_text(b) == "ein Wähler mit der Rangfolge C > B > A gibt B > A > C an, dann gewinnt B statt A (1 Platz besser für ihn)"
    assert "(2 Plätze besser für ihn)" in ev.manipulation_text(A.Manipulation((2, 1, 0), (1, 0, 2), 0, 2, 2))


def test_verdict_for_plurality_that_lives_on_the_tie(seven, tb_ba):
    kind, text = ev.verdict_state(make(seven, tb_ba))
    assert kind == "warning"
    assert text == ("Bei Mehrheitswahl können 2 von 7 Wählern (29 %) das Ergebnis allein zu ihren Gunsten drehen. "
                    "Das beste Beispiel: ein Wähler mit der Rangfolge C > B > A gibt B > A > C an, dann gewinnt B statt A (1 Platz besser für ihn). "
                    "Alle diese Manipulationen **leben vom Gleichstand**: ohne das Los (oder bei einer anderen Gleichstandsregel) gelingt keine.")


def test_verdict_when_nobody_can_manipulate(seven, tb_id):
    kind, text = ev.verdict_state(make(seven, tb_id))
    assert kind == "info"
    assert text == "In diesem Profil kann bei Mehrheitswahl kein Wähler allein ein besseres Ergebnis erzwingen (0 von 7). In anderen Profilen kann das sehr wohl gehen: die Messreihen unten zählen es."


def test_verdict_with_a_manipulation_that_works_without_a_tie(tb_id):
    a = make(FIVE, tb_id, "irv")
    r = a.selected
    assert (r.voters, r.voters_free) == (2, 2) and r.best.honest == 0 and r.best.result == 1                      # Sofortstichwahl: A gewinnt ehrlich, B nach der Abweichung
    kind, text = ev.verdict_state(a)
    assert kind == "warning"
    assert text == ("Bei Sofortstichwahl können 2 von 5 Wählern (40 %) das Ergebnis allein zu ihren Gunsten drehen. "
                    f"Das beste Beispiel: {ev.manipulation_text(r.best)}. **Ohne Hilfe eines Gleichstands** gelingt es 2 von 5.")


def test_verdict_for_two_candidates_and_for_the_dictator(seven, tb_id):
    kind, text = ev.verdict_state(make([[0, 1], [1, 0], [0, 1]], np.array([0, 1])))
    assert kind == "success" and text == "Bei zwei Kandidaten entscheidet die Mehrheit, und keine Regel lässt sich überlisten: kein Wähler kann das Ergebnis allein verbessern (0 von 3)."
    kind, text = ev.verdict_state(make(seven, tb_id, "dictator"))
    assert kind == "success" and text.startswith("Bei der Diktatur kann kein Wähler etwas gewinnen (0 von 7)") and "einzige Regel" in text


def test_rule_rows_by_hand(seven, tb_ba):
    rows = ev.rule_rows(make(seven, tb_ba))
    assert [r["Regel"] for r in rows] == list(C.RULES.values())
    p, d = rows[0], rows[-1]
    assert p["ehrlicher Sieger"] == "A" and p["Wähler, die allein manipulieren können"] == "2 von 7 (29 %)" and p["davon ohne Hilfe eines Gleichstands"] == "0 von 7" and p["größter Gewinn"] == "1 Platz besser"
    assert d["ehrlicher Sieger"] == "A" and d["Wähler, die allein manipulieren können"] == "0 von 7 (0 %)" and d["größter Gewinn"] == "–"


def test_profile_text_and_smallest_examples():
    c = A.counts_of(np.array([[1, 0, 2], [2, 0, 1]]))
    assert ev.profile_text(c, 3) == "1 × B > A > C, 1 × C > A > B"
    rows = ev.smallest_examples()
    assert [r["Wähler"] for r in rows] == [2, 2, 2, 2] and rows[0]["Profil"] == "1 × B > A > C, 1 × C > A > B"
    assert rows[0]["Manipulation"] == "Wähler mit C > A > B gibt A > B > C an: A statt B"
    free = ev.smallest_examples(tie_free=True)
    assert [r["Wähler"] for r in free] == ["–", "–", "–", 5] and free[0]["Profil"] == "bis 9 Wähler keines gefunden" and free[3]["Profil"] == "2 × A > B > C, 1 × B > A > C, 2 × C > B > A"


def rows_rules():
    def row(rule, m, n, p, pf, v):
        return {"rule": rule, "m": m, "n": n, "profiles": p, "profiles_free": pf, "voters": v, "voters_free": 0.0, "runs": 150}

    return [row("plurality", 3, 51, 0.187, 0.0, 0.026), row("borda", 3, 51, 0.14, 0.0, 0.049), row("copeland", 3, 51, 0.053, 0.0, 0.008), row("irv", 3, 51, 0.08, 0.027, 0.021),
            row("plurality", 3, 5, 0.233, 0.0, 0.064), row("plurality", 4, 51, 0.193, 0.0, 0.046)]


def test_rules_row_and_verdict():
    r = rows_rules()[0]
    assert ev.rules_row(r) == {"Regel": "Mehrheitswahl", "Kandidaten": 3, "Wähler": 51, "Profile mit einem Manipulator": "19 %", "davon ohne Hilfe eines Gleichstands": "0 %",
                               "Wähler, die allein manipulieren können (Mittel)": "2,6 %"}
    kind, text = ev.verdict_rules(rows_rules())
    assert kind == "info"
    assert text == ("Bei 3 Kandidaten und 51 Wählern kann in 5 % der Zufallsprofile mindestens ein Wähler allein manipulieren, wenn nach Copeland gezählt wird, "
                    "und in 19 % bei Mehrheitswahl. Bei der Mehrheitswahl gelingt es nur über einen Gleichstand (0 % ohne). "
                    "Eine Regel ohne jede Manipulierbarkeit gibt es mit drei oder mehr Kandidaten nur als Diktatur.")


def test_models_verdict_by_hand():
    def row(model, rule, p):
        return {"model": model, "rule": rule, "m": 4, "n": 21, "profiles": p}

    rows = [row("random", "plurality", 0.327), row("random", "borda", 0.273), row("random", "copeland", 0.22), row("random", "irv", 0.2),
            row("single", "plurality", 0.313), row("single", "borda", 0.253), row("single", "copeland", 0.007), row("single", "irv", 0.347),
            row("camps", "plurality", 0.367), row("camps", "borda", 0.333), row("camps", "copeland", 0.26), row("camps", "irv", 0.193)]
    kind, text = ev.verdict_models(rows)
    assert kind == "info"
    assert text == ("Die am häufigsten manipulierbare Regel je Profilmodell (4 Kandidaten, 21 Wähler, Anteil der Profile mit einem Manipulator): "
                    "Zufall: Mehrheitswahl (33 %); einspitzig: Sofortstichwahl (35 %); zwei Lager: Mehrheitswahl (37 %).")

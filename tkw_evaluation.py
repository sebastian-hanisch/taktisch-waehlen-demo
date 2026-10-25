"""Auswertung: ein Profil auf Manipulierbarkeit analysieren, zwei Messreihen mit festem Programm, alle Verdikte als reine Funktionen."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import tkw_algorithm as A
import tkw_constants as C
from tkw_scenario import make_profile


def num(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def pct(x: float, digits: int = 0) -> str:
    return f"{100 * x:.{digits}f} %".replace(".", ",")


def label(c) -> str:
    return C.CANDIDATE_LABELS[int(c)]


def ranking_text(r) -> str:
    return " > ".join(label(c) for c in r)


@dataclass(frozen=True)
class Settings:
    model: str = C.DEFAULT_MODEL
    rule: str = C.DEFAULT_RULE
    m: int = C.DEFAULT_M
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class RuleResult:
    winner: int
    voters: int                         # Wähler, die allein manipulieren können (das Los eingerechnet)
    best: A.Manipulation | None
    voters_free: int = 0                # davon: auch ohne Gleichstand
    best_free: A.Manipulation | None = None


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    profile: np.ndarray
    tiebreak: np.ndarray
    results: dict                       # Regelname -> RuleResult

    @property
    def selected(self) -> RuleResult:
        return self.results[self.settings.rule]


def evaluate_rule(rule: str, profile: np.ndarray, tiebreak: np.ndarray) -> RuleResult:
    n, m = profile.shape
    if rule == "dictator":
        return RuleResult(A.winner_profile("dictator", profile, tiebreak), A.manipulators_voter_level("dictator", profile, tiebreak), None)
    c = A.counts_of(profile)
    s = A.manipulation_counts(rule, c, m, tiebreak)
    return RuleResult(A.winner_counts(rule, c, m, tiebreak), s.voters, s.best, s.voters_free, s.best_free)


def analyse(settings: Settings) -> Analysis:
    profile, tiebreak = make_profile(settings.model, settings.m, settings.n, settings.seed)
    return Analysis(settings, profile, tiebreak, {rule: evaluate_rule(rule, profile, tiebreak) for rule in C.RULES})


def rule_rows(a: Analysis) -> list[dict]:
    """Tabelle der fünf Regeln: Sieger, Zahl der Wähler, die allein manipulieren können (und davon ohne Gleichstand), größter Gewinn."""
    n = a.settings.n
    rows = []
    for rule, name in C.RULES.items():
        r = a.results[rule]
        rows.append({"Regel": name, "ehrlicher Sieger": label(r.winner), "Wähler, die allein manipulieren können": f"{r.voters} von {n} ({pct(r.voters / n)})",
                     "davon ohne Hilfe eines Gleichstands": f"{r.voters_free} von {n}",
                     "größter Gewinn": "–" if r.best is None else f"{places(r.best.gain)} besser"})
    return rows


def places(gain: int) -> str:
    return f"{gain} Platz" if gain == 1 else f"{gain} Plätze"


def short_rule(rule: str) -> str:
    """Regelname ohne den Zusatz in Klammern: „Sofortstichwahl“, „Copeland“."""
    return C.RULES[rule].split(" (")[0]


def manipulation_text(b: A.Manipulation) -> str:
    return (f"ein Wähler mit der Rangfolge {ranking_text(b.ranking)} gibt {ranking_text(b.ballot)} an, dann gewinnt {label(b.result)} statt {label(b.honest)} "
            f"({places(b.gain)} besser für ihn)")


def verdict_state(a: Analysis) -> tuple[str, str]:
    """Verdikt der Kernfrage für die gewählte Regel als (Art, Text), rein: die App ruft st.<Art>(Text), der Test prüft jede Zahl im Text."""
    s = a.settings
    r = a.selected
    name = short_rule(s.rule)
    if s.m == 2:
        return "success", f"Bei zwei Kandidaten entscheidet die Mehrheit, und keine Regel lässt sich überlisten: kein Wähler kann das Ergebnis allein verbessern (0 von {s.n})."
    if s.rule == "dictator":
        return "success", (f"Bei der Diktatur kann kein Wähler etwas gewinnen (0 von {s.n}): der Diktator bekommt ohnehin seinen ersten Platz, alle anderen ändern nichts. "
                           "Das ist die einzige Regel mit mindestens drei möglichen Siegern, die nicht manipulierbar ist, um den Preis, dass nur eine Stimme zählt.")
    if r.voters == 0:
        return "info", f"In diesem Profil kann bei {name} kein Wähler allein ein besseres Ergebnis erzwingen (0 von {s.n}). In anderen Profilen kann das sehr wohl gehen: die Messreihen unten zählen es."
    text = (f"Bei {name} können {r.voters} von {s.n} Wählern ({pct(r.voters / s.n)}) das Ergebnis allein zu ihren Gunsten drehen. "
            f"Das beste Beispiel: {manipulation_text(r.best)}.")
    if r.voters_free == 0:
        return "warning", text + " Alle diese Manipulationen **leben vom Gleichstand**: ohne das Los (oder bei einer anderen Gleichstandsregel) gelingt keine."
    return "warning", text + f" **Ohne Hilfe eines Gleichstands** gelingt es {r.voters_free} von {s.n}."


def profile_text(c: np.ndarray, m: int) -> str:
    """Zählvektor als Text: „2 × A > B > C, 1 × B > A > C“."""
    rk = A.all_rankings(m)
    return ", ".join(f"{int(c[i])} × {ranking_text(rk[i])}" for i in range(len(c)) if c[i] > 0)


def smallest_examples(m: int = 3, max_n: int = 9, tie_free: bool = False) -> list[dict]:
    """Je anonymer Regel das kleinste Profil (Aufzählung aller Profile bis max_n Wähler, Gleichstand: A vor B vor C), in dem ein einzelner Wähler manipulieren kann.
    `tie_free`: nur Manipulationen, die weder im ehrlichen noch im manipulierten Lauf einen Gleichstand brauchen."""
    tiebreak = np.arange(m)
    rows = []
    for rule in A.COUNT_RULES:
        found = A.smallest_manipulable_profile(rule, m, tiebreak, max_n, tie_free)
        if found is None:
            rows.append({"Regel": C.RULES[rule], "Wähler": "–", "Profil": f"bis {max_n} Wähler keines gefunden", "Manipulation": "–"})
            continue
        n, c, b = found
        rows.append({"Regel": C.RULES[rule], "Wähler": n, "Profil": profile_text(c, m),
                     "Manipulation": f"Wähler mit {ranking_text(b.ranking)} gibt {ranking_text(b.ballot)} an: {label(b.result)} statt {label(b.honest)}"})
    return rows


# --- Messreihen --------------------------------------------------------------------------------------------------------------------------------

def share_profiles_and_voters(rule: str, model: str, m: int, n: int, runs: int, seed: int) -> dict:
    """Anteil der Profile mit mindestens einem Manipulator und mittlerer Anteil der Wähler, die allein manipulieren können; jeweils auch ohne Hilfe eines Gleichstands."""
    out = {"profiles": 0, "voters": 0.0, "profiles_free": 0, "voters_free": 0.0}
    for j in range(runs):
        profile, tiebreak = make_profile(model, m, n, seed + j)
        s = A.manipulation_counts(rule, A.counts_of(profile), m, tiebreak)
        out["profiles"] += s.voters > 0
        out["voters"] += s.voters / n
        out["profiles_free"] += s.voters_free > 0
        out["voters_free"] += s.voters_free / n
    return {k: v / runs for k, v in out.items()}


def series_rules(ms=C.SERIES_MS, ns=C.SERIES_NS, runs: int = C.SERIES_RUNS, seed: int = C.SERIES_SEED) -> list[dict]:
    """Zufallsprofile: je Regel, Kandidaten- und Wählerzahl der Anteil manipulierbarer Profile und der mittlere Anteil manipulierender Wähler (mit und ohne Gleichstandshilfe)."""
    rows = []
    for m in ms:
        for n in ns:
            for rule in A.COUNT_RULES:
                rows.append({"rule": rule, "m": m, "n": n, "runs": runs, **share_profiles_and_voters(rule, "random", m, n, runs, seed)})
    return rows


def series_models(m: int = C.SERIES_MODEL_M, n: int = C.SERIES_MODEL_N, runs: int = C.SERIES_RUNS, seed: int = C.SERIES_SEED) -> list[dict]:
    """Dieselbe Frage für die drei Profilmodelle bei fester Kandidaten- und Wählerzahl."""
    rows = []
    for model in C.MODELS:
        for rule in A.COUNT_RULES:
            rows.append({"model": model, "rule": rule, "m": m, "n": n, "runs": runs, **share_profiles_and_voters(rule, model, m, n, runs, seed)})
    return rows


def rules_row(r: dict) -> dict:
    return {"Regel": C.RULES[r["rule"]], "Kandidaten": r["m"], "Wähler": r["n"], "Profile mit einem Manipulator": pct(r["profiles"]),
            "davon ohne Hilfe eines Gleichstands": pct(r["profiles_free"]), "Wähler, die allein manipulieren können (Mittel)": pct(r["voters"], 1)}


def verdict_rules(rows: list[dict]) -> tuple[str, str]:
    """Verdikt der Reihe 1: bei der kleinsten Kandidaten- und der größten Wählerzahl die am wenigsten und die am meisten manipulierbare Regel (Anteil der Profile)."""
    m = min(r["m"] for r in rows)
    n = max(r["n"] for r in rows if r["m"] == m)
    cell = [r for r in rows if r["m"] == m and r["n"] == n]
    lo, hi = min(cell, key=lambda r: r["profiles"]), max(cell, key=lambda r: r["profiles"])
    plur = next(r for r in cell if r["rule"] == "plurality")
    return "info", (f"Bei {m} Kandidaten und {n} Wählern kann in {pct(lo['profiles'])} der Zufallsprofile mindestens ein Wähler allein manipulieren, wenn nach {short_rule(lo['rule'])} gezählt wird, "
                    f"und in {pct(hi['profiles'])} bei {short_rule(hi['rule'])}. Bei der Mehrheitswahl gelingt es nur über einen Gleichstand ({pct(plur['profiles_free'])} ohne). "
                    "Eine Regel ohne jede Manipulierbarkeit gibt es mit drei oder mehr Kandidaten nur als Diktatur.")


def verdict_models(rows: list[dict]) -> tuple[str, str]:
    """Verdikt der Reihe 2: je Profilmodell die am meisten manipulierbare Regel (Anteil der Profile)."""
    parts = []
    for model in C.MODELS:
        cell = [r for r in rows if r["model"] == model]
        hi = max(cell, key=lambda r: r["profiles"])
        parts.append(f"{C.MODELS[model].split(' (')[0]}: {short_rule(hi['rule'])} ({pct(hi['profiles'])})")
    r0 = rows[0]
    return "info", f"Die am häufigsten manipulierbare Regel je Profilmodell ({r0['m']} Kandidaten, {r0['n']} Wähler, Anteil der Profile mit einem Manipulator): " + "; ".join(parts) + "."

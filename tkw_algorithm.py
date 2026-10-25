"""Kern: Profile erzeugen, fünf Wahlregeln auswerten und prüfen, ob ein einzelner Wähler durch eine falsche Rangfolge ein besseres Ergebnis erzwingen kann.

Ein Profil ist ein Feld (n, m) mit den Rangfolgen der n Wähler (Zeile = Wähler, Spalte = Rangplatz, Wert = Kandidat). Gleichstände entscheidet eine feste
Rangfolge der Kandidaten (`tiebreak`: kleinerer Wert = bevorzugt; bei der Sofortstichwahl scheidet unter mehreren Letzten der am wenigsten bevorzugte aus).

**Schnelle Prüfung:** alle Wähler mit derselben Rangfolge verhalten sich gleich. Ein Profil wird deshalb als Zählvektor über alle m! Rangfolgen geführt;
für jede vorkommende Rangfolge und jede der m! - 1 anderen Rangfolgen wird ein Wähler umgesetzt und der Sieger neu bestimmt. Die Prüfung auf Wählerebene
(`manipulators_voter_level`) rechnet dasselbe ohne diese Abkürzung und dient als Gegenprobe und für die Diktatur.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

RULE_NAMES = {
    "plurality": "Mehrheitswahl",
    "borda": "Borda-Zählung",
    "copeland": "Copeland (paarweise Siege)",
    "irv": "Sofortstichwahl (IRV)",
    "dictator": "Diktatur (ein Wähler entscheidet)",
}
COUNT_RULES = ("plurality", "borda", "copeland", "irv")      # Regeln, die nur von den Zählvektoren abhängen (anonym)
MALLOWS_PHI = 0.7
CAMP_SHARE = 0.55


# --- Profile ---------------------------------------------------------------------------------------------------------------------------------

def profile_random(n: int, m: int, rng: np.random.Generator) -> np.ndarray:
    """Zufall: jeder Wähler zieht eine der m! Rangfolgen mit gleicher Wahrscheinlichkeit."""
    return np.argsort(rng.random((n, m)), axis=1)


def profile_single_peaked(n: int, m: int, rng: np.random.Generator) -> np.ndarray:
    """Einspitzig: Kandidaten auf einer Achse, jeder Wähler reiht nach Abstand zu seinem Idealpunkt."""
    ideal = rng.random(n) * m - 0.5
    dist = np.abs(ideal[:, None] - np.arange(m)[None, :]) + 1e-9 * rng.random((n, m))
    return np.argsort(dist, axis=1)


def mallows_profile(n: int, base: list[int], phi: float, rng: np.random.Generator) -> np.ndarray:
    """n Ziehungen aus dem Mallows-Modell um `base` (wiederholtes Einfügen): Wahrscheinlichkeit einer Rangfolge ∝ phi^(Fehlstände gegenüber `base`)."""
    m = len(base)
    pos = np.zeros((n, m), dtype=int)
    for i in range(1, m):
        weights = phi ** (i - np.arange(i + 1))
        cum = np.cumsum(weights / weights.sum())
        j = np.minimum(np.searchsorted(cum, rng.random(n), side="right"), i)
        pos[:, :i] += (pos[:, :i] >= j[:, None])
        pos[:, i] = j
    out = np.empty((n, m), dtype=int)
    out[np.arange(n)[:, None], pos] = np.array(base)[None, :]
    return out


def profile_camps(n: int, m: int, rng: np.random.Generator, phi: float = MALLOWS_PHI, share: float = CAMP_SHARE) -> np.ndarray:
    """Zwei Lager: 55 % streuen um A > B > C …, 45 % um die umgekehrte Rangfolge."""
    n_a = int(round(share * n))
    arr = np.vstack([mallows_profile(n_a, list(range(m)), phi, rng), mallows_profile(n - n_a, list(range(m - 1, -1, -1)), phi, rng)])
    return arr[rng.permutation(n)]


PROFILE_MODELS = {"random": profile_random, "single": profile_single_peaked, "camps": profile_camps}


# --- Rangfolgen als Index --------------------------------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def all_rankings(m: int) -> np.ndarray:
    """Alle m! Rangfolgen als Feld (m!, m), lexikographisch."""
    return np.array(list(itertools.permutations(range(m))), dtype=int)


@lru_cache(maxsize=None)
def ranking_tables(m: int):
    """(Rangplatz je Kandidat (m!, m), before[i, a, b] = a steht in Rangfolge i vor b (m!, m, m), Index je Rangfolge als Dictionary)."""
    rk = all_rankings(m)
    pos = np.empty_like(rk)
    pos[np.arange(len(rk))[:, None], rk] = np.arange(m)[None, :]
    before = pos[:, :, None] < pos[:, None, :]
    index = {tuple(r): i for i, r in enumerate(rk.tolist())}
    return pos, before, index


def counts_of(profile: np.ndarray) -> np.ndarray:
    """Zählvektor über alle m! Rangfolgen."""
    m = profile.shape[1]
    _, _, index = ranking_tables(m)
    c = np.zeros(len(index), dtype=int)
    for row in profile.tolist():
        c[index[tuple(row)]] += 1
    return c


# --- Regeln auf Zählvektoren -----------------------------------------------------------------------------------------------------------------

def pick(scores: np.ndarray, tiebreak: np.ndarray) -> int:
    best = np.flatnonzero(scores == scores.max())
    return int(best[np.argmin(tiebreak[best])])


def copeland_scores(w: np.ndarray) -> np.ndarray:
    wins = (w > w.T).sum(axis=1).astype(float)
    ties = ((w == w.T).sum(axis=1) - 1) * 0.5
    return wins + ties


def winner_counts(rule: str, c: np.ndarray, m: int, tiebreak: np.ndarray) -> int:
    """Sieger einer anonymen Regel aus dem Zählvektor `c` (Länge m!)."""
    pos, before, _ = ranking_tables(m)
    rk = all_rankings(m)
    if rule == "plurality":
        return pick(np.bincount(rk[:, 0], weights=c, minlength=m), tiebreak)
    if rule == "borda":
        return pick(c @ (m - 1 - pos), tiebreak)
    if rule == "copeland":
        w = np.tensordot(c, before, axes=1).astype(int)
        np.fill_diagonal(w, 0)
        return pick(copeland_scores(w), tiebreak)
    if rule == "irv":
        alive = np.ones(m, dtype=bool)
        while alive.sum() > 1:
            first = np.argmin(np.where(alive[None, :], pos, m + 1), axis=1)
            counts = np.bincount(first, weights=c, minlength=m)
            cand = np.flatnonzero(alive)
            low = cand[counts[cand] == counts[cand].min()]
            alive[int(low[np.argmax(tiebreak[low])])] = False
        return int(np.flatnonzero(alive)[0])
    raise ValueError(f"unbekannte Regel: {rule}")


def winner_profile(rule: str, profile: np.ndarray, tiebreak: np.ndarray) -> int:
    """Sieger einer Regel aus dem Profil auf Wählerebene (die Diktatur: der erste Platz des Wählers 0)."""
    if rule == "dictator":
        return int(profile[0, 0])
    return winner_counts(rule, counts_of(profile), profile.shape[1], tiebreak)


# --- Manipulation ----------------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Manipulation:
    ranking: tuple        # wahre Rangfolge des Manipulators
    ballot: tuple         # angegebene (falsche) Rangfolge
    honest: int           # Sieger bei ehrlicher Stimmabgabe
    result: int           # Sieger mit der falschen Rangfolge
    gain: int             # Plätze besser in der wahren Rangfolge


def winners_for_all_ballots(rule: str, c: np.ndarray, i: int, m: int, tiebreak: np.ndarray) -> np.ndarray:
    """Sieger für ALLE Möglichkeiten, dass ein Wähler mit der Rangfolge i stattdessen die Rangfolge j angibt (j = 0 .. m! - 1), in einem Zug berechnet.
    Eintrag j = i ist der ehrliche Sieger. Dasselbe wie `winner_counts` mit c - e_i + e_j, nur für alle j gleichzeitig."""
    pos, before, _ = ranking_tables(m)
    rk = all_rankings(m)
    k = len(rk)
    if rule in ("plurality", "borda", "copeland"):
        if rule == "plurality":
            feat = np.eye(m)[rk[:, 0]]
            scores = np.bincount(rk[:, 0], weights=c, minlength=m)[None, :] - feat[i][None, :] + feat
        elif rule == "borda":
            feat = (m - 1 - pos).astype(float)
            scores = (c @ feat)[None, :] - feat[i][None, :] + feat
        else:
            w = np.tensordot(c, before, axes=1)[None, :, :] - before[i][None, :, :] + before
            wt = w.transpose(0, 2, 1)
            scores = (w > wt).sum(axis=2) + ((w == wt).sum(axis=2) - 1) * 0.5
        top = np.rint(2 * scores).astype(int)
        tied = (top == top.max(axis=1, keepdims=True)).sum(axis=1) > 1                          # Gleichstand an der Spitze
        return (top * (m + 1) - tiebreak[None, :]).argmax(axis=1), tied
    if rule == "irv":
        c2 = np.tile(c.astype(float), (k, 1))
        c2[:, i] -= 1
        c2[np.arange(k), np.arange(k)] += 1
        alive = np.ones((k, m), dtype=bool)
        tied = np.zeros(k, dtype=bool)
        cands = np.arange(m)
        for _ in range(m - 1):
            first = np.where(alive[:, None, :], pos[None, :, :], m + 1).argmin(axis=2)          # (j, q): erster lebender Kandidat der Rangfolge q
            counts = np.einsum("jq,jqm->jm", c2, (first[:, :, None] == cands[None, None, :]).astype(float))
            low = alive & (counts == np.where(alive, counts, np.inf).min(axis=1, keepdims=True))
            tied |= low.sum(axis=1) > 1                                                         # Gleichstand unter den Letzten in irgendeiner Runde
            out = np.where(low, tiebreak[None, :], -1).argmax(axis=1)                           # unter den Letzten der am wenigsten bevorzugte
            alive[np.arange(k), out] = False
        return alive.argmax(axis=1), tied
    raise ValueError(f"unbekannte Regel: {rule}")


@dataclass(frozen=True)
class ManipulationSummary:
    voters: int                        # Wähler, die allein manipulieren können (das Los eingerechnet)
    best: Manipulation | None          # Beispiel mit dem größten Gewinn
    voters_free: int                   # davon: Wähler, die es auch OHNE Hilfe eines Gleichstands können
    best_free: Manipulation | None


def manipulation_counts(rule: str, c: np.ndarray, m: int, tiebreak: np.ndarray) -> ManipulationSummary:
    """Für jede vorkommende Rangfolge: kann EIN Wähler mit ihr durch eine andere Rangfolge ein besseres Ergebnis erzwingen?

    „Ohne Gleichstand“ heißt: weder im ehrlichen noch im manipulierten Lauf kommt ein Gleichstand vor (Spitze bei den Punkteregeln, irgendeine Runde bei der
    Sofortstichwahl); das Ergebnis hängt dann nicht am Los."""
    pos, _, _ = ranking_tables(m)
    rk = all_rankings(m)
    base = winner_counts(rule, c, m, tiebreak)
    voters = voters_free = 0
    best: Manipulation | None = None
    best_free: Manipulation | None = None
    for i in np.flatnonzero(c > 0):
        winners, tied = winners_for_all_ballots(rule, c, int(i), m, tiebreak)
        gains = pos[i, base] - pos[i, winners]
        j = int(np.argmax(gains))
        if gains[j] > 0:
            voters += int(c[i])
            cand = Manipulation(tuple(rk[i].tolist()), tuple(rk[j].tolist()), base, int(winners[j]), int(gains[j]))
            if best is None or cand.gain > best.gain:
                best = cand
        free_gains = np.where(~tied & ~tied[i], gains, 0)                 # nur Wege, bei denen weder der ehrliche noch der manipulierte Lauf ein Gleichstand hat
        jf = int(np.argmax(free_gains))
        if free_gains[jf] > 0:
            voters_free += int(c[i])
            candf = Manipulation(tuple(rk[i].tolist()), tuple(rk[jf].tolist()), base, int(winners[jf]), int(free_gains[jf]))
            if best_free is None or candf.gain > best_free.gain:
                best_free = candf
    return ManipulationSummary(voters, best, voters_free, best_free)


def compositions(total: int, parts: int):
    """Alle Zerlegungen von `total` in `parts` nichtnegative ganze Zahlen (lexikographisch absteigend im ersten Teil)."""
    if parts == 1:
        yield (total,)
        return
    for first in range(total, -1, -1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def smallest_manipulable_profile(rule: str, m: int, tiebreak: np.ndarray, max_n: int = 7, tie_free: bool = False):
    """Kleinstes Profil (nach Wählerzahl, dann lexikographisch) einer anonymen Regel, in dem ein einzelner Wähler manipulieren kann: Aufzählung ALLER Profile.
    `tie_free`: nur Manipulationen, die ohne Gleichstand auskommen. Rückgabe: (n, Zählvektor, Manipulation) oder None, wenn bis max_n keines existiert."""
    k = len(all_rankings(m))
    for n in range(1, max_n + 1):
        for comp in compositions(n, k):
            c = np.array(comp, dtype=int)
            s = manipulation_counts(rule, c, m, tiebreak)
            if (s.voters_free if tie_free else s.voters) > 0:
                return n, c, (s.best_free if tie_free else s.best)
    return None


def manipulators_voter_level(rule: str, profile: np.ndarray, tiebreak: np.ndarray) -> int:
    """Gegenprobe ohne die Abkürzung über Zählvektoren: jeder Wähler probiert alle m! - 1 anderen Rangfolgen; Rückgabe: Zahl der Wähler, die allein manipulieren können."""
    n, m = profile.shape
    pos, _, _ = ranking_tables(m)
    rk = all_rankings(m)
    base = winner_profile(rule, profile, tiebreak)
    count = 0
    for v in range(n):
        true = profile[v]
        rank_of = np.empty(m, dtype=int)
        rank_of[true] = np.arange(m)
        won = False
        for alt in rk:
            if (alt == true).all():
                continue
            changed = profile.copy()
            changed[v] = alt
            if rank_of[winner_profile(rule, changed, tiebreak)] < rank_of[base]:
                won = True
                break
        count += won
    return count

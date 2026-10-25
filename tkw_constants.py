"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

MODELS = {
    "random": "Zufall (jeder Wähler ordnet beliebig)",
    "single": "einspitzig (Kandidaten auf einer Achse)",
    "camps": "zwei Lager (55 : 45, gegenläufig, mit Streuung)",
}
DEFAULT_MODEL = "random"
RULES = {
    "plurality": "Mehrheitswahl",
    "borda": "Borda-Zählung",
    "copeland": "Copeland (paarweise Siege)",
    "irv": "Sofortstichwahl (IRV)",
    "dictator": "Diktatur (ein Wähler entscheidet)",
}
DEFAULT_RULE = "plurality"

M_MIN, M_MAX, DEFAULT_M = 2, 5, 3             # bei zwei Kandidaten kann keine Regel manipuliert werden: der kleinste Fall gehört dazu
N_MIN, N_MAX, DEFAULT_N = 3, 101, 11          # Schritt 2: immer eine ungerade Zahl von Wählern
SEED_MAX, DEFAULT_SEED = 999999, 36

# Feste Messreihen (unabhängig von den Reglern): nie ein einzelner Seed als Befund
SERIES_SEED = 100000
SERIES_RUNS = 150
SERIES_MS = (3, 4)
SERIES_NS = (5, 11, 21, 51)
SERIES_MODEL_M, SERIES_MODEL_N = 4, 21

COLOR_PLURALITY = "#4c78a8"
COLOR_BORDA = "#e8a838"
COLOR_COPELAND = "#2F6B65"
COLOR_IRV = "#b04a3a"
COLOR_DICTATOR = "#8a8f98"
COLOR_ALERT = "#c0392b"
RULE_COLORS = {"plurality": COLOR_PLURALITY, "borda": COLOR_BORDA, "copeland": COLOR_COPELAND, "irv": COLOR_IRV, "dictator": COLOR_DICTATOR}
CANDIDATE_LABELS = "ABCDE"

PRESETS = {
    "Mehrheitswahl, drei Kandidaten": {"model": "random", "rule": "plurality", "m": 3, "n": 11, "seed": DEFAULT_SEED},
    "Borda: leicht zu überlisten": {"model": "random", "rule": "borda", "m": 4, "n": 21, "seed": 1},
    "Sofortstichwahl: hier unüberlistbar": {"model": "random", "rule": "irv", "m": 3, "n": 21, "seed": 1},
    "Zwei Lager: taktisches Wählen": {"model": "camps", "rule": "copeland", "m": 4, "n": 21, "seed": 20},
    "Einspitzig: Copeland fast sicher": {"model": "single", "rule": "copeland", "m": 4, "n": 21, "seed": 1},
    "Diktatur: nichts zu gewinnen": {"model": "random", "rule": "dictator", "m": 3, "n": 13, "seed": DEFAULT_SEED},
}
PRESET_HELP = {
    "Mehrheitswahl, drei Kandidaten": "Voreinstellung: 11 Wähler ordnen drei Kandidaten zufällig, gewählt wird nach den Erststimmen. Der Zufalls-Seed ist so gewählt, dass einzelne Wähler das Ergebnis drehen können; in Zufallsprofilen mit drei Kandidaten und 11 Wählern gelingt das in 28 % der Profile.",
    "Borda: leicht zu überlisten": "4 Kandidaten, 21 Wähler, Borda-Zählung: wer einen Rivalen seines Favoriten ganz nach hinten setzt, entzieht ihm Punkte. In diesem ausgesuchten Profil können 10 von 21 Wählern das Ergebnis allein zu ihren Gunsten drehen (im Mittel über Zufallsprofile sind es 9,4 % der Wähler).",
    "Sofortstichwahl: hier unüberlistbar": "3 Kandidaten, 21 Wähler, Sofortstichwahl: in diesem Profil kann kein Wähler allein etwas erreichen. Das ist typisch, aber nicht immer so: in 14,7 % der Zufallsprofile geht es doch (Messreihe unten).",
    "Zwei Lager: taktisches Wählen": "4 Kandidaten, zwei gegenläufige Lager, Copeland: einzelne Wähler können knappe Paarmehrheiten kippen, indem sie einen Rivalen nach hinten setzen. Ausgesuchtes Beispiel, in dem das 6 von 21 Wählern gelingt.",
    "Einspitzig: Copeland fast sicher": "4 Kandidaten auf einer Achse, 21 Wähler, Copeland: bei einspitzigen Profilen gewinnt der Kandidat beim mittleren Wähler, und kaum ein einzelner Wähler kann daran etwas ändern (0,7 % der Profile in der Messreihe unten). Hier kann es niemand.",
    "Diktatur: nichts zu gewinnen": "13 Wähler, 3 Kandidaten, der erste Wähler entscheidet allein. Niemand kann das Ergebnis zu seinen Gunsten drehen: der Diktator bekommt seinen ersten Platz, die anderen ändern nichts. Nach dem Satz von Gibbard und Satterthwaite ist das die einzige Regel mit mindestens drei möglichen Siegern, die nicht manipulierbar ist (aus dem Gedächtnis).",
}

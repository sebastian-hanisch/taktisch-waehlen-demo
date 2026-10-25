"""Einmalige Messung der README-Zahlen (nicht Teil der App): feste Pläne, Ausgabe auf stdout."""

import sys
import time

sys.path.insert(0, ".")
import tkw_constants as C
import tkw_evaluation as ev

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

t0 = time.time()
print("PRESETS")
for name, p in C.PRESETS.items():
    a = ev.analyse(ev.Settings(**p))
    r = a.selected
    print(name, "ehrlicher Sieger", ev.label(r.winner), "Wähler", r.voters, "von", p["n"], "ohne Gleichstand", r.voters_free, "Gewinn", None if r.best is None else r.best.gain)

print("KLEINSTE GEGENBEISPIELE (drei Kandidaten, bis 9 Wähler)")
for r in ev.smallest_examples():
    print("  mit Los:", r)
for r in ev.smallest_examples(tie_free=True):
    print("  ohne Gleichstand:", r)

print("REIHE 1 (Zufallsprofile, je Zelle", C.SERIES_RUNS, "Profile): Anteil der Profile mit Manipulator / davon ohne Gleichstand / Wähler im Mittel")
for r in ev.series_rules():
    print(r["rule"], "m", r["m"], "n", r["n"], round(100 * r["profiles"], 1), round(100 * r["profiles_free"], 1), "|", round(100 * r["voters"], 1), round(100 * r["voters_free"], 1))

print("REIHE 2 (m =", C.SERIES_MODEL_M, ", n =", C.SERIES_MODEL_N, ")")
for r in ev.series_models():
    print(r["model"], r["rule"], round(100 * r["profiles"], 1), round(100 * r["profiles_free"], 1), "|", round(100 * r["voters"], 1), round(100 * r["voters_free"], 1))
print("sec", round(time.time() - t0, 1))

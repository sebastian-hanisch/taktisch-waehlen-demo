# Taktisch wählen: wer kann eine Wahl allein zu seinen Gunsten drehen? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-taktisch-waehlen-demo.streamlit.app/)** -->

Stück der Linie **Abstimmen und Fair Teilen** (Konzepte-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“), Nachfolger von [wahlregeln-demo](https://github.com/sebastian-hanisch/wahlregeln-demo) (vier Regeln auf denselben Profilen). Dort wählt jeder Wähler ehrlich;
hier fragt die Demo: **Kann ein einzelner Wähler durch eine falsche Rangfolge ein besseres Ergebnis erzwingen, wie oft, und wie viel hängt dabei am Gleichstand?** Geprüft werden **Mehrheitswahl, Borda, Copeland und Sofortstichwahl**, dazu die **Diktatur** als Gegenprobe (der Satz von Gibbard und Satterthwaite sagt, dass bei mindestens drei möglichen Siegern und unbeschränkten Präferenzen nur eine Diktatur nicht manipulierbar ist).

Der Kern ist eigener Code (`numpy`): Profile, fünf Regeln, die Prüfung „jeder Wähler gegen jede der m! Rangfolgen“ in einer schnellen Fassung über Zählvektoren und einer langsamen Gegenprobe auf Wählerebene.

## Warum dieses Problem

Eine Wahlregel ist nur dann „fair“, wenn ehrliches Abstimmen sich lohnt. Wo es das nicht tut, hängt das Ergebnis davon ab, wer die anderen Stimmen kennt. Die Demo misst, **wie weit das bei vier üblichen Regeln geht**, und deckt dabei eine Feinheit auf:
**Viele Manipulationen leben vom Gleichstand.** Bei der Mehrheitswahl gelingt eine Manipulation durch einen einzelnen Wähler **nie ohne Gleichstand** (ein Satz, hier bewiesen und getestet); bei Borda und Copeland gelingt sie mit drei Kandidaten in keiner Stichprobe ohne Gleichstand, bei der Sofortstichwahl schon.

## Modell

**Manipulation.** Wähler *v* kann manipulieren, wenn es eine Rangfolge gibt, mit der die Regel einen Kandidaten wählt, den *vs* wahre Rangfolge höher reiht als den ehrlichen Sieger; alle anderen bleiben ehrlich, *v* kennt alle anderen Stimmen. Der **Gewinn** sind die Plätze, die der neue Sieger in *vs* wahrer Rangfolge besser liegt.
**Ohne Hilfe eines Gleichstands:** weder im ehrlichen noch im manipulierten Lauf kommt ein Gleichstand vor (an der Spitze bei den Punkteregeln, in irgendeiner Runde bei der Sofortstichwahl); das Ergebnis hängt dann nicht am Los. Die Definition ist **streng**: sie zählt jeden Gleichstand, auch einen, der das Ergebnis nicht entschieden hätte.
**Gleichstand.** Ein Zufallslos aus dem Zufalls-Seed legt vorab eine Rangfolge der Kandidaten fest; bei der Sofortstichwahl scheidet unter mehreren Letzten der am wenigsten bevorzugte aus.
**Regeln und Profilmodelle** wie in `wahlregeln-demo`: Mehrheitswahl, Borda, Copeland, Sofortstichwahl; Profile Zufall (jede Rangfolge gleich wahrscheinlich), einspitzig (Kandidaten auf einer Achse), zwei Lager (55 : 45, gegenläufig, Mallows mit φ = 0,7). **Diktatur:** Wähler 1 entscheidet allein.
Formeln, der Satz zur Mehrheitswahl und die Lesehilfe stehen im 📐-Expander der App.

## Methodik

- **Kern** (`tkw_algorithm.py`): Profile erzeugen, Rangfolgen als Index, die Regeln auf Zählvektoren über alle m! Rangfolgen (alle Wähler mit derselben Rangfolge verhalten sich gleich), die Prüfung für **alle** Abweichungen in einem Zug (`winners_for_all_ballots`), die Gegenprobe auf Wählerebene, das kleinste Gegenbeispiel durch Aufzählung aller Profile.
- **Szenario und Auswertung** (`tkw_scenario.py`, `tkw_evaluation.py`): Profil und Gleichstandslos aus (Modell, m, n, Zufalls-Seed), Analyse aller fünf Regeln je Einstellung, zwei Messreihen mit festem Programm, alle Verdikte als reine Funktionen.
- **Oberfläche** (`app.py`): sechs Schnellstart-Szenarien, Regler für Profilmodell, Regel, Kandidaten, Wähler und Zufalls-Seed, Tabelle aller fünf Regeln, Beispiel mit der besten Manipulation, kleinste Gegenbeispiele, zwei Messreihen auf Klick, Annahmen und Formeln.
- **Messreihen:** je Zelle 150 Profile mit den Zufalls-Seeds 100000 bis 100149; Reihe 1: Zufallsprofile, 3 und 4 Kandidaten, 5, 11, 21, 51 Wähler; Reihe 2: alle drei Profilmodelle bei 4 Kandidaten und 21 Wählern.

## Befunde (gemessen, keine Behauptungen)

Alle Reihen mit festen Zufalls-Seeds, je Zelle 150 Profile (die Standardabweichung eines Anteils liegt bei höchstens 4 Prozentpunkten). Die Schnellstart-Szenarien sind Einzelprofile, **von Hand ausgesucht** (siehe unten). **Die Zufallszahlen eines `numpy`-Generators sind nicht über Versionen stabil**: die Tests prüfen deshalb Bänder um diese Zahlen. Nullen und Sätze stehen ohne Band.

| Frage | Befund | Test |
|---|---|---|
| Stimmt der Kern? | Die Regeln gleich einer Neuimplementierung mit Schleifen (240 Profile, drei Modelle); die schnelle Prüfung gleich der naiven Suche auf Wählerebene (jeder Wähler gegen alle m! − 1 Rangfolgen, mit der naiven Auswertung) für jede Regel bei m = 3 und 4, **sowohl in der Zahl der Manipulatoren als auch in der Zahl ohne Gleichstand**; jede gemeldete Manipulation wird nachgespielt; die Wahl des kleinsten Gegenbeispiels gleich einer naiven Aufzählung. | `tests/test_oracle_taktisch_waehlen.py` |
| Wie oft gelingt es mit dem Los? | Zufallsprofile: bei 3 Kandidaten und 11 Wählern gibt es in **28,0 %** der Profile einen Manipulator bei der Mehrheitswahl, 23,3 % bei Borda, 14,0 % bei Copeland, 12,0 % bei der Sofortstichwahl. Bei 4 Kandidaten und 5 Wählern **52,7 % bei Borda** und 34,0 % bei der Mehrheitswahl. Ab etwa 11 Wählern sinkt der Anteil mit der Wählerzahl (Mehrheitswahl, 4 Kandidaten: **40,0 %** bei 11, **19,3 %** bei 51); von 5 auf 11 Wähler steigt er noch (34,0 auf 40,0 %). Die Zahlen sind Schätzungen aus 150 Profilen (etwa ±4 Punkte). | `test_claims.py::test_with_the_tie_break_every_rule_can_be_manipulated_in_a_tenth_to_half_of_the_random_profiles`, `::test_the_shares_of_manipulable_profiles_fall_with_the_number_of_voters_for_four_candidates` |
| Wie viele Wähler können es? | Im Mittel nur wenige: bei 3 Kandidaten und 51 Wählern **2,6 %** der Wähler bei der Mehrheitswahl, bei 4 Kandidaten und 5 Wählern 19,6 % bei Borda (der größte Wert der Reihe); überall unter 25 %. | `test_claims.py::test_few_voters_manipulate_on_average` |
| **Geht es ohne Gleichstand?** | **Mehrheitswahl: nie** (in keiner Zelle beider Reihen, und als Satz gezeigt: eine Stimme ändert zwei Erststimmenzahlen um eins, ein neuer Sieger braucht dann vorher oder nachher einen Gleichstand). **Borda und Copeland mit 3 Kandidaten: nie** (in allen vier Wählerzahlen, je 150 Profile; eine Stichprobe, kein Satz). **Borda mit 4 Kandidaten: ja**, in 10,0 bis 26,0 % der Profile. **Copeland mit 4 Kandidaten: nie** (Stichprobe). **Sofortstichwahl: ja, schon mit 3 Kandidaten**, in 2,7 bis 10,0 % der Profile. | `test_claims.py::test_plurality_is_never_manipulable_without_a_tie`, `::test_with_three_candidates_borda_and_copeland_need_a_tie_in_these_samples`, `::test_with_four_candidates_borda_has_manipulations_without_a_tie_and_copeland_still_has_none`, `::test_the_sofortstichwahl_has_manipulations_without_a_tie_already_with_three_candidates` |
| Was ändert das Profilmodell? | 4 Kandidaten, 21 Wähler: bei **einspitzigen** Profilen ist Copeland fast sicher (**0,7 %** der Profile; der Condorcet-Sieger ist der Kandidat beim mittleren Wähler), die Sofortstichwahl (**34,7 %**, davon 10,0 % ohne Gleichstand) und die Mehrheitswahl (31,3 %) gehören zu den leicht zu überlistenden, die Unterschiede zwischen diesen Regeln liegen innerhalb der Streuung; bei zwei Lagern Mehrheitswahl 36,7 % und Borda 33,3 %. | `test_claims.py::test_four_candidates_21_voters_by_profile_model` |
| Gibt es eine nicht manipulierbare Regel? | Die **Diktatur**: bei jeder geprüften Kandidatenzahl (3, 4, 5) und jedem Profil null Manipulatoren; bei **zwei Kandidaten** keine Regel (alle vier und die Diktatur). | `test_claims.py::test_the_dictator_rule_has_no_manipulator_for_any_candidate_count`, `tests/test_algorithm.py::test_with_two_candidates_nothing_can_be_manipulated` |
| Wie klein kann ein Gegenbeispiel sein? | Aufzählung aller Profile mit 3 Kandidaten: **mit dem Los** genügen **2 Wähler** bei allen vier Regeln. **Ohne Gleichstand** gibt es bei Mehrheitswahl, Borda und Copeland bis 9 Wähler **keines**; bei der Sofortstichwahl genügen **5 Wähler**: 2 × A > B > C, 1 × B > A > C, 2 × C > B > A, ein Wähler mit C > B > A gibt B > A > C an, dann gewinnt B statt A. | `test_claims.py::test_the_smallest_examples`, `tests/test_algorithm.py::test_smallest_examples_by_hand` |
| Schnellstart-Szenarien | Mehrheitswahl, 11 Wähler, Zufalls-Seed 36: 3 von 11 Wählern können es, keiner ohne Gleichstand. Borda, 4 Kandidaten, 21 Wähler, Zufalls-Seed 1: **10 von 21** (davon 6 ohne Gleichstand), Gewinn 2 Plätze. Sofortstichwahl, 3 Kandidaten, 21 Wähler, Zufalls-Seed 1: niemand. Zwei Lager, Copeland, Zufalls-Seed 20: 6 von 21, alle nur über den Gleichstand. Einspitzig, Copeland: niemand. Diktatur: niemand. | `test_claims.py::test_the_presets_tell_the_stories_in_their_help_texts` |

## Ehrliche Grenzen

- **Obere Schranke.** Der Manipulator kennt alle anderen Stimmen genau. Wer nur Umfragen kennt, erreicht nicht mehr; die Zahlen hier sind das, was unter besten Bedingungen für einen Einzelnen möglich ist.
- **Ein Wähler allein.** Gruppen können mehr; das ist nicht gemessen. Auch Absprachen, Wahlenthaltung und der Kauf von Stimmen kommen nicht vor.
- **Das Los ist Teil der Regel.** Ohne eine feste Gleichstandsregel ist das Ergebnis nicht festgelegt; mit ihr gelten Gibbard und Satterthwaite. Eine andere Regel (ein neuer Zufall je Lauf, die Stimme des Vorsitzenden) ändert, welche Manipulationen gelingen. Deshalb steht in jeder Tabelle, was **ohne** Gleichstand geht.
- **„Ohne Hilfe eines Gleichstands“ ist streng.** Jeder Gleichstand an der Spitze (oder in irgendeiner Runde der Sofortstichwahl) macht eine Manipulation zu einer Manipulation „mit Los“, auch wenn der Gleichstand das Ergebnis nicht entschieden hätte. Die Zahlen ohne Gleichstand sind deshalb eher zu klein als zu groß.
- **„Nie“ heißt in einer Stichprobe.** Für die Mehrheitswahl gilt es als Satz; Borda und Copeland mit drei Kandidaten und Copeland mit vier sind Stichproben (je 150 Profile in vier Wählerzahlen); ein größeres Profil, mehr Wähler oder mehr Kandidaten kann eine finden. Die kleinsten Gegenbeispiele gelten bis 9 Wähler und 3 Kandidaten.
- **Profile sind Modelle, Schnellstart-Szenarien sind ausgesucht.** Die Zufalls-Seeds sind so gewählt, dass die Beispiele ihre Geschichte zeigen; die Häufigkeiten stehen in den Messreihen.
- **Der Satz zur Mehrheitswahl ist hier hergeleitet** (Beweisskizze im 📐-Expander), nicht aus einer Quelle übernommen; der Test über 300 Profile stützt ihn nur, beweist ihn nicht. **Gibbard und Satterthwaite sowie die Literatur** (Bartholdi, Tovey, Trick; Conitzer und Walsh im *Handbook of Computational Social Choice*, 2016) aus dem Gedächtnis beziehungsweise nach einer Websuche (Abstracts), nicht im Original geprüft.

## Befunde und Korrekturen gegenüber dem Plan

- **Port:** 9190 (9188 und 9189 sind vergeben).
- **Neu gegenüber der Vormessung:** die Vormessung S2 zählte nur „kann es einen Wähler geben“ mit dem Los und fand IRV und Copeland am wenigsten, Borda am meisten manipulierbar (bis 52,5 %). Das gilt **mit dem Los**; ohne Gleichstand ändert sich das Bild stark (Copeland bis 4 Kandidaten nie in den Stichproben, ab 5 Kandidaten schon in 6 bis 8 % der Zufallsprofile; Borda erst ab vier Kandidaten, IRV schon mit drei). Die Trennung „mit und ohne Gleichstand“ ist der eigentliche Fund dieser Demo.
- **Zahlen der Vormessung** (400 Profile je Zelle, Zufall): Mehrheitswahl 27,8 %, Borda 24,2 %, Copeland 14,2 %, IRV 11,8 % bei 3 Kandidaten und 11 Wählern; die App rechnet 150 Profile je Zelle und kommt auf 28,0 / 23,3 / 14,0 / 12,0 %, innerhalb der Schwankung.
- **Fünfte Regel:** die Diktatur steht als Gegenprobe in der Tabelle; im Plan war sie nur ein Satz.
- **Reglerspanne:** Kandidaten 2 bis 5, damit die Voreinstellung (3) nicht auf dem Rand liegt; Wähler 3 bis 101 in Zweierschritten.
- **Schnelle Prüfung statt Schleife über alle Wähler:** der Plan nannte „alle m! Alternativlisten je Wähler“ (Vormessung: 400 Profile je Zelle, minutenlang); die App prüft stattdessen jede **vorkommende Rangfolge** gegen alle anderen in einem Zug (150 Profile je Zelle, wenige Sekunden). Die langsame Fassung auf Wählerebene bleibt als Gegenprobe (Diktatur und Tests).

## Verifikation

- **Kern:** jede Einheit an Mini-Profilen von Hand (Tabellen der Rangfolgen, Sieger der vier Regeln, die Mehrheitswahl mit beiden Gleichstandslosen: 2 von 7 Wählern können nur mit „B vor A“ manipulieren, keiner mit „A vor B“), Randfälle (zwei Kandidaten, lauter gleiche Wähler, kleinste und größte Reglerwerte für jedes Modell und jede Regel, ungültige Eingaben).
- **Orakel:** Neuimplementierung der Regeln samt Gleichstandsmarke mit Schleifen, naive Suche auf Wählerebene gegen die schnelle Prüfung (mit und ohne Gleichstand), Nachspielen jeder gemeldeten Manipulation, der Satz zur Mehrheitswahl auf 300 Profilen, die Diktatur, die Wahl des kleinsten Gegenbeispiels gegen eine naive Aufzählung.
- **Verdikte:** reine Funktionen, jeder Zweig (Manipulation vom Gleichstand abhängig, ohne Gleichstand möglich, niemand kann, zwei Kandidaten, Diktatur) und jede Zahl im Text an handgesetzten Profilen (`tests/test_verdicts.py`).
- **Presets, Layout, Oberfläche:** wie in allen Demos (Presets vollständig und im Regelbereich und auf dem Raster der Regler, keines auf einem Reglerrand, kein Preset entsteht durch Änderung eines einzigen Reglers, Schnellstart oben, aktives Preset hervorgehoben, AppTest jeder Button und jeder Regler an den Rändern); die Presets erzählen ihre Geschichte im Test.
- **Mutationsprüfung** (`tools/mutate_demo.py`): 119 Stellen im Kern `tkw_algorithm.py`, **81 gefangen** (18 davon über wortgleiche Zeilen in Nachbar-Demos), **20 als äquivalent festgehalten**, keine Zeitüberschreitung. Der erste Lauf ließ 25 überleben; fünf davon waren **echte Lücken** und haben Tests bekommen: die Auswahl des Beispiels bei gleichem Gewinn (jetzt: erste Rangfolge mit dem größten Gewinn, `test_the_reported_example_is_the_first_one_with_the_largest_gain`), die Grenzen der Suche nach dem kleinsten Gegenbeispiel (`test_smallest_example_search_respects_its_bounds`) und das Überspringen der eigenen Rangfolge auf Wählerebene (ein Borda-Profil, in dem nur eine Rangfolge ohne gemeinsame Stelle hilft). Die 20 äquivalenten Stellen sind Abwandlungen, die jede Punktzahl um dieselbe Konstante verschieben (Borda-Punkte `m - 1 - Rangplatz` mit anderer Konstante, Copeland-Gleichstandspunkte), die Schlüssel des Gleichstands um denselben Faktor strecken (`m + 1` gegen `m` oder `m + 2`, `2 · Punkte` gegen `3 · Punkte`), den Wert für ausgeschiedene Kandidaten in der Sofortstichwahl ändern (`m + 1` gegen `m`, `m + 2`, `m - 1`: unter den Lebenden gibt es immer mindestens zwei, der bessere liegt höchstens auf Platz m − 2) und die Suche bei 0 oder 2 statt bei 1 Wähler beginnen lassen (ein einzelner Wähler bekommt immer seinen ersten Platz).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `tkw_algorithm.py` | Kern: Profile, Regeln, Prüfung auf Manipulierbarkeit |
| `tkw_constants.py` | Regler-Grenzen, feste Pläne, Farben, Presets |
| `tkw_evaluation.py` | Analyse, Messreihen, Verdikte, Tabellen |
| `tkw_layout.py` | Fester Kopf (Stylesheet) |
| `tkw_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `tkw_scenario.py` | Profil und Gleichstandslos aus (Modell, m, n, Zufalls-Seed) |
| `tkw_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `messen.py` | Einmalige Messung der Zahlen in dieser README (nicht Teil der App) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Profile, Kern, Orakel, Verdikte, Randfälle, Presets, Abbildungen, Layout, AppTest, Footer, Laufzeit-Importe, Claims |

## Bewusst nicht umgesetzt

- **Absprachen mehrerer Wähler** (Koalitionen) und **unvollständige Information** (Umfragen): würden die Zahlen anders machen; hier gilt die obere Schranke eines Einzelnen.
- **Andere Gleichstandsregeln** (neuer Zufall je Lauf, Vorsitzender): die feste Rangfolge ist die einfachste Wahl, die Gibbard und Satterthwaite anwendbar macht.
- **Rechenaufwand der Manipulation** (Bartholdi, Tovey, Trick): die Aufzählung aller m! Rangfolgen genügt bei m ≤ 5; ob Manipulation bei vielen Kandidaten rechenschwer ist, wird nicht gemessen.
- **Echte Wahldaten:** nur synthetische Profile (Datenschutz, Positionierung).

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).

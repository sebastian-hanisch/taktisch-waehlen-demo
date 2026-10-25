"""Taktisch wählen: wer kann eine Wahl allein zu seinen Gunsten drehen? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück der Linie „Abstimmen und Fair Teilen“: kann ein einzelner Wähler durch eine falsche Rangfolge ein besseres Ergebnis erzwingen (Gibbard–Satterthwaite)?
Vier Regeln und die Diktatur als Gegenprobe, drei Profilmodelle; ein Manipulator kennt alle anderen Stimmen. Der Kern liegt in tkw_algorithm.py.

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import tkw_constants as C
import tkw_evaluation as ev
from tkw_evaluation import Settings, analyse, num, pct, rule_rows, rules_row, verdict_models, verdict_rules, verdict_state
from tkw_layout import dunkles_design, kopf_css
from tkw_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from tkw_visualization import build_models, build_series, build_voters

st.set_page_config(page_title="Taktisch wählen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _series_rules():
    return ev.series_rules()


@st.cache_data(show_spinner=False)
def _series_models():
    return ev.series_models()


@st.cache_data(show_spinner=False)
def _examples(tie_free):
    return ev.smallest_examples(tie_free=tie_free)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in tkw_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🎭 Taktisch wählen: wer kann eine Wahl allein zu seinen Gunsten drehen?")
st.markdown(
    """
Jeder Wähler gibt eine Rangfolge ab, und eine **Regel** macht daraus einen Sieger. Ehrlich ist das nicht immer klug: wer weiß, wie die anderen abstimmen, kann manchmal mit einer **falschen Rangfolge** ein Ergebnis erzwingen, das er für besser hält als das ehrliche.
Die Demo prüft für **jeden einzelnen Wähler** und **jede der möglichen Rangfolgen**, ob das gelingt, bei vier Regeln (**Mehrheitswahl**, **Borda**, **Copeland**, **Sofortstichwahl**) und bei einer **Diktatur** als Gegenprobe.
Sie zeigt, **wie oft** es gelingt, **wie viel** es bringt und **wie sehr es am Gleichstand hängt**: bei einem Gleichstand entscheidet ein festes Los, und manche Regeln lassen sich nur dort überlisten.
Ein Wähler allein, volle Kenntnis der anderen Stimmen; Absprachen mehrerer Wähler kommen nicht vor.

Weiter unten: der Abschnitt **🔬 Messreihen**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So prüft die Demo, ob jemand überlisten kann", expanded=True):
    st.markdown(
        """
1. **Ehrlicher Lauf:** alle geben ihre wahre Rangfolge an; die gewählte Regel bestimmt den Sieger.
2. **Ein Wähler weicht ab:** er gibt eine andere der m! Rangfolgen an (alle anderen bleiben ehrlich). Wählt die Regel nun einen Kandidaten, den **seine wahre Rangfolge höher reiht** als den ehrlichen Sieger, hat er manipuliert; der **Gewinn** sind die Plätze, die der neue Sieger in seiner wahren Rangfolge besser liegt.
3. **Ohne Hilfe eines Gleichstands:** die Manipulation zählt hier gesondert, wenn **weder im ehrlichen noch im manipulierten Lauf** ein Gleichstand vorkommt (an der Spitze bei den Punkteregeln, in irgendeiner Runde bei der Sofortstichwahl). Dann hängt das Ergebnis nicht am Los.
4. **Gleichstand:** ein festes Zufallslos (aus dem Zufalls-Seed) legt vorab eine Rangfolge der Kandidaten fest.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    model = st.selectbox("Profilmodell", list(C.MODELS), format_func=C.MODELS.get, key="model_select",
                         help="Wie die Wähler ihre Rangfolgen bilden. Zufall: jede Rangfolge gleich wahrscheinlich. Einspitzig: Kandidaten auf einer Achse, jeder Wähler reiht nach Abstand zu seinem Idealpunkt. Zwei Lager: 55 % streuen um eine Rangfolge, 45 % um die umgekehrte.")
    rule = st.selectbox("Regel", list(C.RULES), format_func=C.RULES.get, key="rule_select",
                        help="Die Regel, die im Beispiel und im Urteil unten gezeigt wird; die Tabelle zeigt immer alle fünf. Bei der Diktatur entscheidet Wähler 1 allein.")
    m = st.slider("Kandidaten", *bounds("m_slider"), key="m_slider", help="Wie viele Kandidaten zur Wahl stehen.")
    n = st.slider("Wähler", *bounds("n_slider"), key="n_slider", step=2, help="Immer eine ungerade Zahl: zwischen zwei Kandidaten gibt es dann keinen Gleichstand.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neues Profil ziehen", width="stretch", on_click=randomize_seed)

sync_query_params({"model_select": model, "rule_select": rule, "m_slider": int(m), "n_slider": int(n), "seed_input": int(seed)})

settings = Settings(model=model, rule=rule, m=int(m), n=int(n), seed=int(seed))
with st.spinner("Prüfe jeden Wähler gegen jede mögliche falsche Rangfolge …"):
    a = _analysis(settings)
sel = a.selected

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Ehrlicher Sieger", ev.label(sel.winner), delta=f"bei {ev.short_rule(settings.rule)}", delta_color="off")
m2.metric("Manipulieren können", f"{sel.voters} von {settings.n}", delta=pct(sel.voters / settings.n) + " der Wähler", delta_color="off")
m3.metric("davon ohne Hilfe eines Gleichstands", f"{sel.voters_free} von {settings.n}", delta="das Ergebnis hängt nicht am Los" if sel.voters_free else "wenn überhaupt, nur über den Gleichstand", delta_color="off")
m4.metric("Größter Gewinn", "–" if sel.best is None else ev.places(sel.best.gain), delta="in der wahren Rangfolge des Manipulators", delta_color="off")
st.table(rule_rows(a))
st.plotly_chart(build_voters(a), width="stretch", key="main_voters")
st.caption("Anteil der Wähler dieses Profils, die allein manipulieren können, je Regel; die gewählte Regel ist farbig. Die Diktatur wird auf Wählerebene geprüft (alle n × (m! − 1) Abweichungen), die anderen Regeln über die Zählvektoren der Rangfolgen; beides gibt dasselbe, das prüfen die Tests.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Kann ein einzelner Wähler das Ergebnis zu seinen Gunsten drehen?")
kind, text = verdict_state(a)
getattr(st, kind)(text)

with st.expander("Das kleinste Gegenbeispiel je Regel (drei Kandidaten)"):
    st.markdown("**Mit Los:** das kleinste Profil (Aufzählung aller Profile bis 9 Wähler, Gleichstand A vor B vor C), in dem ein einzelner Wähler manipulieren kann.")
    st.table(_examples(False))
    st.markdown("**Ohne Hilfe eines Gleichstands:** dasselbe, aber nur Manipulationen, die weder im ehrlichen noch im manipulierten Lauf einen Gleichstand brauchen.")
    st.table(_examples(True))
    st.caption("„Keines gefunden“ heißt: unter allen Profilen bis 9 Wähler mit drei Kandidaten gibt es keines; für die Mehrheitswahl ist das ein Satz (siehe 📐 unten), für die anderen eine Aufzählung bis zu dieser Größe.")

st.markdown("---")

# --- Messreihen ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Messreihen: wie oft gelingt es?")
st.caption(f"Feste Programme, unabhängig von den Reglern: je Zelle {C.SERIES_RUNS} Profile mit den Zufalls-Seeds {C.SERIES_SEED} bis {C.SERIES_SEED + C.SERIES_RUNS - 1}. Jede Reihe rechnet auf Klick in einigen Sekunden.")
tab1, tab2 = st.tabs(["Regeln und Wählerzahl", "Profilmodelle"])
with tab1:
    st.markdown("**Zufallsprofile.** Anteil der Profile, in denen mindestens ein Wähler allein manipulieren kann, nach Regel, Kandidaten- und Wählerzahl. Die gepunktete Linie bei 0 ist die Diktatur.")
    if st.button("Reihe rechnen", key="rules_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe (einige Sekunden) …"):
            _series_rules()
        st.session_state["rules_done"] = time.perf_counter() - t0
    if "rules_done" in st.session_state:
        rows = _series_rules()
        c1, c2 = st.columns(2)
        for col, mm in zip((c1, c2), C.SERIES_MS):
            col.markdown(f"**{mm} Kandidaten**")
            col.plotly_chart(build_series(rows, mm), width="stretch", key=f"rules_chart_{mm}")
        st.table([rules_row(r) for r in rows if r["n"] == max(x["n"] for x in rows)])
        kind, text = verdict_rules(rows)
        getattr(st, kind)(text)
        st.caption(f"Die Tabelle zeigt die größte Wählerzahl. Rechenzeit dieser Sitzung: {num(st.session_state['rules_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")
with tab2:
    st.markdown(f"**Wie hängt es vom Profilmodell ab?** {C.SERIES_MODEL_M} Kandidaten, {C.SERIES_MODEL_N} Wähler, Anteil der Profile mit einem Manipulator.")
    if st.button("Reihe rechnen", key="models_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe (einige Sekunden) …"):
            _series_models()
        st.session_state["models_done"] = time.perf_counter() - t0
    if "models_done" in st.session_state:
        rows = _series_models()
        st.plotly_chart(build_models(rows), width="stretch", key="models_chart")
        st.table([{"Profilmodell": C.MODELS[r["model"]], "Regel": C.RULES[r["rule"]], "Profile mit einem Manipulator": pct(r["profiles"]), "davon ohne Hilfe eines Gleichstands": pct(r["profiles_free"]),
                   "Wähler, die allein manipulieren können (Mittel)": pct(r["voters"], 1)} for r in rows])
        kind, text = verdict_models(rows)
        getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Der Manipulator kennt alle anderen Stimmen** | Im Alltag kennt man nur Umfragen; unter Unsicherheit ist das taktische Wählen riskanter und seltener erfolgreich. Die Zahlen hier sind eine **Obergrenze** für das, was ein einzelner Wähler erreichen könnte. | diese Demo (Annahme) |
| **Ein Wähler allein, keine Absprachen** | Gruppen können mehr erreichen als ein Einzelner. Das wird hier nicht gemessen. | – |
| **Das Los entscheidet jeden Gleichstand gleich** | Eine andere Gleichstandsregel (zum Beispiel ein neuer Zufall je Lauf, die Stimme des Vorsitzenden) ändert, welche Manipulationen gelingen. Deshalb steht immer dabei, was ohne Gleichstand geht. | diese Demo (Spalte „ohne Hilfe eines Gleichstands“) |
| **Die Profile sind Modelle** | Die Anteile hängen vom Profilmodell ab (drei Modelle, Messreihe 2). Echte Präferenzen liegen dazwischen. | diese Demo |
| **Vollständige Rangfolgen, ein Sieger** | Mehrere Sieger, offene Plätze oder Gleichstände in den Rangfolgen ändern die Regeln und den Satz von Gibbard und Satterthwaite. | – |
| **Der Rechenaufwand ist kein Schutz** | Daraus, dass Manipulation im ungünstigsten Fall rechenschwer sein kann, folgt nicht, dass sie im Durchschnitt schwer ist; hier genügt die Aufzählung aller m! Rangfolgen. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Profil.** $n$ Wähler, $m$ Kandidaten; $R_v$ ist die wahre strikte Rangfolge von Wähler $v$, $f$ die Regel (ein Sieger, Gleichstand per festem Los). Wähler $v$ **kann manipulieren**, wenn es eine Rangfolge $R'$ gibt, sodass
$f(R', R_{-v})$ in $R_v$ besser liegt als $f(R_v, R_{-v})$. Der **Gewinn** ist der Unterschied der Rangplätze in $R_v$.

**Abkürzung.** Alle Wähler mit derselben Rangfolge verhalten sich gleich; die Prüfung läuft deshalb über die Zählvektoren der $m!$ Rangfolgen: für jede vorkommende Rangfolge $i$ und jede andere Rangfolge $j$ wird $c - e_i + e_j$ ausgewertet.

**Mehrheitswahl und Gleichstand (Satz).** Gibt ein Wähler statt seines ersten Platzes $t$ den Kandidaten $y$ an, ändern sich genau zwei Erststimmenzahlen um je eins. Ein neuer Sieger $y$ setzt $P(y) + 1 \ge P(W)$ voraus, der alte Sieger $W$ hatte aber $P(W) \ge P(y)$ (und $W \ne t$, sonst gäbe es nichts zu gewinnen):
also ist $P(W) \in \{P(y), P(y) + 1\}$, und in beiden Fällen herrscht vorher oder nachher ein **Gleichstand** zwischen $W$ und $y$. Kein anderer Kandidat kann gewinnen, ohne dass er schon vorher hätte gewinnen müssen. **Die Mehrheitswahl lässt sich von einem einzelnen Wähler nur über einen Gleichstand überlisten.**

**Satz von Gibbard und Satterthwaite** (aus dem Gedächtnis; laut Trefferliste einer Websuche: bei mindestens drei möglichen Siegern und unbeschränkten Präferenzen ist jede Regel, die nicht diktatorisch ist, manipulierbar). Die Diktatur ist die Gegenprobe: der Diktator erhält seinen ersten Platz, alle anderen ändern nichts.

**Literatur** (aus dem Gedächtnis, nicht im Original geprüft): Gibbard (1973), Satterthwaite (1975); Bartholdi, Tovey, Trick (1989) zum Rechenaufwand; Conitzer und Walsh, „Barriers to Manipulation in Voting“, in: *Handbook of Computational Social Choice*, Cambridge University Press 2016.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)

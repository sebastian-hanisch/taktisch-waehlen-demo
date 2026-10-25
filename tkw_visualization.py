"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import tkw_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_voters(a):
    """Anteil der Wähler dieses Profils, die allein manipulieren können, je Regel (die gewählte Regel ist hervorgehoben)."""
    n = a.settings.n
    names = [C.RULES[r] for r in C.RULES]
    vals = [a.results[r].voters / n for r in C.RULES]
    colors = [C.RULE_COLORS[r] if r == a.settings.rule else "rgba(150,150,150,0.55)" for r in C.RULES]
    fig = go.Figure(go.Bar(x=names, y=vals, marker_color=colors, text=[f"{a.results[r].voters} von {n}" for r in C.RULES], textposition="outside",
                           hovertemplate="%{x}: %{y:.3f}<extra></extra>"))
    fig.update_yaxes(title_text="Anteil der Wähler, die allein manipulieren können", range=[0, max(0.25, max(vals) * 1.25 + 0.02)], tickformat=".0%")
    fig.update_xaxes(title_text="")
    return _base(fig)


def build_series(rows, m, key="profiles"):
    """Anteil (der Profile mit einem Manipulator, `profiles`, oder der manipulierenden Wähler im Mittel, `voters`) über der Wählerzahl, eine Linie je Regel; Gerade bei 0: die Diktatur."""
    fig = go.Figure()
    for rule in C.RULES:
        if rule == "dictator":
            continue
        pts = sorted((r for r in rows if r["rule"] == rule and r["m"] == m), key=lambda r: r["n"])
        if pts:
            fig.add_trace(go.Scatter(x=[p["n"] for p in pts], y=[p[key] for p in pts], mode="lines+markers", name=C.RULES[rule],
                                     line=dict(color=C.RULE_COLORS[rule], width=3), marker=dict(size=7), hovertemplate="%{x} Wähler: %{y:.3f}<extra>" + C.RULES[rule] + "</extra>"))
    ns = sorted({r["n"] for r in rows if r["m"] == m})
    fig.add_trace(go.Scatter(x=ns, y=[0.0] * len(ns), mode="lines", name=C.RULES["dictator"], line=dict(color=C.COLOR_DICTATOR, width=2, dash="dot"),
                             hovertemplate="Diktatur: 0<extra></extra>"))
    fig.update_xaxes(title_text="Zahl der Wähler", type="log", tickmode="array", tickvals=ns, ticktext=[str(n) for n in ns])
    fig.update_yaxes(title_text="Anteil der Profile mit einem Manipulator" if key == "profiles" else "Anteil der Wähler, die allein manipulieren können (Mittel)",
                     range=[-0.02, 0.62 if key == "profiles" else 0.3], tickformat=".0%")
    return _base(fig, height=340)


def build_models(rows):
    """Je Profilmodell: Anteil der Profile mit einem Manipulator je Regel."""
    models = list(C.MODELS)
    fig = go.Figure()
    for rule in C.RULES:
        if rule == "dictator":
            continue
        vals = [next(r["profiles"] for r in rows if r["model"] == mo and r["rule"] == rule) for mo in models]
        fig.add_trace(go.Bar(x=[C.MODELS[mo].split(" (")[0] for mo in models], y=vals, name=C.RULES[rule], marker_color=C.RULE_COLORS[rule],
                             text=[f"{100 * v:.0f} %" for v in vals], textposition="outside", hovertemplate="%{x}: %{y:.3f}<extra>" + C.RULES[rule] + "</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Anteil der Profile mit einem Manipulator", range=[0, 0.6], tickformat=".0%")
    return _base(fig, height=380)

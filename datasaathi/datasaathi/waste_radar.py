"""Waste Radar: proactively find unusual usage nobody asked about.

Method (all in code, no model involved): for each metric, normalise every building by its own median,
take the cross-building median per month as the "campus index" (captures season and vacations),
expected = building median x campus index. Flag months where a building is far above (or below) its
expectation, using a robust z-score (median/MAD) over that building's own history."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np, pandas as pd
from .card import Card


@dataclass
class Finding:
    entity: str
    metric: str
    label: str
    unit: str
    period: str
    observed: float
    expected: float
    excess: float
    excess_pct: float
    campus_pct: float            # campus index for that month, in % of normal
    kind: str                    # "held_load" | "spike" | "drop"
    z: float

    def facts(self) -> dict:
        return dict(observed=round(self.observed), expected=round(self.expected), excess=round(abs(self.excess)),
                    excess_pct=round(abs(self.excess_pct)), campus_pct=round(self.campus_pct))

    def text(self) -> str:
        f, u, lab = self.facts(), self.unit, self.label.lower()
        head = f"{self.entity} — {self.period}: {f['observed']:,} {u} of {lab}"
        if self.kind == "held_load":
            return (f"{head}, about {f['excess']:,} {u} ({f['excess_pct']}%) more than expected. Campus-wide use was only "
                    f"{f['campus_pct']}% of normal that month, yet {self.entity} stayed near full load. Worth checking for equipment left running.")
        if self.kind == "spike":
            return (f"{head}, about {f['excess']:,} {u} ({f['excess_pct']}%) above what its own pattern and the campus trend predict "
                    f"({f['expected']:,} {u}). Check for a leak, faulty meter or extra load.")
        return (f"{head}, about {f['excess']:,} {u} ({f['excess_pct']}%) below expectation ({f['expected']:,} {u}). "
                "Possible meter fault or missing data rather than real savings.")


def scan(df: pd.DataFrame, card: Card, min_months: int = 6, top: int = 10) -> list[Finding]:
    E, T = card.entity_column, card.time_column
    out: list[Finding] = []
    for m, meta in card.metrics.items():
        pv = df.groupby([T, E])[m].sum(min_count=1).unstack(E)
        pv = pv.loc[:, pv.notna().sum() >= min_months]
        if pv.shape[1] < 3:
            continue
        med = pv.median()
        idx = (pv / med).median(axis=1)                      # campus index per month
        exp = pd.DataFrame({c: med[c] * idx for c in pv.columns})
        ratio = pv / exp
        lr = np.log(ratio.where(ratio > 0))
        center = lr.median()
        mad = (lr - center).abs().median().clip(lower=0.03)
        z = (lr - center) / (1.4826 * mad)
        for c in pv.columns:
            for mo in pv.index:
                r, zz, obs = ratio.at[mo, c], z.at[mo, c], pv.at[mo, c]
                if pd.isna(r) or pd.isna(zz):
                    continue
                kind = None
                if r >= 1.25 and zz >= 3:
                    kind = "held_load" if idx[mo] <= 0.85 else "spike"
                elif r <= 0.6 and zz <= -3:
                    kind = "drop"
                if kind:
                    e = float(exp.at[mo, c])
                    out.append(Finding(c, m, meta.get("label", m), meta.get("unit", ""), mo, float(obs), e, float(obs - e),
                                       float((r - 1) * 100), float(idx[mo] * 100), kind, float(zz)))
    out.sort(key=lambda f: (f.kind == "drop", -abs(f.excess)))
    return out[:top]


def radar_chart(df: pd.DataFrame, card: Card, f: Finding):
    """Entity vs expected-from-campus-pattern for one finding."""
    import plotly.graph_objects as go
    E, T = card.entity_column, card.time_column
    pv = df.groupby([T, E])[f.metric].sum(min_count=1).unstack(E)
    med = pv.median()
    idx = (pv / med).median(axis=1)
    from .charts import metric_color, rgba, style
    col = metric_color(f.metric)
    fig = go.Figure()
    fig.add_scatter(x=pv.index, y=med[f.entity] * idx, name="Expected from campus pattern", mode="lines",
                    line=dict(dash="dot", color="#8FA3BF", width=2, shape="spline"), fill="tozeroy", fillcolor="rgba(143,163,191,.06)")
    fig.add_scatter(x=pv.index, y=pv[f.entity], name=f"{f.entity} (actual)", mode="lines+markers",
                    line=dict(width=3, color=col, shape="spline"), marker=dict(size=7, color="#1E2C50", line=dict(width=2, color=col)))
    fig.add_scatter(x=[f.period], y=[f.observed], mode="markers", showlegend=False, hoverinfo="skip",
                    marker=dict(size=34, color=rgba("#FF7A8A", .18), line=dict(width=0)))
    fig.add_scatter(x=[f.period], y=[f.observed], name="Flagged", mode="markers", marker=dict(size=13, color="#FF7A8A", line=dict(width=2, color="#FFFFFF")))
    fig.update_layout(yaxis_title=f"{f.label} ({f.unit})")
    return style(fig, 320)


def explain(f: Finding, use_gemma: bool = False, model: str | None = None) -> tuple[str, str]:
    """Plain-language alert. Gemma 4 may reword it, but Number Guard must verify every figure; else the template is used."""
    base = f.text()
    if not use_gemma:
        return base, "template"
    try:
        from .explain import guard_values
        from .planner import DEFAULT_MODEL, ollama_chat
        facts = f.facts()
        system = ("You are DataSaathi's Waste Radar. Write 2 short sentences for a campus facility manager about this finding and one "
                  "practical thing to check. Use ONLY the numbers in FACTS; never compute new ones. Write digits 0-9. No bullets. "
                  "Field meanings: observed = actual use; expected = what the building's own history and the campus pattern predict; "
                  "excess = observed minus expected; excess_pct = how much higher than expected, in percent; "
                  "campus_pct = campus-wide use that month as a percent of its normal level (80 means campus use was 80% of normal, "
                  "so it was lower than usual). Do not call campus_pct an average.")
        user = f"ENTITY: {f.entity}\nPERIOD: {f.period}\nMETRIC: {f.label} ({f.unit})\nKIND: {f.kind}\nFACTS: {facts}"
        cand = ollama_chat(model or DEFAULT_MODEL, system, user).strip()
        g = guard_values(cand, {float(v) for v in facts.values()})
        return (cand, model or DEFAULT_MODEL) if g.ok else (base, "template (Number Guard rejected model text)")
    except Exception:
        return base, "template"

"""Plotly charts for each intent, themed to the app (amber = electricity, blue = water)."""
from __future__ import annotations
import plotly.express as px
from .card import Card
from .engine import Result
from .plan import Plan

AMBER, WATER, GREY = "#FFC24D", "#58B8E0", "#6F8A93"
FONT = "IBM Plex Sans, system-ui, -apple-system, Segoe UI, sans-serif"


def metric_color(metric: str) -> str:
    return WATER if "water" in metric.lower() else AMBER


def style(fig, height: int = 380):
    fig.update_layout(margin=dict(l=0, r=48, t=10, b=52), height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family=FONT, size=13, color="#E8F1F3"), legend=dict(orientation="h", y=1.12, title=None))
    fig.update_xaxes(gridcolor="#21525F", zeroline=False, automargin=True, title_standoff=10)
    fig.update_yaxes(gridcolor="#21525F", zeroline=False)
    return fig


def make_chart(plan: Plan, r: Result, card: Card):
    t, E, T, M = r.table, card.entity_column, card.time_column, plan.metric
    unit = f" ({r.unit})" if r.unit else ""
    col = metric_color(M)
    if plan.intent == "rank":
        fig = px.bar(t.iloc[::-1], x=M, y=E, orientation="h", text=M, labels={M: f"{r.label}{unit}", E: ""}, color_discrete_sequence=[col])
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False, marker_cornerradius=5, textfont=dict(color="#E8F1F3"))
        fig.update_xaxes(showgrid=False)
    elif plan.intent == "trend":
        fig = px.line(t, x=T, y=M, markers=True, labels={M: f"{r.label}{unit}", T: ""}, color_discrete_sequence=[col])
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
    elif plan.intent == "compare":
        long = t.melt(id_vars=E, value_vars=[plan.period_a, plan.period_b], var_name="period", value_name=M)
        fig = px.bar(long, x=E, y=M, color="period", barmode="group", labels={M: f"{r.label}{unit}", E: ""},
                     color_discrete_map={plan.period_a: GREY, plan.period_b: col})
        fig.update_traces(marker_cornerradius=4)
    else:
        return None
    return style(fig)

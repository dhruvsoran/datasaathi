"""Plotly charts for each intent, themed to the 2.0 "observatory" look (amber = electricity, blue = water, violet = other)."""
from __future__ import annotations
import plotly.express as px
from .card import Card
from .engine import Result
from .plan import Plan

AMBER, WATER, VIOLET, GREY, INK, GRID = "#FFC24D", "#4FB6FF", "#8B7CFF", "#5C6F8A", "#EAF2FF", "rgba(255,255,255,.07)"
FONT = "Inter, system-ui, -apple-system, Segoe UI, sans-serif"


def metric_color(metric: str) -> str:
    m = metric.lower()
    return WATER if "water" in m else AMBER if any(k in m for k in ("electric", "kwh", "power", "energy")) else VIOLET


def rgba(hex_color: str, a: float) -> str:
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


def style(fig, height: int = 380):
    fig.update_layout(margin=dict(l=4, r=56, t=14, b=48), height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family=FONT, size=13, color=INK), legend=dict(orientation="h", y=1.14, x=0, title=None, bgcolor="rgba(0,0,0,0)"),
                      hoverlabel=dict(bgcolor="#0C1626", bordercolor="rgba(46,230,197,.6)", font=dict(family=FONT, color=INK, size=13)),
                      bargap=0.28)
    fig.update_xaxes(gridcolor=GRID, zeroline=False, automargin=True, title_standoff=12, linecolor="rgba(255,255,255,.12)",
                     tickfont=dict(color="#8FA3BF"), title_font=dict(color="#8FA3BF", size=12))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, griddash="dot", tickfont=dict(color="#B9C7DD"), title_font=dict(color="#8FA3BF", size=12))
    return fig


def make_chart(plan: Plan, r: Result, card: Card):
    t, E, T, M = r.table, card.entity_column, card.time_column, plan.metric
    unit = f" ({r.unit})" if r.unit else ""
    col = metric_color(M)
    if plan.intent == "rank":
        d = t.iloc[::-1]
        fig = px.bar(d, x=M, y=E, orientation="h", text=M, labels={M: f"{r.label}{unit}", E: ""})
        vals = d[M].astype(float)
        lo, hi = vals.min(), vals.max()
        shade = [rgba(col, .35 + .65 * ((v - lo) / (hi - lo) if hi > lo else 1)) for v in vals]      # brighter = larger
        fig.update_traces(marker=dict(color=shade, line=dict(color=col, width=1.2), cornerradius=7), texttemplate="%{text:,.0f}",
                          textposition="outside", cliponaxis=False, textfont=dict(color=INK, size=12),
                          hovertemplate="<b>%{y}</b><br>%{x:,.0f}" + unit + "<extra></extra>")
        fig.update_xaxes(showgrid=False, showticklabels=False)
    elif plan.intent == "trend":
        fig = px.line(t, x=T, y=M, markers=True, labels={M: f"{r.label}{unit}", T: ""}, color_discrete_sequence=[col])
        fig.update_traces(line=dict(width=3.2, shape="spline", smoothing=0.8), fill="tozeroy", fillcolor=rgba(col, .12),
                          marker=dict(size=8, color="#1E2C50", line=dict(width=2.4, color=col)),
                          hovertemplate="<b>%{x}</b><br>%{y:,.0f}" + unit + "<extra></extra>")
        s = t[M].dropna()
        if len(s):
            i = s.idxmax()
            fig.add_annotation(x=t.at[i, T], y=float(t.at[i, M]), text=f"peak {float(t.at[i, M]):,.0f}", showarrow=True, arrowhead=0,
                               arrowcolor=col, ax=0, ay=-34, font=dict(color="#050B14", size=11, family=FONT), bgcolor=col, borderpad=4)
    elif plan.intent == "compare":
        long = t.melt(id_vars=E, value_vars=[plan.period_a, plan.period_b], var_name="period", value_name=M)
        fig = px.bar(long, x=E, y=M, color="period", barmode="group", labels={M: f"{r.label}{unit}", E: ""},
                     color_discrete_map={plan.period_a: GREY, plan.period_b: col})
        fig.update_traces(marker_cornerradius=6, marker_line_width=0, hovertemplate="<b>%{x}</b><br>%{y:,.0f}" + unit + "<extra>%{fullData.name}</extra>")
    else:
        return None
    return style(fig)

"""Plotly charts for each intent, in the lush-forest professional theme (amber = electricity, blue = water, forest green = other)."""
from __future__ import annotations
import plotly.express as px
from .card import Card
from .engine import Result
from .plan import Plan

AMBER, WATER, VIOLET, GREY, INK, TEXT, MUTED, GRID = "#E0930F", "#2B8FC9", "#2E6F40", "#B9DCC3", "#1B2E21", "#2F4A37", "#5A7363", "rgba(37,61,44,.08)"
SURFACE, LINE = "#F7FCF8", "#C9E3D0"
FONT = "Inter, system-ui, -apple-system, Segoe UI, sans-serif"


def metric_color(metric: str) -> str:
    m = metric.lower()
    return WATER if "water" in m else AMBER if any(k in m for k in ("electric", "kwh", "power", "energy")) else VIOLET


def rgba(hex_color: str, a: float) -> str:
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


def style(fig, height: int = 360):
    fig.update_layout(margin=dict(l=4, r=56, t=10, b=40), height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family=FONT, size=13, color=TEXT), legend=dict(orientation="h", y=1.12, x=0, title=None, bgcolor="rgba(0,0,0,0)",
                                                                               font=dict(color=TEXT, size=12)),
                      hoverlabel=dict(bgcolor="#FBFEFC", bordercolor=LINE, font=dict(family=FONT, color=INK, size=13)),
                      bargap=0.32)
    fig.update_xaxes(gridcolor=GRID, zeroline=False, automargin=True, title_standoff=12, linecolor=LINE, showline=True,
                     tickfont=dict(color=MUTED), title_font=dict(color=MUTED, size=12))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=TEXT), title_font=dict(color=MUTED, size=12))
    return fig


def make_chart(plan: Plan, r: Result, card: Card):
    t, E, T, M = r.table, card.entity_column, card.time_column, plan.metric
    unit = f" ({r.unit})" if r.unit else ""
    col = metric_color(M)
    if plan.intent == "rank":
        d = t.iloc[::-1]
        fig = px.bar(d, x=M, y=E, orientation="h", text=M, labels={M: f"{r.label}{unit}", E: ""})
        vals = d[M].astype(float)
        top = vals.max()
        shade = [col if v == top else rgba(col, .36) for v in vals]       # the leader in full colour, the rest as a tint
        fig.update_traces(marker=dict(color=shade, line=dict(width=0), cornerradius=5), texttemplate="%{text:,.0f}",
                          textposition="outside", cliponaxis=False, textfont=dict(color=TEXT, size=12),
                          hovertemplate="<b>%{y}</b><br>%{x:,.0f}" + unit + "<extra></extra>")
        fig.update_xaxes(showgrid=False, showticklabels=False, showline=False)
    elif plan.intent == "trend":
        fig = px.line(t, x=T, y=M, markers=True, labels={M: f"{r.label}{unit}", T: ""}, color_discrete_sequence=[col])
        fig.update_traces(line=dict(width=2.4, shape="spline", smoothing=0.6), fill="tozeroy", fillcolor=rgba(col, .10),
                          marker=dict(size=7, color=SURFACE, line=dict(width=2, color=col)),
                          hovertemplate="<b>%{x}</b><br>%{y:,.0f}" + unit + "<extra></extra>")
        s = t[M].dropna()
        if len(s):
            i = s.idxmax()
            fig.add_annotation(x=t.at[i, T], y=float(t.at[i, M]), text=f"Peak {float(t.at[i, M]):,.0f}", showarrow=False, yshift=16,
                               font=dict(color=TEXT, size=11, family=FONT), bgcolor=SURFACE, bordercolor=LINE, borderpad=3)
    elif plan.intent == "compare":
        long = t.melt(id_vars=E, value_vars=[plan.period_a, plan.period_b], var_name="period", value_name=M)
        fig = px.bar(long, x=E, y=M, color="period", barmode="group", labels={M: f"{r.label}{unit}", E: ""},
                     color_discrete_map={plan.period_a: GREY, plan.period_b: col})
        fig.update_traces(marker_cornerradius=4, marker_line_width=0, hovertemplate="<b>%{x}</b><br>%{y:,.0f}" + unit + "<extra>%{fullData.name}</extra>")
    else:
        return None
    return style(fig)

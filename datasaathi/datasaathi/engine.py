"""Executes a validated Plan. The model never computes numbers: this module does.

The pandas snippet shown in the Proof Receipt is the exact code that runs (built only from
validated, whitelisted values, executed with no builtins)."""
from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd
from .card import Card
from .plan import Plan


class NoData(Exception):
    pass


@dataclass
class Result:
    table: pd.DataFrame
    used: pd.DataFrame
    code: str
    facts: dict
    caveats: list = field(default_factory=list)
    assumptions: list = field(default_factory=list)
    unit: str = ""
    label: str = ""


def build_code(p: Plan, card: Card) -> str:
    E, T, M = repr(card.entity_column), repr(card.time_column), repr(p.metric)
    asc = p.order == "asc"
    ent = f"used = used[used[{E}] == {p.entity!r}]\n" if p.entity else ""
    if p.intent == "rank":
        mon = f"used = df[df[{T}] == {p.month!r}]\n" if p.month else "used = df\n"
        return (mon + f"result = (used.groupby({E}, as_index=False)[{M}].sum(min_count=1).dropna()\n"
                f"          .sort_values({M}, ascending={asc}).head({p.top_n}).reset_index(drop=True).round(2))")
    if p.intent == "total":
        mon = f"used = df[df[{T}] == {p.month!r}]\n" if p.month else "used = df\n"
        return (mon + ent + f"result = pd.DataFrame({{'total': [used[{M}].sum()], "
                f"'readings_used': [used[{M}].notna().sum()]}}).round(2)")
    if p.intent == "average":
        return ("used = df\n" + ent + f"monthly = used.groupby({T})[{M}].sum(min_count=1).dropna()\n"
                "result = pd.DataFrame({'average_per_month': [monthly.mean()], 'months_counted': [monthly.shape[0]]}).round(2)")
    if p.intent == "trend":
        return ("used = df\n" + ent + f"result = (used.groupby({T}, as_index=False)[{M}].sum(min_count=1).dropna()\n"
                f"          .sort_values({T}).reset_index(drop=True).round(2))")
    if p.intent == "anomaly":
        return (f"d = df.dropna(subset=[{M}]).copy()\n"
                f"d['own_median'] = d.groupby({E})[{M}].transform('median')\n"
                f"d['ratio'] = d[{M}] / d['own_median']\n"
                f"peer = d.pivot_table(index={T}, columns={E}, values='ratio')\n"
                f"d['peer_index'] = d.apply(lambda r: peer.loc[r[{T}]].drop(r[{E}]).median(), axis=1)\n"
                "d['expected'] = d['own_median'] * d['peer_index']\n"
                "d['excess'] = d[" + M + "] - d['expected']\n"
                "d['deviation_pct'] = (d[" + M + "] / d['expected'] - 1) * 100\n"
                "used = d[d['deviation_pct'] >= 25]\n"
                f"result = (used.sort_values('excess', ascending=False).head({p.top_n})\n"
                f"          [[{E}, {T}, {M}, 'expected', 'excess', 'deviation_pct']].round(1).reset_index(drop=True))")
    if p.intent == "compare":
        a, b = p.period_a, p.period_b
        return (f"used = df[df[{T}].isin([{a!r}, {b!r}])]\n" + ent +
                f"pv = used.pivot_table(index={E}, columns={T}, values={M}, aggfunc='sum').dropna()\n"
                f"pv['change'] = pv[{b!r}] - pv[{a!r}]\n"
                f"pv['change_pct'] = pv['change'] / pv[{a!r}] * 100\n"
                "result = pv.reset_index().sort_values('change', ascending=False).round(2)")
    raise ValueError(p.intent)


def _facts(p: Plan, t: pd.DataFrame, card: Card, used: pd.DataFrame | None = None) -> dict:
    E, T, M = card.entity_column, card.time_column, p.metric
    if p.intent == "anomaly":
        if t.empty:
            return dict(count=0, threshold_pct=25.0)
        top = t.iloc[0]
        return dict(count=len(used), threshold_pct=25.0, entity=top[E], period=top[T], actual=float(top[M]),
                    expected=float(top["expected"]), excess=float(top["excess"]), deviation_pct=float(top["deviation_pct"]),
                    total_excess=round(float(used["excess"].sum()), 1))
    if p.intent == "rank":
        return dict(scope=p.month or "the whole period", order=p.order, first_entity=t.iloc[0][E], first_value=float(t.iloc[0][M]),
                    last_entity=t.iloc[-1][E], last_value=float(t.iloc[-1][M]), rows=len(t))
    if p.intent == "total":
        return dict(scope=p.month or "the whole period", entity=p.entity, total=float(t.iloc[0]["total"]), readings=int(t.iloc[0]["readings_used"]))
    if p.intent == "average":
        return dict(entity=p.entity, average=float(t.iloc[0]["average_per_month"]), months=int(t.iloc[0]["months_counted"]))
    if p.intent == "trend":
        first, last = t.iloc[0], t.iloc[-1]
        pk, lo = t.loc[t[M].idxmax()], t.loc[t[M].idxmin()]
        pct = round((last[M] - first[M]) / first[M] * 100, 1) if first[M] else 0.0
        return dict(entity=p.entity, first_period=first[T], first_value=float(first[M]), last_period=last[T], last_value=float(last[M]),
                    change_pct=float(pct), peak_period=pk[T], peak_value=float(pk[M]), low_period=lo[T], low_value=float(lo[M]))
    a, b = p.period_a, p.period_b
    ta, tb = float(t[a].sum()), float(t[b].sum())
    up, down = t.iloc[0], t.iloc[-1]
    return dict(a=a, b=b, entity=p.entity, total_a=round(ta, 2), total_b=round(tb, 2), total_change=round(tb - ta, 2),
                total_change_pct=round((tb - ta) / ta * 100, 1) if ta else 0.0,
                rise_entity=up[E], rise_change=float(up["change"]), rise_pct=float(up["change_pct"]),
                fall_entity=down[E], fall_change=float(down["change"]), fall_pct=float(down["change_pct"]), rows=len(t))


def _caveats(p: Plan, df: pd.DataFrame, card: Card) -> list[str]:
    E, T, M = card.entity_column, card.time_column, p.metric
    label = card.metrics[M].get("label", M)
    out: list[str] = []
    if card.synthetic:
        out.append("Sample data is SYNTHETIC (generated for the demo) — not official public records.")
    elif "NOT verified" in card.source:
        out.append("Dataset provenance is not verified (uploaded without a Data Card).")
    ents = [p.entity] if p.entity else sorted(df[E].unique())
    if p.intent == "compare":
        months = [p.period_a, p.period_b]
    elif p.month and p.intent in ("rank", "total"):
        months = [p.month]
    else:
        months = sorted(df[T].unique())
    have = set(zip(*[df.dropna(subset=[M])[c] for c in (E, T)]))
    missing = [(e, m) for e in ents for m in months if (e, m) not in have]
    if missing:
        shown = "; ".join(f"{e} in {m}" for e, m in missing[:4]) + (f"; and {len(missing) - 4} more" if len(missing) > 4 else "")
        out.append(f"Missing {label} reading(s): {shown}. Results use only the readings that exist, so totals and "
                   "rankings that involve them may be understated" + (" and entities missing a reading were left out of the comparison." if p.intent == "compare" else "."))
    if p.intent == "anomaly":
        out.append("The radar compares each reading with the building's own typical level, scaled by how its peers moved that month. "
                   "It flags unusual use, not proven waste — verify on site before acting.")
    if p.intent in ("rank", "compare") and card.not_available:
        out.append(f"These are absolute figures. The dataset has no {card.not_available[0]} or floor-area data, so this is not a per-person or per-area comparison.")
    return out


def run(p: Plan, df: pd.DataFrame, card: Card, assumptions: list[str] | None = None) -> Result:
    code = build_code(p, card)
    scope = {"__builtins__": {}, "df": df.copy(), "pd": pd}
    exec(code, scope)                       # code is built only from validated, whitelisted values
    table, used = scope["result"], scope["used"]
    if p.intent in ("rank", "trend", "compare") and table.empty:
        raise NoData("no readings match the question")
    if p.intent == "total" and table.iloc[0]["readings_used"] == 0:
        raise NoData("no readings match the question")
    if p.intent == "average" and table.iloc[0]["months_counted"] == 0:
        raise NoData("no readings match the question")
    table.columns.name = None
    meta = card.metrics[p.metric]
    facts = _facts(p, table, card, used)
    caveats = _caveats(p, df, card)
    # warn when the data cannot justify a strong conclusion
    if p.intent == "rank" and len(table) >= 2 and table.iloc[0][p.metric]:
        gap = abs(table.iloc[0][p.metric] - table.iloc[1][p.metric]) / abs(table.iloc[0][p.metric]) * 100
        if gap < 3:
            caveats.append(f"The top two are within {gap:.1f}% of each other, so this ranking is close and may not be a meaningful difference.")
    if p.intent == "compare" and abs(facts.get("total_change_pct", 100)) < 2:
        caveats.append(f"The overall change is only {abs(facts['total_change_pct']):.1f}%, which is small; it may be normal variation rather than a real shift.")
    return Result(table=table, used=used, code=code, facts=facts, caveats=caveats,
                  assumptions=list(assumptions or []), unit=meta.get("unit", ""), label=meta.get("label", p.metric))

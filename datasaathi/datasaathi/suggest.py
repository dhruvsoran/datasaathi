"""Suggested questions written from the loaded data: its own entity names, metrics and months, so an uploaded CSV gets
questions about that file, not about the sample campus."""
from __future__ import annotations
import pandas as pd
from .card import Card

UNIT_WORDS = {"kwh", "mwh", "kw", "kl", "l", "m3", "kg", "t", "units", "litres", "liters", "tonnes", "rs", "inr"}
USAGE_WORDS = ("electric", "power", "energy", "kwh", "water", "gas", "fuel", "diesel")


def metric_label(card: Card, m: str) -> str:
    """Plain words for a metric: the Data Card label, without a trailing unit ("Water Kl" -> "water")."""
    words = str(card.metrics.get(m, {}).get("label", m)).replace("_", " ").split()
    while len(words) > 1 and words[-1].lower() in UNIT_WORDS:
        words.pop()
    return " ".join(words).lower()


def entity_word(card: Card) -> str:
    """The thing each row describes, from the entity column name ("building", "block", "ward_name" -> "ward")."""
    w = str(card.entity_column).replace("_", " ").strip().lower()
    for tail in (" name", " id", " code"):
        w = w[: -len(tail)] if w.endswith(tail) else w
    return w.split()[-1] if w else "entity"


def month_name(ym: str) -> str:
    try:
        return pd.Timestamp(f"{ym}-01").strftime("%B %Y")
    except (ValueError, TypeError):
        return str(ym)


def suggestions(df: pd.DataFrame, card: Card) -> dict[str, list[str]]:
    """Grouped questions for this dataset. Every number they lead to is still computed by the engine; these are only prompts."""
    E, T = card.entity_column, card.time_column
    metrics = [m for m in card.metrics if m in df.columns]
    if not metrics or E not in df.columns or T not in df.columns:
        return {}
    m1 = metrics[0]
    m2 = metrics[1] if len(metrics) > 1 else m1
    l1, l2 = metric_label(card, m1), metric_label(card, m2)
    ent = entity_word(card)
    months = sorted(str(x) for x in df[T].dropna().unique())
    totals = df.groupby(E)[m1].sum(min_count=1).dropna().sort_values(ascending=False)
    names = [str(n) for n in totals.index]
    used = lambda m: any(k in f"{m} {card.metrics.get(m, {}).get('label', '')}".lower() for k in USAGE_WORDS)
    most = "used the most" if used(m1) else "had the highest"
    least = "used the least" if used(m2) else "had the lowest"

    rank = [f"Which {ent} {most} {l1} last month?"]
    if len(months) > 1:
        rank.append(f"Compare {l1} in {month_name(months[-2])} and {month_name(months[-1])}")
    if months:
        rank.append(f"Which {ent} {least} {l2} in {month_name(months[-1])}?")

    trends = []
    if names:
        trends.append(f"{names[0]} {l1} trend")
    if months:
        trends.append(f"What was the total {l2} in {month_name(months[-1])}?")
    if len(names) > 1:
        trends.append(f"Average monthly {l1} of {names[1]}")

    groups = {"Rank and compare": rank, "Trends and totals": trends}
    return {k: v for k, v in groups.items() if v}

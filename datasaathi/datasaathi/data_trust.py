"""Data Trust check: audit a dataset BEFORE trusting any answer from it."""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np, pandas as pd
from .card import Card


@dataclass
class Trust:
    table: pd.DataFrame                                  # one row per metric
    issues: list = field(default_factory=list)           # (severity, message)
    overall: int = 100
    per_metric: dict = field(default_factory=dict)       # metric -> {score, duplicates, negatives, extremes, completeness}


def audit(df: pd.DataFrame, card: Card) -> Trust:
    E, T = card.entity_column, card.time_column
    issues: list[tuple[str, str]] = []
    months = sorted(df[T].unique())
    ents = sorted(df[E].unique())
    # gaps in the month sequence
    try:
        full = pd.period_range(months[0], months[-1], freq="M").astype(str)
        gaps = [m for m in full if m not in set(months)]
        if gaps:
            issues.append(("high", f"Month(s) missing from the series entirely: {', '.join(gaps[:6])}."))
    except Exception:
        pass
    dups = int(df.duplicated([E, T]).sum())
    if dups:
        ex = df[df.duplicated([E, T], keep=False)][[E, T]].drop_duplicates().head(3)
        issues.append(("high", f"{dups} duplicate ({E}, {T}) row(s), e.g. " + "; ".join(f"{r[E]} {r[T]}" for _, r in ex.iterrows())
                       + ". Totals will double-count them."))
    present = set(zip(df[E], df[T]))
    absent = [(e, m) for e in ents for m in months if (e, m) not in present]
    if absent:
        issues.append(("medium", f"{len(absent)} expected row(s) absent, e.g. " + "; ".join(f"{e} {m}" for e, m in absent[:3]) + "."))

    rows, per = [], {}
    expected = len(ents) * len(months)
    for m, meta in card.metrics.items():
        label = meta.get("label", m)
        s = df[m]
        missing_total = expected - int(df.drop_duplicates([E, T])[m].notna().sum())
        completeness = max(0.0, 1 - missing_total / expected) if expected else 1.0
        neg = int((s < 0).sum())
        med = df.groupby(E)[m].transform("median")
        ratio = (s / med.replace(0, np.nan))
        ext = df[(ratio > 5) | (ratio < 0.1)]
        if neg:
            issues.append(("high", f"{neg} negative {label} value(s) — physically impossible for usage data."))
        if len(ext):
            r0 = ext.iloc[0]
            issues.append(("high", f"{len(ext)} {label} value(s) far from the building's normal (e.g. {r0[E]} {r0[T]} = {r0[m]:,.0f} vs typical {med.loc[ext.index[0]]:,.0f}) — possible typo or unit error."))
        if missing_total:
            issues.append(("medium", f"{label}: {missing_total} missing reading(s) ({completeness:.0%} complete)."))
        score = int(max(0, round(100 * completeness - 15 * (dups > 0) - 15 * (neg > 0) - 10 * (len(ext) > 0))))
        per[m] = dict(score=score, duplicates=dups, negatives=neg, extremes=int(len(ext)), completeness=round(completeness * 100, 1),
                      rows={"dup": set(df.index[df.duplicated([E, T], keep=False)]), "neg": set(df.index[s < 0]), "ext": set(ext.index)})
        rows.append({"metric": label, "completeness_%": round(completeness * 100, 1), "duplicates": dups,
                     "negatives": neg, "suspect_values": int(len(ext)), "trust_score": score})
    table = pd.DataFrame(rows)
    overall = int(table["trust_score"].min()) if len(table) else 100
    if card.synthetic:
        issues.append(("info", "Dataset is labelled synthetic (demo data), not official records."))
    order = {"high": 0, "medium": 1, "info": 2}
    return Trust(table, sorted(issues, key=lambda x: order[x[0]]), overall, per)

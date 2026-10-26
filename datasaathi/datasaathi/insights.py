"""Data Trust check: shown before any answer so users know how far to trust the data."""
from __future__ import annotations
import pandas as pd
from .card import Card


def data_trust(df: pd.DataFrame, card: Card) -> dict:
    E, T, mets = card.entity_column, card.time_column, list(card.metrics)
    ents, months = sorted(df[E].unique()), sorted(df[T].unique())
    expected = len(ents) * len(months) * len(mets)
    have = {(e, t, m) for m in mets for e, t in df.dropna(subset=[m])[[E, T]].itertuples(index=False)}
    gaps = [f"{card.metrics[m].get('label', m)}: {e} in {t}" for e in ents for t in months for m in mets if (e, t, m) not in have]
    return {
        "completeness_pct": round(len(have) / expected * 100, 1) if expected else 0.0,
        "expected_readings": expected, "missing_readings": len(gaps), "gaps": gaps,
        "duplicate_rows": int(df.duplicated([E, T]).sum()),
        "zero_or_negative": int((df[mets] <= 0).sum().sum()),
        "entities": len(ents), "periods": len(months),
    }

"""Data Card + dataset loading."""
from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd, yaml


@dataclass
class Card:
    name: str
    synthetic: bool
    source: str
    period: str
    entity_column: str
    time_column: str
    metrics: dict                      # name -> {label, unit}
    not_available: list = field(default_factory=list)
    notes: str = ""


def load_card(text: str) -> Card:
    d = yaml.safe_load(text)
    return Card(name=d["name"], synthetic=bool(d.get("synthetic", False)), source=d.get("source", "unknown"),
                period=str(d.get("period", "")), entity_column=d["entity_column"], time_column=d["time_column"],
                metrics=d["metrics"], not_available=d.get("not_available", []), notes=d.get("notes", ""))


def infer_card(df: pd.DataFrame, name: str = "Uploaded dataset") -> Card:
    """Minimal card for a CSV uploaded without one. Provenance stays unverified."""
    # any non-numeric column is text: pandas 2 reads text as `object`, pandas 3 as the new `str` dtype
    text_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    time_col = next((c for c in df.columns if any(k in str(c).lower() for k in ("month", "date", "period"))),
                    text_cols[-1] if text_cols else None)
    entity_col = next((c for c in text_cols if c != time_col), None)
    nums = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c not in (time_col, entity_col)]
    if time_col is None or entity_col is None or not nums:
        raise ValueError("Could not work out the columns of this CSV. It needs one column of names (buildings, wards, plants), "
                         "one month or date column, and at least one numeric column. Add a Data Card YAML to name them.")
    return Card(name=name, synthetic=False, source="User-uploaded file; provenance NOT verified", period="see data",
                entity_column=entity_col, time_column=time_col,
                metrics={c: {"label": c.replace("_", " ").title(), "unit": ""} for c in nums},
                not_available=[], notes="Auto-generated card. Add a Data Card YAML for units and source.")


def load_data(src, card: Card) -> pd.DataFrame:
    df = pd.read_csv(src)
    for col in (card.entity_column, card.time_column, *card.metrics):
        if col not in df.columns:
            raise ValueError(f"Column '{col}' named in the Data Card is missing from the CSV.")
    t = card.time_column
    try:
        df[t] = pd.to_datetime(df[t]).dt.strftime("%Y-%m")
    except Exception:
        df[t] = df[t].astype(str)
    return df

"""Analysis-plan schema (what Gemma 4 must output) and validation against the Data Card."""
from __future__ import annotations
from typing import Literal, Optional
import pandas as pd
from pydantic import BaseModel
from .card import Card


class Plan(BaseModel):
    intent: Literal["rank", "total", "average", "trend", "compare", "anomaly", "unavailable"]
    metric: Optional[str] = None          # key from Data Card metrics
    entity: Optional[str] = None          # e.g. a building name, if the question names one
    month: Optional[str] = None           # YYYY-MM
    period_a: Optional[str] = None        # compare: YYYY-MM
    period_b: Optional[str] = None        # compare: YYYY-MM
    order: Literal["desc", "asc"] = "desc"
    top_n: int = 5
    missing_field: Optional[str] = None   # unavailable: what the question needs but data lacks


def validate_plan(plan: Plan, df: pd.DataFrame, card: Card) -> tuple[Plan, list[str]]:
    """Check every field against the real data. Anything unknown becomes an honest refusal."""
    notes: list[str] = []
    if plan.intent == "unavailable":
        return plan, notes
    months = sorted(df[card.time_column].unique())
    entities = set(df[card.entity_column].unique())

    def refuse(what: str) -> tuple[Plan, list[str]]:
        return Plan(intent="unavailable", missing_field=what), notes

    if plan.metric not in card.metrics:
        if plan.metric is None and len(card.metrics) == 1:
            plan.metric = next(iter(card.metrics))
        else:
            return refuse(f"a metric called '{plan.metric}'")
    if plan.entity and plan.entity not in entities:
        return refuse(f"a {card.entity_column} called '{plan.entity}'")
    for f in ("month", "period_a", "period_b"):
        v = getattr(plan, f)
        if v and v not in months:
            return refuse(f"data for {v} (dataset covers {months[0]} to {months[-1]})")
    if plan.intent == "compare":
        if not (plan.period_a and plan.period_b):
            plan.period_a, plan.period_b = months[-2], months[-1]
            notes.append(f"No two periods named, so compared {plan.period_a} with {plan.period_b} (the two latest months).")
        if plan.period_a == plan.period_b:
            return refuse("two different periods to compare")
    if plan.intent == "anomaly" and len(entities) < 4:
        return refuse(f"at least 4 {card.entity_column} values to compare peers against")
    plan.top_n = max(1, min(int(plan.top_n), 20))
    return plan, notes

"""Plain-language explanation + Number Guard.

Gemma 4 writes the explanation from computed facts. Number Guard then checks that every number in the
text exists in the computed output; if not, the model's text is discarded and a template is used."""
from __future__ import annotations
import json, re
from dataclasses import dataclass, field
import pandas as pd
from .engine import Result
from .planner import ollama_chat, DEFAULT_MODEL


def _n(v: float) -> str:
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:,.1f}"


def template_explain(plan, r: Result) -> str:
    f, u, lab = r.facts, r.unit, r.label.lower()
    if plan.intent == "rank":
        word = "highest" if f["order"] == "desc" else "lowest"
        return (f"{f['first_entity']} had the {word} {lab} use in {f['scope']}: {_n(f['first_value'])} {u}. "
                f"At the other end of the top {f['rows']} shown is {f['last_entity']} with {_n(f['last_value'])} {u}.")
    if plan.intent == "total":
        who = f" for {f['entity']}" if f["entity"] else " overall"
        return f"Total {lab} use{who} in {f['scope']} was {_n(f['total'])} {u}, summed from {f['readings']} readings."
    if plan.intent == "average":
        who = f["entity"] or "the campus"
        return f"The average monthly {lab} use for {who} was {_n(f['average'])} {u}, over {f['months']} months with data."
    if plan.intent == "anomaly":
        if f["count"] == 0:
            return f"No unusual {lab} readings found: every reading is within {f['threshold_pct']:.0f}% of what its own history and its peers' behaviour predict."
        return (f"Waste Radar flagged {f['count']} {lab} readings more than {f['threshold_pct']:.0f}% above expectation. The biggest: "
                f"{f['entity']} in {f['period']} used {_n(f['actual'])} {u} against about {_n(f['expected'])} {u} expected from its own history "
                f"and what peer buildings did that month — {_n(f['excess'])} {u} ({f['deviation_pct']:+.1f}%) more. "
                f"Combined excess across all flagged readings: {_n(f['total_excess'])} {u}. Worth checking schedules (cooling, lighting) and meter readings.")
    if plan.intent == "trend":
        who = f["entity"] or "Campus-wide"
        return (f"{who} {lab} use went from {_n(f['first_value'])} {u} in {f['first_period']} to {_n(f['last_value'])} {u} in "
                f"{f['last_period']} ({f['change_pct']:+.1f}%). It peaked in {f['peak_period']} at {_n(f['peak_value'])} {u} "
                f"and was lowest in {f['low_period']} at {_n(f['low_value'])} {u}.")
    up = "rose" if f["total_change"] >= 0 else "fell"
    s = (f"{f['entity'] or 'Total campus'} {lab} use {up} from {_n(f['total_a'])} {u} in {f['a']} to {_n(f['total_b'])} {u} in {f['b']} "
         f"({f['total_change_pct']:+.1f}%).")
    if f["rows"] > 1:
        kind = "largest increase" if f["rise_change"] >= 0 else "smallest decrease"
        s += (f" The {kind} was {f['rise_entity']} ({f['rise_change']:+,.0f} {u}, {f['rise_pct']:+.1f}%); "
              f"the {'biggest drop' if f['fall_change'] < 0 else 'smallest increase'} was {f['fall_entity']} ({f['fall_change']:+,.0f} {u}, {f['fall_pct']:+.1f}%).")
    return s


# ---------------- Number Guard ----------------
_NUM = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")
_DATE = re.compile(r"\b20\d\d(?:-\d\d)?\b")


@dataclass
class Guard:
    ok: bool
    checked: list = field(default_factory=list)
    unverified: list = field(default_factory=list)


def allowed_numbers(r: Result) -> set[float]:
    vals: set[float] = set()
    for v in r.facts.values():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            vals.add(abs(float(v)))
    for col in r.table.select_dtypes("number").columns:
        vals.update(abs(float(x)) for x in r.table[col].dropna())
    return vals


def number_guard(text: str, r: Result) -> Guard:
    return guard_values(text, allowed_numbers(r), set(range(0, len(r.table) + 1)))


def guard_values(text: str, allowed: set, small_ok: set | None = None) -> Guard:
    """Every number in `text` must match a value in `allowed` (to the precision written)."""
    small_ok = small_ok or set()
    checked, bad = [], []
    for tok in _NUM.findall(_DATE.sub(" ", text)):
        val = float(tok.replace(",", ""))
        d = len(tok.split(".")[1]) if "." in tok else 0
        ok = any(abs(a - val) <= 0.5 * 10 ** -d + 1e-9 for a in allowed) or (d == 0 and val in small_ok)
        (checked if ok else bad).append(tok)
    return Guard(ok=not bad, checked=checked, unverified=bad)


# ---------------- Gemma explainer ----------------
def gemma_explain(question: str, plan, r: Result, model: str = DEFAULT_MODEL) -> str:
    facts = {k: v for k, v in r.facts.items()}
    system = ("You are DataSaathi. Explain a computed result to a non-technical campus user in 2-3 short sentences. "
              "Use ONLY numbers that appear in FACTS or TABLE; never calculate new numbers, estimate or round differently. "
              "Write digits 0-9. Answer in the same language and script as the question (English, Hindi or Hinglish). "
              "Mention one caveat if caveats are given. No bullet points.")
    user = (f"QUESTION: {question}\nUNIT: {r.unit}\nFACTS: {json.dumps(facts, default=str)}\n"
            f"TABLE: {r.table.head(10).to_json(orient='records')}\nCAVEATS: {json.dumps(r.caveats)}")
    return ollama_chat(model, system, user).strip()

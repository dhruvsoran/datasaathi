"""question -> plan -> validated plan -> executed result -> explanation -> Number Guard -> Proof Receipt."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd
from .card import Card
from .engine import NoData, Result, run
from .data_trust import audit
from .explain import Guard, gemma_explain, number_guard, template_explain
from . import logs
from .localize import localize
from .plan import Plan, validate_plan
from .planner import DEFAULT_MODEL, plan_question


@dataclass
class Answer:
    question: str
    status: str                       # "answered" | "refused"
    text: str
    plan: Plan
    planner: str
    notes: list = field(default_factory=list)
    result: Optional[Result] = None
    guard: Optional[Guard] = None
    explainer: str = "template"
    trust_score: Optional[int] = None
    text_en: Optional[str] = None      # English original when the answer was translated

    def receipt(self) -> dict:
        r = self.result
        return {
            "question": self.question, "status": self.status, "planner": self.planner, "explainer": self.explainer,
            "plan": self.plan.model_dump(), "notes": self.notes, "data_trust_score": self.trust_score,
            "answer_text": self.text, "answer_text_english": self.text_en,
            "code_executed": r.code if r else None,
            "rows_used": json.loads(r.used.to_json(orient="records")) if r else [],
            "result_table": json.loads(r.table.to_json(orient="records")) if r else [],
            "assumptions": r.assumptions if r else [], "caveats": r.caveats if r else [],
            "number_guard": ({"passed": self.guard.ok, "numbers_verified": self.guard.checked,
                              "numbers_unverified": self.guard.unverified} if self.guard else None),
        }


def _refusal(plan: Plan, card: Card, df: pd.DataFrame, detail: str | None = None) -> str:
    cols = ", ".join(f"{m['label']} ({m.get('unit', '')})" for m in card.metrics.values())
    need = detail or plan.missing_field or "that information"
    return (f"I can't answer that from this dataset — it needs {need}, which isn't in the data. "
            f"I only have {cols} by {card.entity_column} and {card.time_column}. "
            "I won't guess a number; try a ranking, total, average, trend or comparison of those.")


def _answer(question: str, df: pd.DataFrame, card: Card, use_gemma: bool, model: str) -> Answer:
    po = plan_question(question, df, card, use_gemma, model)
    plan, vnotes = validate_plan(po.plan, df, card)
    notes = po.notes + vnotes
    if plan.intent == "unavailable":
        return Answer(question, "refused", _refusal(plan, card, df), plan, po.name, notes)
    try:
        res = run(plan, df, card, assumptions=notes)
    except NoData:
        who = f" for {plan.entity}" if plan.entity else ""
        when = f" in {plan.month}" if plan.month else ""
        d = f"a reading of {res_label(card, plan)}{who}{when}"
        return Answer(question, "refused", _refusal(plan, card, df, d).replace("isn't in the data", "has no record in the data (a missing observation)"),
                      plan, po.name, notes)
    text, guard, explainer = template_explain(plan, res), None, "template"
    if use_gemma and po.name != "rules":
        try:
            cand = gemma_explain(question, plan, res, po.name)
            guard = number_guard(cand, res)
            if guard.ok:
                text, explainer = cand, po.name
            else:
                notes.append(f"Number Guard rejected the model's wording (unverified numbers: {', '.join(guard.unverified)}); showing a verified template answer.")
        except Exception as e:
            notes.append(f"Gemma explainer unavailable ({type(e).__name__}); showing a verified template answer.")
    if guard is None:
        guard = number_guard(text, res)
    return Answer(question, "answered", text, plan, po.name, notes, res, guard, explainer)


def res_label(card: Card, plan: Plan) -> str:
    return card.metrics[plan.metric].get("label", plan.metric).lower()


def answer(question: str, df: pd.DataFrame, card: Card, use_gemma: bool = True, model: str = DEFAULT_MODEL, log: bool = False) -> Answer:
    """Full pipeline + Data Trust annotation (+ optional DuckDB query log)."""
    a = _answer(question, df, card, use_gemma, model)
    if a.result is not None:
        tr = audit(df, card)
        info = tr.per_metric.get(a.plan.metric, {})
        a.trust_score = info.get("score")
        used_idx = set(a.result.used.index)
        rows = info.get("rows", {})
        hit_dup, hit_neg, hit_ext = (len(rows.get(k, set()) & used_idx) for k in ("dup", "neg", "ext"))
        if hit_dup:
            a.result.caveats.insert(0, f"Data Trust: {hit_dup} duplicate row(s) are among the rows used here — totals count them twice. Fix the source before relying on this number.")
        if hit_neg:
            a.result.caveats.insert(0, f"Data Trust: {hit_neg} negative value(s) are among the rows used here — impossible readings are included in the calculation.")
        if hit_ext:
            a.result.caveats.insert(0, f"Data Trust: {hit_ext} suspicious value(s) far from normal (possible typo or unit error) are among the rows used here and are included in the calculation.")
        if tr.issues and not (hit_dup or hit_neg or hit_ext) and info.get("score", 100) < 95:
            a.notes.append(f"Data Trust: this dataset has quality issues elsewhere (score {info['score']}/100), but none of the flagged rows were used for this answer.")
    # answer in the user's language: translate verified template text and refusals (Gemma 4 only; numbers re-checked)
    if use_gemma and a.planner != "rules" and a.explainer in ("template",):
        translated, ok = localize(a.text, question, a.planner)
        if ok:
            a.text_en, a.text = a.text, translated
    if log:
        logs.log(a, a.trust_score)
    return a

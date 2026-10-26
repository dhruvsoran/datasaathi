"""Question -> Plan. Gemma 4 (via Ollama) is primary; a transparent rule-based planner is the offline fallback."""
from __future__ import annotations
import json, os, re, urllib.request
from dataclasses import dataclass, field
import pandas as pd
from .card import Card
from .plan import Plan
from .lexicon import BILL_RE, LEX, find_native_months

OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("DATASAATHI_MODEL", "gemma4:e4b")   # check `ollama list` for your exact tag


@dataclass
class PlannerOut:
    plan: Plan
    name: str                      # "gemma4:e4b" or "rules"
    notes: list = field(default_factory=list)


# ---------- Ollama helpers ----------
def ollama_models() -> list[str]:
    try:
        with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=1.5) as r:
            return [m["name"] for m in json.load(r).get("models", [])]
    except Exception:
        return []


def ollama_chat(model: str, system: str, user: str, schema: dict | None = None, timeout: int = 120) -> str:
    body = {"model": model, "stream": False, "options": {"temperature": 0},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if schema:
        body["format"] = schema
    req = urllib.request.Request(f"{OLLAMA}/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)["message"]["content"]


# ---------- shared parsing ----------
MONTH_NUM = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7, "august": 8,
             "september": 9, "october": 10, "november": 11, "december": 12, "jan": 1, "feb": 2, "mar": 3,
             "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sept": 9, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
MONTH_RE = re.compile(r"\b(" + "|".join(sorted(MONTH_NUM, key=len, reverse=True)) + r")\b(?:\s+(20\d\d))?")
LATEST = LEX["lastmonth"] + ["last month", "latest month", "most recent month", "previous month", "pichle mahine", "pichhle mahine",
          "pichle maah", "पिछले महीने", "पिछले माह"]
UNAVAILABLE = {  # question stem -> what is missing
    "per student": "student headcount", "per capita": "student headcount", "student": "student headcount",
    "छात्र": "student headcount", "occupan": "occupancy data", "per head": "headcount", "headcount": "headcount",
    "cost": "cost / tariff data", "rupee": "cost / tariff data", "spend": "cost / tariff data",
    "spent": "cost / tariff data", "expens": "cost / tariff data", "bill": "cost / tariff data",
    "tariff": "cost / tariff data", "price": "cost / tariff data", "खर्च": "cost / tariff data",
    "carbon": "an emission factor", "co2": "an emission factor", "emission": "an emission factor",
    "footprint": "an emission factor", "कार्बन": "an emission factor", "waste": "waste records",
    "कचरा": "waste records", "floor area": "floor-area data", "sq ft": "floor-area data",
    "per sqft": "floor-area data", "weather": "weather data", "temperature": "weather data",
    "forecast": "a forecasting model (only recorded data is analysed)", "predict": "a forecasting model (only recorded data is analysed)",
}
METRIC_WORDS = {"electricity": ["electric", "power", "energy", "bijli", "बिजली", "kwh"] + LEX["electric"],
                "water": ["water", "paani", "pani", "पानी", "kilolit"] + LEX["water"]}

ASC_WORDS = ["least", "lowest", "minimum", "fewest", "smallest", "kam", "कम"] + LEX["least"]


def _has(text: str, stems) -> bool:
    for s in stems:
        if any(ord(c) > 127 for c in s):
            if s in text:
                return True
        elif re.search(rf"\b{re.escape(s)}", text):
            return True
    return False


def find_months(text: str, avail: list[str]) -> list[str]:
    found: list[tuple[int, str]] = []
    for m in re.finditer(r"\b(20\d\d)-(\d\d)\b", text):
        found.append((m.start(), m.group(0)))
    for m in MONTH_RE.finditer(text):
        num, year = MONTH_NUM[m.group(1)], m.group(2)
        if year:
            ym = f"{year}-{num:02d}"
        else:
            cands = [a for a in avail if int(a[5:7]) == num]
            ym = cands[-1] if cands else f"????-{num:02d}"
        found.append((m.start(), ym))
    for pos, num in find_native_months(text):
        cands = [a for a in avail if int(a[5:7]) == num]
        found.append((pos, cands[-1] if cands else f"????-{num:02d}"))
    if _has(text, LATEST) or any(k in text for k in LATEST):
        found.append((text.find("last") if "last" in text else 0, avail[-1]))
    out: list[str] = []
    for _, ym in sorted(found):
        if ym not in out:
            out.append(ym)
    return out


def _metric_for(text: str, card: Card) -> tuple[str | None, bool]:
    for key, meta in card.metrics.items():
        label = meta.get("label", key).lower()
        words = [label, key.lower()] + next((w for k, w in METRIC_WORDS.items() if k in label or k in key.lower()), [])
        if _has(text, words):
            return key, True
    return next(iter(card.metrics), None), False


# ---------- rule-based planner ----------
def rule_plan(question: str, df: pd.DataFrame, card: Card) -> PlannerOut:
    q = question.lower().strip()
    avail = sorted(df[card.time_column].unique())
    notes: list[str] = []
    if _has(q, ["anomal", "unusual", "abnormal", "outlier", "wasting", "wasted", "spike", "suspicious", "irregular", "leak", "strange", "weird", "unexpected", "fishy", "anything wrong", "wastage", "wasteful", "any waste", "waste in", "waste of", "असामान्य", "बर्बाद", "बर्बादी"] + LEX["unusual"]):
        metric, matched = _metric_for(q, card)
        if not matched and len(card.metrics) > 1:
            notes.append(f"No metric named, so assumed {card.metrics[metric].get('label', metric)}.")
        return PlannerOut(Plan(intent="anomaly", metric=metric), "rules", notes)
    for words, what in ((LEX["student"], "student headcount"), (LEX["cost"], "cost / tariff data"), (LEX["carbon"], "an emission factor")):
        if _has(q, words):
            return PlannerOut(Plan(intent="unavailable", missing_field=what), "rules")
    if BILL_RE.search(q):
        return PlannerOut(Plan(intent="unavailable", missing_field="cost / tariff data"), "rules")
    for stem, what in UNAVAILABLE.items():
        if _has(q, [stem]):
            return PlannerOut(Plan(intent="unavailable", missing_field=what), "rules")
    metric, matched = _metric_for(q, card)
    if not matched and len(card.metrics) > 1:
        notes.append(f"No metric named, so assumed {card.metrics[metric].get('label', metric)}.")
    ents = [e for e in df[card.entity_column].unique() if e.lower() in q]
    entity = ents[0] if len(ents) == 1 else None
    months = find_months(q, avail)
    n = re.search(r"top\s+(\d+)", q)
    top_n = int(n.group(1)) if n else 5
    asc = _has(q, ASC_WORDS)
    base = dict(metric=metric, entity=entity)

    cmp_words = _has(q, ["compar", "vs", "versus", "tulna", "तुलना", "jump", "increas", "decreas", "drop", "rise", "rose", "fell", "badh", "बढ़"] + LEX["compare"])
    if len(months) >= 2 and (cmp_words or _has(q, ["change", "between", "from", "badla", "बदल"])):
        return PlannerOut(Plan(intent="compare", period_a=months[0], period_b=months[1], **base), "rules", notes)
    if cmp_words:
        return PlannerOut(Plan(intent="compare", **base), "rules", notes)
    if _has(q, ["averag", "avg", "mean", "ausat", "औसत"] + LEX["average"]):
        return PlannerOut(Plan(intent="average", **base), "rules", notes)
    if _has(q, ["trend", "over time", "over the year", "month by month", "change", "pattern", "across months", "badla", "बदल", "रुझान"] + LEX["trend"]):
        return PlannerOut(Plan(intent="trend", **base), "rules", notes)
    if _has(q, ["total", "kul", "कुल", "overall", "altogether", "sum"] + LEX["total"]):
        return PlannerOut(Plan(intent="total", month=months[0] if months else None, **base), "rules", notes)
    if _has(q, ["most", "highest", "max", "top", "least", "lowest", "min", "zyada", "ज्यादा", "ज़्यादा", "sabse", "सबसे", "kam", "कम", "which", "kaun", "कौन", "kisne", "rank"] + LEX["most"] + LEX["least"] + LEX["which"]):
        return PlannerOut(Plan(intent="rank", month=months[0] if months else None, order="asc" if asc else "desc",
                               top_n=top_n, metric=metric), "rules", notes)
    if months or entity:
        return PlannerOut(Plan(intent="total", month=months[0] if months else None, **base), "rules", notes)
    return PlannerOut(Plan(intent="unavailable", missing_field="a supported question type (ranking, total, average, trend or comparison)"), "rules")


# ---------- Gemma 4 planner ----------
def _system_prompt(df: pd.DataFrame, card: Card) -> str:
    months = sorted(df[card.time_column].unique())
    return (
        "You turn a user's question about a small dataset into a JSON analysis plan. Never answer the question.\n"
        f"Dataset: {card.name}. Entity column: {card.entity_column}. Time column: {card.time_column} (YYYY-MM).\n"
        f"Metrics (use the key exactly): {json.dumps({k: v.get('label', k) + ' [' + v.get('unit', '') + ']' for k, v in card.metrics.items()})}\n"
        f"Entities: {json.dumps(sorted(df[card.entity_column].unique().tolist()))}\n"
        f"Months available: {months[0]} to {months[-1]}. 'last month' means {months[-1]}.\n"
        "Intents: rank (entities ordered by a metric, for one month or the whole period; order asc = lowest first), "
        "total, average (per month), trend (monthly series, optionally for one entity), "
        "compare (period_a vs period_b), anomaly (find unusual / wasteful readings the user did not name; metric only), unavailable (needs data the dataset does not have; set missing_field).\n"
        f"Data NOT available: {card.not_available}. If a question needs any of these, or anything else not in the columns, use unavailable.\n"
        "HARD RULES: (1) Always set metric to one of the exact keys above (never null) unless intent is unavailable. "
        f"(2) Set entity ONLY to an exact name from the Entities list when the question names one; otherwise null. Never write the word '{card.entity_column}' as an entity. "
        "(3) If the question names a month, convert it to YYYY-MM using the months available: set month for rank/total, or period_a and period_b (earlier first) for compare. "
        "(4) If the question does not name a month for rank/total, month is null (whole period).\n"
        + _examples(df, card) +
        "The question may be English, Hindi or Hinglish. Output JSON only, matching the schema.")


def _examples(df: pd.DataFrame, card: Card) -> str:
    months = sorted(df[card.time_column].unique())
    ents = sorted(df[card.entity_column].unique())
    keys = list(card.metrics)
    m0, m1 = keys[0], keys[-1]
    l0, l1 = (card.metrics[k].get("label", k).lower() for k in (m0, m1))
    e0 = ents[0]
    mo = lambda i: months[min(i, len(months) - 1)]
    def nm(ym):  # month name for the example question
        import calendar
        return calendar.month_name[int(ym[5:7])]
    ex = [
        (f"Which {card.entity_column} used the most {l1} in {nm(mo(2))}?", dict(intent="rank", metric=m1, month=mo(2), order="desc", top_n=5)),
        (f"Total {l0} in {nm(mo(5))}", dict(intent="total", metric=m0, month=mo(5))),
        (f"{e0} {l1} trend", dict(intent="trend", metric=m1, entity=e0)),
        (f"Compare {e0} {l0} between {nm(mo(1))} and {nm(mo(2))}", dict(intent="compare", metric=m0, entity=e0, period_a=mo(1), period_b=mo(2))),
        (f"Which {card.entity_column} used the least {l0} last month?", dict(intent="rank", metric=m0, month=months[-1], order="asc", top_n=5)),
    ]
    return "Examples:\n" + "\n".join(f"Q: {q}\nJSON: {json.dumps(j)}" for q, j in ex) + "\n"


GENERIC = {"", "building", "buildings", "block", "blocks", "campus", "all", "none", "null", "any", "entity", "n/a", "na", "everything"}


def _norm_month(v, avail):
    if v is None:
        return None
    v = str(v).strip()
    if re.fullmatch(r"\d{4}-\d{2}", v):
        return v
    found = find_months(v.lower(), avail)
    return found[0] if found else v


def repair_plan(plan: Plan, question: str, df: pd.DataFrame, card: Card) -> tuple[Plan, list[str]]:
    """Cross-check the model's plan against deterministic facts from the question; fix, and say so in the receipt.
    Small models often leave metric/month null, write 'May' instead of 2025-05, or put the word 'building' as entity."""
    notes: list[str] = []
    if plan.intent == "unavailable":
        return plan, notes
    q = question.lower()
    avail = sorted(df[card.time_column].unique())
    ents = list(df[card.entity_column].unique())
    # entity
    if plan.entity is not None:
        low = plan.entity.strip().lower()
        hit = next((e for e in ents if e.lower() == low), None) or next((e for e in ents if low and (low in e.lower() or e.lower() in low)), None)
        if hit:
            plan.entity = hit
        elif low in GENERIC:
            plan.entity = None
            notes.append(f"Repaired: model wrote '{low}' as an entity; treated as no entity filter.")
    named = [e for e in ents if e.lower() in q]
    if plan.entity is None and len(named) == 1 and plan.intent in ("trend", "average", "total", "compare"):
        plan.entity = named[0]
        notes.append(f"Repaired: question names {named[0]}; added it as the entity filter.")
    # metric
    if plan.metric not in card.metrics:
        guess, matched = _metric_for(q, card)
        plan.metric = guess
        notes.append(f"Repaired: model gave no valid metric; {'read it from the question' if matched else 'assumed the first metric'} ({guess}).")
    # months
    for f in ("month", "period_a", "period_b"):
        v = getattr(plan, f)
        nv = _norm_month(v, avail)
        if nv != v:
            setattr(plan, f, nv)
            notes.append(f"Repaired: normalised '{v}' to {nv}.")
    in_q = find_months(q, avail)
    if plan.intent in ("rank", "total") and not plan.month and in_q:
        plan.month = in_q[0]
        notes.append(f"Repaired: question names a month; set month to {in_q[0]}.")
    if plan.intent == "compare" and not (plan.period_a and plan.period_b) and len(in_q) >= 2:
        plan.period_a, plan.period_b = in_q[0], in_q[1]
        notes.append(f"Repaired: set comparison periods to {in_q[0]} and {in_q[1]} from the question.")
    if plan.intent == "rank" and plan.order == "desc" and _has(q, ASC_WORDS):
        plan.order = "asc"
        notes.append("Repaired: question asks for the lowest; set order to ascending.")
    return plan, notes


def gemma_plan(question: str, df: pd.DataFrame, card: Card, model: str = DEFAULT_MODEL) -> PlannerOut:
    raw = ollama_chat(model, _system_prompt(df, card), question, schema=Plan.model_json_schema())
    return PlannerOut(Plan.model_validate_json(raw), model)


def plan_question(question: str, df: pd.DataFrame, card: Card, use_gemma: bool = True, model: str = DEFAULT_MODEL) -> PlannerOut:
    if use_gemma:
        try:
            po = gemma_plan(question, df, card, model)
            po.plan, repairs = repair_plan(po.plan, question, df, card)
            po.notes.extend(repairs)
            return po
        except Exception as e:  # model offline / bad JSON -> deterministic fallback, and say so
            out = rule_plan(question, df, card)
            out.notes.append(f"Gemma planner unavailable ({type(e).__name__}); used the rule-based planner instead.")
            return out
    return rule_plan(question, df, card)

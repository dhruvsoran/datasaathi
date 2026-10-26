"""20-question evaluation with independently computed expected answers.
Usage: python evals/run_evals.py                      (rule-based planner, offline)
       python evals/run_evals.py --gemma              (Gemma 4 via Ollama)
       python evals/run_evals.py --heldout [--gemma]  (10 extra questions written AFTER prompt tuning; never used to tune)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datasaathi.card import load_card, load_data
from datasaathi.pipeline import answer

ROOT = Path(__file__).resolve().parents[1]
card = load_card((ROOT / "data/campus_utilities.card.yaml").read_text())
df = load_data(ROOT / "data/campus_utilities.csv", card)
E, T = "building", "month"
LAST = "2026-03"


def by_bldg(metric, month=None):                  # independent pandas, not the engine's code
    d = df if month is None else df[df[T] == month]
    return d.groupby(E)[metric].sum(min_count=1).dropna()


def month_total(metric, m, b=None):
    d = df[df[T] == m]
    d = d[d[E] == b] if b else d
    return float(d[metric].sum())


CASES = [  # (question, expected status, check(answer) -> bool)
    ("Which building used the most electricity last month?", "answered", lambda a: a.result.table.iloc[0][E] == by_bldg("electricity_kwh", LAST).idxmax()),
    ("Which building used the least water in September?", "answered", lambda a: a.result.table.iloc[0][E] == by_bldg("water_kl", "2025-09").idxmin()),
    ("Compare electricity use in September and October", "answered", lambda a: abs(a.result.facts["total_change"] - (month_total("electricity_kwh", "2025-10") - month_total("electricity_kwh", "2025-09"))) < 1),
    ("How did the Engineering Block's electricity change over the year?", "answered", lambda a: a.plan.intent == "trend" and a.plan.entity == "Engineering Block"),
    ("What was total water use in June?", "answered", lambda a: abs(a.result.facts["total"] - month_total("water_kl", "2025-06")) < 1),
    ("Average monthly electricity of Library", "answered", lambda a: abs(a.result.facts["average"] - df[df[E] == "Library"].electricity_kwh.mean()) < 1),
    ("Top 3 buildings by water use", "answered", lambda a: list(a.result.table[E]) == list(by_bldg("water_kl").nlargest(3).index)),
    ("पिछले महीने सबसे ज्यादा बिजली किस बिल्डिंग ने इस्तेमाल की?", "answered", lambda a: a.result.table.iloc[0][E] == by_bldg("electricity_kwh", LAST).idxmax()),
    ("June mein sabse zyada paani kisne use kiya?", "answered", lambda a: a.result.table.iloc[0][E] == by_bldg("water_kl", "2025-06").idxmax()),
    ("Compare Boys Hostel water between May and June", "answered", lambda a: abs(a.result.facts["total_change"] - (month_total("water_kl", "2025-06", "Boys Hostel") - month_total("water_kl", "2025-05", "Boys Hostel"))) < 1),
    ("What is the electricity use per student?", "refused", lambda a: "student" in a.text),
    ("What was the carbon footprint of the library?", "refused", lambda a: "emission" in a.text),
    ("How much did we spend on electricity bills in July?", "refused", lambda a: "cost" in a.text),
    ("Total electricity in December", "answered", lambda a: abs(a.result.facts["total"] - month_total("electricity_kwh", "2025-12")) < 1),
    ("Which building had the lowest electricity in 2025-12?", "answered", lambda a: a.result.table.iloc[0][E] == by_bldg("electricity_kwh", "2025-12").idxmin()),
    ("Trend of campus water use", "answered", lambda a: a.plan.intent == "trend" and a.plan.entity is None),
    ("Which building's electricity jumped most from May to June?", "answered", lambda a: a.result.table.iloc[0][E] == (by_bldg("electricity_kwh", "2025-06") - by_bldg("electricity_kwh", "2025-05")).idxmax()),
    ("Cafeteria water usage trend", "answered", lambda a: any("Cafeteria in 2025-08" in c for c in a.result.caveats)),
    ("Weather impact on Sports Complex electricity", "refused", lambda a: "weather" in a.text),
    ("Show electricity usage for Library in March 2026", "refused", lambda a: "missing observation" in a.text),
]


HELDOUT = [
    ("Tell me the building with the highest water consumption in April", "answered", lambda a: a.result.table.iloc[0][E] == by_bldg("water_kl", "2025-04").idxmax()),
    ("How much electricity did the Library use in total?", "answered", lambda a: abs(a.result.facts["total"] - df[df[E] == "Library"].electricity_kwh.sum()) < 1),
    ("Show me how the Sports Complex's water changed through the year", "answered", lambda a: a.plan.intent == "trend" and a.plan.entity == "Sports Complex" and a.plan.metric == "water_kl"),
    ("Which building consumed the least electricity in November?", "answered", lambda a: a.result.table.iloc[0][E] == by_bldg("electricity_kwh", "2025-11").idxmin()),
    ("Compare water between January and February", "answered", lambda a: abs(a.result.facts["total_change"] - (month_total("water_kl", "2026-02") - month_total("water_kl", "2026-01"))) < 1),
    ("What's the average monthly water use for the Cafeteria?", "answered", lambda a: abs(a.result.facts["average"] - df[df[E] == "Cafeteria"].groupby(T).water_kl.sum(min_count=1).dropna().mean()) < 1),
    ("Is there anything strange in electricity use?", "answered", lambda a: a.plan.intent == "anomaly" and "Girls Hostel" in set(a.result.table[E])),
    ("What is the water bill for August?", "refused", lambda a: "cost" in a.text),
    ("How many students live in the Boys Hostel?", "refused", lambda a: "student" in a.text),
    ("Total electricity for Admin Block in 2025-07", "answered", lambda a: abs(a.result.facts["total"] - month_total("electricity_kwh", "2025-07", "Admin Block")) < 1),
]


def main(use_gemma: bool, cases=None) -> int:
    cases = CASES if cases is None else cases
    ok = 0
    for q, status, check in cases:
        try:
            a = answer(q, df, card, use_gemma=use_gemma)
            passed = a.status == status and check(a) and (a.guard is None or a.guard.ok)
        except Exception as e:
            passed, a = False, e
        ok += passed
        print(("PASS " if passed else "FAIL ") + q + ("" if passed else f"   -> {getattr(a, 'text', a)}"))
    print(f"\n{ok}/{len(cases)} passed ({'Gemma 4' if use_gemma else 'rule-based planner'}{', held-out set' if cases is HELDOUT else ''})")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main("--gemma" in sys.argv, HELDOUT if "--heldout" in sys.argv else None))

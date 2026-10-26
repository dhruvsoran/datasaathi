import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datasaathi.card import load_card, load_data
from datasaathi.plan import Plan, validate_plan
from datasaathi.planner import _system_prompt, repair_plan

ROOT = Path(__file__).resolve().parents[1]
card = load_card((ROOT / "data/campus_utilities.card.yaml").read_text())
df = load_data(ROOT / "data/campus_utilities.csv", card)


def fix(plan, q):
    p, notes = repair_plan(plan, q, df, card)
    return validate_plan(p, df, card)[0], notes


def test_generic_entity_word_is_dropped():       # real Gemma failure: entity="building"
    p, n = fix(Plan(intent="rank", metric="electricity_kwh", entity="building", month="2026-03"), "Which building used the most electricity last month?")
    assert p.intent == "rank" and p.entity is None and n


def test_null_metric_is_read_from_question():    # real Gemma failure: metric=None
    p, _ = fix(Plan(intent="trend", metric=None), "Cafeteria water usage trend")
    assert p.intent == "trend" and p.metric == "water_kl" and p.entity == "Cafeteria"


def test_missing_month_is_filled_from_question():  # real Gemma failure: whole-period total
    p, _ = fix(Plan(intent="total", metric="water_kl"), "What was total water use in June?")
    assert p.month == "2025-06"
    p, _ = fix(Plan(intent="total", metric="electricity_kwh"), "Show electricity usage for Library in March 2026")
    assert p.month == "2026-03" and p.entity == "Library"


def test_month_names_are_normalised():             # real Gemma failure: period 'May'
    p, _ = fix(Plan(intent="compare", metric="water_kl", entity="Boys Hostel", period_a="May", period_b="June"), "Compare Boys Hostel water between May and June")
    assert (p.period_a, p.period_b) == ("2025-05", "2025-06")


def test_prompt_has_rules_and_examples():
    s = _system_prompt(df, card)
    assert "HARD RULES" in s and "Examples:" in s and "2025-" in s


def test_unavailable_is_left_alone():
    p, n = repair_plan(Plan(intent="unavailable", missing_field="students"), "per student?", df, card)
    assert p.intent == "unavailable" and not n

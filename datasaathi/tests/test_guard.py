import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datasaathi.card import load_card, load_data
from datasaathi.explain import number_guard
from datasaathi.pipeline import answer

ROOT = Path(__file__).resolve().parents[1]
card = load_card((ROOT / "data/campus_utilities.card.yaml").read_text())
df = load_data(ROOT / "data/campus_utilities.csv", card)
res = answer("Which building used the most electricity last month?", df, card, use_gemma=False).result


def test_guard_accepts_computed_numbers():
    assert number_guard("Boys Hostel used 47,829 kWh in 2026-03.", res).ok


def test_guard_rejects_invented_number():
    g = number_guard("Boys Hostel used 52,000 kWh in 2026-03.", res)
    assert not g.ok and "52,000" in g.unverified


def test_no_arbitrary_code_paths():
    # unknown metric / entity / month become refusals, never executed
    for q in ["Electricity of Hostel Z", "Compare electricity in January 2030 and February 2030"]:
        assert answer(q, df, card, use_gemma=False).status == "refused"

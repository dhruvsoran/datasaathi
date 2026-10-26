"""Run this FIRST on your machine: confirms Ollama + Gemma 4 work end to end with DataSaathi."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datasaathi.card import load_card, load_data
from datasaathi.planner import DEFAULT_MODEL, gemma_plan, ollama_models
from datasaathi.pipeline import answer

root = Path(__file__).resolve().parents[1]
card = load_card((root / "data/campus_utilities.card.yaml").read_text())
df = load_data(root / "data/campus_utilities.csv", card)
models = ollama_models()
print("Ollama models:", models or "NONE (is `ollama serve` running?)")
if not models:
    sys.exit(1)
model = next((m for m in models if "gemma4" in m), DEFAULT_MODEL)
print("Using:", model)
for q in ["Which building used the most electricity last month?", "पिछले महीने सबसे ज्यादा पानी किसने इस्तेमाल किया?"]:
    po = gemma_plan(q, df, card, model)
    print("\nQ:", q, "\nPlan:", json.dumps(po.plan.model_dump(exclude_none=True)))
    a = answer(q, df, card, use_gemma=True, model=model)
    print("Answer:", a.text, "\n(planner:", a.planner, "| explainer:", a.explainer, "| guard ok:", a.guard.ok if a.guard else None, ")")
print("\nNext: python evals/run_evals.py --gemma")

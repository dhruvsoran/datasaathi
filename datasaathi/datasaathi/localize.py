"""Answer in the user's language. Gemma 4 translates the verified English answer; Number Guard checks the numbers."""
from __future__ import annotations
import re
from .explain import guard_values
from .lexicon import is_indic
from .planner import DEFAULT_MODEL, ollama_chat

_NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def localize(text: str, question: str, model: str | None = None) -> tuple[str, bool]:
    """Return (text, was_translated). Falls back to the English text if the model fails or changes any number."""
    if not text or not is_indic(question):
        return text, False
    try:
        system = ("Translate the TEXT into the same language and script as the QUESTION. Keep every number, unit, building name and "
                  "date exactly as written, using digits 0-9. Do not add or remove information. Output only the translation.")
        out = ollama_chat(model or DEFAULT_MODEL, system, f"QUESTION: {question}\nTEXT: {text}").strip()
        allowed = {float(t.replace(",", "")) for t in _NUM.findall(text)}
        g = guard_values(out, allowed, small_ok=set(range(0, 13)))
        if out and g.ok:
            return out, True
    except Exception:
        pass
    return text, False

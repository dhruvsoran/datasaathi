import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datasaathi import data_trust, logs, waste_radar
from datasaathi.card import load_card, load_data
from datasaathi.explain import guard_values
from datasaathi.pipeline import answer

ROOT = Path(__file__).resolve().parents[1]


def ds(name):
    card = load_card((ROOT / f"data/{name}.card.yaml").read_text())
    return load_data(ROOT / f"data/{name}.csv", card), card


def test_radar_finds_planted_vacation_waste_and_nothing_else():
    df, card = ds("campus_utilities")
    f = waste_radar.scan(df, card)
    assert {(x.entity, x.period, x.kind) for x in f} == {("Girls Hostel", "2025-06", "held_load")}
    assert any(x.metric == "electricity_kwh" for x in f) and any(x.metric == "water_kl" for x in f)


def test_radar_text_numbers_are_verified():
    df, card = ds("campus_utilities")
    f = waste_radar.scan(df, card)[0]
    assert guard_values(f.text(), {float(v) for v in f.facts().values()}).ok


def test_trust_clean_vs_messy():
    clean = data_trust.audit(*ds("campus_utilities"))
    messy = data_trust.audit(*ds("messy_demo"))
    assert clean.overall >= 95 and messy.overall < 80
    txt = " ".join(m for _, m in messy.issues)
    for needle in ("duplicate", "negative", "typo", "absent"):
        assert needle in txt


def test_answers_warn_on_dirty_data():
    df, card = ds("messy_demo")
    a = answer("Total electricity in September", df, card, use_gemma=False)
    assert a.trust_score is not None and a.trust_score < 80
    assert any("duplicate" in c for c in a.result.caveats)


def test_duckdb_query_log():
    os.environ["DATASAATHI_DB"] = os.path.join(tempfile.mkdtemp(), "t.duckdb")
    df, card = ds("campus_utilities")
    answer("Total water in June", df, card, use_gemma=False, log=True)
    answer("electricity per student", df, card, use_gemma=False, log=True)
    h = logs.history()
    assert len(h) == 2 and set(h.status) == {"answered", "refused"}


def test_trust_warnings_only_when_flagged_rows_are_used():
    df, card = ds("messy_demo")
    march = answer("Which building used the most electricity last month?", df, card, use_gemma=False)
    assert not any("Data Trust" in c for c in march.result.caveats)           # typo is in July, duplicate in September
    assert any("elsewhere" in n for n in march.notes)
    july = answer("Which building used the most electricity in July?", df, card, use_gemma=False)
    assert any("suspicious" in c for c in july.result.caveats)
    sept = answer("Which building used the most water in September?", df, card, use_gemma=False)
    assert any("duplicate" in c for c in sept.result.caveats)


def test_close_ranking_and_tiny_change_are_flagged():
    import pandas as pd
    from datasaathi.engine import run
    from datasaathi.plan import Plan
    card = load_card((ROOT / "data/campus_utilities.card.yaml").read_text())
    rows = [(b, m, v, 1.0) for b, v in (("A", 1000), ("B", 990), ("C", 500)) for m in ("2026-01", "2026-02")]
    d = pd.DataFrame(rows, columns=["building", "month", "electricity_kwh", "water_kl"])
    r = run(Plan(intent="rank", metric="electricity_kwh", month="2026-01"), d, card)
    assert any("close" in c for c in r.caveats)
    c = run(Plan(intent="compare", metric="electricity_kwh", period_a="2026-01", period_b="2026-02"), d, card)
    assert any("small" in x for x in c.caveats)


def test_waste_questions_trigger_the_radar_but_waste_records_are_refused():
    df, card = ds("campus_utilities")
    a = answer("Is there any waste in water use?", df, card, use_gemma=False)
    assert a.plan.intent == "anomaly" and a.status == "answered"
    b = answer("How much waste was collected last month?", df, card, use_gemma=False)
    assert b.status == "refused"


# ---------------- Indian languages (rule-based planner) ----------------
import pytest

LANG_CASES = [
    ("Gujarati", "ગયા મહિને સૌથી વધુ વીજળી કઈ બિલ્ડિંગે વાપરી?", "rank", "electricity_kwh", "2026-03"),
    ("Tamil", "கடந்த மாதம் அதிக மின்சாரம் பயன்படுத்திய கட்டிடம் எது?", "rank", "electricity_kwh", "2026-03"),
    ("Punjabi", "ਪਿਛਲੇ ਮਹੀਨੇ ਸਭ ਤੋਂ ਵੱਧ ਬਿਜਲੀ ਕਿਹੜੀ ਇਮਾਰਤ ਨੇ ਵਰਤੀ?", "rank", "electricity_kwh", "2026-03"),
    ("Marathi", "मागील महिन्यात सर्वाधिक वीज कोणत्या इमारतीने वापरली?", "rank", "electricity_kwh", "2026-03"),
    ("Bengali", "গত মাসে কোন ভবন সবচেয়ে বেশি বিদ্যুৎ ব্যবহার করেছে?", "rank", "electricity_kwh", "2026-03"),
    ("Telugu", "గత నెల ఏ భవనం అత్యధిక విద్యుత్ వాడింది?", "rank", "electricity_kwh", "2026-03"),
    ("Kannada", "ಕಳೆದ ತಿಂಗಳು ಯಾವ ಕಟ್ಟಡ ಅತಿ ಹೆಚ್ಚು ವಿದ್ಯುತ್ ಬಳಸಿತು?", "rank", "electricity_kwh", "2026-03"),
    ("Malayalam", "കഴിഞ്ഞ മാസം ഏറ്റവും കൂടുതൽ വൈദ്യുതി ഉപയോഗിച്ച കെട്ടിടം ഏത്?", "rank", "electricity_kwh", "2026-03"),
    ("Hindi", "पिछले महीने सबसे ज्यादा बिजली किस बिल्डिंग ने इस्तेमाल की?", "rank", "electricity_kwh", "2026-03"),
    ("Gujarati-water-june", "જૂનમાં સૌથી વધુ પાણી કોણે વાપર્યું?", "rank", "water_kl", "2025-06"),
    ("Tamil-water-june", "ஜூன் மாதத்தில் அதிக தண்ணீர் பயன்படுத்திய கட்டிடம் எது?", "rank", "water_kl", "2025-06"),
    ("Punjabi-total", "ਜੂਨ ਵਿੱਚ ਕੁੱਲ ਪਾਣੀ ਦੀ ਵਰਤੋਂ ਕਿੰਨੀ ਸੀ?", "total", "water_kl", "2025-06"),
]


@pytest.mark.parametrize("name,q,intent,metric,month", LANG_CASES)
def test_indian_language_questions(name, q, intent, metric, month):
    df, card = ds("campus_utilities")
    a = answer(q, df, card, use_gemma=False)
    assert a.status == "answered", (name, a.text)
    assert (a.plan.intent, a.plan.metric, a.plan.month) == (intent, metric, month), (name, a.plan)


@pytest.mark.parametrize("q", [
    "પ્રતિ વિદ્યાર્થી વીજળીનો ઉપયોગ કેટલો?",           # Gujarati: per student
    "ஒரு மாணவருக்கு மின்சார பயன்பாடு என்ன?",            # Tamil: per student
    "ਪ੍ਰਤੀ ਵਿਦਿਆਰਥੀ ਬਿਜਲੀ ਦੀ ਵਰਤੋਂ ਕਿੰਨੀ ਹੈ?",         # Punjabi: per student
    "जुलाई का बिजली का बिल कितना आया?",                # Hindi: bill
])
def test_indian_language_unavailable_questions_are_refused(q):
    df, card = ds("campus_utilities")
    assert answer(q, df, card, use_gemma=False).status == "refused"


# ---------------- translation and voice plumbing ----------------
def test_localize_keeps_numbers_or_falls_back(monkeypatch):
    import datasaathi.localize as loc
    en = "Boys Hostel had the highest electricity use in 2026-03: 47,829 kWh."
    q = "ગયા મહિને સૌથી વધુ વીજળી કઈ બિલ્ડિંગે વાપરી?"
    monkeypatch.setattr(loc, "ollama_chat", lambda *a, **k: "બોયઝ હોસ્ટેલે 2026-03 માં સૌથી વધુ વીજળી વાપરી: 47,829 kWh.")
    text, ok = loc.localize(en, q, "gemma4:e4b")
    assert ok and "47,829" in text
    monkeypatch.setattr(loc, "ollama_chat", lambda *a, **k: "બોયઝ હોસ્ટેલે 52,000 kWh વાપરી.")      # invented number
    text, ok = loc.localize(en, q, "gemma4:e4b")
    assert not ok and text == en
    assert loc.localize(en, "Which building used the most?", "x") == (en, False)                    # English question: untouched


def _wav(rate=48000, channels=1, seconds=1.0, width=2):
    import io, wave
    import numpy as np
    t = np.linspace(0, seconds, int(rate * seconds), False)
    x = 0.4 * np.sin(2 * np.pi * 220 * t)
    if channels == 2:
        x = np.stack([x, x * 0.5], axis=1).reshape(-1)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(channels); w.setsampwidth(width); w.setframerate(rate)
        w.writeframes((x * (2 ** (8 * width - 1) - 1)).astype({1: "u1", 2: "<i2", 4: "<i4"}[width]).tobytes() if width != 1 else ((x * 127 + 128).astype("u1")).tobytes())
    return buf.getvalue()


def test_wav_decoding_does_not_need_pyav():
    import numpy as np
    from datasaathi import voice
    for rate, ch in [(48000, 1), (44100, 1), (16000, 1), (48000, 2)]:
        a = voice.wav_to_audio(_wav(rate, ch))
        assert a.dtype == np.float32 and a.ndim == 1
        assert abs(len(a) - 16000) <= 2 and 0.05 < np.abs(a).max() <= 1.0, (rate, ch, len(a))
    assert len(voice.wav_to_audio(_wav(16000, 1, 1.0, 4))) == 16000      # 32-bit PCM too


def test_voice_transcribe_with_injected_model():
    import numpy as np
    from datasaathi import voice

    class Seg:
        def __init__(self, t): self.text = t

    class Info:
        language = "gu"

    class Fake:
        def transcribe(self, audio, **kw):
            assert isinstance(audio, np.ndarray) and audio.dtype == np.float32       # decoded here, not by PyAV
            assert kw["language"] == "gu" and kw["task"] == "transcribe"
            return [Seg(" ગયા મહિને "), Seg("સૌથી વધુ વીજળી")], Info()

    text, lang = voice.transcribe(_wav(), "gu", model=Fake())
    assert text == "ગયા મહિને સૌથી વધુ વીજળી" and lang == "gu"
    assert set(voice.STT_LANGUAGES.values()) >= {"hi", "gu", "ta", "pa", "mr", "bn", "te", "kn", "ml", "en"}


def test_upload_without_card_infers_columns_on_any_pandas():
    import pandas as pd
    import pytest
    from datasaathi.card import infer_card
    raw = pd.read_csv(ROOT / "data/campus_demo_upload.csv")        # pandas 3 reads text as `str`, pandas 2 as `object`
    c = infer_card(raw)
    assert (c.entity_column, c.time_column, list(c.metrics)) == ("block", "month", ["electricity_kwh", "water_kl"])
    with pytest.raises(ValueError):
        infer_card(pd.DataFrame({"a": [1, 2], "b": [3, 4]}))       # no name or month column: a clear error, not IndexError


def test_silent_recording_is_detected():
    import io, wave
    from datasaathi import voice
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
        w.writeframes(b"\x00\x00" * 96000)                      # 2 s of digital silence (muted microphone)
    secs, peak = voice.level(buf.getvalue())
    assert abs(secs - 2.0) < 0.01 and peak < voice.SILENT_PEAK
    assert voice.level(_wav())[1] > voice.SILENT_PEAK
    assert voice.level(b"not a wav") is None


def test_real_audio_path_reaches_whisper_vad_without_error():
    """Runs faster-whisper's own voice-activity detector on a decoded recording (needs faster-whisper installed)."""
    import pytest
    pytest.importorskip("faster_whisper")
    from faster_whisper.vad import VadOptions, get_speech_timestamps
    from datasaathi import voice
    a = voice.wav_to_audio(_wav(48000, 1, 2.0))
    get_speech_timestamps(a, VadOptions())              # raises if the array is the wrong type or shape


def test_suggestions_are_written_from_the_loaded_data():
    import io
    import pandas as pd
    from datasaathi.card import infer_card
    from datasaathi.suggest import suggestions
    df, card = ds("campus_utilities")
    groups = suggestions(df, card)
    assert "Try to break it" not in groups and set(groups) == {"Rank and compare", "Trends and totals", "In your language"}
    assert any("2026" in q for q in groups["Rank and compare"])                      # the file's own months
    assert any(q.startswith(str(n)) for n in df[card.entity_column].unique() for q in groups["Trends and totals"])
    # an unrelated CSV without a Data Card: its own words, no electricity/water questions in Indian languages
    rows = [f"Ward {w},2024-{m:02d},{40 + w * 7 + m},{w + m % 3}" for w in range(1, 5) for m in range(1, 13)]
    csv = "ward_name,month,garbage_tonnes,complaints\n" + "\n".join(rows)
    card2 = infer_card(pd.read_csv(io.StringIO(csv)))
    df2 = load_data(io.StringIO(csv), card2)
    g2 = suggestions(df2, card2)
    qs = [q for v in g2.values() for q in v]
    assert "In your language" not in g2 and any("ward" in q and "garbage" in q for q in qs) and any("December 2024" in q for q in qs)
    for q in qs:                                                                      # every suggestion is answerable from that file
        a = answer(q, df2, card2, use_gemma=False)
        assert a.status == "answered", q

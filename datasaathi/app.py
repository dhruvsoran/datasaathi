"""DataSaathi 2.0: ask community data questions in English or Indian languages, by typing or speaking.
Every answer is computed by code and ships with a Proof Receipt.
Tabs: Ask · Waste Radar · Data Trust · History. 2.0 changes only the visual layer (ui.py, theme.css, charts)."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from datasaathi import data_trust, logs, ui, voice, waste_radar
from datasaathi.card import infer_card, load_card, load_data
from datasaathi.charts import make_chart
from datasaathi.pipeline import answer
from datasaathi.planner import DEFAULT_MODEL, ollama_models, ollama_warm

ROOT = Path(__file__).parent
st.set_page_config(page_title="DataSaathi: ask your campus data", page_icon="🛰️", layout="wide", initial_sidebar_state="expanded")
st.markdown(ui.CSS, unsafe_allow_html=True)
show_intro = not st.session_state.get("intro_seen") and st.query_params.get("intro") != "0"   # welcome curtain: once per session (?intro=0 skips it)
# The curtain always gets its own slot, empty after the first run. Without it every element below would move up one place on
# the next run, and while that run is busy (answering, transcribing) the old tabs and suggestions would show as a second copy.
intro_slot = st.empty()
if show_intro:
    st.session_state["intro_n"] = st.session_state.get("intro_n", 0) + 1
    intro_slot.markdown(ui.intro(st.session_state["intro_n"]), unsafe_allow_html=True)
    st.session_state["intro_seen"] = True

SUGGESTIONS = {
    "Rank and compare": ["Which building used the most electricity last month?",
                         "Compare electricity use in September and October",
                         "Which building's water use dropped most from May to June?"],
    "Trends and Indian languages": ["Cafeteria water usage trend",
                                    "पिछले महीने सबसे ज्यादा बिजली किस बिल्डिंग ने इस्तेमाल की?",
                                    "ગયા મહિને સૌથી વધુ વીજળી કઈ બિલ્ડિંગે વાપરી?",
                                    "கடந்த மாதம் அதிக மின்சாரம் பயன்படுத்திய கட்டிடம் எது?",
                                    "ਪਿਛਲੇ ਮਹੀਨੇ ਸਭ ਤੋਂ ਵੱਧ ਬਿਜਲੀ ਕਿਹੜੀ ਇਮਾਰਤ ਨੇ ਵਰਤੀ?"],
    "Try to break it": ["What is the electricity use per student?",
                        "Show electricity usage for Library in March 2026",
                        "Is there any waste in water use?"],
}
GROUP_LOOK = {"Rank and compare": ("rank", ui.AMBER, ":material/leaderboard:"),
              "Trends and Indian languages": ("globe", ui.TEAL, ":material/translate:"),
              "Try to break it": ("flask", ui.CORAL, ":material/science:")}

@st.cache_resource(show_spinner=False)
def warm_model(name: str):
    """Load Gemma into memory in the background once per model, so the first question does not wait for the load."""
    import threading
    threading.Thread(target=ollama_warm, args=(name,), daemon=True).start()
    return True


@st.cache_resource(show_spinner=False)
def warm_voice():
    """Load the speech model in the background once, so the first voice note does not wait for it."""
    import threading
    threading.Thread(target=voice.warm, daemon=True).start()
    return True


# ---------------- sidebar ----------------
with st.sidebar:
    st.markdown(ui.brand(), unsafe_allow_html=True)
    st.markdown(ui.side_h("layers", "Dataset"), unsafe_allow_html=True)
    source = st.radio("Dataset", ["Sample campus data", "Messy demo (data-quality test)", "Upload my own CSV"], label_visibility="collapsed",
                      help="The sample is synthetic. The messy demo has planted errors to show the Data Trust check.")
    up_csv = up_card = None
    if source == "Upload my own CSV":
        up_csv = st.file_uploader("CSV file", type="csv")
        up_card = st.file_uploader("Data Card (YAML, optional)", type=["yaml", "yml"])
    st.markdown(ui.side_h("cpu", "Model"), unsafe_allow_html=True)
    models = ollama_models()
    gemma = [m for m in models if "gemma4" in m or "gemma-4" in m]
    use_gemma = st.toggle("Use Gemma 4", value=bool(gemma), disabled=not gemma,
                          help="Gemma 4 runs locally through Ollama. Without it the app uses a built-in rule-based planner.")
    model = st.selectbox("Model", gemma or models or [DEFAULT_MODEL], disabled=not use_gemma, label_visibility="collapsed")
    if use_gemma:
        warm_model(model)
    if gemma:
        st.markdown('<span class="chip ok live">Gemma 4 connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="chip lite">Lite mode</span>', unsafe_allow_html=True)
        st.caption("Gemma 4 was not found on this machine, so questions are planned by the built-in rule-based planner (English, Hindi and "
                   "eight other Indian languages for common phrasings). To enable Gemma 4: `ollama pull gemma4:e4b`, then refresh.")
    st.markdown(ui.side_h("mic", "Voice"), unsafe_allow_html=True)
    voice_lang = st.selectbox("Spoken language", list(voice.STT_LANGUAGES), help="Pick the language you will speak, or Auto-detect.")
    if voice.available():
        warm_voice()
    st.markdown(ui.side_h("spark", "Experience"), unsafe_allow_html=True)
    if st.button("Replay welcome intro", width="stretch", icon=":material/replay:"):
        st.session_state["intro_seen"] = False
        st.session_state["hero_seen"] = False
        st.rerun()
    st.markdown(ui.side_foot(), unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_named(name: str):
    f = {"Sample campus data": "campus_utilities", "Messy demo (data-quality test)": "messy_demo"}[name]
    card = load_card((ROOT / f"data/{f}.card.yaml").read_text())
    return load_data(ROOT / f"data/{f}.csv", card), card


@st.cache_data(show_spinner=False)
def explain_finding(f, use_gemma: bool, model: str):
    """Waste Radar wording, cached so Gemma is not asked again on every click (the text itself is unchanged)."""
    return waste_radar.explain(f, use_gemma=use_gemma, model=model)


def voice_to_text(clip: bytes, lang_label: str) -> tuple[str | None, str]:
    """(transcript, problem): the transcript of a voice note, or None and a plain reason why there is none."""
    lvl = voice.level(clip)
    if lvl and lvl[1] < voice.SILENT_PEAK:
        return None, (f"Could not hear anything: the {lvl[0]:.1f} s voice note is silent, so the browser got no sound from your "
                      "microphone. Check that the mic is not muted (Windows: Settings → System → Sound → Input) and that the "
                      "browser may use it (the icon at the left of the address bar), then record again.")
    try:
        heard, _ = voice.transcribe(clip, voice.STT_LANGUAGES[lang_label])
    except Exception as exc:
        return None, f"Could not turn the voice note into text ({type(exc).__name__}: {exc}). Please type the question instead."
    if not heard.strip():
        return None, "No speech was found in the voice note. Speak a little closer to the microphone and send it again."
    return heard.strip(), ""


def campus_kpis(df: pd.DataFrame, card, limit: int = 4) -> list[dict]:
    """Display-only KPI strip: campus total per metric for the latest month, change vs the month before, last 12 months."""
    T, out = card.time_column, []
    for m, meta in list(card.metrics.items())[:limit]:
        s = df.groupby(T)[m].sum(min_count=1).dropna().sort_index()
        if s.empty:
            continue
        prev = float(s.iloc[-2]) if len(s) > 1 else None
        out.append(dict(metric=m, label=meta.get("label", m), unit=meta.get("unit", ""), month=str(s.index[-1]), value=float(s.iloc[-1]),
                        delta=(float(s.iloc[-1]) / prev - 1) * 100 if prev else None, series=s.iloc[-12:].tolist()))
    return out


mode_text = f"Gemma 4 · {model}" if use_gemma else "Lite mode · rule-based planner"
if source == "Upload my own CSV":
    if up_csv is None:
        st.markdown(ui.hero("No dataset yet", False, "waiting for a file", None, None, mode_text, bool(use_gemma), animate=False), unsafe_allow_html=True)
        st.markdown(ui.empty_state("Upload a CSV to begin", "Use the sidebar. One column of names (buildings, wards, plants), one month or date column, "
                                   "and one or more numeric columns. A Data Card YAML is optional but adds units and a source.", "db"), unsafe_allow_html=True)
        st.stop()
    try:
        raw = pd.read_csv(up_csv); up_csv.seek(0)
        card = load_card(up_card.getvalue().decode()) if up_card else infer_card(raw)
        df = load_data(up_csv, card)
    except Exception as exc:             # a bad file gets a readable message, not a traceback
        st.markdown(ui.empty_state("This file could not be loaded", f"{exc}", "alert"), unsafe_allow_html=True)
        st.stop()
else:
    df, card = load_named(source)

trust = data_trust.audit(df, card)
findings = waste_radar.scan(df, card)
animate_hero = not st.session_state.get("hero_seen")      # count-up and entrance effects play once per session
st.session_state["hero_seen"] = True
st.markdown(ui.hero(card.name, card.synthetic, card.period, trust.overall, findings, mode_text, bool(use_gemma), kpis=campus_kpis(df, card),
                    animate=animate_hero, delay=4.4 if show_intro else 0.0), unsafe_allow_html=True)
st.session_state.setdefault("history", [])


def scroll_to(selector: str, block: str = "start"):
    """Smoothly scroll the page to an element (a hidden iframe runs our fixed script; the nonce makes it run on every call)."""
    st.session_state["scroll_n"] = st.session_state.get("scroll_n", 0) + 1
    with st.container(key=f"scroller{st.session_state['scroll_n']}"):
        st.iframe(ui.scroll_script(selector, block, st.session_state["scroll_n"]), height=1)


def show(a, where: str, fresh: bool):
    """Render one answer: question, answer, pipeline trace, chart/table, caveats and the Proof Receipt."""
    clip = st.session_state.get("voice_clips", {}).get(id(a))
    st.markdown(ui.question(a.question, voice=clip is not None), unsafe_allow_html=True)
    if clip is not None:
        with st.container(key=f"vnote_{where}"):
            st.audio(clip, format="audio/wav")
    refused = a.status == "refused"
    st.markdown(ui.answer_box(a.text, refused, None if refused else (a.guard.ok if a.guard else None),
                              len(a.guard.checked) if a.guard else 0, a.planner, a.trust_score, fresh=fresh), unsafe_allow_html=True)
    if a.text_en:
        with st.expander("English original", icon=":material/translate:"):
            st.write(a.text_en)
    st.markdown(ui.pipeline_trace(a, fresh=fresh), unsafe_allow_html=True)
    if a.result is not None:
        r = a.result
        if a.plan.intent in ("total", "average"):
            v = r.facts.get("total", r.facts.get("average"))
            st.markdown(ui.bignum(f"{r.label} · {a.plan.intent}", r.unit, v, a.plan.metric), unsafe_allow_html=True)
        else:
            fig = make_chart(a.plan, r, card)
            if fig is not None:
                st.plotly_chart(fig, width="stretch", key=f"{where}c{id(a)}", config={"displayModeBar": False})
            st.dataframe(r.table, width="stretch", hide_index=True)
        st.markdown(ui.rows_used(len(r.used), ", ".join([card.entity_column, card.time_column, a.plan.metric])), unsafe_allow_html=True)
        for j, c in enumerate(r.caveats):
            st.markdown(ui.callout(c, "warn", j, fresh), unsafe_allow_html=True)
    for j, n in enumerate(a.notes):
        st.markdown(ui.callout(n, "note", j, fresh), unsafe_allow_html=True)
    with st.expander("Proof receipt: code, plan and rows", expanded=fresh, icon=":material/receipt_long:"):
        st.markdown(ui.receipt(a, fresh=fresh), unsafe_allow_html=True)
        if a.result is not None:
            st.markdown(ui.group_label("cpu", "Code that ran", ui.TEAL), unsafe_allow_html=True)
            st.code(a.result.code, language="python")
            st.markdown(ui.group_label("table", f"Rows used ({len(a.result.used)})", ui.TEAL), unsafe_allow_html=True)
            st.dataframe(a.result.used, width="stretch", hide_index=True)
        st.markdown(ui.group_label("list", "Analysis plan", ui.TEAL), unsafe_allow_html=True)
        st.json(a.plan.model_dump(), expanded=False)
        st.download_button("Download receipt (JSON)", json.dumps(a.receipt(), indent=2, default=str, ensure_ascii=False),
                           file_name="proof_receipt.json", key=f"{where}d{id(a)}", icon=":material/download:")


tab_ask, tab_radar, tab_trust, tab_hist = st.tabs([":material/forum: Ask", f":material/radar: Waste Radar ({len(findings)})",
                                                   ":material/verified_user: Data Trust", ":material/history: History"])

# ---------------- Ask ----------------
with tab_ask:
    history = st.session_state.history
    clicked = None
    # a new key after every answer: Streamlit would otherwise keep the panel open, showing the suggestions again above the answer
    with st.expander("Suggested questions" if not history else "Ask something else", expanded=not history, icon=":material/lightbulb:",
                     key=f"suggest{len(history)}"):
        for gi, (label, items) in enumerate(SUGGESTIONS.items()):
            ic, col, mat = GROUP_LOOK[label]
            st.markdown(ui.group_label(ic, label, col), unsafe_allow_html=True)
            per_row = 3
            for start in range(0, len(items), per_row):
                chunk = items[start:start + per_row]
                cols = st.columns(per_row)
                for i, s_ in enumerate(chunk):
                    if cols[i].button(s_, key=f"s{gi}_{start + i}", width="stretch", icon=mat):
                        clicked = s_

    # one message bar like WhatsApp: type, or tap the mic, record, replay or delete the clip, then send
    voice_ok = voice.available()
    sent = st.chat_input("Type a question, or tap the mic to speak (English or Indian languages)", accept_audio=voice_ok,
                         key="ask_bar")
    typed, clip, heard = None, None, None
    if sent is not None:
        typed = ((sent.text if voice_ok else sent) or "").strip() or None
        clip = sent.audio.getvalue() if voice_ok and sent.audio is not None else None
    if clip:
        busy = st.empty()                          # our own loader while Whisper turns the voice note into text
        busy.markdown(ui.listening(), unsafe_allow_html=True)
        scroll_to(".listen", "center")
        heard, problem = voice_to_text(clip, voice_lang)
        busy.empty()
        if heard:
            typed = heard
        else:
            st.markdown(ui.callout(problem, "warn"), unsafe_allow_html=True)
    question = clicked or typed
    if question:
        ph = st.empty()
        ph.markdown(ui.thinking(), unsafe_allow_html=True)
        scroll_to(".think", "center")             # bring the running analysis into view right away
        st.session_state["scroll_answer"] = True
        a = answer(question, df, card, use_gemma=use_gemma, model=model, log=True)
        st.session_state.history.append(a)
        if heard:                                  # keep the voice note so it can be replayed next to the question
            st.session_state.setdefault("voice_clips", {})[id(a)] = clip
        ph.empty()
        st.rerun()          # re-render so the suggestions fold away and the newest answer is shown

    if history:
        with st.container(key="latest"):          # only the newest answer is shown here; earlier ones live in the History tab
            show(history[-1], "ask", True)
        if st.session_state.pop("scroll_answer", False):
            scroll_to(".st-key-latest .ask-bubble", "start")
    else:
        st.markdown(ui.empty_state("Pick a question above, speak, or type your own.",
                                   "Try one from “Try to break it” to see what happens when the data cannot answer: the app refuses instead of guessing.",
                                   "chat"), unsafe_allow_html=True)

# ---------------- Waste Radar ----------------
with tab_radar:
    st.markdown(ui.section("radar", "Problems nobody asked about",
                           "Each building is compared with its own history and the campus-wide pattern. Detection is statistical code. "
                           "Gemma 4 only explains the findings, and Number Guard checks every figure it states.", ui.CORAL), unsafe_allow_html=True)
    if not findings:
        st.markdown(ui.empty_state("Nothing unusual found.", "No building drifted far from its own pattern in this dataset.", "check"), unsafe_allow_html=True)
    else:
        spikes = [f for f in findings if f.kind != "drop"]
        total = ", ".join(f"{sum(f.excess for f in spikes if f.metric == m):,.0f} {mt.get('unit', '')} of {mt.get('label', m).lower()}"
                          for m, mt in card.metrics.items() if any(f.metric == m for f in spikes))
        st.markdown(ui.radar_summary(findings, total), unsafe_allow_html=True)
        for i, f in enumerate(findings):
            text, by = explain_finding(f, bool(use_gemma), model)
            st.markdown(ui.finding_card(f, text, by, i), unsafe_allow_html=True)
            with st.expander("Show the chart", expanded=(i == 0), icon=":material/show_chart:"):
                st.plotly_chart(waste_radar.radar_chart(df, card, f), width="stretch", key=f"r{i}", config={"displayModeBar": False})

# ---------------- Data Trust ----------------
with tab_trust:
    st.markdown(ui.section("shield", "How reliable is this data?",
                           "Computed live from the loaded file before any answer: completeness, month gaps, duplicates, impossible values and likely typos. "
                           "A different file gives a different score.", ui.GREEN), unsafe_allow_html=True)
    st.markdown(ui.trust_bars(trust.table), unsafe_allow_html=True)
    st.markdown(ui.group_label("alert", "What was found", ui.AMBER), unsafe_allow_html=True)
    if trust.issues:
        st.markdown(ui.issues(trust.issues), unsafe_allow_html=True)
    else:
        st.markdown(ui.empty_state("No data-quality issues found.", "Completeness, duplicates and value ranges all look fine.", "check"), unsafe_allow_html=True)
    with st.expander("Data Card", icon=":material/badge:"):
        st.markdown(ui.card_sheet(card), unsafe_allow_html=True)
    with st.expander("Raw data", icon=":material/table:"):
        st.dataframe(df, width="stretch")

# ---------------- History ----------------
with tab_hist:
    st.markdown(ui.section("history", "Your questions", "This session, newest last. Pick one to open its full answer and receipt again.", ui.VIOLET),
                unsafe_allow_html=True)
    sess = st.session_state.history
    if sess:
        st.markdown(ui.history_list(sess), unsafe_allow_html=True)
        pick = st.selectbox("Open an earlier answer", range(len(sess)), index=len(sess) - 1,
                            format_func=lambda i: f"{i + 1}. {sess[i].question}", label_visibility="collapsed")
        with st.container(key="hist_view"):
            show(sess[pick], "hist", False)
        st.markdown("---")
    st.markdown(ui.group_label("db", "Query log", ui.VIOLET), unsafe_allow_html=True)
    st.caption("Stored locally in DuckDB. Nothing leaves your computer.")
    h = logs.history()
    if len(h):
        st.dataframe(h, width="stretch", hide_index=True)
        st.download_button("Download log (CSV)", h.to_csv(index=False), file_name="datasaathi_query_log.csv", icon=":material/download:")
    else:
        st.markdown(ui.empty_state("No questions yet.", "Ask something in the Ask tab and it will appear here.", "history"), unsafe_allow_html=True)

st.markdown(ui.footer(mode_text), unsafe_allow_html=True)

"""DataSaathi: ask community data questions in English or Indian languages, by typing or speaking.
Every answer is computed by code and ships with a Proof Receipt.
Tabs: Ask · Waste Radar · Data Trust · History."""
import hashlib
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from datasaathi import data_trust, logs, ui, voice, waste_radar
from datasaathi.card import infer_card, load_card, load_data
from datasaathi.charts import make_chart
from datasaathi.pipeline import answer
from datasaathi.planner import DEFAULT_MODEL, ollama_models

ROOT = Path(__file__).parent
st.set_page_config(page_title="DataSaathi: ask your campus data", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.markdown(ui.CSS, unsafe_allow_html=True)
show_intro = not st.session_state.get("intro_seen") and st.query_params.get("intro") != "0"   # welcome curtain: once per session (?intro=0 skips it)
if show_intro:
    st.markdown(ui.intro(), unsafe_allow_html=True)
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

# ---------------- sidebar ----------------
with st.sidebar:
    st.markdown(ui.brand(), unsafe_allow_html=True)
    st.markdown('<div class="side-h">DATASET</div>', unsafe_allow_html=True)
    source = st.radio("Dataset", ["Sample campus data", "Messy demo (data-quality test)", "Upload my own CSV"], label_visibility="collapsed",
                      help="The sample is synthetic. The messy demo has planted errors to show the Data Trust check.")
    up_csv = up_card = None
    if source == "Upload my own CSV":
        up_csv = st.file_uploader("CSV file", type="csv")
        up_card = st.file_uploader("Data Card (YAML, optional)", type=["yaml", "yml"])
    st.markdown('<div class="side-h">MODEL</div>', unsafe_allow_html=True)
    models = ollama_models()
    gemma = [m for m in models if "gemma4" in m or "gemma-4" in m]
    use_gemma = st.toggle("Use Gemma 4", value=bool(gemma), disabled=not gemma,
                          help="Gemma 4 runs locally through Ollama. Without it the app uses a built-in rule-based planner.")
    model = st.selectbox("Model", gemma or models or [DEFAULT_MODEL], disabled=not use_gemma, label_visibility="collapsed")
    if gemma:
        st.markdown('<span class="chip ok live">Gemma 4 connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="chip lite">Lite mode</span>', unsafe_allow_html=True)
        st.caption("Gemma 4 was not found on this machine, so questions are planned by the built-in rule-based planner (English, Hindi and "
                   "eight other Indian languages for common phrasings). To enable Gemma 4: `ollama pull gemma4:e4b`, then refresh.")
    st.markdown('<div class="side-h">VOICE</div>', unsafe_allow_html=True)
    voice_lang = st.selectbox("Spoken language", list(voice.STT_LANGUAGES), help="Pick the language you will speak, or Auto-detect.")
    st.markdown("---")
    if st.button("Replay welcome intro", width="stretch"):
        st.session_state["intro_seen"] = False
        st.session_state["hero_seen"] = False
        st.rerun()
    st.caption("Open source · Apache-2.0  \nSynthetic sample data is not an official record.")


@st.cache_data(show_spinner=False)
def load_named(name: str):
    f = {"Sample campus data": "campus_utilities", "Messy demo (data-quality test)": "messy_demo"}[name]
    card = load_card((ROOT / f"data/{f}.card.yaml").read_text())
    return load_data(ROOT / f"data/{f}.csv", card), card


if source == "Upload my own CSV":
    if up_csv is None:
        st.markdown(ui.hero("No dataset yet", False, "", 100, 0, "Waiting for a file", False), unsafe_allow_html=True)
        st.markdown(ui.empty_state("Upload a CSV to begin", "Use the sidebar. One column of names (buildings, wards, plants), one month or date column, "
                                   "and one or more numeric columns. A Data Card YAML is optional but adds units and a source."), unsafe_allow_html=True)
        st.stop()
    raw = pd.read_csv(up_csv); up_csv.seek(0)
    card = load_card(up_card.getvalue().decode()) if up_card else infer_card(raw)
    df = load_data(up_csv, card)
else:
    df, card = load_named(source)

trust = data_trust.audit(df, card)
findings = waste_radar.scan(df, card)
mode = f"Gemma 4 · {model}" if use_gemma else "Lite mode · rule-based planner"
animate_hero = not st.session_state.get("hero_seen")      # count-up and entrance effects play once per session
st.session_state["hero_seen"] = True
st.markdown(ui.hero(card.name, card.synthetic, card.period, trust.overall, len(findings), mode, bool(use_gemma), animate=animate_hero, delay=4.4 if show_intro else 0.0), unsafe_allow_html=True)
st.session_state.setdefault("history", [])


def show(a, where: str, fresh: bool):
    """Render one answer: question, answer, pipeline trace, chart/table, caveats and the Proof Receipt."""
    st.markdown(f'<div class="q-label">You asked</div><div class="q-text">{ui.e(a.question)}</div>', unsafe_allow_html=True)
    refused = a.status == "refused"
    st.markdown(ui.answer_box(a.text, refused, None if refused else (a.guard.ok if a.guard else None),
                              len(a.guard.checked) if a.guard else 0, a.planner, a.trust_score, fresh=fresh), unsafe_allow_html=True)
    if a.text_en:
        with st.expander("English original"):
            st.write(a.text_en)
    st.markdown(ui.pipeline_trace(a, fresh=fresh), unsafe_allow_html=True)
    if a.result is not None:
        r = a.result
        if a.plan.intent in ("total", "average"):
            v = r.facts.get("total", r.facts.get("average"))
            st.metric(f"{r.label} ({r.unit})", f"{v:,.0f}")
        else:
            fig = make_chart(a.plan, r, card)
            if fig is not None:
                st.plotly_chart(fig, width="stretch", key=f"{where}c{id(a)}", config={"displayModeBar": False})
            st.dataframe(r.table, width="stretch", hide_index=True)
        cols_used = ", ".join([card.entity_column, card.time_column, a.plan.metric])
        st.caption(f"Based on {len(r.used)} rows of the dataset · columns: {cols_used} · full rows in the proof receipt below")
        for j, c in enumerate(r.caveats):
            st.markdown(ui.callout(c, "warn", j, fresh), unsafe_allow_html=True)
    for j, n in enumerate(a.notes):
        st.markdown(ui.callout(n, "note", j, fresh), unsafe_allow_html=True)
    with st.expander("Proof receipt: code, plan and rows", expanded=fresh):
        st.markdown(ui.receipt(a, fresh=fresh), unsafe_allow_html=True)
        if a.result is not None:
            st.markdown("**Code that ran**")
            st.code(a.result.code, language="python")
            st.markdown(f"**Rows used ({len(a.result.used)})**")
            st.dataframe(a.result.used, width="stretch", hide_index=True)
        st.markdown("**Analysis plan**")
        st.json(a.plan.model_dump(), expanded=False)
        st.download_button("Download receipt (JSON)", json.dumps(a.receipt(), indent=2, default=str, ensure_ascii=False),
                           file_name="proof_receipt.json", key=f"{where}d{id(a)}")


tab_ask, tab_radar, tab_trust, tab_hist = st.tabs(["Ask", f"Waste Radar ({len(findings)})", "Data Trust", "History"])

# ---------------- Ask ----------------
with tab_ask:
    history = st.session_state.history
    clicked = None
    with st.expander("Suggested questions" if not history else "Ask something else", expanded=not history):
        for gi, (label, items) in enumerate(SUGGESTIONS.items()):
            st.markdown(f'<div class="sug-label">{label}</div>', unsafe_allow_html=True)
            per_row = 3
            for start in range(0, len(items), per_row):
                chunk = items[start:start + per_row]
                cols = st.columns(per_row)
                for i, s_ in enumerate(chunk):
                    if cols[i].button(s_, key=f"s{gi}_{start + i}", width="stretch"):
                        clicked = s_

    voice_q = None
    with st.expander("Ask by voice"):
        if not voice.available():
            st.info("Voice questions need the speech model. Run `pip install faster-whisper` and restart the app. "
                    "The Colab notebook installs it for you.")
        else:
            audio = st.audio_input("Record your question, then press stop", key="mic")
            if audio is not None:
                data = audio.getvalue()
                digest = hashlib.md5(data).hexdigest()
                if st.session_state.get("voice_hash") != digest:
                    with st.spinner("Listening to your question… (the first time loads the speech model)"):
                        try:
                            heard, detected = voice.transcribe(data, voice.STT_LANGUAGES[voice_lang])
                            st.session_state["voice_text"] = heard
                            st.session_state["voice_note"] = f"Detected language: {detected}" if detected else ""
                            st.session_state["voice_trace"] = ""
                        except Exception as exc:
                            import traceback
                            st.session_state["voice_text"] = ""
                            st.session_state["voice_note"] = f"Could not transcribe: {type(exc).__name__}: {exc}"
                            st.session_state["voice_trace"] = traceback.format_exc()
                    st.session_state["voice_hash"] = digest
            heard_text = st.text_input("What I heard (edit it if needed)", key="voice_text")
            if st.session_state.get("voice_note"):
                st.caption(st.session_state["voice_note"])
                if st.session_state.get("voice_trace") and str(st.session_state["voice_note"]).startswith("Could not"):
                    with st.expander("Technical details (send this if you ask for help)"):
                        st.code(st.session_state["voice_trace"])
            if st.button("Ask this question", type="primary", disabled=not heard_text.strip()):
                voice_q = heard_text.strip()

    typed = st.chat_input("Ask in English, Hindi, Gujarati, Tamil, Punjabi, Marathi, Bengali, Telugu, Kannada or Malayalam")
    question = clicked or voice_q or typed
    if question:
        ph = st.empty()
        ph.markdown(ui.thinking(), unsafe_allow_html=True)
        st.session_state.history.append(answer(question, df, card, use_gemma=use_gemma, model=model, log=True))
        ph.empty()
        st.rerun()          # re-render so the suggestions fold away and the newest answer is shown

    if history:
        with st.container(key="latest"):          # only the newest answer is shown here; earlier ones live in the History tab
            show(history[-1], "ask", True)
    else:
        st.markdown(ui.empty_state("Pick a question above, speak, or type your own.",
                                   "Try one from “Try to break it” to see what happens when the data cannot answer: the app refuses instead of guessing."),
                    unsafe_allow_html=True)

# ---------------- Waste Radar ----------------
with tab_radar:
    st.markdown("### Problems nobody asked about")
    st.caption("Each building is compared with its own history and the campus-wide pattern. Detection is statistical code. "
               "Gemma 4 only explains the findings, and Number Guard checks every figure it states.")
    if not findings:
        st.markdown(ui.empty_state("Nothing unusual found.", "No building drifted far from its own pattern in this dataset."), unsafe_allow_html=True)
    else:
        spikes = [f for f in findings if f.kind != "drop"]
        total = ", ".join(f"{sum(f.excess for f in spikes if f.metric == m):,.0f} {mt.get('unit', '')} of {mt.get('label', m).lower()}"
                          for m, mt in card.metrics.items() if any(f.metric == m for f in spikes))
        if total:
            st.markdown(ui.callout(f"Estimated excess flagged: {total}.", "warn"), unsafe_allow_html=True)
        for i, f in enumerate(findings):
            text, by = waste_radar.explain(f, use_gemma=use_gemma, model=model)
            st.markdown(ui.finding_card(f, text, by, i), unsafe_allow_html=True)
            with st.expander("Show the chart", expanded=(i == 0)):
                st.plotly_chart(waste_radar.radar_chart(df, card, f), width="stretch", key=f"r{i}", config={"displayModeBar": False})

# ---------------- Data Trust ----------------
with tab_trust:
    st.markdown("### How reliable is this data?")
    st.caption("Computed live from the loaded file before any answer: completeness, month gaps, duplicates, impossible values and likely typos. "
               "A different file gives a different score.")
    st.markdown(ui.trust_bars(trust.table), unsafe_allow_html=True)
    st.markdown("#### What was found")
    if trust.issues:
        st.markdown("".join(ui.issue_row(sev, msg) for sev, msg in trust.issues), unsafe_allow_html=True)
    else:
        st.markdown(ui.empty_state("No data-quality issues found.", "Completeness, duplicates and value ranges all look fine."), unsafe_allow_html=True)
    with st.expander("Data Card"):
        st.write(f"**Source:** {card.source}  \n**Period:** {card.period}  \n**Not in this dataset:** {', '.join(card.not_available) or '—'}  \n**Notes:** {card.notes}")
    with st.expander("Raw data"):
        st.dataframe(df, width="stretch")

# ---------------- History ----------------
with tab_hist:
    st.markdown("### Your questions")
    sess = st.session_state.history
    if sess:
        st.caption("This session. Pick one to open its full answer and receipt again.")
        pick = st.selectbox("Open an earlier answer", range(len(sess)), index=len(sess) - 1,
                            format_func=lambda i: f"{i + 1}. {sess[i].question}", label_visibility="collapsed")
        with st.container(key="hist_view"):
            show(sess[pick], "hist", False)
        st.markdown("---")
    st.markdown("#### Query log")
    st.caption("Stored locally in DuckDB. Nothing leaves your computer.")
    h = logs.history()
    if len(h):
        st.dataframe(h, width="stretch", hide_index=True)
        st.download_button("Download log (CSV)", h.to_csv(index=False), file_name="datasaathi_query_log.csv")
    else:
        st.markdown(ui.empty_state("No questions yet.", "Ask something in the Ask tab and it will appear here."), unsafe_allow_html=True)

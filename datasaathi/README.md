# DataSaathi

**Ask your community data in plain language. Get answers you can check.**

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dhruvsoran/datasaathi/blob/main/notebooks/DataSaathi_Colab.ipynb)
![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Model](https://img.shields.io/badge/model-Gemma%204-0F6E7A)

Hacktoberfest Hackday 2026 · PS 03 *Community and Environmental Data Intelligence* · Track 1 *Best Use of Gemma 4*
Built by Dhruv Soran, IIMT University, Meerut

![DataSaathi home screen](docs/screenshots/home.png)

DataSaathi lets anyone ask questions about campus electricity and water data by **typing or speaking**, in **English or nine Indian languages** (Hindi, Gujarati, Tamil, Punjabi, Marathi, Bengali, Telugu, Kannada, Malayalam).

1. **Gemma 4** turns the question into a structured analysis plan.
2. **Code (pandas) calculates every number.** The model never produces the final figure.
3. The app shows a chart, the answer, the rows used, honest caveats and a **Proof Receipt**.
4. **Number Guard** blocks any figure in the model's wording that the code did not compute.
5. **Waste Radar** finds problems nobody asked about, and the **Data Trust check** says how reliable the data is.
6. When the data cannot answer, it **refuses instead of guessing**.

---

## Contents
- [Quick start](#quick-start)
- [For judges: a 5-minute tour](#for-judges-a-5-minute-tour)
- [PS 03 requirements checklist](#ps-03-requirements-checklist)
- [Languages and voice](#languages-and-voice)
- [Screenshots](#screenshots)
- [How it works](#how-it-works)
- [Choosing a Gemma 4 model](#choosing-a-gemma-4-model)
- [Verify the numbers](#verify-the-numbers)
- [Bring your own data](#bring-your-own-data)
- [Troubleshooting](#troubleshooting)
- [Honest limits](#honest-limits)
- [Repository layout](#repository-layout)
- [Licence](#licence)

---

## Quick start

Pick one route. **Route A needs no installation and uses Gemma 4**, so it is the best way to see the project as intended.

### Route A: Google Colab with Gemma 4 (recommended)
1. Click the **Open in Colab** badge at the top. (The repository must be public.)
2. In Colab choose **Runtime → Change runtime type → T4 GPU**.
3. Run the cells in order. The first run downloads the model (about 9.6 GB) and takes roughly 10 to 15 minutes.
4. Cell 6 prints Gemma 4 plans and the evaluation score. Cell 7 prints a public link. Open it.
5. In the app sidebar you should see **Gemma 4 connected**.

Keep the Colab tab open while you use the app; free sessions disconnect when idle.

### Route B: your own computer
Requirements: **Python 3.11 or newer**, and [Ollama](https://ollama.com/download) for Gemma 4 (optional, see lite mode below).

**Windows (PowerShell)**
```powershell
git clone https://github.com/dhruvsoran/datasaathi.git
cd datasaathi
py -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux**
```bash
git clone https://github.com/dhruvsoran/datasaathi.git
cd datasaathi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-voice.txt     # optional: voice questions
```

Then, on any system:
```bash
ollama pull gemma4:e4b          # about 9.6 GB; needs roughly 16 GB RAM or 10 GB VRAM. Use gemma4:e2b for 8 GB machines
python scripts/check_gemma.py   # confirms Ollama and Gemma 4 work with this app
streamlit run app.py            # opens http://localhost:8501
```

### Route C: Docker
```bash
docker compose up --build       # app + Ollama + model download; then open http://localhost:8501
```
The Docker files are provided but have not been tested end to end by the author. Routes A and B are the tested paths.

> **Lite mode.** If Ollama or Gemma 4 is not found, the app still runs with a transparent rule-based planner, and every Proof Receipt names the planner that answered. Lite mode is a safety net, not the Gemma 4 experience. To judge the Gemma 4 track, use Route A or B.

---

## For judges: a 5-minute tour

1. **Load.** The sidebar defaults to the synthetic sample data, labelled as such. The banner shows the Data Trust score and Waste Radar status.
2. **Rank.** Ask *Which building used the most electricity last month?* Open the **Proof Receipt** to see the plan, the exact code that ran and the rows used. A five-step trace shows what the backend did.
3. **Compare.** *Compare electricity use in September and October.*
4. **Unavailable statistic.** *What is the electricity use per student?* The app refuses: there is no headcount in the data.
5. **Missing observation.** *Show electricity usage for Library in March 2026.*
6. **Indian languages.** *पिछले महीने सबसे ज्यादा बिजली किस बिल्डिंग ने इस्तेमाल की?* (Hindi), or the Gujarati, Tamil and Punjabi suggestions. Or press **Ask by voice** and speak.
7. **Unasked problems.** *Is there any waste in water use?* or open the **Waste Radar** tab. Girls Hostel stays near full load in the June vacation.
8. **Bad data.** Switch to *Messy demo* and watch the Data Trust score fall and answers carry warnings.
9. **New data.** Choose *Upload my own CSV* and upload `data/campus_demo_upload.csv` with `data/campus_demo_upload.card.yaml`. It has different columns and names, and a hidden water leak. Questions are in `docs/UPLOAD_DEMO_QUESTIONS.txt`.

---

## PS 03 requirements checklist

| Requirement from the brief | How it is met | Where to see it |
|---|---|---|
| Load one documented CSV with several records and clearly named columns | `data/campus_utilities.csv` (95 rows: building, month, electricity_kwh, water_kl) with a Data Card documenting columns, units, period, source and what is missing | `data/*.card.yaml`, Data Trust tab |
| Answer at least three question types (highest/lowest, trend, comparison) | Ranking, trend and period comparison, plus total, average and "unusual usage" | Ask tab |
| Calculate with code, not only a model-generated number | Every number comes from pandas. The code shown is the code that ran | Proof Receipt |
| Chart or table with a plain-language explanation, citing rows or fields | Chart, table and explanation; a line under each answer states the rows and fields used; full rows in the receipt | Ask tab |
| Warn when information is absent, a denominator is missing, or data cannot justify the conclusion | Refusals, missing-reading warnings, "no headcount or area" warning, close-ranking and tiny-change warnings, Data Trust warnings | Ask and Data Trust tabs |
| Use Gemma 4 to connect questions with evidence | Gemma 4 via Ollama plans the analysis and explains results; Number Guard verifies every figure it states | Receipt shows `Planner: gemma4:...` |
| Clearly distinguish sample or synthetic data from official records | Data Card `synthetic` flag, a visible badge, and a caveat on every answer | Banner badge, caveats |
| Demonstration checklist (ranking, comparison, unavailable statistic, visual result and calculation) | All covered in the tour above | Tour |
| Explain patterns, missing information and possible actions | Waste Radar explains findings with a suggested check; caveats explain missing information | Waste Radar tab |
| State assumptions and verify calculations in code | Assumptions and plan repairs are shown on screen and in the receipt; evaluation compares against independent pandas | Receipt, `evals/` |

**Not built (honest):** combining documents and images with structured data, and scenario comparisons. Both are on the roadmap.

---

## Languages and voice

**Typing.** Ask in English, Hindi, Gujarati, Tamil, Punjabi, Marathi, Bengali, Telugu, Kannada or Malayalam (or Hinglish). The answer comes back in the language of the question.

| | With Gemma 4 | Lite mode (no Gemma) |
|---|---|---|
| Understanding the question | Free-form wording in 140+ languages; plans are checked against the data | Keyword coverage for common phrasings in the nine Indian languages above (`datasaathi/lexicon.py`) |
| Answer language | Verified English answer is translated by Gemma 4; **Number Guard re-checks every number** and falls back to English if any changed | English |
| Warnings and notes | English | English |

**Voice.** Open **Ask by voice** on the Ask tab, allow the microphone, speak, press stop, check the text it heard (you can edit it), then press **Ask this question**. Speech is turned into text by Whisper (`faster-whisper`), which runs on your machine or Colab GPU after a one-time model download.

```bash
pip install -r requirements-voice.txt                    # optional; the Colab notebook does this for you
DATASAATHI_STT_MODEL=small streamlit run app.py          # tiny/base for small laptops, small/medium for better Indian-language accuracy
```
Choose the language you will speak in the sidebar (or leave it on Auto-detect). Microphone access works on `localhost` and `https` links (including the Colab tunnel link).

Limits, stated plainly: the keyword lists were written carefully but are not reviewed by native speakers; speech accuracy varies by language and model size; building names spoken in a non-Latin script may not match the English names in the data unless Gemma 4 maps them; and the voice path was tested with a stand-in model, not yet with real recordings.

---

## Screenshots

| Answer, pipeline trace and chart | Proof Receipt, code and rows |
|---|---|
| ![answer](docs/screenshots/ask-answer.png) | ![receipt](docs/screenshots/receipt.png) |
| **Waste Radar** | **Data Trust** |
| ![radar](docs/screenshots/waste-radar.png) | ![trust](docs/screenshots/data-trust.png) |

The welcome curtain, mid-opening:

![welcome curtain](docs/screenshots/intro.png)

Captured in lite mode with the rule-based planner. With Gemma 4 running, the banner shows `Gemma 4 · gemma4:e4b` with a live indicator.

---

## How it works

```
CSV + Data Card ─► Data Trust audit
                                         ┌──────── Waste Radar (statistics in code)
question ─► Gemma 4 plan (JSON) ─► validate against Data Card ─► whitelisted pandas ─► chart + answer + caveats
                  │ unknown metric / entity / month => refusal            │
                  └──── repair step (logged) ◄─ small-model slips         ▼
                        Proof Receipt ◄─ Number Guard ◄─ Gemma 4 wording ◄┘      DuckDB query log
```

| Piece | What it does | File |
|---|---|---|
| Planner | Gemma 4 via Ollama with structured JSON output; rule-based fallback | `datasaathi/planner.py` |
| Plan validation and repair | Checks every field against the data, fixes small-model slips and logs each fix | `plan.py`, `planner.py` |
| Engine | Builds and runs the pandas code (validated values only, no builtins); produces facts and caveats | `engine.py` |
| Number Guard | Every number in model text must exist in the computed output, else a verified template answer is shown | `explain.py` |
| Waste Radar | Compares each building with its own history and the campus-wide pattern; flags unusual readings | `waste_radar.py` |
| Data Trust | Completeness, month gaps, duplicates, impossible values, likely typos, a 0 to 100 score | `data_trust.py` |
| Interface | Streamlit app, dark theme and animated components | `app.py`, `ui.py`, `theme.css`, `charts.py`, `.streamlit/config.toml` |
| Languages and voice | Indian-language vocabulary, answer translation, speech to text | `lexicon.py`, `localize.py`, `voice.py` |
| Query log | Local DuckDB file and History tab | `logs.py` |

Each question replaces the previous answer on the Ask tab, so the page stays short; earlier answers are one click away in the **History** tab.

On first open, a short **welcome curtain** ("HACKTOBER | FEST" written across two curtains that part to reveal the app) plays once per session. Add `?intro=0` to the address to skip it, or press **Replay welcome intro** in the sidebar. A **liquid motion** layer (drifting gooey blobs and slow waves in the banner, buttons that fill like liquid on hover, answers that drop in with a small bounce) runs in the background. Both are pure CSS and are switched off automatically for visitors who ask their system for reduced motion.

The interface uses CSS animation only (count-ups, a pipeline trace, a receipt that prints out) and respects the reduced-motion setting.

---

## Choosing a Gemma 4 model

| Ollama tag | Download | Hardware | Notes |
|---|---|---|---|
| `gemma4:e2b` | about 7.2 GB | 8 GB RAM minimum | Smallest; not tested with this app |
| `gemma4:e4b` | about 9.6 GB | about 16 GB RAM or 10 GB VRAM; fits the free Colab T4 | **Default. The model we validated** |
| `gemma4:12b` | about 7.6 GB | fits the free Colab T4 | Larger dense model; not yet tested with this app |
| `gemma4:26b` | about 18 GB | 24 GB GPU (Colab L4 or A100) | Higher quality; does not fit a free T4 |
| `gemma4:31b` | about 20 GB | 24 GB GPU or more | Largest; not tested |

Choose a model in the sidebar, or run `DATASAATHI_MODEL=gemma4:12b streamlit run app.py`. Sizes come from public Ollama and community documentation and may change.

---

## Verify the numbers

```bash
python evals/run_evals.py                    # 20 questions; expected answers computed with independent pandas
python evals/run_evals.py --gemma            # the same set through Gemma 4
python evals/run_evals.py --heldout --gemma  # 10 extra questions written after prompt tuning
pytest -q tests                              # Number Guard, plan repair, Data Trust, Waste Radar, query log
```

What we measured: with Gemma 4 (`gemma4:e4b` on a Colab T4) the main set first scored 11/20. After adding the validation and repair step and prompt examples it scored 20/20. The held-out set exists so you can check for overfitting; run it with `--gemma` and judge for yourself. GitHub Actions runs the offline evaluations and tests on every push.

---

## Bring your own data

Upload a CSV with one column of names (buildings, wards, plants), one month or date column, and one or more numeric columns. For best results add a Data Card (YAML). Example: `data/campus_utilities.card.yaml`.

```yaml
name: Campus utilities (monthly)
synthetic: true                     # set false for real records
source: Where the data came from
period: 2025-04 to 2026-03
entity_column: building
time_column: month
metrics:
  electricity_kwh: {label: Electricity, unit: kWh}
  water_kl: {label: Water, unit: kL}
not_available: [students / occupancy, cost / tariff]   # what the dataset does NOT contain
```
Data is treated as monthly. Daily readings should be summed to months first. Without a Data Card the app builds a basic one and warns that the source is not verified.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Sidebar says **Lite mode** | Ollama or the model was not found. Start Ollama, run `ollama pull gemma4:e4b`, refresh the page |
| `pip` or `python` not found (Windows) | Reinstall Python and tick "Add to PATH", then reopen PowerShell |
| `Activate.ps1 cannot be loaded` | Run `Set-ExecutionPolicy -Scope Process Bypass` first |
| Port 8501 is busy | `streamlit run app.py --server.port 8502` |
| Gemma 4 is very slow or runs out of memory | Use `gemma4:e2b`, close other applications, or use Colab |
| Colab shows no link | Re-run the last cell, or run `!tail -5 /tmp/cf.log` to see why |
| Colab says no GPU | Runtime → Change runtime type → T4 GPU, then reconnect |
| Welcome curtain is in the way | Add `?intro=0` to the address (for example `http://localhost:8501/?intro=0`), or use it once and it will not return in that session |
| Sidebar closed and gone | Click the teal **»** button at the top-left of the page to reopen it |
| **Ask by voice** says it needs the speech model | `pip install -r requirements-voice.txt`, then restart the app |
| Microphone does not record | Allow microphone access for the page; use `localhost` or an `https` link |
| Question answered "not answerable" unexpectedly | Open the Proof Receipt; the plan and `missing_field` say what the app thought was missing |

---

## Honest limits

- The sample data is **synthetic** and labelled as such. It is not an official record.
- "Sandbox" means the code is built only from validated, whitelisted values and run with no Python builtins. It is not an operating-system sandbox.
- Waste Radar thresholds are simple statistical rules tuned on the sample. Treat flags as leads to check, not proof of waste. It needs several buildings (3 or more) and at least 6 months to compare.
- Each question is independent (no follow-up memory yet), and one question maps to one plan.
- Indian-language quality depends on the Gemma 4 model you run. The rule-based fallback covers common phrasings only, and its word lists have not been reviewed by native speakers.
- Tested: Gemma 4 `e4b` on a Colab T4, and lite mode on Linux with Python 3.12 (including the nine-language keyword tests). Not tested: Docker, Windows and macOS installs, other Gemma 4 sizes, and voice input with real recordings.
- Not benchmarked on large datasets. The brief asks for small ones.
- Documents and images as inputs, and scenario comparisons, are not built.

---

## Repository layout

```
app.py                     Streamlit app (tabs: Ask, Waste Radar, Data Trust, History)
datasaathi/                planner, lexicon, plan, engine, explain (Number Guard), localize, voice, waste_radar, data_trust, charts, ui, theme.css, logs
data/                      synthetic sample, messy demo, and an upload demo (CSV + Data Card each)
evals/run_evals.py         20-question set and held-out set
tests/                     unit tests
notebooks/                 Google Colab notebook (Gemma 4)
scripts/                   check_gemma.py, colab_launch.py, make_data.py
docs/                      screenshots and upload-demo questions
.streamlit/config.toml     colour theme
.github/workflows/ci.yml   evaluations and tests on every push
PITCH.md                   demo script and likely judge questions
requirements.txt, requirements-voice.txt
Dockerfile, docker-compose.yml
```

## Licence

Apache-2.0 (see `LICENSE` and `NOTICE`). Gemma 4 weights are released by Google DeepMind under Apache-2.0.

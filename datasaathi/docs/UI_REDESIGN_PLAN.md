# DataSaathi — UI redesign plan

Scope of the redesign: **visual layer only.** The planner, engine, Number Guard, Waste Radar statistics, Data Trust
audit, voice pipeline, query log and every number the app shows stay as in the original interface (the `main` branch).
A few fixes outside the visual layer came later; they are listed in section 5.

## 1. What the original interface has (analysis)

| Layer | File | Role | Redesign action |
|---|---|---|---|
| Page flow | `app.py` | sidebar, hero, 4 tabs (Ask, Waste Radar, Data Trust, History), `show()` renders an answer | keep the flow and every widget key; swap the HTML pieces and layout |
| Components | `datasaathi/ui.py` | HTML strings: hero, answer box, receipt, pipeline trace, finding card, trust bars, intro curtain | rewrite as a component kit with the same function names plus new ones |
| Styling | `datasaathi/theme.css` | midnight teal + amber, liquid blobs, curtain | replace with a new design system (kept CSS-only, reduced-motion safe) |
| Charts | `datasaathi/charts.py`, `waste_radar.radar_chart` | Plotly bar/line/grouped bar, radar line chart | new chart theme: gradients, area fills, peak labels, styled hover |
| Logic | planner, plan, engine, explain, pipeline, waste_radar (scan), data_trust, voice, logs | the product | **not touched** |

Constraints taken from the tests (`tests/test_app.py`):
- answer markup keeps `class="answer"`; only the newest answer shows on Ask, History re-opens one;
- the stylesheet never hides `[data-testid="stToolbar"]` and keeps the `stExpandSidebarButton` rule;
- the welcome curtain keeps `class="intro"` and the "HACKTOBER" text, plays once, `?intro=0` skips it, "Replay welcome intro" replays it;
- suggestion buttons keep their full question text as the label.

## 2. Design direction: "Data observatory"

A calm control-room look on a dusk-blue canvas (lightened after the first review: a mixed theme with a deeper navy sidebar), an aurora of teal / violet / amber light, frosted-glass
panels with gradient hairline borders, and instruments (gauges, radar sweep, sparklines) instead of plain numbers.

- **Tokens:** canvas `#1A2643` to `#2A3466`, glass panels `rgba(255,255,255,.07-.13)` with blur, accents teal `#2EE6C5`,
  violet `#8B7CFF`, amber `#FFC24D`, coral `#FF7A8A`, water blue `#4FB6FF`.
- **Type:** Space Grotesk (display, numbers), Inter (body), JetBrains Mono (receipt, code).
- **Motion:** slow aurora drift, radar sweep, ring-gauge fill, staggered card entrances, count-ups.
  Everything is CSS; `prefers-reduced-motion` turns it all off.

## 3. Work items

1. **Design system** (`theme.css`): tokens, aurora background with grain, glass panels, gradient borders,
   typography scale, restyled native widgets (tabs as a segmented pill bar, expanders, inputs, chat bar,
   buttons, dataframes, metrics, scrollbars), sidebar.
2. **Command deck** (replaces the hero): bento grid with
   - title panel with gradient headline and live mode orb (Gemma 4 / Lite);
   - **Data Trust ring gauge** (SVG, animated fill, colour by score);
   - **Waste Radar scope** (SVG sweep, one blip per finding);
   - dataset panel with synthetic badge and period;
   - **KPI strip**: per metric, latest-month campus total, change vs previous month and a 12-month
     **sparkline** (pandas sums of the loaded data, display only).
3. **Ask tab:** section headings with icons; suggestion groups as cards with language tags; voice panel with
   an animated mic header; the answer as a glass card with a gradient edge and a **"Verified" seal**
   when Number Guard passed (red "Refused" seal when it refused); pipeline trace as a glowing stepper;
   caveat / note callouts with icons; restyled thinking state (scanning beam + steps).
4. **Proof Receipt:** thermal-paper receipt kept (it is the signature), new barcode footer and stamp.
5. **Charts:** shared theme with transparent background, soft grid, gradient bars with value labels,
   spline trend with area fill and the peak marked, grouped compare bars in muted vs accent, Waste Radar
   chart with an expected-range band and a glowing flagged point, dark hover labels.
6. **Waste Radar tab:** header with a large radar scope and the excess summary; finding cards as incident
   cards (severity strip, actual vs expected mini bars, delta pill).
7. **Data Trust tab:** per-metric ring gauges with completeness / duplicate / negative / suspect counts;
   issues as a severity timeline; the Data Card as a spec sheet.
8. **History tab:** session timeline (answered / refused dots) above the re-open picker; query log table.
9. **Sidebar:** brand mark, grouped sections, model status orb, footer credit.
10. **Responsiveness:** Waste Radar explanations are cached per finding (`st.cache_data`) so Gemma is not
    called again on every click; the text itself is unchanged.

## 4. Verification

- `pytest -q tests` (all original tests must pass; app tests with Gemma off, as before).
- `python evals/run_evals.py` must keep 20/20.
- Visual check of every tab in the browser, desktop and phone width, sample and messy datasets, a refused answer.

## 5. Later changes (after review)

Interface:
- the page scrolls to the running analysis when a question is asked, then to the answer;
- no page-wide fade during reruns; own loaders instead (analysis steps, and "Listening to your recording…" for voice);
- voice: play/pause hidden after recording, transcript box with a **Send** button, cleared after sending;
- the suggestions panel collapses after every answer (a new expander key per question), so it is not shown twice;
- the welcome curtain covers the whole window even with the sidebar open, and "Replay welcome intro" restarts it;
- no version label on screen.

Outside the visual layer (each with a test or an evaluation run):
- **speed:** Gemma 4 calls use `think: false` and `keep_alive: 30m`, and the model is warmed up in the background
  when the app starts (`planner.py`). Thinking made each call several times slower (about 35 s against 5 s for one plan
  on a laptop RTX 3050) and the app never uses its output.
  `DATASAATHI_THINK=1` turns it back on;
- **plan repairs** (logged in the receipt, `planner.py`): a plan with two periods but intent anomaly or trend becomes a
  comparison; a month the data does not have, for a question that gave no year, is mapped to the one month it does have;
- **explanations** stay in the language of the question (an English question no longer gets a Hinglish answer);
- **upload without a Data Card** works on pandas 3 (text columns are no longer `object`) and a file without usable
  columns gets a readable message instead of a crash (`card.py`).

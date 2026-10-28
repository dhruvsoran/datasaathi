# DataSaathi Pro: clean, professional interface

This folder is a copy of `DataSaathi_2.0`. The goal is a calm, professional interface with room to breathe.
Only the visual layer changes: `datasaathi/theme.css`, `datasaathi/ui.py`, `datasaathi/charts.py`, the chart style in
`waste_radar.radar_chart`, `.streamlit/config.toml` and a few markup calls in `app.py`. The planner, engine, Number Guard,
Waste Radar statistics, Data Trust audit, voice pipeline, suggestions and query log are not touched.

## 1. What makes the 2.0 screen feel crowded (audit)

| Problem | Where |
|---|---|
| Everything sits in a glowing glass box, so nothing stands out | deck, KPI tiles, tabs, answer, pipeline, charts, findings |
| Too much ambient motion at once: aurora, star grid, film grain, gooey blobs, waves, liquid ring fill, radar sweep, rotating seal, flowing links, pulsing dots | `theme.css`, `ui.py` |
| Five accent colours used as decoration (teal, violet, amber, coral, blue) and gradient text | headline, tabs, buttons, pipeline |
| Letter-spaced mono capitals for almost every label | eyebrows, KPI labels, group labels, answer head |
| Dark low-contrast text on dark glass (`#AEBDD6` on navy) | sub-texts, captions |
| Big decorative instruments (132-190 px gauge and scope) take more room than the number they show | deck, Waste Radar header |
| Tight vertical rhythm: cards touch, sections start right under each other | whole page |

## 2. Design direction

A light, neutral workspace with a deep navy sidebar (keeps the "mixed" theme), white surfaces, hairline borders and one
brand accent. Colour carries meaning only: amber for electricity, sky blue for water, violet for other metrics,
green / amber / red for status.

- **Tokens:** canvas `#F6F7F9`, surface `#FFFFFF`, border `#E4E7EC`, text `#101828` / `#475467` / `#667085`,
  brand teal `#0E7C70`, sidebar `#0B1324`.
- **Type:** Inter for everything, JetBrains Mono only for code and the receipt. Sentence case labels.
  Scale: page title 30 px, section 18 px, body 15 px, small 13 px.
- **Space:** 4 / 8 / 12 / 16 / 24 / 32 / 48 px steps; 24-32 px between sections; content width 1180 px.
- **Depth:** 1 px borders and one soft shadow level. No glows, blur or gradients on surfaces.
- **Motion:** a short fade-in for new answers and the loaders' spinners only. No infinite decorative animation.
  `prefers-reduced-motion` still turns everything off.

## 3. Work items

1. **Theme** (`config.toml`, `theme.css`): light base theme, navy sidebar, new tokens, native widgets restyled
   (underline tabs, flat expanders, white suggestion buttons, chat bar, dataframes, charts in plain cards).
2. **Page header** (replaces the command deck): plain title, one-line description, a meta line (dataset, period,
   synthetic, model) and one row of equal stat cards: Data Trust (score + meter, opens its tab), Waste Radar
   (count + breakdown, opens its tab), one card per metric (latest total, change, small sparkline).
3. **Ask:** quiet question line, answer card with a status badge in its header instead of the rotating seal,
   meta as one muted line, a compact one-line pipeline, white chart card, callouts as soft tinted rows,
   simple loaders (spinner and step list) for thinking and listening.
4. **Proof Receipt:** a clean document card (mono rows, dashed rules, status badge); no paper edge, barcode or tilted stamp.
5. **Charts:** light chart theme: grey grid, metric colour for the leader and a tint for the rest, white-filled markers,
   a small peak label, grey "before" bars in comparisons, a calm Waste Radar chart.
6. **Waste Radar tab:** summary card (count, breakdown, estimated excess) instead of the large scope; finding cards with a
   thin severity bar and slim actual-vs-expected bars.
7. **Data Trust tab:** metric cards with score and meter; issues as a plain list with severity badges; Data Card as a
   two-column definition list.
8. **History tab:** a simple numbered list with a status dot.
9. **Sidebar and corner:** brand mark, small section labels, a status line for the model, a white "Speak in" pill.
10. **Phone width:** two stat cards per row, smaller header, full-width answer.

Kept on purpose: the welcome curtain (recoloured), WhatsApp-style voice notes in the question bar, clickable stat cards,
data-driven suggestions, the layout-stability slots, and every test-facing markup (`class="answer"`, `class="intro"`,
"HACKTOBER", `stExpandSidebarButton`, no `stToolbar` rule).

## 4. Verification

- `pytest -q tests`: all 47 tests pass.
- Screens captured before and after at 1440 x 900 and 390 x 844: home, answer, receipt, refusal, Waste Radar, Data Trust,
  History, upload without data, voice note.
- No speed or evaluation runs (the logic is unchanged).

## 5. Revision: darker and more animated (after review)

The light version read as too bright. The same layout now uses a **slate dusk** palette and purposeful motion:

- **Palette:** canvas `#121A2B`, surfaces `#182235`, borders `#27334B`, text `#EEF2F8` / `#C3CCDB` / `#8E9AB0`,
  brand teal `#2DD4BF`, sidebar `#0B1120`. Charts and the Waste Radar chart follow the same tokens.
- **Entrance (once per view):** header lines fade up in order; stat cards rise one after another; the Data Trust score
  and the Waste Radar count count up; meters fill; sparklines draw and their end dot pops.
- **Answers:** the card rises, its accent bar grows, the verified badge pops, the five pipeline steps light up in turn,
  callouts slide in, receipt rows print one by one, the chart and table rise.
- **Ambient (slow and quiet):** two soft background lights drift; live status dots pulse; a sheen passes along the
  title phrase and across the meters every few seconds; the Waste Radar count has a ring pulse when something was found.
- **Interaction:** cards lift with a light sweep on hover, the tab underline springs open, suggestion icons nudge,
  the question bar glows on focus, the send button pops in, the logo bars bounce on hover.
- **Loaders:** spinner, step highlight and a moving progress line; voice notes show a green equaliser.
- `prefers-reduced-motion` still turns all of it off.

## 6. Revision: cream palette (after review)

The slate version was a little too dark. The page now uses a warm **cream** palette, between white and dark; the
animations from section 5 are unchanged.

- Canvas `#F4EFE6`, cards `#FBF8F2` (ivory, not pure white), borders `#E4DACA`, text `#2B2620` / `#4A4237` / `#776D60`.
- Brand teal `#0F766E`; meaning colours tuned for a warm light background (amber `#C2740A`, blue `#1F6FA8`, green `#2F7D4A`, red `#C8372D`).
- Espresso sidebar and welcome curtain `#26211C`; charts and the Waste Radar chart use the same warm greys.

## 7. Revision: "Lush forest" palette (requested)

The interface now uses the Lush forest palette; layout and animations are unchanged.

| Colour | Hex | Used for |
|---|---|---|
| Forest | `#2E6F40` | brand: tabs, links, buttons, answer edge, pipeline steps, good Data Trust scores, "other" metrics in charts |
| Mint | `#CFFFDC` | soft highlights: hover on suggestions, empty-state icons, voice-note bubble, background light |
| Sage | `#68BA7F` | live status dots, sidebar icons and toggles, curtain lines, focus glow |
| Deep forest | `#253D2C` | sidebar and welcome curtain |

The page is a light mint (`#E6F5EA`) with near-white mint cards (`#F7FCF8`) and dark green text (`#1B2E21`).
Electricity stays amber and water blue so the two metrics remain easy to tell apart; red and amber still mark problems.

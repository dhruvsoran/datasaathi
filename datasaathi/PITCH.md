# Hackathon playbook

## 3-minute live demo (matches the PS 03 checklist)
1. **(15s) Hook.** "Charts hide missing data and chatbots invent numbers. DataSaathi answers campus data questions — and proves every number."
2. **(20s) Load.** Sidebar → *Sample campus data* (labelled SYNTHETIC). Point at **Data Trust 98/100** and **Waste Radar: 2 alerts**.
3. **(40s) Ranking.** Ask: *Which building used the most electricity last month?* → chart + answer → open **Proof Receipt** (plan JSON, code that ran, rows used).
4. **(25s) Comparison.** *Compare electricity use in September and October.*
5. **(25s) Unanswerable.** *What is the electricity use per student?* → refusal: no headcount in the data; it will not guess.
6. **(15s) Missing observation.** Type *Show electricity usage for Library in March 2026* → "missing observation" (a Library reading is absent).
7. **(25s) Hindi.** *पिछले महीने सबसे ज्यादा बिजली किस बिल्डिंग ने इस्तेमाल की?*
8. **(25s) Waste Radar.** Open the tab: Girls Hostel stayed near full load in the June vacation (~20,000 kWh extra). "Nobody asked — it found it." Then type *Is there any waste in water use?* to show the same radar running through the normal pipeline, with its code in the receipt.
9. **(20s) Data Trust.** Switch to *Messy demo*: duplicate row, typo (×10), negative value, missing row — and answers now carry warnings.
10. **(10s) Close.** "Offline on a laptop with Gemma 4. Open source, Apache-2.0."

**Before you go on stage:** run `python scripts/check_gemma.py`, run each demo question once, and keep a screen recording as a backup.

## Likely judge questions
- **Where exactly does Gemma 4 add value?** Understanding messy, multilingual questions → structured plans, and explaining results/alerts in plain language. Numbers never come from the model.
- **What if Gemma hallucinates the plan?** Plans are validated against the Data Card; unknown things become refusals. The Proof Receipt shows the plan and code.
- **What if Gemma writes a wrong number in the explanation?** Number Guard rejects it and shows a verified template answer (see the unit tests).
- **Is the sample data real?** No — synthetic and labelled. The tool works on any CSV + Data Card.
- **How do you know it works?** 20-question eval with independently computed answers, run in CI; run `--gemma` for the model score.
- **Why not just use ChatGPT on a CSV?** Cloud upload of institutional data, no verification, no refusal on missing data, no proactive findings.
- **Real-world path?** Pilot at IIMT University with real meter data (with permission); the Data Card lets other campuses reuse it.


## New: Indian languages and voice (add to the demo)
- Ask the same question in **Gujarati, Tamil or Punjabi** (suggestion buttons) and, with Gemma 4 on, the answer comes back in that language with the same verified numbers. Say: "Number Guard re-checks every number after translation."
- Open **Ask by voice**, speak a question in your language, show the text it heard, press *Ask this question*. Say: "Speech runs locally with Whisper; nothing is sent to a cloud service."
- Honest line if asked: voice and keyword lists for the Indian languages are new and not reviewed by native speakers; Gemma 4 handles free-form wording.

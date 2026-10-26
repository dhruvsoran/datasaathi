"""Visual layer: theme CSS and small HTML components (kept out of app.py so the logic stays readable)."""
from __future__ import annotations
import html

INK, TEAL, AMBER, PAPER, RED, GREEN, MUTED = "#E8F1F3", "#2FB5A3", "#FFC24D", "#08171F", "#FF8A80", "#5FD39A", "#9DB8BF"

from pathlib import Path as _Path
CSS = "<style>" + (_Path(__file__).with_name("theme.css")).read_text(encoding="utf-8") + "</style>"

LOGO = (f'<svg width="40" height="34" viewBox="0 0 40 34" aria-hidden="true"><defs><filter id="goo-logo" x="-30%" y="-30%" width="160%" height="160%">'
        '<feGaussianBlur in="SourceGraphic" stdDeviation="1.7" result="b"/>'
        '<feColorMatrix in="b" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 20 -8"/></filter></defs>'
        f'<g filter="url(#goo-logo)"><circle class="la" cx="14" cy="17" r="10" fill="{AMBER}"/>'
        f'<circle class="lb" cx="25" cy="17" r="10" fill="{TEAL}"/></g></svg>')


def e(x) -> str:
    return html.escape(str(x))


def trust_color(score: int) -> str:
    return GREEN if score >= 90 else AMBER if score >= 70 else RED


def brand() -> str:
    return (f'<div class="brand">{LOGO}<b>DataSaathi</b></div>'
            '<div class="brand-sub">Ask your campus data by typing or speaking, in English or Indian languages. Every number comes with proof.</div>')


def hero(card_name: str, synthetic: bool, period: str, trust: int, alerts: int, mode: str, mode_ok: bool, animate: bool = True, delay: float = 0.0) -> str:
    syn = '<span class="chip syn">Synthetic demo data</span>' if synthetic else '<span class="chip info">Your data</span>'
    mchip = f'<span class="chip {"ok live" if mode_ok else "lite"}">{e(mode)}</span>'
    col = "#5FD39A" if trust >= 90 else "#FFC24D" if trust >= 70 else "#FF8A80"
    unit = lambda t: f'<span style="font-size:.9rem;color:#A9C6CC">{t}</span>'
    return f"""
<div class="wrap{'' if animate else ' still'}" style="--d0:{delay}s">
<svg class="goo-defs" width="0" height="0" aria-hidden="true"><defs><filter id="goo"><feGaussianBlur in="SourceGraphic" stdDeviation="14" result="b"/><feColorMatrix in="b" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -9" result="g"/></filter></defs></svg>
<div class="blobs" aria-hidden="true"><i class="b1"></i><i class="b2"></i><i class="b3"></i><i class="b4"></i></div>
<svg class="waves back" viewBox="0 0 2400 120" preserveAspectRatio="none" aria-hidden="true"><path d="M0,60 C150,100 350,20 600,60 C850,100 1050,20 1200,60 C1350,100 1550,20 1800,60 C2050,100 2250,20 2400,60 L2400,120 L0,120 Z"/></svg>
<svg class="waves front" viewBox="0 0 2400 120" preserveAspectRatio="none" aria-hidden="true"><path d="M0,75 C200,40 400,110 600,75 C800,40 1000,110 1200,75 C1400,40 1600,110 1800,75 C2000,40 2200,110 2400,75 L2400,120 L0,120 Z"/></svg>
<div class="hero"><h1>Ask your campus data.<br><span class="hl">Get answers you can check.</span></h1>
<p>Gemma 4 understands the question. Code does the maths. Every answer ships with the code, the rows and a receipt.</p></div>
<div class="status">
  <div class="tile"><div class="k">Dataset · {e(period)}</div><div class="v" style="font-size:1.1rem">{e(card_name)}</div>
    <div class="s" style="margin-top:.55rem">{syn} {mchip}</div></div>
  <div class="tile" title="Computed live from the loaded dataset: completeness, month gaps, duplicates, impossible values and likely typos. A different file gives a different score."><div class="k">Data trust</div><div class="v" style="color:{col}"><span class="cnt" style="--to:{trust}">{trust}</span>{unit(" / 100")}</div>
    <div class="meter"><i style="width:{trust}%;background:{col}"></i></div><div class="s">Live check of this file: gaps, duplicates, odd values</div></div>
  <div class="tile" title="Statistical check of every building against its own history and the campus-wide pattern. The count changes with the data."><div class="k">Waste Radar</div><div class="v" style="color:{'#FF8A80' if alerts else '#5FD39A'}"><span class="cnt" style="--to:{alerts}">{alerts}</span>{unit(" alert" if alerts == 1 else " alerts")}{'<span class="ping"></span>' if alerts else ''}</div>
    <div class="s">{'Unusual readings found by statistics. See the Waste Radar tab.' if alerts else 'Nothing unusual found in this data.'}</div></div>
</div></div>"""


def answer_box(text: str, refused: bool, guard_ok, n_verified: int, planner: str, trust: int | None, fresh: bool = False) -> str:
    chips = []
    if refused:
        chips.append('<span class="chip bad">Not answerable from this data</span>')
    else:
        if guard_ok is True:
            chips.append(f'<span class="chip ok">Numbers verified ({n_verified})</span>')
        elif guard_ok is False:
            chips.append('<span class="chip lite">Model wording replaced by verified text</span>')
        if trust is not None:
            chips.append(f'<span class="chip {"ok" if trust >= 90 else "lite" if trust >= 70 else "bad"}">Data trust {trust}/100</span>')
    chips.append(f'<span class="chip info">Planner: {e(planner)}</span>')
    cls = "answer" + (" refused" if refused else "") + (" fx" if fresh else "")
    return f'<div class="{cls}" style="--i:1"><div class="t">{e(text)}</div><div class="meta">{"".join(chips)}</div></div>'


def callout(text: str, kind: str = "warn", idx: int = 0, fresh: bool = False) -> str:
    ic = "!" if kind == "warn" else "i"
    return f'<div class="callout {kind}{" fx" if fresh else ""}" style="--i:{idx + 3}"><span class="ic">{ic}</span><span>{e(text)}</span></div>'


def receipt(a, fresh: bool = False) -> str:
    r = a.result
    g = a.guard
    k = [0]
    def row(name, v, cls=""):
        k[0] += 1
        return f'<div class="row" style="--i:{k[0]}"><span>{e(name)}</span><span class="{cls}">{e(v)}</span></div>'
    p = a.plan
    plan_bits = ", ".join(f"{key}={val}" for key, val in p.model_dump(exclude_none=True).items() if key not in ("top_n",) or p.intent == "rank")
    out = [f'<div class="receipt{" print" if fresh else ""}"><h4>DATASAATHI · PROOF RECEIPT</h4><div class="rule"></div>',
           row("Question", a.question), row("Planner", a.planner), row("Plan", plan_bits), '<div class="rule"></div>']
    if r is not None:
        out += [row("Rows used", len(r.used)), row("Result rows", len(r.table)), row("Explained by", a.explainer)]
        if g is not None:
            out.append(row("Number Guard", "PASSED" if g.ok else "REJECTED MODEL TEXT", "pass" if g.ok else "fail"))
            out.append(row("Numbers verified", len(g.checked)))
        if a.trust_score is not None:
            out.append(row("Data trust", f"{a.trust_score}/100"))
        out.append(row("Caveats", len(r.caveats)))
        for n in a.notes:
            out.append(row("Assumption", n))
    else:
        out += [row("Outcome", "REFUSED (no guess made)", "fail")]
    out.append('<div class="rule"></div>' + row("Code and rows below", "✓ checkable"))
    out.append('</div>')
    return "".join(out)


def finding_card(f, text: str, by: str, idx: int = 0) -> str:
    kind = {"held_load": ("bad", "Held full load"), "spike": ("lite", "Spike"), "drop": ("info", "Unusual drop")}[f.kind]
    return (f'<div class="finding {f.kind} fx" style="--i:{idx}"><div class="h"><span class="chip {kind[0]}">{kind[1]}</span><span>{e(f.entity)}</span>'
            f'<span style="color:{MUTED};font-weight:500">{e(f.label)} · {e(f.period)} · {f.excess_pct:+.0f}% vs expected</span></div>'
            f'<p class="p">{e(text)}</p><div style="color:{MUTED};font-size:.8rem;margin-top:.4rem">Explained by {e(by)}</div></div>')


def trust_bars(table) -> str:
    rows = []
    for _, r in table.iterrows():
        sc = int(r["trust_score"]); col = trust_color(sc)
        rows.append(f'<div class="tbar"><div class="n">{e(r["metric"])}</div><div class="m"><div class="meter" style="margin:0"><i style="width:{sc}%;background:{col}"></i></div></div>'
                    f'<div class="sc" style="color:{col}">{sc}</div></div>'
                    f'<div style="color:{MUTED};font-size:.82rem;margin:-.2rem 0 .5rem">{r["completeness_%"]}% complete · {int(r["duplicates"])} duplicate · {int(r["negatives"])} negative · {int(r["suspect_values"])} suspect</div>')
    return "".join(rows)


def issue_row(sev: str, msg: str) -> str:
    chip = {"high": ("bad", "Fix"), "medium": ("lite", "Check"), "info": ("info", "Note")}[sev]
    return f'<div class="issue {sev}"><span class="chip {chip[0]}">{chip[1]}</span><span>{e(msg)}</span></div>'


def empty_state(title: str, body: str) -> str:
    return f'<div class="empty"><b>{e(title)}</b><br>{e(body)}</div>'


def pipeline_trace(a, fresh: bool = False) -> str:
    """Five-step trace of what the backend actually did for this answer."""
    r, g = a.result, a.guard
    repairs = sum(1 for n in a.notes if n.startswith("Repaired"))
    refused = r is None
    steps = [("Understand", a.planner, "ok"),
             ("Validate", "stopped: no guess made" if refused else (f"{repairs} repair{'s' if repairs != 1 else ''} logged" if repairs else "plan checked"), "stop" if refused else "ok"),
             ("Calculate", "skipped" if refused else f"{len(r.used)} rows · pandas", "skip" if refused else "ok"),
             ("Verify", "skipped" if refused else (f"{len(g.checked)} numbers checked" if g and g.checked else "no figures stated"), "skip" if refused else "ok"),
             ("Receipt", "ready", "ok")]
    mark = {"ok": "✓", "stop": "✕", "skip": "–"}
    out = []
    for i, (name, detail, st_) in enumerate(steps):
        out.append(f'<div class="node {st_}" style="--i:{i}"><span class="dot">{mark[st_]}</span><b>{e(name)}</b><small>{e(detail)}</small></div>')
        if i < len(steps) - 1:
            out.append(f'<span class="link" style="--i:{i}"></span>')
    return f'<div class="pipe{" fx" if fresh else ""}">{"".join(out)}</div>'


def thinking() -> str:
    labels = ["Understanding your question", "Checking it against the Data Card", "Calculating with code",
              "Verifying every number", "Writing the proof receipt"]
    return '<div class="think"><span class="drops"><i></i><i></i><i></i></span>' + "".join(f'<div class="s" style="--d:{i}s">{i + 1}. {e(t)}</div>' for i, t in enumerate(labels)) + '</div>'


def intro() -> str:
    """Welcome curtain, shown once per session: 'HACKTOBER | FEST' written across two curtains that part to reveal the app."""
    return """
<div class="intro" aria-hidden="true">
  <div class="stage">
    <svg class="goo-defs" width="0" height="0"><defs><filter id="goo2"><feGaussianBlur in="SourceGraphic" stdDeviation="16" result="b"/><feColorMatrix in="b" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -9"/></filter></defs></svg>
    <div class="blobs"><i class="b1"></i><i class="b2"></i><i class="b3"></i><i class="b4"></i></div>
    <div class="welcome"><div class="w1">Welcome to DataSaathi</div><div class="w2">Ask your data. Trust the answer.</div></div>
  </div>
  <div class="curtain l"><div class="big">HACKTOBER</div><div class="rule"></div><div class="sub">Hackday@Meerut</div><div class="sub2">2026</div></div>
  <div class="curtain r"><div class="big">FEST</div><div class="rule"></div><div class="sub">&times; E-Cell IIMTU</div><div class="sub2">PS 03 &middot; Gemma 4</div></div>
  <div class="rod"></div>
</div>"""

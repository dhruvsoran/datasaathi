"""Visual layer (2.0 "data observatory"): theme CSS and small HTML components, kept out of app.py so the logic stays readable.
Every number shown here is passed in from code (pandas, the engine, Number Guard); components only format it."""
from __future__ import annotations
import html
import math
from pathlib import Path as _Path

INK, TEAL, VIOLET, AMBER, CORAL, GREEN, BLUE, MUTED = "#EAF2FF", "#2EE6C5", "#8B7CFF", "#FFC24D", "#FF7A8A", "#4BE39A", "#4FB6FF", "#8FA3BF"
RED = CORAL

CSS = "<style>" + (_Path(__file__).with_name("theme.css")).read_text(encoding="utf-8") + "</style>"

# stroke icons (24x24, drawn for this app)
_ICONS = {
    "spark": "M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8",
    "bolt": "M13 2 4 14h7l-1 8 9-12h-7z",
    "drop": "M12 2.7c-3.6 4.4-6 7.9-6 11.3a6 6 0 0 0 12 0c0-3.4-2.4-6.9-6-11.3z",
    "radar": "M12 12l7-7M21 12a9 9 0 1 1-9-9M17 12a5 5 0 1 1-5-5M12 12h.01",
    "shield": "M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6zM9 12l2 2 4-4",
    "history": "M3 12a9 9 0 1 0 3-6.7L3 8M3 3v5h5M12 7v5l3 2",
    "chat": "M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z",
    "check": "M5 12l5 5 9-10",
    "x": "M6 6l12 12M18 6 6 18",
    "alert": "M12 3 2 20h20zM12 10v4M12 17.5v.01",
    "info": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 11v5M12 8v.01",
    "db": "M4 6c0-1.7 3.6-3 8-3s8 1.3 8 3-3.6 3-8 3-8-1.3-8-3zM4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3",
    "cpu": "M7 7h10v10H7zM9 3v4M15 3v4M9 17v4M15 17v4M3 9h4M3 15h4M17 9h4M17 15h4",
    "mic": "M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3zM5 11a7 7 0 0 0 14 0M12 18v3",
    "user": "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0",
    "table": "M3 5h18v14H3zM3 10h18M9 10v9",
    "trend": "M3 17l6-6 4 4 8-8M15 7h6v6",
    "flask": "M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.7 3h10.6a2 2 0 0 0 1.7-3l-5-9V3M7.5 14h9",
    "globe": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18",
    "layers": "M12 3l9 5-9 5-9-5zM3 13l9 5 9-5",
    "list": "M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01",
    "receipt": "M5 3h14v18l-3-2-2 2-2-2-2 2-2-2-3 2zM9 8h6M9 12h6",
    "rank": "M4 20V10M10 20V4M16 20v-7M22 20H2",
}


def e(x) -> str:
    return html.escape(str(x))


def icon(name: str, cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"{c} '
            f'aria-hidden="true"><path d="{_ICONS[name]}"/></svg>')


def trust_color(score: int) -> str:
    return GREEN if score >= 90 else AMBER if score >= 70 else CORAL


def metric_style(metric: str) -> tuple[str, str]:
    """(icon, colour) for a metric column: water is blue, electricity amber, anything else violet."""
    m = metric.lower()
    if "water" in m:
        return "drop", BLUE
    if any(k in m for k in ("electric", "kwh", "power", "energy")):
        return "bolt", AMBER
    return "trend", VIOLET


LOGO = ('<svg width="38" height="38" viewBox="0 0 40 40" aria-hidden="true"><defs><linearGradient id="dsg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{TEAL}"/><stop offset=".55" stop-color="{VIOLET}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient></defs>'
        '<circle cx="20" cy="20" r="17" fill="none" stroke="url(#dsg)" stroke-width="2.5" stroke-dasharray="78 29"/>'
        '<circle cx="20" cy="20" r="9.5" fill="url(#dsg)"/><circle cx="34.5" cy="12" r="3" fill="#FFC24D"/></svg>')


# ---------------- sidebar ----------------
def brand() -> str:
    return (f'<div class="brand">{LOGO}<div><span class="word">DataSaathi</span></div></div>'
            '<div class="brand-sub">Ask your campus data by typing or speaking, in English or Indian languages. Every number comes with proof.</div>')


def side_h(ic: str, text: str) -> str:
    return f'<div class="side-h">{icon(ic)}{e(text)}</div>'


def side_foot() -> str:
    return ('<div class="side-foot"><b>Open source · Apache-2.0</b><br>Synthetic sample data is not an official record. '
            'Numbers are computed by pandas and checked by Number Guard.</div>')


# ---------------- instruments ----------------
_C = 2 * math.pi * 52      # ring circumference (r = 52 in a 120 box)


def ring(score: int | None, small: bool = False) -> str:
    """Ring gauge with a liquid fill whose level is the score. `None` means no data loaded: an empty ring and a dash."""
    size = "1.5rem" if small else "2.2rem"
    if score is None:
        return (f'<div class="ring nodata{" sm" if small else ""}" style="--fs:{size}"><svg viewBox="0 0 120 120">'
                '<circle class="track" cx="60" cy="60" r="52"/><circle class="ticks" cx="60" cy="60" r="40"/></svg>'
                '<div class="num"><b>—</b><small>no data</small></div></div>')
    col = trust_color(score)
    off = _C * (1 - max(0, min(100, score)) / 100)
    return (f'<div class="ring{" sm" if small else ""}" style="--fs:{size};--lc:{col};--lvl:{max(0, min(100, score))}%">'
            '<div class="liquid"><i></i><i></i></div><svg viewBox="0 0 120 120">'
            '<circle class="track" cx="60" cy="60" r="52"/><circle class="ticks" cx="60" cy="60" r="40"/>'
            f'<circle class="val" cx="60" cy="60" r="52" stroke="{col}" style="color:{col};stroke-dasharray:{_C:.2f};stroke-dashoffset:{off:.2f}"/></svg>'
            f'<div class="num"><b style="color:{col}"><span class="cnt" style="--to:{score}">{score}</span></b><small>/ 100</small></div></div>')


def scope(findings, large: bool = False) -> str:
    """Radar scope: a rotating sweep with one blip per Waste Radar finding (angle spread evenly, distance grows with the % excess).
    `None` means no data loaded: an idle scope with a dash."""
    if findings is None:
        return f'<div class="scope idle{" lg" if large else ""}"><div class="sweep"></div><div class="count" style="color:#8395B4">—</div></div>'
    blips = []
    for i, f in enumerate(findings):
        ang = math.radians(i * 137.5 + 35)
        rf = 0.32 + 0.55 * min(1.0, abs(f.excess_pct) / 120)
        x, y = 50 + 50 * rf * math.cos(ang), 50 + 50 * rf * math.sin(ang)
        blips.append(f'<i class="blip {f.kind}" style="left:{x:.1f}%;top:{y:.1f}%;--bd:{i * .45:.2f}s"></i>')
    n = len(findings)
    col = CORAL if n else GREEN
    return (f'<div class="scope{" lg" if large else ""}"><div class="sweep"></div>{"".join(blips)}'
            f'<div class="count" style="color:{col};--fs:{"2.8rem" if large else "2rem"}"><span class="cnt" style="--to:{n}">{n}</span></div></div>')


def sparkline(values, color: str, uid: str, w: int = 128, h: int = 46) -> str:
    v = [float(x) for x in values]
    if len(v) < 2:
        return ""
    lo, hi = min(v), max(v)
    span = (hi - lo) or 1.0
    pts = [(4 + i * (w - 8) / (len(v) - 1), h - 5 - (x - lo) / span * (h - 10)) for i, x in enumerate(v)]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = line + f" L{pts[-1][0]:.1f},{h} L{pts[0][0]:.1f},{h} Z"
    lx, ly = pts[-1]
    return (f'<svg class="spark" viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="{uid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{color}" stop-opacity=".35"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
            f'<path d="{area}" fill="url(#{uid})"/><path class="l" d="{line}"/><circle cx="{lx:.1f}" cy="{ly:.1f}" r="3.2"/></svg>')


GOO = ('<svg class="goo-defs" width="0" height="0" aria-hidden="true"><defs>'
       '<filter id="goo"><feGaussianBlur in="SourceGraphic" stdDeviation="14" result="b"/>'
       '<feColorMatrix in="b" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -9"/></filter>'
       '<filter id="goo-sm"><feGaussianBlur in="SourceGraphic" stdDeviation="4" result="b"/>'
       '<feColorMatrix in="b" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7"/></filter></defs></svg>')
BLOBS = '<div class="blobs" aria-hidden="true"><i class="b1"></i><i class="b2"></i><i class="b3"></i><i class="b4"></i></div>'


def waves(cls: str = "") -> str:
    """Two slow liquid waves for the bottom edge of a panel (each path is two periods wide and slides half its width)."""
    back = "M0,60 C150,100 350,20 600,60 C850,100 1050,20 1200,60 C1350,100 1550,20 1800,60 C2050,100 2250,20 2400,60 L2400,120 L0,120 Z"
    front = "M0,75 C200,40 400,110 600,75 C800,40 1000,110 1200,75 C1400,40 1600,110 1800,75 C2000,40 2200,110 2400,75 L2400,120 L0,120 Z"
    return (f'<svg class="waves back {cls}" viewBox="0 0 2400 120" preserveAspectRatio="none" aria-hidden="true"><path d="{back}"/></svg>'
            f'<svg class="waves front {cls}" viewBox="0 0 2400 120" preserveAspectRatio="none" aria-hidden="true"><path d="{front}"/></svg>')


def kpi_tile(k: dict, j: int) -> str:
    """k: label, unit, metric, month, value, delta (% vs previous month or None), series (monthly campus totals)."""
    ic, col = metric_style(k["metric"])
    d = k.get("delta")
    if d is None:
        dl = ""
    else:
        cls = "flat" if abs(d) < 0.5 else "up" if d > 0 else "down"
        dl = f'<span class="delta {cls}">{"▲" if d > 0 else "▼" if d < 0 else "•"} {abs(d):.1f}%</span>'
    return (f'<div class="glass kpi" style="--i:{3 + j};--c:{col}"><div class="k">{icon(ic)}{e(k["label"])} · campus total</div>'
            f'<div class="v">{k["value"]:,.0f}<small>{e(k["unit"])}</small></div>{sparkline(k["series"], col, f"sp{j}")}'
            f'<div class="sub">{e(k["month"])} {dl}<span>vs previous month</span></div>{waves("tint")}</div>')


def hero(card_name: str, synthetic: bool, period: str, trust: int, findings, mode: str, mode_ok: bool,
         kpis: list | None = None, animate: bool = True, delay: float = 0.0) -> str:
    """Command deck: title, Data Trust ring gauge, Waste Radar scope and a KPI strip with sparklines."""
    syn = (f'<span class="chip syn">{icon("flask")}Synthetic demo data</span>' if synthetic else
           "" if trust is None else f'<span class="chip info">{icon("db")}Your data</span>')
    mchip = f'<span class="chip {"ok" if mode_ok else "lite"}"><span class="orb{"" if mode_ok else " off"}"></span>{e(mode)}</span>'
    n = len(findings) if findings is not None else 0
    if findings is None:
        radar_note = "Waiting for a file. Every building is checked once data is loaded."
    elif n:
        radar_note = f"{n} unusual reading{'s' if n != 1 else ''} found by statistics. See the Waste Radar tab."
    else:
        radar_note = "Nothing unusual found in this data."
    trust_note = "Waiting for a file. The score is computed from the data itself." if trust is None else "Live check of this file: gaps, duplicates, odd values"
    title = (f'<div class="glass title" style="--i:0">{GOO}{BLOBS}{waves()}<div class="eyebrow"><i></i>Community data observatory</div>'
             '<h1>Ask your data.<br><span class="grad">Get answers you can check.</span></h1>'
             '<p>Gemma 4 understands the question. Code does the maths. Every answer ships with the code, the rows and a proof receipt.</p>'
             f'<div class="chips"><span class="chip info">{icon("layers")}{e(card_name)}</span>'
             f'<span class="chip info">{icon("history")}{e(period)}</span>{syn}{mchip}</div></div>')
    gauge = ('<div class="glass inst" style="--i:1" title="Computed live from the loaded dataset: completeness, month gaps, duplicates, impossible values '
             f'and likely typos. A different file gives a different score."><div class="k">Data trust</div>{ring(trust)}'
             f'<div class="s">{trust_note}</div></div>')
    radar = ('<div class="glass inst" style="--i:2" title="Statistical check of every building against its own history and the campus-wide pattern.">'
             f'<div class="k">Waste radar</div>{scope(findings)}'
             f'<div class="s">{radar_note}</div></div>')
    strip = f'<div class="kpis">{"".join(kpi_tile(k, j) for j, k in enumerate(kpis or []))}</div>' if kpis else ""
    return f'<div class="deck{"" if animate else " still"}" style="--d0:{delay}s">{title}{gauge}{radar}{strip}</div>'


# ---------------- Ask ----------------
def section(ic: str, title: str, sub: str = "", color: str = TEAL) -> str:
    return (f'<div class="sec" style="--c:{color}"><div class="ico">{icon(ic)}</div><div><h3>{e(title)}</h3>'
            f'{f"<p>{e(sub)}</p>" if sub else ""}</div></div>')


def group_label(ic: str, text: str, color: str = AMBER) -> str:
    return f'<div class="grp" style="--c:{color}">{icon(ic)}{e(text)}</div>'


def question(q: str) -> str:
    return (f'<div class="ask-bubble"><div class="av">{icon("user")}</div><div class="b"><div class="l">You asked</div>'
            f'<div class="q">{e(q)}</div></div></div>')


def _seal(kind: str) -> str:
    words, cls, ic = {"ok": ("NUMBER GUARD · VERIFIED · ", "", "check"), "code": ("COMPUTED · IN · CODE · ", "", "check"),
                      "warn": ("VERIFIED TEXT · SHOWN · ", "warn", "shield"), "no": ("NO GUESS · REFUSED · ", "no", "x")}[kind]
    pid = f"sealp-{kind}"
    return (f'<div class="seal {cls}" aria-hidden="true"><svg class="rim" viewBox="0 0 100 100"><defs>'
            f'<path id="{pid}" d="M50,50 m-38,0 a38,38 0 1,1 76,0 a38,38 0 1,1 -76,0"/></defs>'
            f'<text><textPath href="#{pid}">{words}</textPath></text></svg><div class="core">{icon(ic)}</div></div>')


def answer_box(text: str, refused: bool, guard_ok, n_verified: int, planner: str, trust: int | None, fresh: bool = False) -> str:
    chips = []
    if refused:
        chips.append(f'<span class="chip bad">{icon("x")}Not answerable from this data</span>')
    else:
        if guard_ok is True:
            chips.append(f'<span class="chip ok">{icon("shield")}Numbers verified ({n_verified})</span>')
        elif guard_ok is False:
            chips.append(f'<span class="chip lite">{icon("alert")}Model wording replaced by verified text</span>')
        if trust is not None:
            chips.append(f'<span class="chip {"ok" if trust >= 90 else "lite" if trust >= 70 else "bad"}">{icon("db")}Data trust {trust}/100</span>')
    chips.append(f'<span class="chip info">{icon("cpu")}Planner: {e(planner)}</span>')
    seal = _seal("no" if refused else "ok" if guard_ok is True else "warn" if guard_ok is False else "code")
    head = f'{icon("x")}Refused · no guess made' if refused else f'{icon("spark")}Answer'
    cls = "answer" + (" refused" if refused else "") + (" fx" if fresh else "")
    return (f'<div class="{cls}" style="--i:1">{seal}<div class="hd">{head}</div><div class="t">{e(text)}</div>'
            f'<div class="meta">{"".join(chips)}</div></div>')


def callout(text: str, kind: str = "warn", idx: int = 0, fresh: bool = False) -> str:
    ic = icon("alert" if kind == "warn" else "info")
    return f'<div class="callout {kind}{" fx" if fresh else ""}" style="--i:{idx + 3}"><span class="ic">{ic}</span><span>{e(text)}</span></div>'


def rows_used(n: int, cols: str) -> str:
    return f'<div class="rows-used">{icon("table")}Based on {n} rows of the dataset · columns: {e(cols)} · full rows in the proof receipt below</div>'


def bignum(label: str, unit: str, value: float, metric: str) -> str:
    ic, col = metric_style(metric)
    return (f'<div class="glass bignum" style="--c:{col}"><div class="ico">{icon(ic)}</div><div><div class="k">{e(label)}</div>'
            f'<div class="v">{value:,.0f}<small>{e(unit)}</small></div></div></div>')


def receipt(a, fresh: bool = False) -> str:
    r = a.result
    g = a.guard
    k = [0]
    def row(name, v, cls=""):
        k[0] += 1
        return f'<div class="row" style="--i:{k[0]}"><span>{e(name)}</span><span class="{cls}">{e(v)}</span></div>'
    p = a.plan
    plan_bits = ", ".join(f"{key}={val}" for key, val in p.model_dump(exclude_none=True).items() if key not in ("top_n",) or p.intent == "rank")
    refused = r is None
    stamp = '<div class="stamp no">REFUSED</div>' if refused else ('<div class="stamp">VERIFIED</div>' if g is None or g.ok else '<div class="stamp no">REPLACED</div>')
    out = [f'<div class="receipt{" print" if fresh else ""}">{stamp}<h4>DATASAATHI · PROOF RECEIPT</h4><div class="sub">COMPUTED IN CODE · CHECKABLE</div><div class="rule"></div>',
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
    out.append('<div class="barcode"></div></div>')
    return "".join(out)


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
    steps = "".join(f'<div class="s" style="--d:{i}s">{i + 1}. {e(t)}</div>' for i, t in enumerate(labels))
    return (f'<div class="glass think">{GOO}<div class="core"><i></i><i></i><i></i></div><div class="steps">{steps}</div>'
            '<span class="drops" aria-hidden="true"><i></i><i></i><i></i></span></div>')


def scroll_script(selector: str, block: str = "start", nonce: int = 0) -> str:
    """Tiny script for a zero-height component: waits for `selector` in the app page and scrolls it into view smoothly."""
    return (f'<script>(function(){{const d=window.parent.document;let n=0;const t=setInterval(function(){{'
            f'const els=[...d.querySelectorAll({selector!r})].filter(function(x){{return x.offsetParent!==null;}});'
            f'if(els.length||++n>60){{clearInterval(t);if(!els.length)return;const el=els[els.length-1],y0=el.getBoundingClientRect().top;'
            f'el.scrollIntoView({{behavior:"smooth",block:{block!r}}});'
            f'setTimeout(function(){{if(Math.abs(el.getBoundingClientRect().top-y0)<2)el.scrollIntoView({{block:{block!r}}});}},700);}}}},100);}})();</script>'
            f'<!-- {nonce} -->')


def listening() -> str:
    return (f'<div class="glass think listen"><div class="core"><i></i><i></i><i></i></div><div class="steps">'
            f'<div class="lt">{icon("mic")}Listening to your recording…</div>'
            '<div class="ls">Turning your voice into text on this computer. The first time also loads the speech model.</div></div></div>')


def voice_head() -> str:
    bars = "".join(f'<i style="animation-delay:{i * .12:.2f}s"></i>' for i in range(9))
    return (f'<div class="vhead"><div class="mic">{icon("mic")}</div><div class="eq">{bars}</div>'
            '<div class="tx"><b>Speak your question</b><span>Press the mic, speak, press stop. Then check the text and press Send.</span></div></div>')


# ---------------- Waste Radar ----------------
def radar_summary(findings, excess_text: str) -> str:
    n = len(findings)
    kinds = [("held_load", CORAL, "Held full load"), ("spike", AMBER, "Spike"), ("drop", BLUE, "Unusual drop")]
    legend = "".join(f'<span><i style="background:{c};box-shadow:0 0 8px {c}"></i>{e(t)} · {sum(f.kind == k for f in findings)}</span>' for k, c, t in kinds)
    sub = f"Estimated excess flagged: {e(excess_text)}." if excess_text else "Readings below expectation are listed for checking."
    return (f'<div class="glass radar-top">{waves()}{scope(findings, large=True)}<div class="txt"><div class="big">{n} unusual reading{"s" if n != 1 else ""} on the scope</div>'
            f'<div style="color:#B9C7DD;line-height:1.5">{sub}</div><div class="legend">{legend}</div></div></div>')


def finding_card(f, text: str, by: str, idx: int = 0) -> str:
    kind = {"held_load": ("bad", "Held full load"), "spike": ("lite", "Spike"), "drop": ("info", "Unusual drop")}[f.kind]
    top = max(f.observed, f.expected) or 1.0
    bars = (f'<span>Actual</span><div class="tr"><i style="width:{f.observed / top * 100:.1f}%;background:var(--c)"></i></div><span class="num">{f.observed:,.0f} {e(f.unit)}</span>'
            f'<span>Expected</span><div class="tr"><i style="width:{f.expected / top * 100:.1f}%;background:rgba(255,255,255,.35)"></i></div><span class="num">{f.expected:,.0f} {e(f.unit)}</span>')
    return (f'<div class="finding {f.kind} fx" style="--i:{idx}"><div class="h"><span class="chip {kind[0]}">{kind[1]}</span><span class="ent">{e(f.entity)}</span>'
            f'<span class="when">{e(f.label)} · {e(f.period)}</span><span class="pct">{f.excess_pct:+.0f}%</span></div>'
            f'<p class="p">{e(text)}</p><div class="bars">{bars}</div><div class="by">Explained by {e(by)}</div></div>')


# ---------------- Data Trust ----------------
def trust_bars(table) -> str:
    cards = []
    for _, r in table.iterrows():
        sc = int(r["trust_score"])
        cards.append(f'<div class="glass tcard">{ring(sc, small=True)}<div><div class="n">{e(r["metric"])}</div><div class="st">'
                     f'<span>Complete</span><b>{r["completeness_%"]}%</b><span>Duplicates</span><b>{int(r["duplicates"])}</b>'
                     f'<span>Negatives</span><b>{int(r["negatives"])}</b><span>Suspect</span><b>{int(r["suspect_values"])}</b></div></div></div>')
    return f'<div class="trust-grid">{"".join(cards)}</div>'


def issue_row(sev: str, msg: str) -> str:
    chip = {"high": ("bad", "Fix"), "medium": ("lite", "Check"), "info": ("info", "Note")}[sev]
    return f'<div class="issue {sev}"><span class="chip {chip[0]}">{chip[1]}</span><span>{e(msg)}</span></div>'


def issues(rows) -> str:
    return f'<div class="tl">{"".join(issue_row(s, m) for s, m in rows)}</div>'


def card_sheet(card) -> str:
    metrics = ", ".join(f'{m.get("label", k)} ({m.get("unit", "")})' for k, m in card.metrics.items())
    items = [("Name", card.name), ("Source", card.source), ("Period", card.period), ("Entity column", card.entity_column),
             ("Time column", card.time_column), ("Metrics", metrics), ("Not in this dataset", ", ".join(card.not_available) or "—"),
             ("Notes", card.notes or "—"), ("Synthetic", "Yes, demo data" if card.synthetic else "No")]
    return '<div class="glass sheet">' + "".join(f'<div><div class="k">{e(k)}</div><div class="v">{e(v)}</div></div>' for k, v in items) + '</div>'


# ---------------- History ----------------
def history_list(sess) -> str:
    rows = [f'<div class="it"><span class="ix">{i + 1:02d}</span><span class="d{" no" if a.status == "refused" else ""}"></span>'
            f'<span class="qq">{e(a.question)}</span><span class="pl">{e(a.planner)}</span></div>' for i, a in enumerate(sess)]
    return f'<div class="hist">{"".join(rows)}</div>'


# ---------------- misc ----------------
def empty_state(title: str, body: str, ic: str = "spark") -> str:
    return f'<div class="empty"><div class="ic">{icon(ic)}</div><div><b>{e(title)}</b>{e(body)}</div></div>'


def footer(mode: str) -> str:
    return (f'<div class="foot"><span><b>DataSaathi</b> · ask community data, get answers you can check</span>'
            f'<span>{e(mode)} · numbers by pandas · Number Guard on</span></div>')


def intro(nonce: int = 0) -> str:
    """Welcome curtain, shown once per session: 'HACKTOBER | FEST' written across two curtains that part to reveal the app.
    `nonce` flips the outer tag on each replay so React builds fresh elements and the animation starts again
    (identical markup would reuse the finished, hidden element)."""
    tag = "section" if nonce % 2 else "div"
    return f'<{tag} class="intro" aria-hidden="true">' + """
  <div class="stage">
    <div class="orbit"></div><div class="orbit o2"></div>
    <div class="welcome"><div class="w1">Welcome to DataSaathi</div><div class="w2 grad">Ask your data. Trust the answer.</div></div>
  </div>
  <div class="curtain l"><div class="big">HACKTOBER</div><div class="rule"></div><div class="sub">Hackday@Meerut</div><div class="sub2">2026</div></div>
  <div class="curtain r"><div class="big">FEST</div><div class="rule"></div><div class="sub">&times; E-Cell IIMTU</div><div class="sub2">PS 03 &middot; Gemma 4</div></div>
  <div class="rod"></div>
""" + f"</{tag}>"

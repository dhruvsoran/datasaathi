"""Visual layer: theme CSS and small HTML components, kept out of app.py so the logic stays readable.
Every number shown here is passed in from code (pandas, the engine, Number Guard); components only format it."""
from __future__ import annotations
import html
from pathlib import Path as _Path

# brand and meaning colours (match theme.css)
INK, TEAL, VIOLET, AMBER, CORAL, GREEN, BLUE, MUTED = "#1B2E21", "#2E6F40", "#6D4FD8", "#C2740A", "#C8372D", "#2E6F40", "#1F6FA8", "#5A7363"
FOREST, MINT, SAGE, DEEP = "#2E6F40", "#CFFFDC", "#68BA7F", "#253D2C"      # the "lush forest" palette
RED = CORAL
WARN = "#B7791F"

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
    "arrow": "M5 12h14M13 6l6 6-6 6",
    "calendar": "M4 6h16v14H4zM4 10h16M8 3v4M16 3v4",
}


def e(x) -> str:
    return html.escape(str(x))


def icon(name: str, cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"{c} '
            f'aria-hidden="true"><path d="{_ICONS[name]}"/></svg>')


def trust_color(score: int) -> str:
    return GREEN if score >= 90 else WARN if score >= 70 else CORAL


def metric_style(metric: str) -> tuple[str, str]:
    """(icon, colour) for a metric column: water is blue, electricity amber, anything else violet."""
    m = metric.lower()
    if "water" in m:
        return "drop", BLUE
    if any(k in m for k in ("electric", "kwh", "power", "energy")):
        return "bolt", AMBER
    return "trend", FOREST


LOGO = ('<svg width="30" height="30" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="#2E6F40"/>'
        + "".join(f'<path class="b" d="M{x} 22V{y}" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>' for x, y in ((9, 16), (14, 11), (19, 18), (24, 9)))
        + '</svg>')


# ---------------- sidebar ----------------
def brand() -> str:
    return (f'<div class="brand">{LOGO}<span class="word">DataSaathi</span></div>'
            '<div class="brand-sub">Ask your campus data by typing or speaking, in English or Indian languages. Every number comes with proof.</div>')


def side_h(ic: str, text: str) -> str:
    return f'<div class="side-h">{e(text)}</div>'


def side_status(text: str, ok: bool) -> str:
    return f'<div class="side-status{"" if ok else " lite"}"><i></i>{e(text)}</div>'


def side_foot() -> str:
    return ('<div class="side-foot"><b>Open source · Apache-2.0</b><br>Synthetic sample data is not an official record. '
            'Numbers are computed by pandas and checked by Number Guard.</div>')


# ---------------- page header + stat cards ----------------
def sparkline(values, color: str, uid: str, w: int = 96, h: int = 32) -> str:
    v = [float(x) for x in values]
    if len(v) < 2:
        return ""
    lo, hi = min(v), max(v)
    span = (hi - lo) or 1.0
    pts = [(2 + i * (w - 4) / (len(v) - 1), h - 3 - (x - lo) / span * (h - 6)) for i, x in enumerate(v)]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = line + f" L{pts[-1][0]:.1f},{h} L{pts[0][0]:.1f},{h} Z"
    lx, ly = pts[-1]
    return (f'<svg class="spark" viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="{uid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{color}" stop-opacity=".22"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
            f'<path d="{area}" fill="url(#{uid})"/><path class="l" d="{line}" pathLength="100"/><circle cx="{lx:.1f}" cy="{ly:.1f}" r="2.6"/></svg>')


def kpi_tile(k: dict, j: int) -> str:
    """k: label, unit, metric, month, value, delta (% vs previous month or None), series (monthly campus totals)."""
    ic, col = metric_style(k["metric"])
    d = k.get("delta")
    if d is None:
        dl = ""
    else:
        cls = "flat" if abs(d) < 0.5 else "up" if d > 0 else "down"
        dl = f'<span class="delta {cls}">{"▲" if d > 0 else "▼" if d < 0 else "•"} {abs(d):.1f}%</span><span>vs previous month</span>'
    return (f'<div class="card stat kpi" style="--i:{2 + j};--c:{col}" title="Sum over every {e(k["label"].lower())} reading in {e(k["month"])}">'
            f'<div class="sh"><span class="lb">{icon(ic)}{e(k["label"])} total</span><span class="when">{e(k["month"])}</span></div>'
            f'<div class="sv"><b>{k["value"]:,.0f}</b><small>{e(k["unit"])}</small></div>'
            f'{sparkline(k["series"], col, f"sp{j}", w=200, h=30)}<div class="kf">{dl}</div></div>')


_KINDS = [("held_load", CORAL, "Held full load"), ("spike", AMBER, "Spike"), ("drop", BLUE, "Unusual drop")]


def hero(card_name: str, synthetic: bool, period: str, trust: int, findings, mode: str, mode_ok: bool,
         kpis: list | None = None, animate: bool = True, delay: float = 0.0) -> str:
    """Page header (title, description, dataset line) and one row of stat cards: Data Trust, Waste Radar, one per metric."""
    meta = [f'<span>{icon("layers")}{e(card_name)}</span>', f'<span>{icon("calendar")}{e(period)}</span>']
    if synthetic:
        meta.append(f'<span>{icon("flask")}Synthetic demo data</span>')
    elif trust is not None:
        meta.append(f'<span>{icon("db")}Your data</span>')
    meta.append(f'<span><i class="dot{"" if mode_ok else " off"}"></i>{e(mode)}</span>')
    head = ('<div class="phead"><div class="ttl"><div class="over">Community data assistant</div>'
            '<h1>Ask your data. <span class="hl">Get answers you can check.</span></h1>'
            '<p>Gemma 4 understands the question, code does the maths, and every answer comes with the code, the rows and a proof receipt.</p>'
            f'<div class="meta-line">{"".join(meta)}</div></div></div>')

    open_t = f'<span class="open"><span>Open</span>{icon("arrow")}</span>'
    if trust is None:
        tv, tbar, tnote = '<b>—</b><small>no data</small>', "", "Waiting for a file. The score is computed from the data itself."
    else:
        col = trust_color(trust)
        tv = f'<b style="color:{col}"><span class="cnt" style="--to:{trust}">{trust}</span></b><small>/ 100</small>'
        tbar = f'<div class="meter"><i style="width:{max(0, min(100, trust))}%;background:{col}"></i></div>'
        tnote = "Gaps, duplicates and odd values in this file"
    gauge = (f'<div class="card stat go{" nodata" if trust is None else ""}" data-goto="Data Trust" role="button" tabindex="0" style="--i:0;--c:{GREEN}" '
             'title="Open the Data Trust tab: completeness, month gaps, duplicates, impossible values and likely typos, computed from the loaded file.">'
             f'<div class="sh"><span class="lb">{icon("shield")}Data trust</span>{open_t}</div><div class="sv">{tv}</div>{tbar}<div class="ss">{tnote}</div></div>')

    if findings is None:
        rv, kinds, rnote = '<b>—</b><small>no data</small>', "", "Waiting for a file. Every building is checked once data is loaded."
    else:
        n = len(findings)
        rv = f'<b><span class="cnt" style="--to:{n}">{n}</span></b><small>unusual reading{"s" if n != 1 else ""}</small>'
        kinds = "".join(f'<span><i style="background:{c}"></i>{sum(f.kind == k for f in findings)} {e(t.lower())}</span>'
                        for k, c, t in _KINDS if any(f.kind == k for f in findings))
        kinds = f'<div class="kinds">{kinds}</div>' if kinds else ""
        rnote = "Found by statistics, explained in the Waste Radar tab" if n else "Nothing unusual found in this data"
    radar = (f'<div class="card stat go{" nodata" if findings is None else ""}" data-goto="Waste Radar" role="button" tabindex="0" style="--i:1;--c:{CORAL}" '
             'title="Open the Waste Radar tab: every building checked against its own history and the campus-wide pattern.">'
             f'<div class="sh"><span class="lb">{icon("radar")}Waste radar</span>{open_t}</div><div class="sv">{rv}</div>{kinds}<div class="ss">{rnote}</div></div>')

    tiles = "".join(kpi_tile(k, j) for j, k in enumerate(kpis or []))
    return f'<div class="deck{"" if animate else " still"}" style="--d0:{delay}s">{head}<div class="stats">{gauge}{radar}{tiles}</div></div>'


# ---------------- Ask ----------------
def section(ic: str, title: str, sub: str = "", color: str = TEAL) -> str:
    return (f'<div class="sec" style="--c:{color}"><div class="ico">{icon(ic)}</div><div><h3>{e(title)}</h3>'
            f'{f"<p>{e(sub)}</p>" if sub else ""}</div></div>')


def group_label(ic: str, text: str, color: str = AMBER) -> str:
    return f'<div class="grp" style="--c:{color}">{icon(ic)}{e(text)}</div>'


def question(q: str, voice: bool = False) -> str:
    label = f'{icon("mic")}You said · voice note' if voice else "You asked"
    return (f'<div class="ask-bubble{" voice" if voice else ""}"><div class="av">{icon("mic" if voice else "user")}</div><div class="b">'
            f'<div class="l">{label}</div><div class="q">{e(q)}</div></div></div>')


def answer_box(text: str, refused: bool, guard_ok, n_verified: int, planner: str, trust: int | None, fresh: bool = False) -> str:
    if refused:
        title, badge = f'{icon("x")}Refused · no guess made', f'<span class="badge bad">{icon("x")}Not answerable from this data</span>'
    else:
        title = f'{icon("spark")}Answer'
        if guard_ok is True:
            badge = f'<span class="badge ok">{icon("shield")}Numbers verified ({n_verified})</span>'
        elif guard_ok is False:
            badge = f'<span class="badge warn">{icon("alert")}Model wording replaced by verified text</span>'
        else:
            badge = f'<span class="badge neutral">{icon("check")}Computed in code</span>'
    meta = []
    if trust is not None and not refused:
        meta.append(f'<span>{icon("db")}Data trust {trust}/100</span>')
    meta.append(f'<span>{icon("cpu")}Planner: {e(planner)}</span>')
    cls = "answer" + (" refused" if refused else "") + (" fx" if fresh else "")
    return (f'<div class="{cls}" style="--i:1"><div class="hd"><span class="ah">{title}</span>{badge}</div>'
            f'<div class="t">{e(text)}</div><div class="meta">{"".join(meta)}</div></div>')


def callout(text: str, kind: str = "warn", idx: int = 0, fresh: bool = False) -> str:
    ic = icon("alert" if kind == "warn" else "info")
    return f'<div class="callout {kind}{" fx" if fresh else ""}" style="--i:{idx + 3}"><span class="ic">{ic}</span><span>{e(text)}</span></div>'


def rows_used(n: int, cols: str) -> str:
    return f'<div class="rows-used">{icon("table")}Based on {n} rows · columns: {e(cols)} · full rows in the proof receipt below</div>'


def bignum(label: str, unit: str, value: float, metric: str) -> str:
    ic, col = metric_style(metric)
    return (f'<div class="card bignum" style="--c:{col}"><div class="ico">{icon(ic)}</div><div><div class="k">{e(label)}</div>'
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
    badge = ('<span class="badge bad">Refused</span>' if refused else
             '<span class="badge ok">Verified</span>' if g is None or g.ok else '<span class="badge warn">Model text replaced</span>')
    out = [f'<div class="receipt{" fx" if fresh else ""}"><div class="rh"><div><h4>Proof receipt</h4><div class="sub">Computed in code · checkable</div></div>{badge}</div>'
           '<div class="rule"></div>', row("Question", a.question), row("Planner", a.planner), row("Plan", plan_bits), '<div class="rule"></div>']
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
    out.append('<div class="rule"></div>' + row("Code and rows", "below ✓") + '</div>')
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
        out.append(f'<div class="node {st_}" style="--i:{i}"><span class="dot">{mark[st_]}</span><div><b>{e(name)}</b><small>{e(detail)}</small></div></div>')
        if i < len(steps) - 1:
            out.append(f'<span class="link" style="--i:{i}"></span>')
    return f'<div class="pipe{" fx" if fresh else ""}" style="--i:2">{"".join(out)}</div>'


def thinking() -> str:
    labels = ["Understanding your question", "Checking it against the Data Card", "Calculating with code",
              "Verifying every number", "Writing the proof receipt"]
    steps = "".join(f'<div class="s" style="--d:{i}s">{i + 1}. {e(t)}</div>' for i, t in enumerate(labels))
    return f'<div class="card think"><div class="spin"></div><div class="steps">{steps}</div><i class="bar"></i></div>'


def scroll_script(selector: str, block: str = "start", nonce: int = 0) -> str:
    """Tiny script for a zero-height component: waits for `selector` in the app page and scrolls it into view smoothly."""
    return (f'<script>(function(){{const d=window.parent.document;let n=0;const t=setInterval(function(){{'
            f'const els=[...d.querySelectorAll({selector!r})].filter(function(x){{return x.offsetParent!==null;}});'
            f'if(els.length||++n>60){{clearInterval(t);if(!els.length)return;const el=els[els.length-1],y0=el.getBoundingClientRect().top;'
            f'el.scrollIntoView({{behavior:"smooth",block:{block!r}}});'
            f'setTimeout(function(){{if(Math.abs(el.getBoundingClientRect().top-y0)<2)el.scrollIntoView({{block:{block!r}}});}},700);}}}},100);}})();</script>'
            f'<!-- {nonce} -->')


def goto_script() -> str:
    """Installed once per page in a hidden iframe: a click (or Enter / Space) on an element with data-goto="Tab name" opens that tab
    and brings the tab bar to the top. The bar is re-checked a few times because the newly shown tab can still be drawing (charts)
    and push the page while it scrolls. Fixed text from our code; it only reads the page, clicks the tab button and sets
    html[data-scrolling] while the page is being scrolled."""
    # The handlers belong to this iframe: if Streamlit removed the iframe (the upload screen without a file stops the page early),
    # they stop running, so a new iframe installs them again unless the one that installed them is still alive.
    # While the page scrolls, html[data-scrolling] pauses the purely decorative loops so scrolling stays smooth.
    return ("<script>(function(){const w=window.parent,d=w.document;if(w.__dsGoto&&!w.__dsGoto.closed)return;w.__dsGoto=window;"
            "let st=null;d.addEventListener('scroll',function(e){if(!e.target||e.target.getAttribute===undefined||"
            "e.target.getAttribute('data-testid')!=='stMain')return;d.documentElement.dataset.scrolling='1';clearTimeout(st);"
            "st=setTimeout(function(){delete d.documentElement.dataset.scrolling;},180);},{capture:true,passive:true});"
            "function scroller(){return d.querySelector('[data-testid=stMain]')||d.scrollingElement;}"
            "function go(card){const name=card.getAttribute('data-goto');"
            "const tab=[...d.querySelectorAll('[role=tab]')].find(function(t){return t.innerText.indexOf(name)>-1;});"
            "if(!tab)return;tab.click();const bar=tab.closest('[data-testid=stTabs]')||tab;"
            "const target=function(s){return s.scrollTop+bar.getBoundingClientRect().top-70;};"
            "setTimeout(function(){const s=scroller();s.scrollTo({top:target(s),behavior:'smooth'});},40);"
            "[450,900,1500].forEach(function(t){setTimeout(function(){const s=scroller();"
            "if(Math.abs(bar.getBoundingClientRect().top-70)>30)s.scrollTop=target(s);},t);});}"
            "d.addEventListener('click',function(e){const c=e.target.closest&&e.target.closest('[data-goto]');if(c)go(c);});"
            "d.addEventListener('keydown',function(e){if(e.key!=='Enter'&&e.key!==' ')return;"
            "const c=e.target.closest&&e.target.closest('[data-goto]');if(c){e.preventDefault();go(c);}});})();</script>")


def lang_label() -> str:
    return (f'<div class="lang-pill" title="The language you will speak in voice notes. Auto-detect works for most questions; '
            f'picking the language improves accuracy for Indian languages.">{icon("mic")}<span>Speak in</span></div>')


def listening() -> str:
    bars = "".join(f'<i style="animation-delay:{i * .11:.2f}s"></i>' for i in range(7))
    return (f'<div class="card think listen"><div class="eq">{bars}</div><div class="steps">'
            '<div class="lt">Listening to your recording…</div>'
            '<div class="ls">Turning your voice into text on this computer. The first time also loads the speech model.</div></div><i class="bar"></i></div>')


# ---------------- Waste Radar ----------------
def radar_summary(findings, excess_text: str) -> str:
    n = len(findings)
    legend = "".join(f'<span><i style="background:{c}"></i>{e(t)} · {sum(f.kind == k for f in findings)}</span>' for k, c, t in _KINDS)
    sub = f"Estimated excess flagged: {e(excess_text)}." if excess_text else "Readings below expectation are listed for checking."
    return (f'<div class="card radar-top"><div class="rc{" live" if n else ""}"><b>{n}</b><span>unusual reading{"s" if n != 1 else ""}</span></div>'
            f'<div class="txt"><div class="big">What the radar found</div><div class="sub2">{sub}</div><div class="legend">{legend}</div></div></div>')


def finding_card(f, text: str, by: str, idx: int = 0) -> str:
    kind = {"held_load": ("bad", "Held full load"), "spike": ("warn", "Spike"), "drop": ("info", "Unusual drop")}[f.kind]
    top = max(f.observed, f.expected) or 1.0
    bars = (f'<span>Actual</span><div class="tr"><i style="width:{f.observed / top * 100:.1f}%;background:var(--c)"></i></div><span class="num">{f.observed:,.0f} {e(f.unit)}</span>'
            f'<span>Expected</span><div class="tr"><i style="width:{f.expected / top * 100:.1f}%;background:#A9C9B2"></i></div><span class="num">{f.expected:,.0f} {e(f.unit)}</span>')
    return (f'<div class="card finding {f.kind} fx" style="--i:{idx}"><div class="h"><span class="badge {kind[0]}">{kind[1]}</span><span class="ent">{e(f.entity)}</span>'
            f'<span class="when">{e(f.label)} · {e(f.period)}</span><span class="pct">{f.excess_pct:+.0f}%</span></div>'
            f'<p class="p">{e(text)}</p><div class="bars">{bars}</div><div class="by">Explained by {e(by)}</div></div>')


# ---------------- Data Trust ----------------
def trust_bars(table) -> str:
    cards = []
    for j, (_, r) in enumerate(table.iterrows()):
        sc = int(r["trust_score"])
        col = trust_color(sc)
        cards.append(f'<div class="card tcard" style="--i:{j}"><div class="n"><span>{e(r["metric"])}</span><b style="color:{col}">{sc}<small>/100</small></b></div>'
                     f'<div class="meter"><i style="width:{max(0, min(100, sc))}%;background:{col}"></i></div><div class="st">'
                     f'<span>Complete</span><b>{r["completeness_%"]}%</b><span>Duplicates</span><b>{int(r["duplicates"])}</b>'
                     f'<span>Negatives</span><b>{int(r["negatives"])}</b><span>Suspect</span><b>{int(r["suspect_values"])}</b></div></div>')
    return f'<div class="trust-grid">{"".join(cards)}</div>'


def issue_row(sev: str, msg: str, i: int = 0) -> str:
    chip = {"high": ("bad", "Fix"), "medium": ("warn", "Check"), "info": ("info", "Note")}[sev]
    return f'<div class="issue {sev}" style="--i:{i}"><span class="badge {chip[0]}">{chip[1]}</span><span>{e(msg)}</span></div>'


def issues(rows) -> str:
    return f'<div class="card issue-list">{"".join(issue_row(s, m, i) for i, (s, m) in enumerate(rows))}</div>'


def card_sheet(card) -> str:
    metrics = ", ".join(f'{m.get("label", k)} ({m.get("unit", "")})' for k, m in card.metrics.items())
    items = [("Name", card.name), ("Source", card.source), ("Period", card.period), ("Entity column", card.entity_column),
             ("Time column", card.time_column), ("Metrics", metrics), ("Not in this dataset", ", ".join(card.not_available) or "—"),
             ("Notes", card.notes or "—"), ("Synthetic", "Yes, demo data" if card.synthetic else "No")]
    return '<div class="sheet">' + "".join(f'<div><div class="k">{e(k)}</div><div class="v">{e(v)}</div></div>' for k, v in items) + '</div>'


# ---------------- History ----------------
def history_list(sess) -> str:
    rows = [f'<div class="it" style="--i:{i}"><span class="ix">{i + 1:02d}</span><span class="d{" no" if a.status == "refused" else ""}"></span>'
            f'<span class="qq">{e(a.question)}</span><span class="pl">{e(a.planner)}</span></div>' for i, a in enumerate(sess)]
    return f'<div class="card hist">{"".join(rows)}</div>'


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
    <div class="welcome"><div class="w1">Welcome to DataSaathi</div><div class="w2">Ask your data. Trust the answer.</div></div>
  </div>
  <div class="curtain l"><div class="big">HACKTOBER</div><div class="rule"></div><div class="sub">Hackday@Meerut</div><div class="sub2">2026</div></div>
  <div class="curtain r"><div class="big">FEST</div><div class="rule"></div><div class="sub">&times; E-Cell IIMTU</div><div class="sub2">PS 03 &middot; Gemma 4</div></div>
""" + f"</{tag}>"

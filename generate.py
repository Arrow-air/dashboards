#!/usr/bin/env python3
"""Generate the state-of-Arrow dashboard (static HTML) from data.json."""
import json
import html
import pathlib

HERE = pathlib.Path(__file__).parent
data = json.loads((HERE / "data.json").read_text())
e = html.escape

def project_card(p):
    parked = p["status"] == "parked"
    cls = "card parked" if parked else "card"
    blocker = p["blocker"]
    blocker_html = (
        f'<div class="row blocker"><span class="lbl">Blocker</span>{e(blocker)}</div>'
        if blocker and blocker != "—" else
        '<div class="row blocker none"><span class="lbl">Blocker</span>—</div>'
    )
    badge = '<span class="badge parked-badge">parked</span>' if parked else '<span class="badge active-badge">active</span>'
    return f'''
    <div class="{cls}">
      <div class="card-head"><span class="pemoji">{p["emoji"]}</span><h3>{e(p["name"])}</h3>{badge}</div>
      <div class="row"><span class="lbl">Lead</span>{e(p["lead"])}</div>
      <div class="row"><span class="lbl">Phase</span>{e(p["phase"])}</div>
      <div class="row"><span class="lbl">Next</span>{e(p["milestone"])}</div>
      {blocker_html}
      <div class="updated">updated {e(p["updated"])}</div>
    </div>'''

def action_row(a):
    return f'<tr><td class="owner">{e(a["owner"])}</td><td>{e(a["item"])}</td><td class="due">{e(a["due"])}</td><td class="where">{e(a["where"])}</td></tr>'

def gov_row(g):
    return f'<li class="gov {g["state"]}"><span class="dot"></span>{e(g["item"])}<span class="gstate">{e(g["state"])}</span></li>'

def pulse_row(p):
    url = f'https://github.com/Arrow-air/{p["repo"]}/pull/{p["pr"]}'
    return (f'<tr><td class="repo">{e(p["repo"])}</td>'
            f'<td><a href="{url}">#{p["pr"]}</a> {e(p["title"])}</td>'
            f'<td class="owner">{e(p["author"])}</td><td class="due">{e(p["age"])} open</td></tr>')

def cal_row(c):
    return f'<li><span class="when">{e(c["when"])}</span>{e(c["what"])}</li>'

html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Arrow — State of the DAO</title>
<style>
  :root {{
    --bg: #0d1117; --panel: #161b22; --border: #2d333b; --text: #e6edf3;
    --dim: #8b949e; --accent: #e8590c; --green: #3fb950; --amber: #d29922; --red: #f85149;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font: 15px/1.5 -apple-system, "Segoe UI", Roboto, sans-serif; padding: 28px 32px 60px; }}
  header {{ display: flex; align-items: baseline; gap: 14px; margin-bottom: 6px; flex-wrap: wrap; }}
  header h1 {{ font-size: 26px; letter-spacing: .5px; }}
  header h1 .arrow {{ color: var(--accent); }}
  .gen {{ color: var(--dim); font-size: 13px; }}
  .tagline {{ color: var(--dim); margin-bottom: 26px; font-size: 14px; }}
  h2 {{ font-size: 15px; text-transform: uppercase; letter-spacing: 1.5px; color: var(--dim); margin: 34px 0 14px; border-bottom: 1px solid var(--border); padding-bottom: 6px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }}
  .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 16px 18px; }}
  .card.parked {{ opacity: .55; }}
  .card-head {{ display: flex; align-items: center; gap: 9px; margin-bottom: 10px; }}
  .card-head h3 {{ font-size: 17px; flex: 1; }}
  .pemoji {{ font-size: 20px; }}
  .badge {{ font-size: 11px; padding: 2px 9px; border-radius: 20px; text-transform: uppercase; letter-spacing: .5px; }}
  .active-badge {{ background: rgba(63,185,80,.15); color: var(--green); border: 1px solid rgba(63,185,80,.4); }}
  .parked-badge {{ background: rgba(139,148,158,.15); color: var(--dim); border: 1px solid var(--border); }}
  .row {{ margin: 6px 0; font-size: 14px; }}
  .lbl {{ display: inline-block; min-width: 62px; color: var(--dim); font-size: 12px; text-transform: uppercase; letter-spacing: .8px; }}
  .blocker {{ color: var(--amber); }}
  .blocker.none {{ color: var(--dim); }}
  .updated {{ margin-top: 10px; font-size: 12px; color: var(--dim); text-align: right; }}
  table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }}
  td {{ padding: 9px 14px; border-top: 1px solid var(--border); font-size: 14px; }}
  tr:first-child td {{ border-top: none; }}
  .owner {{ color: var(--accent); white-space: nowrap; font-weight: 600; }}
  .due {{ color: var(--dim); white-space: nowrap; }}
  .where, .repo {{ color: var(--dim); white-space: nowrap; }}
  a {{ color: #58a6ff; text-decoration: none; }}
  ul {{ list-style: none; }}
  .gov {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }}
  .dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--dim); flex-shrink: 0; }}
  .gov.draft .dot {{ background: var(--amber); }}
  .gov.quiet .dot {{ background: var(--green); }}
  .gov.future .dot {{ background: var(--dim); }}
  .gstate {{ margin-left: auto; font-size: 12px; color: var(--dim); text-transform: uppercase; letter-spacing: .5px; }}
  .cal li {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; }}
  .when {{ display: inline-block; min-width: 110px; color: var(--accent); font-weight: 600; }}
  .treasury {{ background: var(--panel); border: 1px dashed var(--border); border-radius: 10px; padding: 14px 18px; color: var(--dim); font-size: 14px; }}
  footer {{ margin-top: 46px; color: var(--dim); font-size: 12.5px; border-top: 1px solid var(--border); padding-top: 14px; }}
  .cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }}
  @media (max-width: 900px) {{ .cols {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<header><h1><span class="arrow">🏹 Arrow</span> — State of the DAO</h1><span class="gen">generated {e(data["generated"])} · by Vector</span></header>
<div class="tagline">Open-source VTOL aircraft, built by a global community. This page regenerates from meeting notes, GitHub, Discord, and chain state.</div>

<h2>Projects</h2>
<div class="grid">{''.join(project_card(p) for p in data["projects"])}</div>

<h2>Action Register — who has the ball</h2>
<table>{''.join(action_row(a) for a in data["actions"])}</table>

<div class="cols">
<div>
<h2>Governance</h2>
<ul>{''.join(gov_row(g) for g in data["governance"])}</ul>
<h2>Treasury</h2>
<div class="treasury">{e(data["treasury"]["note"])}</div>
</div>
<div>
<h2>Calendar</h2>
<ul class="cal">{''.join(cal_row(c) for c in data["calendar"])}</ul>
</div>
</div>

<h2>GitHub Pulse — PRs awaiting review</h2>
<table>{''.join(pulse_row(p) for p in data["pulse"])}</table>

<footer>🏹 Arrow DAO · arrowair.com · Maintained by Vector — report stale info in #bot-chat · Every card shows its last-updated date; staleness is a bug.</footer>
</body>
</html>'''

(HERE / "index.html").write_text(html_out)
print(f"wrote {HERE / 'index.html'} ({len(html_out)} bytes)")

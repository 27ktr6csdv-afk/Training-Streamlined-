#!/usr/bin/env python3
"""Dealer Pit Rotation & Break Scheduler.

Generates a self-contained interactive HTML tool (no internet required) where a
pit manager can:

  1. Paste the dealer roster (one dealer per line, optionally with games).
  2. Fine-tune each dealer's game qualifications in a checkbox grid.
  3. Define the pit's open tables and shift settings.
  4. Generate a fair rotation in 20-minute pushes with staggered 20-minute
     breaks, plus per-dealer fairness stats, CSV export, and a print view.

Usage:
    python3 dealer_scheduler.py                 # writes dealer_scheduler.html
    python3 dealer_scheduler.py -o pit_a.html   # custom output path
    python3 dealer_scheduler.py --open          # also open in your browser
    python3 dealer_scheduler.py --serve 8000    # serve it at http://localhost:8000
"""

import argparse
import sys
import webbrowser
from pathlib import Path

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dealer Pit Rotation Scheduler</title>
<style>
  :root {
    --bg: #10141c; --panel: #1a2130; --panel-2: #222b3e; --line: #32405c;
    --text: #e8edf6; --muted: #93a1ba; --accent: #4da3ff; --accent-2: #35c98f;
    --warn: #ffb54d; --bad: #ff6b6b; --break-bg: #2c3a2f; --break-fg: #8fd6a5;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 24px; background: var(--bg); color: var(--text);
    font: 15px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  }
  h1 { margin: 0 0 4px; font-size: 26px; }
  h2 { font-size: 17px; margin: 0 0 10px; color: var(--accent); }
  .sub { color: var(--muted); margin-bottom: 22px; }
  .card {
    background: var(--panel); border: 1px solid var(--line); border-radius: 10px;
    padding: 18px; margin-bottom: 18px;
  }
  .step { display: inline-block; background: var(--accent); color: #06121f;
    border-radius: 50%; width: 24px; height: 24px; text-align: center;
    line-height: 24px; font-weight: 700; margin-right: 8px; font-size: 14px; }
  textarea, input[type=text], input[type=time], input[type=number], select {
    background: var(--panel-2); color: var(--text); border: 1px solid var(--line);
    border-radius: 6px; padding: 8px 10px; font: inherit;
  }
  textarea { width: 100%; min-height: 130px; resize: vertical; }
  textarea:focus, input:focus, select:focus { outline: 2px solid var(--accent); outline-offset: -1px; }
  button {
    background: var(--accent); color: #06121f; border: 0; border-radius: 7px;
    padding: 9px 16px; font: inherit; font-weight: 600; cursor: pointer;
  }
  button:hover { filter: brightness(1.12); }
  button.secondary { background: var(--panel-2); color: var(--text); border: 1px solid var(--line); }
  button.small { padding: 4px 10px; font-size: 13px; }
  button.danger { background: transparent; color: var(--bad); border: 1px solid var(--bad); }
  .row { display: flex; gap: 14px; flex-wrap: wrap; align-items: flex-end; }
  .field { display: flex; flex-direction: column; gap: 4px; }
  .field label { font-size: 13px; color: var(--muted); }
  .hint { font-size: 13px; color: var(--muted); margin-top: 8px; }
  .scroll { overflow-x: auto; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid var(--line); padding: 7px 10px; text-align: left; font-size: 14px; }
  th { background: var(--panel-2); position: sticky; top: 0; }
  #qualGrid td.check { text-align: center; cursor: pointer; user-select: none; }
  #qualGrid td.check.on { background: rgba(53, 201, 143, .18); color: var(--accent-2); font-weight: 700; }
  #qualGrid td.check.off { color: #4a566e; }
  .sched td.duty { background: rgba(77, 163, 255, .10); }
  .sched td.brk { background: var(--break-bg); color: var(--break-fg); font-weight: 600; }
  .sched td.uncovered { background: rgba(255, 107, 107, .22); color: var(--bad); font-weight: 700; }
  .sched td.timecol { white-space: nowrap; color: var(--muted); }
  .pill { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12.5px;
    background: var(--panel-2); border: 1px solid var(--line); margin: 2px 4px 2px 0; }
  .warnbox { border-left: 4px solid var(--warn); background: rgba(255,181,77,.08);
    padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: var(--warn); }
  .errbox { border-left: 4px solid var(--bad); background: rgba(255,107,107,.08);
    padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: var(--bad); }
  .toolbar { display: flex; gap: 10px; margin: 12px 0; flex-wrap: wrap; }
  .tableRow { display: flex; gap: 10px; align-items: center; margin-bottom: 8px; }
  #results { display: none; }
  @media print {
    body { background: #fff; color: #000; padding: 0; }
    .card { border: 1px solid #999; }
    .no-print, #setup { display: none !important; }
    #results { display: block !important; }
    th, td { border-color: #999; }
    .sched td.brk { background: #dfeee2 !important; color: #1e5c34; }
    .sched td.duty { background: #eef4fc !important; }
    th { background: #e8e8e8 !important; color: #000; }
  }
</style>
</head>
<body>
<h1>🎰 Dealer Pit Rotation Scheduler</h1>
<div class="sub">Paste your roster, set qualifications, and generate fair 20-minute pit rotations with staggered 20-minute breaks.</div>

<div id="setup">
  <div class="card">
    <h2><span class="step">1</span>Paste Dealer Roster</h2>
    <textarea id="rosterInput" placeholder="One dealer per line. Optionally list games after a colon or comma:
Maria Lopez: Blackjack, Roulette, Baccarat
James Chen: Blackjack, Craps
Tina Brooks
DeShawn Riley: Blackjack, Pai Gow, Three Card Poker"></textarea>
    <div class="row" style="margin-top:10px">
      <div class="field" style="flex:1; min-width:280px">
        <label>Games offered in this pit (comma-separated)</label>
        <input type="text" id="gamesInput" value="Blackjack, Craps, Roulette, Baccarat, Pai Gow, Three Card Poker">
      </div>
      <button onclick="parseRoster()">Load Roster →</button>
    </div>
    <div class="hint">Games listed next to a name are pre-checked in the grid below. Names without games start unqualified — check their games in step 2.</div>
  </div>

  <div class="card" id="qualCard" style="display:none">
    <h2><span class="step">2</span>Game Qualifications</h2>
    <div class="hint" style="margin:0 0 10px">Click a cell to toggle. ✔ = qualified to deal that game.</div>
    <div class="scroll"><table id="qualGrid"></table></div>
  </div>

  <div class="card" id="pitCard" style="display:none">
    <h2><span class="step">3</span>Pit Tables &amp; Shift Settings</h2>
    <div id="tableList"></div>
    <button class="secondary small" onclick="addTableRow()">+ Add Table</button>
    <div class="row" style="margin-top:16px">
      <div class="field"><label>Shift start</label><input type="time" id="shiftStart" value="20:00"></div>
      <div class="field"><label>Shift length (hours)</label>
        <input type="number" id="shiftHours" value="8" min="1" max="12" step="0.5" style="width:90px"></div>
      <div class="field"><label>Time on tables before break</label>
        <select id="workSlots">
          <option value="3" selected>60 min (3 pushes)</option>
          <option value="4">80 min (4 pushes)</option>
          <option value="2">40 min (2 pushes)</option>
          <option value="1">20 min (1 push)</option>
        </select></div>
      <button onclick="generateSchedule()" style="background:var(--accent-2)">⚡ Generate Schedule</button>
    </div>
    <div class="hint">Rotations run in fixed 20-minute pushes; every break is one full 20-minute push. Breaks are staggered so tables stay covered.</div>
  </div>
</div>

<div id="results" class="card">
  <h2>📋 Rotation Schedule</h2>
  <div id="messages"></div>
  <div class="scroll"><table class="sched" id="schedTable"></table></div>
  <h2 style="margin-top:22px">⚖️ Fairness Summary</h2>
  <div class="scroll"><table id="fairTable"></table></div>
  <div class="toolbar no-print">
    <button class="secondary" onclick="window.print()">🖨 Print</button>
    <button class="secondary" onclick="exportCSV()">⬇ Export CSV</button>
    <button class="secondary" onclick="document.getElementById('setup').scrollIntoView({behavior:'smooth'})">↑ Back to Setup</button>
  </div>
</div>

<script>
"use strict";
const SLOT_MIN = 20;                 // one push = 20 minutes; one break = 20 minutes
let dealers = [];                    // {name, quals:Set}
let games = [];
let lastSchedule = null;

/* ---------- Step 1: roster parsing ---------- */
function parseRoster() {
  games = document.getElementById('gamesInput').value
    .split(',').map(g => g.trim()).filter(Boolean);
  const lines = document.getElementById('rosterInput').value
    .split('\n').map(l => l.trim()).filter(Boolean);
  if (!games.length) { alert('Please list at least one game.'); return; }
  if (!lines.length) { alert('Please paste at least one dealer.'); return; }

  const gameLookup = {};
  games.forEach(g => gameLookup[g.toLowerCase()] = g);
  dealers = lines.map(line => {
    // Split "Name: game, game" or "Name - game, game"; else whole line = name
    let name = line, gamePart = '';
    const m = line.match(/^([^:\-–]+)[:\-–](.+)$/);
    if (m && m[2].split(',').some(t => gameLookup[t.trim().toLowerCase()])) {
      name = m[1].trim(); gamePart = m[2];
    }
    const quals = new Set();
    gamePart.split(',').forEach(t => {
      const g = gameLookup[t.trim().toLowerCase()];
      if (g) quals.add(g);
    });
    return { name, quals };
  });
  renderQualGrid();
  ensureTableRows();
  document.getElementById('qualCard').style.display = 'block';
  document.getElementById('pitCard').style.display = 'block';
  saveState();
}

function renderQualGrid() {
  const t = document.getElementById('qualGrid');
  let h = '<tr><th>Dealer</th>' + games.map(g => `<th>${esc(g)}</th>`).join('') + '</tr>';
  dealers.forEach((d, i) => {
    h += `<tr><td><strong>${esc(d.name)}</strong></td>`;
    games.forEach(g => {
      const on = d.quals.has(g);
      h += `<td class="check ${on ? 'on' : 'off'}" onclick="toggleQual(${i},'${esc(g)}')">${on ? '✔' : '·'}</td>`;
    });
    h += '</tr>';
  });
  t.innerHTML = h;
}

function toggleQual(i, game) {
  const d = dealers[i];
  d.quals.has(game) ? d.quals.delete(game) : d.quals.add(game);
  renderQualGrid();
  saveState();
}

/* ---------- Step 3: pit tables ---------- */
function ensureTableRows() {
  const list = document.getElementById('tableList');
  if (!list.children.length) { addTableRow('BJ-1', games[0]); addTableRow('BJ-2', games[0]); }
  else list.querySelectorAll('select').forEach(refreshGameOptions);
}

function addTableRow(name, game) {
  const div = document.createElement('div');
  div.className = 'tableRow';
  const sel = document.createElement('select');
  refreshGameOptions(sel, game);
  div.innerHTML = `<input type="text" placeholder="Table name (e.g. BJ-3)" value="${esc(name || '')}" style="width:180px">`;
  div.appendChild(sel);
  const del = document.createElement('button');
  del.className = 'danger small'; del.textContent = '✕';
  del.onclick = () => div.remove();
  div.appendChild(del);
  document.getElementById('tableList').appendChild(div);
}

function refreshGameOptions(sel, chosen) {
  const cur = chosen || sel.value;
  sel.innerHTML = games.map(g => `<option ${g === cur ? 'selected' : ''}>${esc(g)}</option>`).join('');
}

function getTables() {
  return [...document.querySelectorAll('#tableList .tableRow')].map((r, i) => ({
    name: r.querySelector('input').value.trim() || `Table ${i + 1}`,
    game: r.querySelector('select').value
  }));
}

/* ---------- Scheduling engine ---------- */
function generateSchedule() {
  const tables = getTables();
  const msgs = [];
  if (!tables.length) { alert('Add at least one table.'); return; }
  if (!dealers.length) { alert('Load a roster first.'); return; }

  // Hard feasibility checks
  const errors = [];
  tables.forEach(t => {
    if (!dealers.some(d => d.quals.has(t.game)))
      errors.push(`No dealer is qualified for ${t.game} (table ${t.name}).`);
  });
  if (dealers.length < tables.length)
    errors.push(`You have ${dealers.length} dealers for ${tables.length} tables — not enough to open every table.`);
  const workSlots = parseInt(document.getElementById('workSlots').value, 10);
  const minStaff = Math.ceil(tables.length * (workSlots + 1) / workSlots);
  if (!errors.length && dealers.length < minStaff)
    msgs.push(`Tight staffing: covering ${tables.length} tables with ${workSlots * SLOT_MIN}-minute pushes ideally needs ${minStaff}+ dealers (you have ${dealers.length}). Breaks may run late.`);

  const shiftHours = parseFloat(document.getElementById('shiftHours').value) || 8;
  const numSlots = Math.round(shiftHours * 60 / SLOT_MIN);
  const startMin = timeToMin(document.getElementById('shiftStart').value || '20:00');

  if (errors.length) {
    document.getElementById('results').style.display = 'block';
    document.getElementById('messages').innerHTML =
      errors.map(e => `<div class="errbox">⛔ ${esc(e)}</div>`).join('');
    document.getElementById('schedTable').innerHTML = '';
    document.getElementById('fairTable').innerHTML = '';
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    return;
  }

  // Per-dealer running stats
  const st = dealers.map(() => ({
    consec: 0, sinceBreak: 0, totalWork: 0, breaks: 0,
    lastTable: -1, gameTime: {}, tableTime: {}
  }));
  const grid = [];       // grid[slot][table] = dealer index or -1 (uncovered)
  const breakGrid = [];  // breakGrid[slot] = [dealer indices on break]
  let uncoveredCount = 0;

  // Stagger initial break offsets so the whole crew isn't due at once
  const cycle = workSlots + 1;
  dealers.forEach((d, i) => { st[i].consec = i % cycle === workSlots ? workSlots : (i % cycle); });

  for (let s = 0; s < numSlots; s++) {
    const assigned = new Array(tables.length).fill(-1);
    const used = new Set();

    // Dealers who must break this push (hit their consecutive-work limit)
    const mustBreak = new Set();
    dealers.forEach((d, i) => { if (st[i].consec >= workSlots) mustBreak.add(i); });

    // Fill most-constrained tables first (fewest currently-available qualified dealers)
    const order = tables.map((t, ti) => ({
      ti,
      n: dealers.filter((d, i) => d.quals.has(t.game) && !mustBreak.has(i)).length
    })).sort((a, b) => a.n - b.n).map(o => o.ti);

    for (const ti of order) {
      const t = tables[ti];
      let pick = pickDealer(t, ti, used, i => !mustBreak.has(i), st);
      if (pick === -1) {
        // Nobody free & qualified — pull the breaker who most recently rested
        pick = pickDealer(t, ti, used, i => true, st, true);
        if (pick !== -1) mustBreak.delete(pick);
      }
      if (pick === -1) { uncoveredCount++; }
      else { assigned[ti] = pick; used.add(pick); }
    }

    // Everyone unassigned takes this push as a break
    const onBreak = [];
    dealers.forEach((d, i) => {
      if (used.has(i)) {
        st[i].consec++; st[i].sinceBreak++; st[i].totalWork++;
      } else {
        onBreak.push(i);
        st[i].breaks++; st[i].consec = 0; st[i].sinceBreak = 0;
      }
    });
    assigned.forEach((di, ti) => {
      if (di === -1) return;
      const g = tables[ti].game;
      st[di].gameTime[g] = (st[di].gameTime[g] || 0) + 1;
      st[di].tableTime[ti] = (st[di].tableTime[ti] || 0) + 1;
      st[di].lastTable = ti;
    });
    dealers.forEach((d, i) => { if (!used.has(i)) st[i].lastTable = -1; });

    grid.push(assigned);
    breakGrid.push(onBreak);
  }

  if (uncoveredCount)
    msgs.push(`${uncoveredCount} table push(es) could not be covered by a qualified dealer — shown in red. Add cross-trained dealers or close a table.`);

  lastSchedule = { grid, breakGrid, tables, numSlots, startMin, st };
  renderSchedule(msgs);
}

// Choose the best dealer for a table this push.
// Cost prefers: least total work → variety (least time on this game/table) →
// avoids leaving someone at the same table twice in a row → most-rested first.
function pickDealer(t, ti, used, allow, st, fromBreak) {
  let best = -1, bestCost = Infinity;
  dealers.forEach((d, i) => {
    if (used.has(i) || !d.quals.has(t.game) || !allow(i)) return;
    const s = st[i];
    const cost =
      (s.lastTable === ti ? 1000 : 0) +          // don't repeat the same table
      s.totalWork * 50 +                          // balance total table time
      (s.tableTime[ti] || 0) * 20 +               // spread across tables
      (s.gameTime[t.game] || 0) * 10 +            // spread across games
      (fromBreak ? s.consec * 5 : -s.consec * 2); // pulling from break: prefer most rested
    if (cost < bestCost) { bestCost = cost; best = i; }
  });
  return best;
}

/* ---------- Rendering & export ---------- */
function renderSchedule(msgs) {
  const { grid, breakGrid, tables, numSlots, startMin, st } = lastSchedule;
  document.getElementById('messages').innerHTML =
    msgs.map(m => `<div class="warnbox">⚠️ ${esc(m)}</div>`).join('');

  let h = '<tr><th>Time</th>' +
    tables.map(t => `<th>${esc(t.name)}<br><span style="font-weight:400;color:var(--muted)">${esc(t.game)}</span></th>`).join('') +
    '<th>On Break ☕</th></tr>';
  for (let s = 0; s < numSlots; s++) {
    h += `<tr><td class="timecol">${minToTime(startMin + s * SLOT_MIN)}–${minToTime(startMin + (s + 1) * SLOT_MIN)}</td>`;
    grid[s].forEach(di => {
      h += di === -1 ? '<td class="uncovered">UNCOVERED</td>'
                     : `<td class="duty">${esc(dealers[di].name)}</td>`;
    });
    h += `<td class="brk">${breakGrid[s].map(i => esc(dealers[i].name)).join(', ') || '—'}</td></tr>`;
  }
  document.getElementById('schedTable').innerHTML = h;

  let f = '<tr><th>Dealer</th><th>Table time</th><th>Breaks</th><th>Games dealt</th></tr>';
  dealers.forEach((d, i) => {
    const gamesDealt = Object.entries(st[i].gameTime)
      .map(([g, n]) => `<span class="pill">${esc(g)} × ${n}</span>`).join(' ') || '—';
    f += `<tr><td><strong>${esc(d.name)}</strong></td>` +
      `<td>${st[i].totalWork * SLOT_MIN} min</td>` +
      `<td>${st[i].breaks} × ${SLOT_MIN} min</td><td>${gamesDealt}</td></tr>`;
  });
  document.getElementById('fairTable').innerHTML = f;

  document.getElementById('results').style.display = 'block';
  document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

function exportCSV() {
  if (!lastSchedule) return;
  const { grid, breakGrid, tables, numSlots, startMin } = lastSchedule;
  const rows = [['Time', ...tables.map(t => `${t.name} (${t.game})`), 'On Break']];
  for (let s = 0; s < numSlots; s++) {
    rows.push([
      `${minToTime(startMin + s * SLOT_MIN)}-${minToTime(startMin + (s + 1) * SLOT_MIN)}`,
      ...grid[s].map(di => di === -1 ? 'UNCOVERED' : dealers[di].name),
      breakGrid[s].map(i => dealers[i].name).join('; ')
    ]);
  }
  const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
  a.download = 'pit_rotation_schedule.csv';
  a.click();
  URL.revokeObjectURL(a.href);
}

/* ---------- Helpers & persistence ---------- */
function esc(s) { return String(s).replace(/[&<>"']/g,
  c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
function timeToMin(t) { const [h, m] = t.split(':').map(Number); return h * 60 + m; }
function minToTime(m) {
  m = ((m % 1440) + 1440) % 1440;
  return `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`;
}

function saveState() {
  try {
    localStorage.setItem('pitScheduler', JSON.stringify({
      roster: document.getElementById('rosterInput').value,
      games,
      quals: dealers.map(d => ({ name: d.name, quals: [...d.quals] }))
    }));
  } catch (e) { /* private mode — skip */ }
}

(function restore() {
  try {
    const raw = localStorage.getItem('pitScheduler');
    if (!raw) return;
    const s = JSON.parse(raw);
    if (s.roster) document.getElementById('rosterInput').value = s.roster;
    if (s.games && s.games.length) document.getElementById('gamesInput').value = s.games.join(', ');
    if (s.quals && s.quals.length) {
      games = s.games || [];
      dealers = s.quals.map(d => ({ name: d.name, quals: new Set(d.quals) }));
      renderQualGrid();
      ensureTableRows();
      document.getElementById('qualCard').style.display = 'block';
      document.getElementById('pitCard').style.display = 'block';
    }
  } catch (e) { /* corrupt state — start fresh */ }
})();
</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the interactive dealer pit rotation scheduler (HTML)."
    )
    parser.add_argument(
        "-o", "--output", default="dealer_scheduler.html",
        help="output HTML file path (default: dealer_scheduler.html)",
    )
    parser.add_argument(
        "--open", action="store_true", help="open the generated file in a browser"
    )
    parser.add_argument(
        "--serve", nargs="?", const=8000, type=int, metavar="PORT",
        help="serve the tool over HTTP on PORT (default 8000) instead of just writing the file",
    )
    args = parser.parse_args()

    out = Path(args.output)
    out.write_text(HTML_PAGE, encoding="utf-8")
    print(f"Wrote {out.resolve()}")

    if args.serve is not None:
        import http.server

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                body = HTML_PAGE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_):
                pass

        addr = ("127.0.0.1", args.serve)
        print(f"Serving at http://{addr[0]}:{addr[1]}  (Ctrl+C to stop)")
        if args.open:
            webbrowser.open(f"http://{addr[0]}:{addr[1]}")
        try:
            http.server.HTTPServer(addr, Handler).serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
    elif args.open:
        webbrowser.open(out.resolve().as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())

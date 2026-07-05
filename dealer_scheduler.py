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
    --bg: #0c1310; --panel: #141e18; --panel-2: #1b2820; --line: #2b4033;
    --text: #ecf2ed; --muted: #8fa79a;
    --felt: #3fcb82; --felt-ink: #06170e;
    --gold: #d9a441; --gold-soft: rgba(217, 164, 65, .14);
    --bad: #ff6b6b; --warn: #e8b558;
    --duty-bg: rgba(63, 203, 130, .09);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 28px clamp(16px, 4vw, 48px); background: var(--bg); color: var(--text);
    font: 15px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  }
  h1 { margin: 0 0 4px; font-size: 27px; letter-spacing: -.01em; }
  h2 {
    font-size: 13px; margin: 0 0 14px; color: var(--gold);
    text-transform: uppercase; letter-spacing: .14em; font-weight: 700;
  }
  .sub { color: var(--muted); margin-bottom: 26px; max-width: 62ch; }
  .card {
    background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
    padding: 20px; margin-bottom: 18px;
  }
  .step {
    display: inline-block; background: var(--panel-2); color: var(--felt);
    border: 1px solid var(--felt); border-radius: 50%; width: 24px; height: 24px;
    text-align: center; line-height: 22px; font-weight: 700; margin-right: 10px; font-size: 13px;
  }
  textarea, input[type=text], input[type=time], input[type=number], select {
    background: var(--panel-2); color: var(--text); border: 1px solid var(--line);
    border-radius: 7px; padding: 8px 10px; font: inherit;
  }
  textarea { width: 100%; min-height: 130px; resize: vertical; }
  textarea:focus, input:focus, select:focus, button:focus-visible {
    outline: 2px solid var(--felt); outline-offset: -1px;
  }
  button {
    background: var(--felt); color: var(--felt-ink); border: 0; border-radius: 8px;
    padding: 9px 18px; font: inherit; font-weight: 650; cursor: pointer;
  }
  button:hover { filter: brightness(1.1); }
  button.secondary { background: var(--panel-2); color: var(--text); border: 1px solid var(--line); }
  button.small { padding: 4px 10px; font-size: 13px; }
  button.danger { background: transparent; color: var(--bad); border: 1px solid var(--bad); }
  .row { display: flex; gap: 14px; flex-wrap: wrap; align-items: flex-end; }
  .field { display: flex; flex-direction: column; gap: 4px; }
  .field label { font-size: 13px; color: var(--muted); }
  .hint { font-size: 13px; color: var(--muted); margin-top: 10px; max-width: 78ch; }
  .scroll { overflow-x: auto; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid var(--line); padding: 7px 11px; text-align: left; font-size: 14px; }
  th {
    background: var(--panel-2); position: sticky; top: 0; font-size: 12.5px;
    text-transform: uppercase; letter-spacing: .06em; color: var(--muted);
  }
  th strong, .sched th { color: var(--text); }
  #qualGrid td.check { text-align: center; cursor: pointer; user-select: none; }
  #qualGrid td.check.on { background: var(--duty-bg); color: var(--felt); font-weight: 700; }
  #qualGrid td.check.off { color: #44584c; }
  .sched td.duty { background: var(--duty-bg); }
  .sched td.brk { background: var(--gold-soft); color: var(--gold); font-weight: 600; }
  .sched td.uncovered { background: rgba(255, 107, 107, .18); color: var(--bad); font-weight: 700; }
  .sched td.timecol {
    white-space: nowrap; color: var(--muted);
    font-variant-numeric: tabular-nums; font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    font-size: 13px;
  }
  .pill {
    display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12.5px;
    background: var(--panel-2); border: 1px solid var(--line); margin: 2px 4px 2px 0;
    font-variant-numeric: tabular-nums;
  }
  .warnbox { border-left: 3px solid var(--warn); background: rgba(232,181,88,.08);
    padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: var(--warn); }
  .errbox { border-left: 3px solid var(--bad); background: rgba(255,107,107,.08);
    padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: var(--bad); }
  .okbox { border-left: 3px solid var(--felt); background: var(--duty-bg);
    padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: var(--felt); }
  .toolbar { display: flex; gap: 10px; margin: 14px 0 0; flex-wrap: wrap; }
  .tableRow { display: flex; gap: 10px; align-items: center; margin-bottom: 8px; }
  #results { display: none; }
  @media print {
    body { background: #fff; color: #000; padding: 0; }
    .card { border: 1px solid #999; }
    .no-print, #setup { display: none !important; }
    #results { display: block !important; }
    th, td { border-color: #999; }
    .sched td.brk { background: #f4e8cf !important; color: #7a5b17; }
    .sched td.duty { background: #e6f3ea !important; }
    th { background: #e8e8e8 !important; color: #000; }
    h2 { color: #000; }
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
      <button id="loadRosterBtn">Load Roster →</button>
      <button id="uploadBtn" class="secondary">📂 Upload CSV / Excel</button>
      <input type="file" id="fileInput" accept=".csv,.tsv,.txt,.xlsx,.xlsm,.xls" style="display:none">
    </div>
    <div id="step1Msg" style="margin-top:12px"></div>
    <div class="hint">Games listed next to a name are pre-checked in the grid below. Names without games start unqualified — check their games in step 2.
    Uploads accept CSV or Excel (.xlsx): either <em>Name, Games…</em> rows, or a grid with dealer names in the first column, game names as column headers, and X marks for qualifications.</div>
  </div>

  <div class="card" id="qualCard" style="display:none">
    <h2><span class="step">2</span>Game Qualifications</h2>
    <div class="hint" style="margin:0 0 10px">Click a cell to toggle. ✔ = qualified to deal that game.</div>
    <div class="scroll"><table id="qualGrid"></table></div>
  </div>

  <div class="card" id="pitCard" style="display:none">
    <h2><span class="step">3</span>Pit Tables &amp; Shift Settings</h2>
    <div id="tableList"></div>
    <button class="secondary small" id="addTableBtn">+ Add Table</button>
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
      <button id="generateBtn" style="background:var(--gold)">⚡ Generate Schedule</button>
    </div>
    <div id="pitMsg" style="margin-top:12px"></div>
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
    <button class="secondary" id="printBtn">🖨 Print</button>
    <button class="secondary" id="csvBtn">⬇ Export CSV</button>
    <button class="secondary" id="backBtn">↑ Back to Setup</button>
  </div>
</div>

<script>
"use strict";
const SLOT_MIN = 20;                 // one push = 20 minutes; one break = 20 minutes
let dealers = [];                    // {name, quals:Set}
let games = [];
let lastSchedule = null;

/* ---------- Inline notices (alert() is blocked in sandboxed embeds) ---------- */
function showMsg(elId, text, kind) {
  const cls = kind === 'error' ? 'errbox' : kind === 'ok' ? 'okbox' : 'warnbox';
  document.getElementById(elId).innerHTML = text ? `<div class="${cls}">${text}</div>` : '';
}

/* ---------- Step 1: roster parsing ---------- */
function parseRoster() {
  showMsg('step1Msg', '');
  games = document.getElementById('gamesInput').value
    .split(',').map(g => g.trim()).filter(Boolean);
  const lines = document.getElementById('rosterInput').value
    .split('\n').map(l => l.trim()).filter(Boolean);
  if (!games.length) { showMsg('step1Msg', '⛔ Please list at least one game.', 'error'); return false; }
  if (!lines.length) {
    showMsg('step1Msg', '⛔ The roster box is empty — the grey text is just an example. Paste your dealers above or upload a CSV/Excel file.', 'error');
    return false;
  }

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
  showMsg('step1Msg', `✅ Loaded ${dealers.length} dealer${dealers.length === 1 ? '' : 's'}. Review qualifications in step 2, then set up your pit in step 3.`, 'ok');
  return true;
}

function renderQualGrid() {
  const t = document.getElementById('qualGrid');
  let h = '<tr><th>Dealer</th>' + games.map(g => `<th>${esc(g)}</th>`).join('') + '</tr>';
  dealers.forEach((d, i) => {
    h += `<tr><td><strong>${esc(d.name)}</strong></td>`;
    games.forEach(g => {
      const on = d.quals.has(g);
      h += `<td class="check ${on ? 'on' : 'off'}" data-i="${i}" data-g="${esc(g)}">${on ? '✔' : '·'}</td>`;
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
  showMsg('pitMsg', '');
  if (!tables.length) { showMsg('pitMsg', '⛔ Add at least one table.', 'error'); return; }
  if (!dealers.length) { showMsg('pitMsg', '⛔ Load a roster in step 1 first.', 'error'); return; }

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

/* ---------- Roster file upload (CSV / Excel) ---------- */
async function handleRosterFile(file) {
  showMsg('step1Msg', `⏳ Reading ${esc(file.name)}…`);
  try {
    let rows;
    const fname = file.name.toLowerCase();
    if (fname.endsWith('.xlsx') || fname.endsWith('.xlsm')) rows = await readXlsx(file);
    else if (fname.endsWith('.xls'))
      throw new Error('Legacy .xls files are not supported — in Excel use File → Save As → .xlsx or CSV.');
    else rows = parseDelimited(await file.text());
    const { lines, added } = rowsToRoster(rows);
    document.getElementById('rosterInput').value = lines.join('\n');
    if (parseRoster()) {
      showMsg('step1Msg',
        `✅ Loaded ${dealers.length} dealer${dealers.length === 1 ? '' : 's'} from ${esc(file.name)}.` +
        (added.length ? ` Added games from the file: ${added.map(esc).join(', ')}.` : '') +
        ' Review qualifications in step 2.', 'ok');
    }
  } catch (e) {
    showMsg('step1Msg', '⛔ ' + esc(e && e.message ? e.message : e), 'error');
  }
}

// Turn spreadsheet rows into roster lines. Two layouts are recognized:
//  A) Matrix: dealer names in column 1, game names as column headers, and
//     any mark (X, yes, 1, ✓ …) meaning "qualified".
//  B) List: each row is "Name, game, game" (or games comma-packed in one cell).
function rowsToRoster(rows) {
  rows = rows.map(r => r.map(c => String(c == null ? '' : c).trim())).filter(r => r.some(Boolean));
  if (!rows.length) throw new Error('The file has no data rows.');

  const gamesInput = document.getElementById('gamesInput');
  const known = gamesInput.value.split(',').map(g => g.trim()).filter(Boolean);
  const lower = new Map(known.map(g => [g.toLowerCase(), g]));
  const NO = /^(no|n|0|false|-|–|—)$/i;
  const MARK = /^(x+|yes|y|1|true|✓|✔|q|qual(ified)?)$/i;

  const header = rows[0];
  const nameHeader = /^(dealer|name|employee|staff)/i.test(header[0] || '');
  const gameCols = header.slice(1).map((h, j) => ({ h, j: j + 1 })).filter(o => o.h);
  const headerHasKnownGame = gameCols.some(o => lower.has(o.h.toLowerCase()));
  const dataCells = rows.slice(1).flatMap(r => r.slice(1)).filter(Boolean);
  const mostlyMarks = dataCells.length > 0 &&
    dataCells.filter(c => MARK.test(c) || NO.test(c)).length / dataCells.length > 0.6;
  const isMatrix = gameCols.length > 0 && (headerHasKnownGame || (nameHeader && mostlyMarks));

  const added = [];
  const claim = (label) => {
    const k = label.toLowerCase();
    if (!lower.has(k)) { lower.set(k, label); added.push(label); }
    return lower.get(k);
  };
  const lines = [];

  if (isMatrix) {
    const cols = gameCols.map(o => ({ j: o.j, g: claim(o.h) }));
    rows.slice(1).forEach(r => {
      if (!r[0]) return;
      const gs = cols.filter(o => r[o.j] && !NO.test(r[o.j])).map(o => o.g);
      lines.push(gs.length ? `${r[0]}: ${gs.join(', ')}` : r[0]);
    });
  } else {
    (nameHeader ? rows.slice(1) : rows).forEach(r => {
      if (!r[0]) return;
      const gs = r.slice(1).join(',').split(',').map(t => t.trim())
        .filter(t => t && /[a-z]/i.test(t))   // skip IDs, dates, bare numbers
        .map(claim);
      lines.push(gs.length ? `${r[0]}: ${gs.join(', ')}` : r[0]);
    });
  }

  if (!lines.length) throw new Error('No dealer names found in the first column.');
  if (added.length) gamesInput.value = [...new Set([...known, ...added])].join(', ');
  return { lines, added };
}

// Quote-aware CSV/TSV parser; auto-detects comma, semicolon, or tab.
function parseDelimited(text) {
  text = text.replace(/^\uFEFF/, '');
  const first = text.split(/\r?\n/, 1)[0] || '';
  const delim = first.includes('\t') ? '\t'
    : first.split(';').length > first.split(',').length ? ';' : ',';
  const rows = []; let row = [], cell = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) {
      if (ch === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; }
      else cell += ch;
    }
    else if (ch === '"') q = true;
    else if (ch === delim) { row.push(cell); cell = ''; }
    else if (ch === '\n') { row.push(cell); rows.push(row); row = []; cell = ''; }
    else if (ch !== '\r') cell += ch;
  }
  if (cell !== '' || row.length) { row.push(cell); rows.push(row); }
  return rows;
}

// Minimal .xlsx reader: a .xlsx is a zip of XML files. The zip directory is
// walked by hand and entries are inflated with the browser's built-in
// DecompressionStream, so no external library is needed (CSP-safe, offline).
async function readXlsx(file) {
  if (typeof DecompressionStream === 'undefined')
    throw new Error('This browser cannot read .xlsx directly — save the roster as CSV instead.');
  const entries = unzipEntries(new Uint8Array(await file.arrayBuffer()));

  const sheetName = Object.keys(entries)
    .filter(n => /^xl\/worksheets\/sheet\d+\.xml$/.test(n))
    .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }))[0];
  if (!sheetName) throw new Error('No worksheet found in this Excel file.');

  const xml = s => new DOMParser().parseFromString(s, 'application/xml');
  const shared = [];
  if (entries['xl/sharedStrings.xml']) {
    xml(await entries['xl/sharedStrings.xml']()).querySelectorAll('si').forEach(si =>
      shared.push([...si.querySelectorAll('t')].map(t => t.textContent).join('')));
  }

  const rows = [];
  xml(await entries[sheetName]()).querySelectorAll('row').forEach(rowEl => {
    const row = [];
    rowEl.querySelectorAll('c').forEach(c => {
      const letters = (c.getAttribute('r') || '').replace(/\d+$/, '');
      let col = row.length;
      if (letters) {
        col = 0;
        for (const ch of letters.toUpperCase()) col = col * 26 + (ch.charCodeAt(0) - 64);
        col -= 1;
      }
      const t = c.getAttribute('t');
      const v = c.querySelector('v');
      row[col] = t === 's' ? (shared[+(v ? v.textContent : 0)] ?? '')
        : t === 'inlineStr' ? [...c.querySelectorAll('t')].map(x => x.textContent).join('')
        : (v ? v.textContent : '');
    });
    rows.push(Array.from(row, x => x ?? ''));
  });
  return rows;
}

function unzipEntries(u8) {
  const dv = new DataView(u8.buffer, u8.byteOffset, u8.byteLength);
  let eocd = -1;
  for (let i = u8.length - 22; i >= Math.max(0, u8.length - 22 - 65535); i--)
    if (dv.getUint32(i, true) === 0x06054b50) { eocd = i; break; }
  if (eocd < 0) throw new Error('Not a valid .xlsx file.');
  let off = dv.getUint32(eocd + 16, true);
  const count = dv.getUint16(eocd + 10, true);
  const entries = {};
  for (let k = 0; k < count; k++) {
    if (dv.getUint32(off, true) !== 0x02014b50) break;
    const method = dv.getUint16(off + 10, true);
    const csize = dv.getUint32(off + 20, true);
    const nlen = dv.getUint16(off + 28, true);
    const elen = dv.getUint16(off + 30, true);
    const clen = dv.getUint16(off + 32, true);
    const lho = dv.getUint32(off + 42, true);
    const name = new TextDecoder().decode(u8.subarray(off + 46, off + 46 + nlen));
    entries[name] = async () => {
      const lnlen = dv.getUint16(lho + 26, true), lelen = dv.getUint16(lho + 28, true);
      const start = lho + 30 + lnlen + lelen;
      const data = u8.subarray(start, start + csize);
      if (method === 0) return new TextDecoder().decode(data);
      if (method !== 8) throw new Error('Unsupported compression inside this .xlsx.');
      return await new Response(
        new Blob([data]).stream().pipeThrough(new DecompressionStream('deflate-raw'))
      ).text();
    };
    off += 46 + nlen + elen + clen;
  }
  return entries;
}

/* ---------- Event wiring (inline handlers are blocked under strict CSP) ---------- */
document.getElementById('loadRosterBtn').addEventListener('click', parseRoster);
document.getElementById('uploadBtn').addEventListener('click',
  () => document.getElementById('fileInput').click());
document.getElementById('fileInput').addEventListener('change', e => {
  if (e.target.files[0]) handleRosterFile(e.target.files[0]);
  e.target.value = '';
});
document.getElementById('qualGrid').addEventListener('click', e => {
  const td = e.target.closest('td.check');
  if (td) toggleQual(+td.dataset.i, td.dataset.g);
});
document.getElementById('addTableBtn').addEventListener('click', () => addTableRow());
document.getElementById('generateBtn').addEventListener('click', generateSchedule);
document.getElementById('printBtn').addEventListener('click', () => window.print());
document.getElementById('csvBtn').addEventListener('click', exportCSV);
document.getElementById('backBtn').addEventListener('click',
  () => document.getElementById('setup').scrollIntoView({ behavior: 'smooth' }));

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

# Dealer Pit Rotation Scheduler

A Python script that generates a self-contained, interactive HTML tool for
building fair casino pit rotations and 20-minute break schedules.

## Quick start

```bash
python3 dealer_scheduler.py --open
```

This writes `dealer_scheduler.html` and opens it in your browser. No internet
connection or extra packages are needed — everything runs locally in the page.

Other options:

```bash
python3 dealer_scheduler.py -o swing_shift.html   # custom output file
python3 dealer_scheduler.py --serve 8000          # serve at http://localhost:8000
```

## How to use the tool

1. **Paste your roster** — one dealer per line. You can pre-fill qualifications
   inline, e.g. `Maria Lopez: Blackjack, Roulette, Baccarat`, or paste plain
   names and check games in the grid. The pit's game list is editable.
2. **Set qualifications** — click cells in the dealer × game grid to toggle ✔.
3. **Define the pit** — add each open table (name + game), set the shift start
   time, shift length, and how long dealers stay on tables between breaks
   (default 60 minutes on / 20 minutes off).
4. **Generate** — the schedule shows who deals each table for every 20-minute
   push and who is on break, plus a fairness summary (total table time, break
   count, and game variety per dealer). Export to CSV or print for the podium.

## How the rotation works

- Time is divided into fixed **20-minute pushes**; every break is one full push.
- Dealers work at most the configured number of consecutive pushes (default 3
  = 60 min) before they are rotated to a 20-minute break.
- Breaks are **staggered** across the crew so every table stays covered.
- Assignments only ever put dealers on games they are qualified for, and the
  engine balances total table time, spreads dealers across different tables
  and games for variety, and avoids leaving anyone at the same table two
  pushes in a row.
- If staffing is too tight or a game has no qualified dealer, the tool warns
  you up front and flags any uncoverable pushes in red.

Your roster and qualifications are saved in the browser (localStorage), so
they're still there the next time you open the page.

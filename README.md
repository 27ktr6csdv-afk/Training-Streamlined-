# Dealer Hand Logger

A single-file, mobile-responsive web app for casino supervisors to log dealer
speed and procedural errors from an iPad (or any phone/tablet/laptop).

## How to use

Open `index.html` in any browser — no install, no server, no dependencies.
On an iPad, you can use Safari's **Share → Add to Home Screen** to run it
full-screen like a native app.

1. **Start a session** — enter the dealer's name, pick the game, optionally a
   table number.
2. **Tap "HAND COMPLETE"** every time a hand finishes. The app records the
   time per hand and keeps live stats: hand count, average hand time,
   hands per hour.
3. **Tap an error button** (Misdeal, Card Flash, Wrong Payout, Procedure) the
   moment a procedural error occurs — it attaches to the hand currently in
   progress and shows up tagged in the hand log.
4. **Undo** removes the most recent entry (a pending error first, otherwise
   the last hand) if you mis-tap.
5. **End Session** shows a summary: total hands, session length, average /
   fastest / slowest hand, hands per hour, and an error breakdown — with a
   one-tap **PDF report** (measurables, error breakdown, a ruled Trainer
   Notes area, and signature/date lines for a personal training file) and a
   **CSV export** of the raw per-hand data.

## Details

- **Data stays on the device** in `localStorage`. The last 50 sessions are
  kept under **View Past Sessions**, and each can be re-opened and exported.
- An in-progress session **survives a refresh or accidental tab close** — the
  app resumes it automatically.
- Hand time is measured from the end of the previous hand (or session start)
  to the tap, so shuffles and pauses are included in the hand they precede.

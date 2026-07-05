# Casino Dealer Training Simulator

An interactive quiz tool for training casino dealers, available in two forms:

- **Web app** — `webapp/index.html`, a self-contained single file (no build,
  no dependencies). Open it in any browser: felt-table UI with card, dice,
  chip and roulette graphics, clickable answers, scoring, and light/dark
  themes.
- **Terminal app** — pure Python 3.10+ standard library, same drills and
  payout schedules.

Both cover the same five drills described below.

## Run the web app

```bash
open webapp/index.html        # or just double-click it
```

## Run the terminal app

```bash
python -m dealer_trainer
```

Pick a drill from the menu, choose how many questions, and answer each one.
Dollar answers accept `40`, `$40`, `37.50`, or `$1,250`. Type `q` at any
prompt to end a drill early; wrong answers show the correct payout and a short
explanation of the math.

## Drills

### 1. Blackjack — payouts, insurance & soft totals
Every question displays the player's hand and the dealer's upcard, then quizzes:
- **Payouts** — blackjack pays 3:2, standard wins pay even money.
- **Insurance logic** — offered only on a dealer ace, maximum half the bet,
  pays 2:1, collected when the dealer has no blackjack, and even money on a
  player blackjack.
- **Soft-hand totals** — call the hand like a dealer: "soft 17", "hard 12".

### 2. Craps — base dealing payouts
- Pass / Don't Pass / Come / Don't Come at even money.
- True odds: 4 & 10 pay 2:1, 5 & 9 pay 3:2, 6 & 8 pay 6:5.
- Place bets: 4 & 10 pay 9:5, 5 & 9 pay 7:5, 6 & 8 pay 7:6.
- Field: 2 pays double, 12 pays triple, everything else even money.
- Buy bets on the 4 and 10 at true odds with a 5% commission.

### 3. Craps — proposition (center) payouts
- Hard 4/10 at 7:1 and hard 6/8 at 9:1.
- One-roll bets: Any Seven 4:1, Any Craps 7:1, Aces & Twelve 30:1,
  Ace-Deuce & Yo 15:1.
- Split bets quizzed on the **net** payout the stick calls: Horn, C & E,
  and the World (including the push on a 7).

### 4. Roulette — payouts
American double-zero schedule: straight up 35:1, split 17:1, street 11:1,
corner 8:1, top line 6:1, six line 5:1, dozens/columns 2:1, even-money bets
1:1 — plus "stacked" questions where one winning number is covered by several
bets and you pay the whole picture.

### 5. Baccarat — banker commission
- Marking 5% commission on a winning banker bet.
- Paying in full with lammers vs. netting the commission out immediately.
- Totaling the commission owed across a whole shoe at color-up.
- Player-bet wins as a no-commission control question.

There is also a **mixed drill** that pulls questions from every game.

## House rules

Payout schedules follow the most common Las Vegas rules (3:2 blackjack,
triple-12 field, 5% baccarat commission). They live in small tables at the top
of each module in `dealer_trainer/` and are easy to adjust for your house.

## Tests

```bash
python -m unittest discover tests
```

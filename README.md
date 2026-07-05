# Casino Dealer Training Simulator

An interactive quiz tool for training casino dealers, available in two forms:

- **Web app** — `webapp/index.html`, a self-contained single file (no build,
  no dependencies). Open it in any browser: felt-table UI with card, dice,
  chip and roulette graphics, clickable answers, scoring, and light/dark
  themes.
- **Terminal app** — pure Python 3.10+ standard library, the same games and
  payout schedules with classic fixed-difficulty drills.

Both cover the five games described below.

## Dealer-readiness engine (web app)

The web app trains real dealer math, not just game knowledge. Every game has a
catalog of question concepts across **five difficulty levels**:

| Level | Focus | Example |
|---|---|---|
| 1 | Basic rules | "What does a straight-up bet pay?" — 35 to 1 |
| 2 | Basic payouts | $5 on the Yo, 11 rolls — pay $75 |
| 3 | Multi-bet payouts | C&E / Horn / High-Low split-bet breakdowns |
| 4 | Real dealer math | Commission on a $675 banker bet — $33.75 |
| 5 | Compound math | 7 straight + 8 corner + 6 split units = 411 units |

### Training modes

- **Learn** — payout tables, split-bet anatomy, and worked examples per game.
- **Practice** — adaptive drills: three straight correct promotes the game a
  level; a miss becomes a *drill-back* (same concept, different phrasing) that
  must be answered clean twice before the level can rise; three misses steps
  the level back down. Levels persist per game.
- **Speed Drill** — 20 hands, 60 seconds, auto-advancing; scored on accuracy
  and pace.
- **Floor Ready Test** — 12 hard (Level 3+) hands across every game; 85%+
  earns the FLOOR READY stamp.
- **Weakness Review** — every answer in every mode is tracked by game and bet
  type; the menu recommends the most-missed categories and this mode drills
  them directly.
- **Unit Conversion** — roulette is taught **units first** (3 straight-up
  units pays 105 units), then converted to dollars at the player's chip value
  ($5 unit → $525; $25 unit → $2,625).

### Compound craps engine

Split bets settle piece by piece with the standard anatomy: a $10 C&E is
$5 Any Craps + $5 Eleven; a $15 Horn High 12 is $3/$3/$3 with $6 on the 12;
a $6 High-Low is $3 on 2 + $3 on 12. Questions default to the **gross winning
payout** (how dealers learn it) with a settings toggle for net-after-take, and
explanations show the full winning/losing breakdown — e.g. with all three bets
up, an 11 pays $120 gross, a 12 pays $305, a 3 pays $80.

### Property settings & custom questions

Baccarat commission defaults to exact math with an optional round-up-to-quarter
mode (property rounding rules vary — set to match yours). An admin page lets
trainers write house-specific questions (dollars or units) that mix into
Practice and can appear on the Floor Ready Test.

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
